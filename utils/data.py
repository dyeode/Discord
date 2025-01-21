import json
import os


def load_data(file_name, default=None):
    try:
        if not os.path.exists(file_name):
            return default if default is not None else {}
        with open(file_name, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print(f"⚠️ Error decoding JSON in {file_name}. Returning default.")
        return default if default is not None else {}
    except Exception as e:
        print(f"⚠️ Error loading {file_name}: {e}")
        return default if default is not None else {}


def save_data(file_name, data):
    try:
        with open(file_name, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"⚠️ Error saving to {file_name}: {e}")


def load_fun_data():
    return load_data("fun_data.json", default={
        "dadjokes": [],
        "compliments": [],
        "trivia": {},
        "wouldyourather": [],
        "facts": []
    })


def save_fun_data(data):
    save_data("fun_data.json", data)


def load_ban_data():
    return load_data("ban_history.json", default={})


def save_ban_data(data):
    save_data("ban_history.json", data)


def load_help_data():
    return load_data("help_data.json", default={})


def save_help_data(data):
    save_data("help_data.json", data)


def load_config(config_file="config.json"):
    return load_data(config_file, default={})


def load_blacklist():
    return load_data("blacklist.json", default=[])


def save_blacklist(data):
    save_data("blacklist.json", data)


def load_muted_data():
    return load_data("muted_members.json", default={})


def save_muted_data(data):
    save_data("muted_members.json", data)


def load_warnings_data():
    return load_data("warnings.json", default={})


def save_warnings_data(data):
    save_data("warnings.json", data)