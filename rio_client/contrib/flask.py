# -*- coding: utf-8 -*-

from __future__ import absolute_import

from collections import namedtuple

from flask import request

from rio_client.base import Client


class Current(namedtuple('Current', 'action project uuid')):
    pass

class Rio(object):
    """Flask extension for rio."""

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


    def emit(self, action, payload, level='instant'):
        """Emit action."""
        if level == 'instant':
            return self.emit_instantly(action, payload)
        elif level == 'session':
            return self.emit_context(action, payload)
        elif level == 'later':
            return self.emit_delayed(action, payload)
        else:
            raise Exception('InvalidEmitLevel: %s' % level)

    def emit_instantly(self, action, payload):
        """ Emit instantly. """
        return self.client.emit(action, payload)

    def emit_context(self, action, payload):
        """ Emit on exiting request context."""
        pass

    def emit_delayed(self, action, payload):
        """ Emit by an independent worker."""
        pass

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
