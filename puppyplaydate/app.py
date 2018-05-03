# -*- coding: utf-8 -*-
# Flask Setup
from flask import Flask, render_template
app = Flask(__name__)

# Templating Setup
from jinja2 import Environment, PackageLoader, select_autoescape
env = Environment(
    loader=PackageLoader('puppyplaydate', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

# Routing
@app.route("/")
def home():
    t = env.get_template('home.html')
    return t.render()
