from django.conf import settings

class SettingsForTemplates(object):
    def __init__(self):
        self._settings = {
            key: getattr(settings, key)
            for key in settings.SETTINGS_FOR_TEMPLATES
        }

    def __getattr__(self, name):
        return self._settings[name]


def settings_for_templates(request):
    return {
        'settings': SettingsForTemplates(),
    }
