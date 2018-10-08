import os
import json
import shutil
import datetime
import time

from wargame_web.settings import base
from wargame.models import Challenge

export_keys = ["title", "flag_qpa", "flag_hacktivity", "hint", "short_description"]


def export_challenges():
    export_folder_name = F"challenge-export-{datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d-%H%M%S')}"
    export_folder = os.path.join(base.MEDIA_ROOT, export_folder_name)
    os.mkdir(export_folder)

    for c in Challenge.objects.all():
        # Calculate directories
        challenge_folder = os.path.join(export_folder, "challenges", c.import_name or c.title.encode('ascii', 'ignore').replace(" ", "_"))

        qpa_folder = os.path.join(challenge_folder, "qpa-files")
        private_qpa_folder = os.path.join(qpa_folder, "private")

        hack_folder = os.path.join(challenge_folder, "hacktivity-files")
        private_hack_folder = os.path.join(hack_folder, "private")

        # Recursively create challenge directories
        os.makedirs(private_qpa_folder)
        os.makedirs(private_hack_folder)

        # Create .gitkeep files
        open(os.path.join(private_qpa_folder, ".gitkeep"), "w+").close()
        open(os.path.join(private_hack_folder, ".gitkeep"), "w+").close()

        # Export setup file, if it exists
        if c.setup:
            with open(os.path.join(challenge_folder, "setup.txt"), "w", encoding='utf-8-sig') as setup_file:
                setup_file.write(c.setup)

        # Export solution file
        with open(os.path.join(challenge_folder, "solution.txt"), "w", encoding='utf-8-sig') as solution_file:
            solution_file.write(c.solution)

        # Export description file
        with open(os.path.join(challenge_folder, "description.md"), "w", encoding='utf-8-sig') as description_file:
            description_file.write(c.description)

        # Export challenge metadata file
        with open(os.path.join(challenge_folder, "challenge.json"), "w", encoding='utf-8-sig') as challenge_file:
            challenge_file.write(json.dumps({key: c.__dict__[key] for key in export_keys}))

        # Copy challenge files to appropriate directories
        for f in c.files.all():
            if f.config_name == 'qpa':
                if f.private:
                    destination_path = private_qpa_folder
                else:
                    destination_path = qpa_folder
            else:
                if f.private:
                    destination_path = private_hack_folder
                else:
                    destination_path = hack_folder

            shutil.copy2(f.file.path, destination_path)

    # Archive the export folder
    shutil.make_archive(os.path.join(base.MEDIA_ROOT, export_folder_name), 'zip', export_folder)

    # Delete the export folder
    shutil.rmtree(export_folder)

    return F"{export_folder_name}.zip"

