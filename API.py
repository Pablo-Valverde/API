#!/usr/bin/python3
# -*- coding: utf-8 -*-

from werkzeug.exceptions import NotFound, ServiceUnavailable

from ipaddress import ip_address
from pathlib import Path
from flask import Flask, request, jsonify
import random
import sys
import datetime
import argparse
import logging
import traceback


__doc__ = {
    "version":              "0.0.0"
}

#---- Initial configuration ----#
def parse():
    parser = argparse.ArgumentParser()
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
    parser.add_argument(
        "-data_path",
        "-data",
        help="Path where the data is going to be looked for",
        type=lambda s: str(s),
        default="data"
    )

    return parser.parse_args()

args = parse()

logger = logging.getLogger("werkzeug")
logger.setLevel(logging.ERROR)

root = logging.getLogger("felaciano")
root.setLevel(logging.DEBUG)

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stdout_handler.setFormatter(formatter)

root.addHandler(stdout_handler)

SERVER_IP = args.ip
SERVER_PORT = args.port
DIR_NAME = args.data_path

root.info("Reading data files from '%s' directory" % DIR_NAME)
#---- End of Initial configuration ----#

errors = {
    404: "Resource not found",
    500: "Unexpected internal behaviour",
    503: "This service is actually unavailable"
}

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

    return jsonify(response) 

def normalize_error(code, message):
    now = datetime.datetime.now()

    status = {
        "timestamp":        now,
        "error_code":       code,
        "error_message":    message
    }

    response = {
        "status":           status
    }

    aux = jsonify(response)
    aux.status_code = code
    return aux

@app.after_request
def request_in(response) -> str:
    status = response.status_code
    try:
        sender_ip = request.headers["X-Forwarded-For"]
    except KeyError:
        sender_ip = request.remote_addr
    method = request.method
    path = request.path
    root.info("%d - %s - %s %s" % (status, sender_ip, method, path))
    return response

@app.errorhandler(Exception)
def on_error(error:Exception) -> str:
    excp = traceback.format_exc()
    try:
        code = error.code
        message = errors[code]
    except (KeyError, AttributeError):
        code = 500
        message = errors[code]
        root.error(excp)
    return normalize_error(code, message)

@app.route("/version/")
@app.route("/version")
def get_version() -> str:
    return normalize_dict(__doc__)

@app.route("/<route>/aleatorio/")
@app.route("/<route>/aleatorio")
def get_random(route) -> str:
    path = Path(DIR_NAME, route)
    buffer = []
    if not path.is_file():
        raise NotFound()
    try:
        with open(path, mode="r", encoding="UTF-8") as file:
            buffer = file.readlines()
    except PermissionError:
        raise NotFound()

    if not buffer:
        raise ServiceUnavailable()
    item = random.choice(buffer).replace("\n","")
    return normalize_dict({"value":item.lower()})

if __name__ == "__main__":

    root.info("Server running on address https://%s:%d/" % (SERVER_IP, SERVER_PORT))

    app.run(
        host=   SERVER_IP,
        port=   SERVER_PORT
    )
