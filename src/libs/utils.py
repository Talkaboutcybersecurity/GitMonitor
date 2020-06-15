import os
import json
import datetime
from parse.config import get_file_config


def get_config(config_file):
    if not os.path.exists(config_file):
        print("Can not find " + config_file)
        exit()
    return get_file_config(config_file)


def exists_file(filename):
    if not os.path.isfile(filename):
        return False
    return True


def exists_dir(path):
    if not os.path.exists(path):
        return False
    return True


def write_file(filename, log):
    with open(filename, 'w') as f:
        json.dump(log, f)
    f.close()


def get_json(log_name):
    log = {}
    if exists_file(log_name):
        with open(log_name) as f:
            log = f.read()
            log = json.loads(log)
            f.close()
    return log


def get_extension(filename):
    tmp = filename.split(".")
    l = len(tmp)
    return tmp[l-1]


def get_filename(path2file):
    tmp = path2file.split("/")
    l = len(tmp)
    return tmp[l-1]


def get_time():
    current = datetime.datetime.now()
    time = current.strftime("%d/%m/%Y")
    return time


def initialization(config_file):
    conf = get_config(config_file)
    if not conf['path_source'] or not conf['path_rule'] or not conf['path_log'] or not conf['slack_webhooks']:
        print("ERROR: Make sure you have defined all the information in the configuration file - config.ini")
        exit(1)
    else:
        if not exists_dir(conf['path_source']):
            os.mkdir(conf['path_source'])
        if not exists_dir(conf['path_log']):
            os.mkdir(conf['path_log'])
        if not exists_dir(conf['path_rule']):
            print("ERROR: Not found rule folder.")
            exit(1)
        conf['path_source'] = conf['path_source'].rstrip("/")
    return conf


def readfile(filename):
    with open(filename) as f:
        contents = f.readlines()
    return contents

