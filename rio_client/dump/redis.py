# -*- coding: utf-8 -*-

from __future__ import absolute_import

import json
from contextlib import contextmanager

import redis

class RedisDump(object):

    def __init__(self, host, port, db, key):
        self.redis = redis.Redis(host=host, port=port, db=db)
        self.key= key

    def dump(self, action, payload):
        self.redis.lpush(self.key, json.dumps({'action': action, 'payload': payload}))

    @contextmanager
    def next(self):
        raw_data = self.redis.lindex(self.key, 0)
        if raw_data:
            data = json.loads(raw_data)
            yield data.get('action'), data.get('payload')
            self.remove(data.get('action'), data.get('payload'))
        else:
            yield None

    def remove(self, action, payload):
        self.redis.lrem(self.key, json.dumps({'action': action, 'payload': payload}))
