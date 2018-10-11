import json
import os
import re
import shutil
from enum import Enum
from zipfile import ZipFile

from django.core.files import File
from django.db import transaction

from wargame.models import Challenge, Tag, File as ChallengeFile
from wargame_web.settings.base import MEDIA_ROOT
from utils.export_challenges import export_keys

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

    valid, import_setup, files = validate_challenge_structure(challenge_path)

    if not valid:
        return

    # Get or create challenge
    try:
        challenge = Challenge.objects.get(import_name=challenge_name)
    except Challenge.DoesNotExist:
        challenge = Challenge()
        challenge.import_name = challenge_name

    with open(os.path.join(challenge_path, "challenge.json"), encoding='utf-8-sig') as file:
        if not import_challenge_json(file, challenge):
            return

    with open(os.path.join(challenge_path, "description.md"), encoding='utf-8-sig') as file:
        challenge.description = file.read()

    with open(os.path.join(challenge_path, "solution.txt"), encoding='utf-8-sig') as file:
        challenge.solution = file.read()

    if import_setup:
        with open(os.path.join(challenge_path, "setup.txt"), encoding='utf-8-sig') as file:
            challenge.setup = file.read()

    challenge.save()

    import_files(challenge, files)

    messages.append((MessageType.SUCCESS, F"Challenge imported: {challenge_name}"))


def save_tags(challenge, tag_list):
    for tag in tag_list:
        challenge.tags.add(tag)
    challenge.save()


def import_files(challenge, files):
    for file in files:
        filename = os.path.basename(file['path'])

        if challenge.files.filter(display_name=filename, private=file['private'], config_name=file['conf']).exists():
            messages.append((MessageType.WARNING, "Skipping import of file: " + filename))
            continue

        with open(os.path.join(file['path']), 'rb') as fp:
            challenge_file = ChallengeFile()
            challenge_file.challenge = challenge
            challenge_file.private = file['private']
            challenge_file.display_name = filename
            challenge_file.config_name = file['conf']
            challenge_file.file.save(filename, File(fp))
            challenge_file.save()


def validate_challenge_structure(challenge_path):
    valid = True
    import_setup = False
    challenge_files = []

    challenge_json_found = False
    description_md_found = False
    solution_txt_found = False

    for root, dirs, files in os.walk(challenge_path):
        if root == challenge_path:
            for file in files:
                if file == "challenge.json":
                    challenge_json_found = True
                elif file == "description.md":
                    description_md_found = True
                elif file == "solution.txt":
                    solution_txt_found = True
                elif file == "setup.txt":
                    import_setup = True
                else:
                    valid = False
                    messages.append((MessageType.ERROR, "Challenge directory contains unknown file"))
        else:
            private = False
            config_folder = root
            if os.path.basename(root) == "private":
                private = True
                config_folder = os.path.dirname(root)

            if os.path.basename(config_folder) == "qpa-files":
                conf = "qpa"
            elif os.path.basename(config_folder) == "hacktivity-files":
                conf = "hacktivity"
            else:
                valid = False
                messages.append((MessageType.ERROR, "Challenge directory structure contain unknown directory: " + os.path.basename(root)))
                continue
            for f in files:
                if f == ".gitkeep":
                    continue
                challenge_files.append({
                    'private': private,
                    'conf': conf,
                    'path': os.path.join(root, f)
                })

    if not challenge_json_found:
        messages.append((MessageType.ERROR, "challenge.json not found"))
        valid = False
    if not description_md_found:
        messages.append((MessageType.ERROR, "description.md not found"))
        valid = False
    if not solution_txt_found:
        messages.append((MessageType.ERROR, "solution.txt not found"))
        valid = False

    return valid, import_setup, challenge_files


def import_challenge_json(file, challenge):
    data = json.load(file)
    valid = True

    if not list(data.keys()) == export_keys:
        messages.append((MessageType.ERROR, "Error: challenges.json contains invalid keys or does not contain all keys"))
        return False

    for key, value in data.items():
        challenge.__setattr__(key, value)

    if not re.match("^SECURITEAM{[a-f0-9]{32}}$", challenge.flag_qpa, re.RegexFlag.IGNORECASE):
        messages.append((MessageType.ERROR, "Invalid QPA flag format"))
        valid = False

    if not re.match("^SECURITEAM{[a-f0-9]{32}}$", challenge.flag_hacktivity, re.RegexFlag.IGNORECASE):
        messages.append((MessageType.ERROR, "Invalid hacktivity flag format"))
        valid = False

    return valid


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
