#! /usr/bin/env python2
#  -*- coding: utf-8 -*-
#
# fileupload.py - braindead file uploder. don't use. ever.
#
# Author: slowpoke <mail+git@slowpoke.io>
#
# This program is free software under the non-terms
# of the Anti-License. Do whatever the fuck you want.

import os
import json
import base64

from flask import Flask
from flask import request
from flask import render_template
from flask import session
from flask import redirect
from werkzeug import secure_filename

site = Flask(__name__)

UPLOAD_FOLDER = "."
ALLOWED_EXT = set(["png", "jpeg", "jpg", "gif"])
USERS = {}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXT


def load_users(file):
    '''(Re)load the users.json file.'''
    if not os.access(file, os.F_OK):
        return
    with open(file) as f:
        global USERS
        try:
            USERS = json.load(f)
        except ValueError:
            return  # no, we really don't care


def save_users(file):
    '''Save the users.json file.'''
    with open(file, 'w') as f:
        json.dump(USERS, f)


@site.route("/adduser", methods=["GET", "POST"])
def add_user():
    '''Add a new user with a randomly generated key and return the key.'''
    if not session.get("loggedin", False):
        return '''gtfo'''
    if request.method == "POST":
        user = request.form.get("user")
        if not user:
            return '''wat'''
        else:
            global USERS
            USERS[user] = base64.encodestring(os.urandom(24)).decode().strip("\n")
            save_users("users.json")
            return '''{0}'s key is now {1}'''.format(user, USERS[user])
    else:
        return render_template("adduser.html")


@site.route("/login", methods=["GET", "POST"])
def login():
    if session.get("loggedin", False):
        return redirect("/status")
    if request.method == "POST":
        user = request.form.get("user").strip("\n")
        if not user:
            return render_template("login.html", nouser=True)
        if not user in USERS.keys():
            return render_template("login.html", unknown_user=True)
        passwd = request.form.get("pass")
        print(passwd)
        print(USERS[user])
        if not passwd:
            return render_template("login.html", nopass=True)
        if passwd == USERS[user]:
            session["loggedin"] = True
            return render_template("login.html", login=True, success=True,
                                   user=user)
        else:
            return render_template("login.html", login=True, success=False)
    else:
        return render_template("login.html")


@site.route("/logout")
def logout():
    if not session.get('loggedin', False):
        return '''Wat. I don't know you.'''
    else:
        session["loggedin"] = False
        return '''Bye.'''


@site.route("/status")
def status():
    return render_template("status.html",
                           loggedin=session.get("loggedin", False))


@site.route("/upload", methods=["GET", "POST"])
def upload():
    if not session.get("loggedin", False):
        return '''Nothing to see here, move along.'''
    if request.method == "POST":
        file = request.files["file"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(site.config["UPLOAD_FOLDER"], filename))
            return render_template("upload.html", uploaded=True, success=True)
        else:
            return render_template("upload.html", uploaded=True, success=False)
    else:
        return render_template("upload.html", uploaded=False)
    return


if __name__ == "__main__":
    load_users("users.json")
    site.secret_key = os.urandom(24)
    site.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    site.run()
