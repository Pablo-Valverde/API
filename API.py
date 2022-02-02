#!/usr/bin/python
# -*- coding: utf-8 -*-

from ipaddress import ip_address
from pathlib import Path
from time import sleep
from flask import Flask, Response, request
from waitress import serve
from os import mkdir, path
import random
import sys
import datetime
import argparse
import logging


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

logs_file = "logs/"

if not path.isdir("logs"):
    if not path.exists("logs"):
        mkdir("logs")
    else:
        logs_file = ""

app_logging = logging.getLogger("")
app_logging.setLevel(logging.DEBUG)

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stdout_handler.setFormatter(formatter)

now = datetime.datetime.now()
now = now.strftime("%d.%m.%Y-%H.%M.%S")
file_handler = logging.FileHandler("%s%sAPI.log" % (logs_file,now), "w", encoding="UTF-8")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

app_logging.addHandler(stdout_handler)
app_logging.addHandler(file_handler)

SERVER_IP = args.ip
SERVER_PORT = args.port
DIR_NAME = args.data_path

app_logging.info("Reading data files from '%s' directory" % DIR_NAME)
#---- End of Initial configuration ----#

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

    return Response(response.__str__()) 

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

    return Response(response.__str__(), status=code) 

@app.after_request
def request_in(response) -> str:
    status = response.status_code
    try:
        sender_ip = request.headers["X-Forwarded-For"]
    except KeyError:
        sender_ip = request.remote_addr
    method = request.method
    path = request.path
    app_logging.info("%d - %s - %s %s" % (status, sender_ip, method, path))
    return response

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
        return normalize_error(404, "Ruta incorrecta")
    try:
        with open(path, mode="r", encoding="UTF-8") as file:
            buffer = file.readlines()
    except PermissionError:
        return normalize_error(404, "Ruta incorrecta")

    if not buffer:
        return normalize_error(503, "Servicio no disponible actualmente")
    item = random.choice(buffer).replace("\n","")
    return normalize_dict({"value":item})

if __name__ == "__main__":

    serve(
        app,
        host=   SERVER_IP,
        port=   SERVER_PORT
    )
