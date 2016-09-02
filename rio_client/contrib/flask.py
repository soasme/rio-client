# -*- coding: utf-8 -*-

from __future__ import absolute_import

from collections import namedtuple

from flask import g
from flask import request
from flask import current_app
from werkzeug.utils import import_string

from rio_client.base import Client


class Current(namedtuple('Current', 'action project uuid')):
    pass

class Rio(object):
    """Flask extension for rio."""

    class Level:
        INSTANT = 0
        CONTEXTUAL = 1
        DELAY = 2

    def __init__(self, app=None, dsn=None):
        self.app = app
        if app is not None:
            self.init_app(app, dsn)

    def init_app(self, app, dsn=None):
        client_options = {}

        client_options['dsn'] = dsn or app.config.get('RIO_DSN')
        client_options['timeout'] = app.config.get('RIO_TIMEOUT')

        self.client = Client(**client_options)

        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['rio'] = self

        app.config.setdefault('RIO_DUMP_CLASS', 'rio_client.dump.redis.RedisDump')
        app.config.setdefault('RIO_DUMP_PARAMS', {})

        @app.before_request
        def before_request():
            g.rio_client_contextual = []

        @app.after_request
        def after_request(response):
            dumper = self.dumper
            for action, payload in g.rio_client_contextual:
                self.emit_instantly(action, payload)
                dumper.remove(action, payload)
            return response


    @property
    def dump_config(self):
        return {
            'class': current_app.config['RIO_CLIENT_DUMP_CLASS'],
            'params': current_app.config.get('RIO_CLIENT_DUMP_PARAMS', {}),
        }

    def emit(self, action, payload, level=Level.INSTANT):
        """Emit action."""
        if level == self.Level.INSTANT:
            return self.emit_instantly(action, payload)
        elif level == self.Level.CONTEXTUAL:
            return self.emit_contextually(action, payload)
        elif level == self.Level.DELAY:
            return self.emit_delayed(action, payload)
        else:
            raise Exception('InvalidEmitLevel: %s' % level)

    def emit_instantly(self, action, payload):
        """ Emit instantly. """
        return self.client.emit(action, payload)

    def emit_contextually(self, action, payload):
        """ Emit on exiting request context."""
        self.dump(action, payload)
        return g.rio_client_contextual.append((action, payload, ))

    def emit_delayed(self, action, payload):
        """ Emit by an independent worker."""
        self.dump(action, payload)

    def delay_emit(self):
        dumper = self.dumper
        while True:
            with dumper.next() as data:
                if not data:
                    break
                action, payload = data
                self.emit_instantly(action, payload)
                dumper.remove(action, payload)

    @property
    def dumper(self):
        dump_class_string = self.dump_config['class']
        dump_class = import_string(dump_class_string)
        dump_params = self.dump_config['params']
        return dump_class(**dump_params)

    def dump(self, action, payload):
        self.dumper.dump(action, payload)

    @property
    def current(self):
        """A namedtuple contains `uuid`, `project`, `action`.

        Example::

            @app.route('/webhook/broadcast-news')
            def broadcast_news():
                if rio.current.action.startswith('news-'):
                    broadcast(request.get_json())
        """
        event = request.headers.get('X-RIO-EVENT')
        data = dict([elem.split('=') for elem in event.split(',')])
        return Current(**data)
