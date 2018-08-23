import json

from django.db.models import Model, CharField, Manager


class ConfigManager(Manager):
    def is_qpa(self):
        return Config.objects.get(key='qpa_hack').value == 'qpa'

    def stage_tasks(self):
        return Config.objects.get(key='stage_tasks').get_int()


class Config(Model):
    key = CharField(max_length=255, primary_key=True)
    value = CharField(max_length=255)
    display_name = CharField(max_length=255)
    description = CharField(max_length=255, blank=True, default="")
    possible_values = CharField(max_length=500, blank=True, default="")
    objects = ConfigManager()

    def get_int(self):
        return int(self.value)

    def get_possible_values(self):
        if self.possible_values is "":
            return None
        return json.loads(self.possible_values)

    def set_possible_values(self, values):
        self.possible_values = json.dumps(values)
