from flask import Flask, Response, request
from os import path
from requests import get
import reporeader
import iptools
import datetime
import threading
import json


__doc__ = {
    "version":              "0.0.0"
}

#TODO: Pass as program arguments
DIR_NAME = "temp"
REMOTE_URL = "https://github.com/Pablo-Valverde/bot_data.git"


AXOLOTS = "axolots"
META = "https://api.github.com/meta"
META_FILE = "meta"

try:
    raise KeyError()
    meta = get(META).json()
    ips = meta["hooks"]
    with open(META_FILE, "w") as fp:
        json.dump(meta, fp)
except KeyError:
    with open(META_FILE, "r") as fp:
        meta = json.load(fp)
    ips = meta["hooks"]

#threading.Thread(target=reporeader.pull, args=(DIR_NAME, REMOTE_URL)).start()

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

@app.post("/")
def hook():
    request.get_json(force=True)
    for ip in ips:
        range = iptools.IpRangeList(ip)
        try:
            if not request.headers["X-Forwarded-For"] in range:
                continue    
        except KeyError:
            if not request.remote_addr in range:
                continue
        try:
            from_repo = request.json["repository"]["html_url"]
            if REMOTE_URL.find(from_repo) == -1:
                break
        except KeyError:
            break

        threading.Thread(target=reporeader.pull, args=(DIR_NAME, REMOTE_URL)).start()
        return Response(status=200)
    return Response(status=400)
    
@app.route("/test/")
def get_test() -> str:
    buffer = ""
    with open(path.join(DIR_NAME, AXOLOTS), "r") as axolots_file:
        for line in axolots_file:
            buffer += line
    print(buffer)
    return buffer

if __name__ == "__main__":
    app.run(
        debug=              True,
        host=               "0.0.0.0",
        port=               443,
        ssl_context=        'adhoc'
    )
