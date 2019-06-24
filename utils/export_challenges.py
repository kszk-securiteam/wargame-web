import json
import os
import shutil
import traceback

from wargame.models import Challenge
from wargame_admin.models import Export
from wargame_web.settings import base

export_keys = ["title", "flag_qpa", "flag_hacktivity", "hint", "short_description", "tags"]


def export_challenges():
    export = Export()
    export.save()
    export_folder_name = F"challenge-export-{export.started_at.strftime('%Y%m%d-%H%M%S')}"
    export_folder = None
    archive_path = None

    # noinspection PyBroadException
    try:
        export_folder = os.path.join(base.MEDIA_ROOT, export_folder_name)
        os.mkdir(export_folder)

        for c in Challenge.objects.all():
            # Load tags
            c.tags = list(c.tags.names())

            # Calculate directories
            challenge_folder = os.path.join(export_folder, "challenges",
                                            c.import_name or c.title.replace(" ", "_").encode('ascii', 'ignore').decode("ascii"))

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

                shutil.copy2(f.file.path, os.path.join(destination_path, f.filename))  # keep the original file name

        # Archive the export folder
        archive_path = shutil.make_archive(os.path.join(base.MEDIA_ROOT, export_folder_name), 'zip', export_folder)

        # Create media/exports/ folder
        os.makedirs(os.path.join(base.MEDIA_ROOT, "exports"), exist_ok=True)

        # Move the archive into the media/exports/ folder
        archive_path = shutil.move(archive_path, os.path.join(base.MEDIA_ROOT, "exports"))

        # Delete the export folder
        shutil.rmtree(export_folder)

        # Update the export entry in the database
        export.status = 'DONE'
        export.file.name = os.path.join(base.MEDIA_ROOT, "exports", archive_path)
        export.save()

    except Exception:
        log_path = os.path.join(base.MEDIA_ROOT, "exports", export_folder_name + "-log.txt")

        with open(log_path, 'w') as text_file:
            text_file.write(traceback.format_exc())

        export.status = 'ERROR'
        export.file.name = log_path
        export.save()

        # Clean up potential orphaned files
        if export_folder:
            shutil.rmtree(export_folder)

        if archive_path:
            os.remove(archive_path)
