import os
import shutil
from libs.utils import get_filename, get_extension
from libs.init import ignore_file, special, ignore_ex
from libs.regexs import to_match


def check_regex(path2file, matches):
    for m in to_match:
        if m['match_type'] in matches:
            continue
        cmd = os.popen("egrep -e \"{}\" {}".format(m['match_regex'], path2file)).read()
        if cmd != "":
            print("{}-{}".format(m['match_type'], path2file))
            matches.append(m['match_type'])


def find_sensitive(path2src):
    matches = []
    for r, d, f in os.walk(path2src):
        for file in f:
            path2file = os.path.join(r, file)
            for s in special:
                if s in path2file:
                    path2file = path2file.replace(s, "\\" + s)
            filename = get_filename(path2file)
            ex = get_extension(filename)
            if "/.git/" not in path2file and filename not in ignore_file and ex not in ignore_ex:
                check_regex(path2file, matches)
    return matches


def handle_directory(logs, conf, possible, fn):
    matches = []
    if logs[fn]['state'] == "new":
        logs[fn]['state'] = 'old'
        path2src = "{}/{}".format(conf['path_source'], fn)
        matches = find_sensitive(path2src)
        shutil.rmtree(path2src)
    if len(matches) != 0:
        m = ""
        for i in matches:
            m += i + ", "
        possible[fn] = {"html_url": logs[fn]['html_url'], 'matched': m.rstrip(", ")}