from flask import Flask
from os import path
import datetime
import random


__doc__ = {
    "version":              "0.0.0"
}

#TODO: Get from config file
DIR_NAME = "repositories"
REMOTE_FILE = "data"#Path(REMOTE_URL).stem
AXOLOTS = "axolots"

AXOLOTS_FILE = path.join(DIR_NAME, REMOTE_FILE, AXOLOTS)


def get_from_file_or_saved(path, iterable = None):
    iterable = iterable if iterable else []
    buffer = read_lines(path)
    iterable.clear()
    iterable += buffer if buffer else iterable
    return iterable

def read_lines(path):
    buffer = []
    try:
        with open(path, "r") as axolots_file:
            buffer = axolots_file.readlines()
    except (FileNotFoundError, PermissionError):
        pass
    return buffer

axolots_data = get_from_file_or_saved(AXOLOTS_FILE)

app = Flask(__name__)

def normalize_dict(dict) -> dict:
    now = datetime.datetime.now()

    status = {
        "timestamp":        now,
        "error_code":       0,
        "error_message":    ""
    }

    response = {
        "data":             dict,
        "status":           status
    }

    return response

@app.route("/version/")
def get_version() -> str:
    return normalize_dict(__doc__).__str__()

@app.route("/axolot/random/")
def get_axolot() -> str:
    get_from_file_or_saved(AXOLOTS_FILE, axolots_data)
    axolot = random.choice(axolots_data).replace("\n","")
    return normalize_dict({"img_url":axolot}).__str__()

if __name__ == "__main__":

    app.run(
        host=               "0.0.0.0",
        port=               80
    )