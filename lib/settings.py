import ujson

class Settings(object):
    def __init__(self,  settings_file):
        self.settings_file = settings_file
        
    def get(self,  key):
        with open(self.settings_file,  'r') as fp:
            data = ujson.load(fp)
            return data[key]
        
    def set(self,  key,  value):
        with open(self.settings_file,  'w') as fp:
            data = ujson.load(fp)
            data[key] = value
            json_data = ujson.dumps(data)
            # TODO maybe necessary to rewind fp
            fp.write(json_data)
