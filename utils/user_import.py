import csv
import time

from django.core.mail import send_mass_mail

from wargame.models import User
from django.utils.crypto import get_random_string

from wargame_admin.consumers import log, MessageType


def do_user_import(path, dry_run, log_var):
    time.sleep(5)  # Wait for client to connect
    log("Starting user import", log_var, MessageType.INFO)

    if dry_run:
        log("Dry run: no changes will be saved or emails sent", log_var, MessageType.WARNING)

    messages = []

    with open(path, 'r', encoding='utf-8-sig') as fp:
        reader = csv.reader(fp, delimiter=",")
        for row in reader:
            team_name = row[0]
            email = row[1]
            password = get_random_string(16)

            if not dry_run:
                User.objects.create_user(team_name, email, password)

            message = F"""Kedves Csapatkapitány!
Elindult a SecurITeam által szervezett Wargame, ahol további értékes pontokat szerezhettek a Schönherz QPA-ra! 
A feladatokat a https://wargame.sch.bme.hu/ oldalon érhetitek el.
A csapatod felhasználóneve: {team_name}
És jelszava: {password}
Jó szórakozást!"""
            subject = "Elindult a Wargame!"
            messages.append((subject, message, "SecurITeam Wargame <securiteam.wargame2018@gmail.com>", [email]))
            log(F"Imported {team_name}", log_var, MessageType.SUCCESS)

    log("Sending emails...", log_var, MessageType.INFO)

    if not dry_run:
        send_mass_mail(messages)

    log("User import complete", log_var, MessageType.SUCCESS)
