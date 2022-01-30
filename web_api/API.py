from ipaddress import ip_address
from flask import Flask
from waitress import serve
from os import path
import datetime
import random
import json
import argparse
try:
    from cachedfile import cachedfile
except ImportError:
    from .cachedfile import cachedfile


__doc__ = {
    "version":              "0.0.0"
}

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "config_file",
        help="Configuration file",
        type=lambda s: str(s) 
    )
    parser.add_argument(
        "-ip",
        help="IP address of this server",
        type=lambda s: ip_address(s).__str__(),
        default="127.0.0.1"
    )
    parser.add_argument(
        "-port",
        "-p",
        help="Bind this server to this PORT",
        type=lambda s: int(s),
        default=80
    )

    return parser.parse_args()

args = parse()

config_file = args.config_file

try:
    with open(config_file, "r", encoding="UTF-8") as config:
        conf = json.load(config)
except json.decoder.JSONDecodeError:
    print("%s must be a valid configuration file" % config_file)

SERVER_IP = args.ip
SERVER_PORT = args.port

DIR_NAME = conf["ruta_repositorios"]
INSULTS = conf["fichero_insultos"]

INSULTOS_PHRS_FILE = path.join(DIR_NAME, INSULTS)

insultos_data = cachedfile(INSULTOS_PHRS_FILE)

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
@app.route("/version")
def get_version() -> str:
    return normalize_dict(__doc__).__str__()

@app.route("/insulto/aleatorio/")
@app.route("/insulto/aleatorio")
def get_insulto() -> str:
    insultos_data.update()
    insulto = random.choice(insultos_data).replace("\n","")
    return normalize_dict({"insulto":insulto}).__str__()

if __name__ == "__main__":

    serve(
        app,
        host=   SERVER_IP,
        port=   SERVER_PORT
    )
