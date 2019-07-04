import csv
import os
import time

from django.core.mail import send_mass_mail

from wargame.models import User
from django.utils.crypto import get_random_string

from wargame_admin.consumers import log, MessageType
from wargame_admin.models import StaticContent
from wargame_web.settings import base


def do_user_import(path, dry_run, log_var):
    time.sleep(5)  # Wait for client to connect
    log("Starting user import", log_var, MessageType.INFO)

    if dry_run:
        log("Dry run: no changes will be saved or emails sent", log_var, MessageType.WARNING)

    messages = []

    subject = StaticContent.objects.get(key="email_subject").html
    email_template = StaticContent.objects.get(key="email_text").html

    with open(path, "r", encoding="utf-8-sig") as fp:
        reader = csv.reader(fp, delimiter=",")
        for row in reader:
            team_name = row[0]
            email = row[1]
            password = get_random_string(16)

            if not dry_run:
                User.objects.create_user(team_name, email, password)

            message = email_template.replace("%TEAM%", team_name).replace("%PASSWORD%", password)
            messages.append((subject, message, base.EMAIL_FROM, [email]))

            log(f"Imported {team_name}", log_var, MessageType.SUCCESS)

    log("Sending emails...", log_var, MessageType.INFO)

    if not dry_run:
        send_mass_mail(messages)

    os.remove(path)
    log("User import complete", log_var, MessageType.SUCCESS)
