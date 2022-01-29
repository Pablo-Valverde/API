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

def readlines():
    try:
        with open(path.join(DIR_NAME, REMOTE_FILE, AXOLOTS), "r") as axolots_file:
            axolots_data = axolots_file.readlines()
    except (FileNotFoundError, PermissionError):
        pass
    return axolots_data

axolots_data = readlines()

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
    try:
        with open(path.join(DIR_NAME, REMOTE_FILE, AXOLOTS), "r") as axolots_file:
            axolots_data = axolots_file.readlines()
    except FileNotFoundError:
        pass    
    axolot = random.choice(axolots_data).replace("\n","")
    return normalize_dict({"img_url":axolot}).__str__()

if __name__ == "__main__":

    app.run(
        host=               "0.0.0.0",
        port=               80
    )