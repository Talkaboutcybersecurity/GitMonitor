import time
import os
from libs.utils import initialization, write_file, get_json, get_time
from libs.init import config_file, possible, type_search
from libs.github import get_page_number, search_repository, handle_page
from libs.slack import send_message, send_list
from libs.rules import build_query


conf = initialization(config_file)
logs = get_json("{}/{}".format(conf['path_log'], "old_result"))
send_message(conf['msg_start'].format(get_time()), conf)
for r, d, f in os.walk(conf['path_rule']):
    for file in f:
        clone = {}
        rule_file = os.path.join(r, file)
        if rule_file[-5:] != ".yaml":
            continue
        queries, rule_id = build_query(rule_file)
        if rule_id not in logs:
            logs[rule_id] = {}
        if rule_id not in possible:
            possible[rule_id] = {}
        for typ in type_search:
            for query in queries:
                if typ != "code":
                    query = query.split(" ", 1)[0]
                pages, rep = get_page_number(query, conf, typ)
                if pages is None or rep is None:
                    continue
                print("\nINFO: Working with Searching Rule ...\n")
                handle_page(rep['items'], logs[rule_id], conf, clone, rule_id)
                if pages > 2:
                    for i in range(2, pages):
                        repo = search_repository(query, conf, typ, "&per_page={}&page={}".format(conf['git_rpp'], str(i)))
                        if repo is None:
                            continue
                        time.sleep(10)
                        print("\nINFO: Working with Searching Rule ...\n")
                        handle_page(repo['items'], logs[rule_id], conf, clone, rule_id)
                if typ != "code":
                    break
        send_message(conf['msg_end'].format(get_time()), conf)
        send_list(clone, conf, rule_id)
send_message(conf['msg_all'], conf)
for rule_id in logs:
    send_list(logs[rule_id], conf, rule_id)
write_file("{}/{}".format(conf['path_log'], "old_result"), logs)