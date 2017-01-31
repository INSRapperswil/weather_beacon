import ujson


class Settings(object):
    def __init__(self, settings_file):
        self.settings_file = settings_file

    def get(self, key):
        with open(self.settings_file, 'r') as fp:
            data = ujson.load(fp)
            try:
                return data[key]
            except KeyError:
                return ''

    def set(self, key, value):
        data = None
        with open(self.settings_file, 'r') as fp:
            data = ujson.load(fp)

        with open(self.settings_file, 'w') as fp:
            data[key] = value
            json_data = ujson.dumps(data)
            fp.write(json_data)
