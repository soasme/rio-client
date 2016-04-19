# -*- coding: utf-8 -*-

from flask import Flask
from rio_client.contrib.flask import Rio

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'no-secret'
app.config['RIO_DSN'] = 'http://docker:dummy@192.168.99.100:5010/1/project'
app.config['RIO_TIMEOUT'] = 3


rio = Rio()
rio.init_app(app)

if __name__ == '__main__':
    with app.app_context():
        print rio.emit('scrapy-item-scraped', {'item': {'type': 'sale'}})
