# -*- coding: utf-8 -*-

from flask import Flask, request
from rio_client.contrib.flask import Rio

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'no-secret'
app.config['RIO_DSN'] = 'http://docker:dummy@192.168.99.100:5010/1/project'
app.config['RIO_TIMEOUT'] = 3
app.config['RIO_CLIENT_DUMP_PARAMS'] = {'port': 6379, 'host': 'localhost', 'db': 0, 'key': 'rio-client-example'}


rio = Rio()
rio.init_app(app)

@app.route('/admin')
def index():
    rio.emit('admin.visit', {'ip': request.remote_addr}, rio.Level.DELAY)
    return 'hello world'

if __name__ == '__main__':
    import sys
    if sys.argv[1] == 'runserver':
        app.run(debug=True)
    elif sys.argv[1] == 'runriodelayed':
        with app.app_context():
            rio.delay_emit()
