def read_config(path_to_conf="bugzilla.conf"):
    login = None
    password = None

    conf = open(path_to_conf)
    for line in conf.readlines():
        values = map(lambda x: x.strip(), line.split("="))
        if values[0] == "login":
            login = values[1]

        if values[0] == "password":
            password = values[1]

    return (login, password)
