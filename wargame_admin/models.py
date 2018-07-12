from django.db.models import Model, CharField


class Config(Model):
    key = CharField(max_length=255, primary_key=True),
    value = CharField(max_length=255)
