#! /usr/bin/env python2
#  -*- coding: utf-8 -*-
#
# fileuploader - braindead file uploader. don't use. ever.
#
# Author: slowpoke <mail+git@slowpoke.io>
#
# This program is free software under the non-terms
# of the Anti-License. Do whatever the fuck you want.

import requests
import argparse


def login(url, user, passwd):
    '''Get session cookies.'''
    r = requests.post(url, data={"user": user, "pass": passwd})
    r.raise_for_status()
    return r.cookies


def upload(url, filename, cookies):
    '''Upload a given file. Return the url of the uploaded file.'''
    with open(filename, 'r') as file:
        r = requests.post(url, files={"file": file}, cookies=cookies)
        r.raise_for_status()
        return r.url


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("files", type=str, help="the files to upload",
                        nargs="+")
    parser.add_argument("-u", "--user", type=str, help="user for the server",
                        required=True)
    parser.add_argument("-p", "--pass", type=str, help="password for the server",
                        required=True, dest="passwd")

    args = parser.parse_args()

    url = "http://i.slowpoke.io"
    cookies = login(url + "/login", args.user, args.passwd)
    for file in args.files:
        try:
            url = upload(url + "/upload", file, cookies)
            print("File uploaded: {0}".format(url))
        except Exception as e:
            print("Failed to upload {0}: {1}".format(url, e))

if __name__ == "__main__":
    main()
