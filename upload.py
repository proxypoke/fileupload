#! /usr/bin/env python2
#  -*- coding: utf-8 -*-
#
# fileuploader - braindead file uploader. don't use. ever.
#
# Author: slowpoke <mail+git@slowpoke.io>
#
# This program is free software under the non-terms
# of the Anti-License. Do whatever the fuck you want.

from __future__ import print_function

import requests
import argparse
import os
import json


def login(url, user, passwd):
    '''Get session cookies.'''
    print(url, user, passwd)
    r = requests.post(url, data={"user": user, "pass": passwd})
    r.raise_for_status()
    return r.cookies


def upload(url, filename, cookies):
    '''Upload a given file. Return the url of the uploaded file.'''
    with open(filename, 'r') as file:
        r = requests.post(url, files={"file": file}, cookies=cookies)
        r.raise_for_status()
        return r.url


def look_for_config():
    '''See if we can find a config.'''
    rc_path = os.path.join(os.getenv("HOME"), ".fileuploadrc")
    if os.path.exists(rc_path):
        return rc_path
    rc_path = os.path.join(os.curdir, "fileuploadrc")
    if os.path.exists(rc_path):
        return rc_path
    return None


def load_config(file):
    '''Load the config from the given file.'''
    with open(file) as cfile:
        return json.load(cfile)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("files", type=str, help="the files to upload",
                        nargs="+")
    parser.add_argument("-u", "--user", type=str, help="user for the server")
    parser.add_argument("-p", "--pass", type=str, help="password for the server",
                        dest="passwd")
    parser.add_argument("-w", "--url", type=str, help="base url of the server")

    args = parser.parse_args()

    v = vars(args)
    url = v.get("url")
    user = v.get("user")
    passwd = v.get("pass")

    cfile = look_for_config()
    if cfile:
        config = load_config(cfile)
        url = config.get("url") if not url else url
        user = config.get("user") if not user else user
        passwd = config.get("pass") if not passwd else passwd
    else:
        print("No config found.")

    if not all((url, user, passwd)):
        print("Error: missing one of url, user or password.")
        exit(1)

    loginurl = os.path.join(url, "login")
    cookies = login(loginurl, user, passwd)
    for file in args.files:
        try:
            uploadurl = os.path.join(url, "upload")
            finalurl = upload(uploadurl, file, cookies)
            print("File uploaded: {0}".format(finalurl))
        except Exception as e:
            print("Failed to upload {0}: {1}".format(file, e))

if __name__ == "__main__":
    main()
