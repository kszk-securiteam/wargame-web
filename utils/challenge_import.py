import json
import os
import re
import shutil
import time
from zipfile import ZipFile

from django.core.files import File
from django.db import transaction

from utils.export_challenges import export_keys
from wargame.models import Challenge, File as ChallengeFile
from wargame_admin.consumers import MessageType, log
from wargame_web.settings.base import MEDIA_ROOT


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
            log(f"Exception during challenge import: {e}", log_var, MessageType.ERROR)

    # Cleanup: delete folder where the zip was extracted
    shutil.rmtree(path)
    os.remove(file)
    log("Challenge import completed", log_var, MessageType.SUCCESS)


def import_challenge(challenge_dir, challenge_name, dry_run, log_var):
    log(f"Importing challenge {challenge_name}", log_var, MessageType.INFO)
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
    else:
        log("Challenge already exists, replacng values", log_var, MessageType.WARNING)

    with open(os.path.join(challenge_path, "challenge.json"), encoding="utf-8-sig") as file:
        valid, tags = import_challenge_json(file, challenge, log_var)
        if not valid:
            return

    with open(os.path.join(challenge_path, "description.md"), encoding="utf-8-sig") as file:
        challenge.description = file.read()

    with open(os.path.join(challenge_path, "solution.txt"), encoding="utf-8-sig") as file:
        challenge.solution = file.read()

    if import_setup:
        with open(os.path.join(challenge_path, "setup.txt"), encoding="utf-8-sig") as file:
            challenge.setup = file.read()

    if not dry_run:
        challenge.save()
        challenge.tags.add(*tags)
        challenge.save()

    import_files(challenge, files, dry_run, log_var)

    log(f"Challenge imported: {challenge_name}", log_var, MessageType.SUCCESS)


def import_files(challenge, files, dry_run, log_var):
    for file in files:
        filename = os.path.basename(file["path"])
        file_entity = challenge.files.filter(filename=filename, private=file["private"], config_name=file["conf"])
        if file_entity.exists():
            log(f"{filename} already exists, deleting...", log_var, MessageType.WARNING)
            if not dry_run:
                file_entity.delete()
            continue

        with open(os.path.join(file["path"]), "rb") as fp:
            challenge_file = ChallengeFile()
            challenge_file.challenge = challenge
            challenge_file.private = file["private"]
            challenge_file.display_name = filename
            challenge_file.config_name = file["conf"]
            challenge_file.filename = filename
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
                    log(f"Challenge directory contains unknown file: {file}", log_var, MessageType.ERROR)
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
                log(f"Challenge directory contains unknown directory: {os.path.basename(root)}", log_var, MessageType.ERROR)
                continue
            for f in files:
                if f == ".gitkeep":
                    continue
                challenge_files.append({"private": private, "conf": conf, "path": os.path.join(root, f)})

    if not challenge_json_found:
        log("challenge.json not found", log_var, MessageType.ERROR)
        valid = False
    if not description_md_found:
        log(f"description.md not found", log_var, MessageType.ERROR)
        valid = False
    if not solution_txt_found:
        log(f"solution.txt not found", log_var, MessageType.ERROR)
        valid = False

    return valid, import_setup, challenge_files


def import_challenge_json(file, challenge, log_var):
    data = json.load(file)
    valid = True
    tags = []

    if not list(data.keys()) == export_keys:
        log("Error: challenges.json contains invalid keys or does not contain all keys", log_var, MessageType.ERROR)
        return False

    for key, value in data.items():
        if key == "tags":
            tags = value
        else:
            challenge.__setattr__(key, value)

    if not re.match("^SECURITEAM{[a-f0-9]{32}}$", challenge.flag_qpa, re.RegexFlag.IGNORECASE):
        log("Invalid QPA flag format", log_var, MessageType.ERROR)
        valid = False

    if not re.match("^SECURITEAM{[a-f0-9]{32}}$", challenge.flag_hacktivity, re.RegexFlag.IGNORECASE):
        log("Invalid hacktivity flag format", log_var, MessageType.ERROR)
        valid = False

    return valid, tags


def find_challenge_dir(path, log_var):
    for root, dirs, _ in os.walk(path):
        if os.path.basename(root) == "challenges":
            log(f"{len(dirs)} challenges found", log_var, MessageType.INFO)
            return root, dirs
    return None, None


def extract_zip(file, log_var):
    # noinspection PyBroadException
    try:
        path = os.path.join(MEDIA_ROOT, "challenge-temp")
        with ZipFile(file) as archive:
            archive.extractall(path=path)
        return path
    except Exception as e:
        log(f"Error during zip extraction: {e}", log_var, MessageType.ERROR)
        return None
