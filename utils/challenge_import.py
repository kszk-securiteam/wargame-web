import json
import os
import re
import shutil
import time
from zipfile import ZipFile

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.files import File
from django.db import transaction

from wargame.models import Challenge, File as ChallengeFile
from wargame_admin.consumers import MessageType
from wargame_web.settings.base import MEDIA_ROOT
from utils.export_challenges import export_keys


def log(message, log_var, log_level):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(log_var, {"type": 'log_event', "message": message, 'level': log_level.name})


def do_challenge_import(file, dry_run, log_var):
    time.sleep(5)  # Wait for client to connect
    log("Staring challenge import", log_var, MessageType.INFO)

    if dry_run:
        log("Dry run: no changes will be saved", log_var, MessageType.WARNING)

    path = extract_zip(file, log_var)

    if path is None:
        return

    challenge_dir, challenge_names = find_challenge_dir(path, log_var)

    if not challenge_dir:
        log("Uploaded file does not contain challenges directory", log_var, MessageType.ERROR)
        return

    for challenge_name in challenge_names:
        # noinspection PyBroadException
        try:
            with transaction.atomic():
                import_challenge(challenge_dir, challenge_name, dry_run, log_var)
        except Exception as e:
            log(F"Exception during challenge import: {e}", log_var, MessageType.ERROR)

    # Cleanup: delete folder where the zip was extracted
    shutil.rmtree(path)
    os.remove(file)
    log("Challenge import completed", log_var, MessageType.SUCCESS)


def import_challenge(challenge_dir, challenge_name, dry_run, log_var):
    log(F"Importing challenge {challenge_name}", log_var, MessageType.INFO)
    challenge_path = os.path.join(challenge_dir, challenge_name)

    valid, import_setup, files = validate_challenge_structure(challenge_path, log_var)

    if not valid:
        return

    # Get or create challenge
    try:
        challenge = Challenge.objects.get(import_name=challenge_name)
    except Challenge.DoesNotExist:
        challenge = Challenge()
        challenge.import_name = challenge_name
        challenge.level = 1
        challenge.points = 0

    with open(os.path.join(challenge_path, "challenge.json"), encoding='utf-8-sig') as file:
        if not import_challenge_json(file, challenge, log_var):
            return

    with open(os.path.join(challenge_path, "description.md"), encoding='utf-8-sig') as file:
        challenge.description = file.read()

    with open(os.path.join(challenge_path, "solution.txt"), encoding='utf-8-sig') as file:
        challenge.solution = file.read()

    if import_setup:
        with open(os.path.join(challenge_path, "setup.txt"), encoding='utf-8-sig') as file:
            challenge.setup = file.read()

    if not dry_run:
        challenge.save()

    import_files(challenge, files, dry_run, log_var)

    log(F"Challenge imported: {challenge_name}", log_var, MessageType.SUCCESS)


def save_tags(challenge, tag_list):
    for tag in tag_list:
        challenge.tags.add(tag)
    challenge.save()


def import_files(challenge, files, dry_run, log_var):
    for file in files:
        filename = os.path.basename(file['path'])

        if challenge.files.filter(display_name=filename, private=file['private'], config_name=file['conf']).exists():
            log(F"Skipping import of file: {filename}", log_var, MessageType.WARNING)
            continue

        with open(os.path.join(file['path']), 'rb') as fp:
            challenge_file = ChallengeFile()
            challenge_file.challenge = challenge
            challenge_file.private = file['private']
            challenge_file.display_name = filename
            challenge_file.config_name = file['conf']
            if not dry_run:
                challenge_file.file.save(filename, File(fp))
                challenge_file.save()


def validate_challenge_structure(challenge_path, log_var):
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
                    log(F"Challenge directory contains unknown file: {file}", log_var, MessageType.ERROR)
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
                log(F"Challenge directory contains unknown directory: {os.path.basename(root)}", log_var, MessageType.ERROR)
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
        log("challenge.json not found", log_var, MessageType.ERROR)
        valid = False
    if not description_md_found:
        log(F"description.md not found", log_var, MessageType.ERROR)
        valid = False
    if not solution_txt_found:
        log(F"solution.txt not found", log_var, MessageType.ERROR)
        valid = False

    return valid, import_setup, challenge_files


def import_challenge_json(file, challenge, log_var):
    data = json.load(file)
    valid = True

    if not list(data.keys()) == export_keys:
        log("Error: challenges.json contains invalid keys or does not contain all keys", log_var, MessageType.ERROR)
        return False

    for key, value in data.items():
        challenge.__setattr__(key, value)

    if not re.match("^SECURITEAM{[a-f0-9]{32}}$", challenge.flag_qpa, re.RegexFlag.IGNORECASE):
        log("Invalid QPA flag format", log_var, MessageType.ERROR)
        valid = False

    if not re.match("^SECURITEAM{[a-f0-9]{32}}$", challenge.flag_hacktivity, re.RegexFlag.IGNORECASE):
        log("Invalid hacktivity flag format", log_var, MessageType.ERROR)
        valid = False

    return valid


def find_challenge_dir(path, log_var):
    for root, dirs, _ in os.walk(path):
        if os.path.basename(root) == "challenges":
            log(F"{len(dirs)} challenges found", log_var, MessageType.INFO)
            return root, dirs
    return None, None


def extract_zip(file, log_var):
    # noinspection PyBroadException
    try:
        path = os.path.join(MEDIA_ROOT, 'challenge-temp')
        with ZipFile(file) as archive:
            archive.extractall(path=path)
        return path
    except Exception as e:
        log(F"Error during zip extraction: {e}", log_var, MessageType.ERROR)
        return None
