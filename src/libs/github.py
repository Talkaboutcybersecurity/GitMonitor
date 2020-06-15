import requests
import json
import math
import git
import time
import os
from libs.init import list_info
from libs.utils import write_file
from libs.slack import send_message
from libs.directory import handle_directory


def handle_error_search(repo, conf):
    if repo['message'] == "Validation Failed":
        return True
    elif "API rate limit exceeded for user" in repo['message'] or "You have triggered an abuse detection mechanism" in repo['message']:
        time.sleep(15)
        return False
    else:
        send_message("*ERROR*: {}".format(repo['message']), conf)
        exit()


def search_repository(query, conf, typ, uri=""):
    git_user = os.environ.get('GIT_USERNAME')
    git_pass = os.environ.get('GIT_PASSWORD')
    if git_pass is None or git_pass is None:
        if not conf['git_user'] or not conf['git_pass']:
            print('ERROR: Make sure you have defined github credential in the ENV or config file - config.ini')
            exit(1)
        else:
            git_user = conf['git_user']
            git_pass = conf['git_pass']

    url = conf['git_url_' + typ].format(query) + uri
    headers = {"Accept": "application/vnd.github.cloak-preview"}
    r = requests.get(url, auth=(git_user, git_pass), headers=headers)
    while "total_count" not in json.loads(r.text) and "message" in json.loads(r.text):
        if handle_error_search(json.loads(r.text), conf):
            return None
        r = requests.get(url, auth=(git_user, git_pass), headers=headers)
    return json.loads(r.text)


def get_page_number(query, conf, typ):
    rpp = int(conf['git_rpp'])
    repos = search_repository(query, conf, typ)
    if repos is None:
        return None, None
    total = repos['total_count']
    if total > 1000:
        total = 1000
    pages = math.ceil(total / rpp) + 1
    return pages, search_repository(query, conf, typ, "&per_page={}&page=1".format(conf['git_rpp']))


def handle_error_download(conf, e, logs):
    print("ERROR: " + str(e))
    if "enough space" in str(e):
        send_message("*ERROR*: Not enough space when cloning repository", conf)
        write_file("{}/{}".format(conf['path_source'], conf['file_log']), logs)
        exit()
    pass


def handle_page(rp_items, logs, conf, cloned, rule_id):
    git_user = os.environ.get('GIT_USERNAME')
    git_pass = os.environ.get('GIT_PASSWORD')
    if git_pass is None or git_pass is None:
        if not conf['git_user'] or not conf['git_pass']:
            print('ERROR: Make sure you have defined github credential in the ENV or config file - config.ini')
            exit(1)
        else:
            git_user = conf['git_user']
            git_pass = conf['git_pass']

    for rp in rp_items:
        rpi = {}
        if "repository" in rp:
            r = requests.get(rp['repository']['url'], auth=(git_user, git_pass))
            rp = json.loads(r.text)
        for i in list_info:
            rpi[i] = rp[i]
        folder_name = "{}_{}".format(rpi['full_name'].split("/")[0], rpi['full_name'].split("/")[1])
        if folder_name not in logs or rpi["updated_at"] != logs[folder_name]['updated_at']:
            try:
                print("Cloning " + rpi['clone_url'])
                git.Repo.clone_from(rpi['clone_url'], "{}/{}".format(conf['path_source'], folder_name))
                js = {"html_url": rpi['html_url'], "updated_at": rpi['updated_at'], "state": 'new'}
                logs[folder_name] = js
                cloned[folder_name] = {"html_url": rpi['html_url']}
                handle_directory(logs, conf, folder_name, rule_id)
            except Exception as e:
                handle_error_download(conf, e, logs)