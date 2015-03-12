
class DuckDict(dict):
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            self[k] = v

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, item):
        return self[item]