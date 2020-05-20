from configparser import ConfigParser


def get_file_config(file):
    confi = {}
    config = ConfigParser()
    config.read(file)
    sections = config.sections()
    for section in sections:
        options = config.options(section)
        for option in options:
            value = config.get(section, option)
            name = str(section) + "_" + str(option)
            confi[name] = value
    return confi