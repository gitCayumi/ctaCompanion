from app import app
from flask import render_template, url_for, flash, redirect, request
from app.models import User


@app.route('/resources/', methods=['GET'])
def resources():
    return render_template('resources.html', title='Guides', resources_active=1)


@app.route('/quick_start/', methods=['GET'])
def quick_start():
    return render_template('qsg.html', title='Quickstart Guide', resources_active=1)
