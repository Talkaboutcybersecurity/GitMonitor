import requests
import json


def get_message(dic, rule_id):
    msg = ''
    if len(dic) == 0:
        msg = ">There are no new findings"
    for i in dic:
        if "matched" not in dic[i]:
            msg += ">{}\n".format(dic[i]['html_url'])
        else:
            msg += ">{} - May contain the following sensitive information: {}\n".format(dic[i]['html_url'], dic[i]["matched"])
    msg = "[Rule ID: {}]\n{}".format(rule_id, msg)
    return msg


def send_message(msg, conf):
    headers = {'Content-type': 'application/json'}
    data = {'text': msg}
    requests.post(conf['slack_webhooks'], data=json.dumps(data), headers=headers)


def send_list(dic, conf, rule_id):
    message = get_message(dic, rule_id)
    send_message(message, conf)
