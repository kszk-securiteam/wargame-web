import os
import re
import shutil
from enum import Enum
from zipfile import ZipFile

from django.core.files import File
from django.db import transaction

from wargame.models import Challenge, Tag, File as ChallengeFile
from wargame_web.settings.base import MEDIA_ROOT

messages = []


class MessageType(Enum):
    ERROR = 0,
    WARNING = 1,
    INFO = 2,
    SUCCESS = 3


def do_challenge_import(file):
    global messages
    messages = []  # Clear message list

    path = extract_zip(file)

    if path is None:
        return messages

    challenge_dir, challenge_names = find_challenge_dir(path)

    if not challenge_dir:
        messages.append((MessageType.ERROR, 'Uploaded file does not contain challenges directory'))
        return messages

    challenge_names = remove_imported(challenge_names)

    for challenge_name in challenge_names:
        # noinspection PyBroadException
        try:
            with transaction.atomic():
                import_challenge(challenge_dir, challenge_name)
        except Exception as e:
            messages.append((MessageType.ERROR, F"Exception during challenge import: {e}"))

    # Cleanup: delete folder where the zip was extracted
    shutil.rmtree(path)
    return messages


def import_challenge(challenge_dir, challenge_name):
    messages.append((MessageType.INFO, F"Importing challenge {challenge_name}..."))
    challenge_path = os.path.join(challenge_dir, challenge_name)

    valid, import_setup, public_files, private_files = validate_challenge(challenge_path)

    if not valid:
        return

    challenge = Challenge()
    challenge.import_name = challenge_name

    with open(os.path.join(challenge_path, "challenge.txt"), encoding='utf-8-sig') as file:
        success, tag_list = import_challenge_txt(file, challenge)
        if not success:
            return

    with open(os.path.join(challenge_path, "description.md"), encoding='utf-8-sig') as file:
        challenge.description = file.read()

    with open(os.path.join(challenge_path, "solution.txt"), encoding='utf-8-sig') as file:
        challenge.solution = file.read()

    if import_setup:
        with open(os.path.join(challenge_path, "setup.txt"), encoding='utf-8-sig') as file:
            challenge.setup = file.read()

    challenge.save()
    import_files(challenge, challenge_path, public_files, private=False)
    import_files(challenge, challenge_path, private_files, private=True)
    save_tags(challenge, tag_list)
    messages.append((MessageType.SUCCESS, F"Challenge imported: {challenge_name}"))


def save_tags(challenge, tag_list):
    for tag in tag_list:
        challenge.tags.add(tag)
    challenge.save()


def import_files(challenge, challenge_path, file_names, private):
    if private:
        challenge_path = os.path.join(challenge_path, "private")

    for file in file_names:
        with open(os.path.join(challenge_path, file), 'rb') as fp:
            challenge_file = ChallengeFile()
            challenge_file.challenge = challenge
            challenge_file.private = private
            challenge_file.display_name = file
            challenge_file.file.save(file, File(fp))
            challenge_file.save()


def validate_challenge(challenge_path):
    valid = True
    import_setup = False
    public_files = []
    private_files = []

    _, dirs, files = os.walk(challenge_path).__next__()

    # Process private files
    if dirs:
        if len(dirs) > 1:
            messages.append((MessageType.ERROR, "Challenge directory contains more than one folder"))
            valid = False
        else:
            private_dir = dirs[0]
            if private_dir != 'private':
                messages.append((MessageType.ERROR, "Challenge directory contains directory other than private"))
                valid = False
            else:
                _, private_directories, private_files = os.walk(os.path.join(challenge_path, private_dir)).__next__()
                if private_directories:
                    messages.append((MessageType.ERROR, "Private files directory cannot contain directories"))
                    valid = False

    challenge_txt_found = False
    description_md_found = False
    solution_txt_found = False

    for file in files:
        if file == "challenge.txt":
            challenge_txt_found = True
        elif file == "description.md":
            description_md_found = True
        elif file == "solution.txt":
            solution_txt_found = True
        elif file == "setup.txt":
            import_setup = True
        else:
            public_files.append(file)

    if not challenge_txt_found:
        messages.append((MessageType.ERROR, "challenge.txt not found"))
        valid = False
    if not description_md_found:
        messages.append((MessageType.ERROR, "description.md not found"))
        valid = False
    if not solution_txt_found:
        messages.append((MessageType.ERROR, "solution.txt not found"))
        valid = False

    return valid, import_setup, public_files, private_files


def import_challenge_txt(file, challenge):
    tag_list = []
    for line in file:
        if line.isspace():
            continue
        line = line.strip()

        m = re.match(r"(\w+): (\S.*)", line)
        if not m:
            messages.append((MessageType.ERROR, F'Cannot parse line "{line}" in challenge.txt'))
            return False, None

        if m.group(1) == "Title":
            challenge.title = m.group(2)
        elif m.group(1) == "Level":
            try:
                challenge.level = int(m.group(2))
            except ValueError:
                messages.append((MessageType.ERROR, "Could not parse level in challenge.txt"))
                return False, None
        elif m.group(1) == "Flag":
            challenge.flag_qpa = m.group(2)
        elif m.group(1) == "Points":
            try:
                challenge.points = int(m.group(2))
            except ValueError:
                messages.append((MessageType.ERROR, "Could not parse points in challenge.txt"))
                return False, None
        elif m.group(1) == "Hint":
            challenge.hint = m.group(2)
        elif m.group(1) == "Tags":
            for s in m.group(2).split(','):
                tag, created = Tag.objects.get_or_create(name=s.strip())
                if created:
                    messages.append((MessageType.SUCCESS, F"Created new tag: {tag.name}"))
                    tag.save()
                tag_list.append(tag)
        elif m.group(1) == "ShortDesc":
            challenge.short_description = m.group(2)
        else:
            messages.append((MessageType.ERROR, F"Unrecognized variable in challenge.txt: {m.group(1)}"))
            return False, None
    return True, tag_list


def remove_imported(challenge_names):
    imported_challenges = Challenge.objects.filter(import_name__isnull=False).values_list('import_name', flat=True)
    skipped_challenges = set(imported_challenges).intersection(challenge_names)

    for c in skipped_challenges:
        messages.append((MessageType.WARNING, F'Challenge "{c}" already imported, skipping...'))

    return [c for c in challenge_names if c not in skipped_challenges]


def find_challenge_dir(path):
    for root, dirs, _ in os.walk(path):
        if os.path.basename(root) == "challenges":
            messages.append((MessageType.INFO, F'{len(dirs)} challenges found'))
            return root, dirs
    return None, None


def extract_zip(file):
    # noinspection PyBroadException
    try:
        zip_path = file.temporary_file_path()
        path = os.path.join(MEDIA_ROOT, 'challenge-temp')
        with ZipFile(zip_path) as archive:
            archive.extractall(path=path)
        return path
    except Exception as e:
        messages.append((MessageType.ERROR, F"Error during zip extraction: {e}"))
        return None
