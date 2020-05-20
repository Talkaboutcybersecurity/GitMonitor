import yaml


def get_rule(rule_file):
    a_yaml_file = open(rule_file)
    parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
    if "key" not in parsed_yaml_file:
        print("ERROR: Not found key in rule file - {}".format(rule_file))
        exit()
    if "id" not in parsed_yaml_file:
        print("ERROR: Not found id in rule file - {}".format(rule_file))
        exit()
    return parsed_yaml_file


def build_query(rule_file):
    rule = get_rule(rule_file)
    queries = []
    key = "\"{}\"".format(rule['key'].strip())
    for k in rule:
        if k.strip() not in ['key', 'id', 'ignore'] and rule[k] is not None:
            for i in rule[k]:
                query = key + " {}:{}".format(k, i)
                queries.append(query)
        if k == 'ignore':
            query = key
            for j in rule[k]:
                if rule[k][j] is not None:
                    for l in rule[k][j]:
                        query += " -{}:{}".format(j, l)
            if query != key:
                queries.append(query)
    if len(queries) == 0:
        queries.append(key)
    return queries, rule['id'].strip()
