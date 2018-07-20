#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   Copyright: © 2018 hualee215@gmail.com and contributors
#
import getopt
import sys
import os
import git
import yaml

__version__ = "0.1"


def usage():
    help = """
usage gitcheckadd options

Basic Options: 
     -d,--dest  new commit,required
     -p,--path  git repo path,required
     -s,--source source commit,required
     -t,--ctype   ctype support  tag,commit and branch
     -h,--help  print usage information for this commad  
     -v,--verbose print debug info

example:
     
  compare commit id 032d and 7099
     
     >gitcheckadd -t commit -s 7099fa4adf80fecf72c3c4ef1bc97770eaecd41f -d 032d3b53fb40e978148326a4ed397b9c1b24f855 /home/joe/gitrepo/testrepo
  
  compare branch dev and master 
     
     >gitcheckadd -t branch -s dev -d master /home/joe/gitrepo/testrepo
  
  compare tag v1.1 and v1.0
     
     >gitcheckadd -t tag -s v1.1 -d v1.0 /home/joe/gitrepo/testrepo
  
    """.format(file=__file__)

    print(help)


global gfile_whitelist
global gfile_max_size
global gmime_blacklist

gfile_whitelist = set(["gradle/wrapper/gradle-wrapper.jar", "maven/maven-wrapper.jar"])
gfile_max_size = 1024000
gmime_blacklist = set(["application/docx", "application/java-archive", "java-serialized-object", "java-vm"])


def compare_commit(source_commit, dest_commit):
    errlist = []
    try:
        for diff_added in dest_commit.diff(source_commit).iter_change_type('A'):
            strFile = diff_added.a_rawpath
            size = diff_added.b_blob.size
            mime_type = diff_added.b_blob.mime_type

            if mime_type in gmime_blacklist:
                if strFile not in gfile_whitelist:
                    errlist.append(dict({"path": strFile, "size": size, "type": mime_type}))

    except Exception, err:
        print("execute compare error", err)
        sys.exit(1)
    return errlist


def compare(ctype, source, dest, repo_path):
    try:
        repo = git.Repo(repo_path)

        if ctype == "tag" or ctype == "branch" or ctype == "commit":
            source_commit = repo.commit(source)
            dest_commit = repo.commit(dest)
            return compare_commit(source_commit, dest_commit)
        elif ctype == "patchset":
            tcommit = list(repo.iter_commits(max_count=2))
            source_commit = tcommit[0]
            dest_commit = tcommit[-1]
            return compare_commit(source_commit, dest_commit)
        else:
            print("not support type {0}".format(ctype))
            sys.exit(1)

    except Exception, err:
        print("execute compare error", err)
        sys.exit(1)


def init():
    defaultpath = "/etc/gitcheckadd/config.yaml"
    config = ""
    err_message = ""
    if os.path.exists(defaultpath):
        stream = file(defaultpath, 'r')
        config = yaml.load(stream)
    elif os.path.exists(os.path.join(os.getcwd(), "../config.yaml")):
        stream = file(os.path.join(os.getcwd(), "../config.yaml"), 'r')
        config = yaml.load(stream)
    else:
        print("config file not found.")
        sys.exit(1)
    if config:
        if config.has_key("file_whitelist") and config["file_whitelist"]:
            global gfile_whitelist
            gfile_whitelist = set(config["file_whitelist"])
        else:
            err_message = err_message + " file_whitelist is not config\n"

        if config.has_key("mime_blacklist") and config["mime_blacklist"]:
            global gmime_blacklist
            gmime_blacklist = set(config["mime_blacklist"])
        else:
            err_message = err_message + " mime_blacklist is not config\n"

        if config.has_key("file_max_size") and config["file_max_size"]:
            global gfile_max_size
            gfile_max_size = config["file_max_size"]
    else:
        err_message = "config.yaml parser error"

    if not (err_message == ""):
        print(err_message)
        sys.exit(1)

    print("init is over")


def main():
    dest = ""
    source = ""
    path = ""
    ctype = ""

    if len(sys.argv[1:]) < 1:
        usage()
        sys.exit(1)

    try:
        options, args = getopt.getopt(sys.argv[1:], "hvd:s:t:p:",
                                      ["help", "verbose", "dest=", "source=", "type=", "path="])
    except getopt.GetoptError:
        sys.exit(1)

    for option, value in options:
        if option in ("-h", "--help"):
            usage()
        if option in ("-d", "--dest"):
            dest = value
        if option in ("-s", "--source"):
            source = value
        if option in ("-t", "--type"):
            ctype = value
        if option in ("-p", "--path"):
            path = value

    if ctype and ctype != "patchset" and (dest == "" or source == ""):
        print("dest or source is null")
        usage()
        sys.exit(1)

    if not os.path.exists(path):
        print("path : {0} is not exit.".format(path))
        usage()
        sys.exit(1)

    init()

    result = compare(ctype, source, dest, path)

    if result and len(result) > 0:
        print(result)
        sys.exit(1)


if __name__ == '__main__':
    main()
