import csv

from django.core.mail import send_mass_mail

from wargame.models import User
from django.utils.crypto import get_random_string


def do_user_import(file, dry_run):
    path = file.temporary_file_path()

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

    if not dry_run:
        send_mass_mail(messages)
