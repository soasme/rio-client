# -*- coding: utf-8 -*-

class SQLAlchemyDump(object):

    def dump(self, action, payload):
        raise NotImplementedError

class RedisDump(object):

    def __init__(self, host, port, db, key):
        self.redis = Redis(host=host, port=port, db=db)
        self.key= key

    def dump(self, action, payload):
        self.redis.lpush(self.key, json.dumps({'action': action, 'payload': payload}))

    def load_next(self):
        data = self.redis.lindex(self.key, 0)
        if data:
            data = json.loads(data)
            return data.get('action'), data.get('payload')
