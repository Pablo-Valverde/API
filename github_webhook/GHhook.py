from flask import Flask, Response, request
from pathlib import Path
from requests import get
import json
import threading
import iptools
try:
    import pytimer
    import reporeader
except ImportError:
    from . import pytimer
    from . import reporeader


#TODO: Get from config file
REMOTE_URL = "https://github.com/Pablo-Valverde/bot_data.git"
DIR_NAME = "C:/Users/pablo/Documents/GitHub/API/repositories"
WAIT_FOR_EVENTS = 5

META = "https://api.github.com/meta"
META_FILE = Path(META).stem

app = Flask(__name__)

@app.post("/")
def hook():
    request.get_json(force=True)

    try:
        from_repo = request.json["repository"]["html_url"]
    except KeyError:
        return Response(status=400)

    try:
        sender_ip = request.headers["X-Forwarded-For"]
    except KeyError:
        sender_ip = request.remote_addr

    for ip in ips:
        range = iptools.IpRangeList(ip)

        if not sender_ip in range:
            continue

        if not REMOTE_URL.find(from_repo) == -1:
            t = threading.Thread(target=reporeader.pull, args=(DIR_NAME, REMOTE_URL))
            pytimer.refresh(lambda x: x.start(), WAIT_FOR_EVENTS, t)
            return Response(status=200)

        break

    return Response(status=400)

if __name__ == "__main__":

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

    t = threading.Thread(target=reporeader.pull, args=(DIR_NAME, REMOTE_URL))
    pytimer.refresh(lambda x: x.start(), 3, t)

    app.run(
        host=               "0.0.0.0",
        port=               443,
        ssl_context=        'adhoc'
    )