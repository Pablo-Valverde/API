from time import sleep
import requests
import threading


base_url = "http://127.0.0.1/"

always_ok_or_503 = [
    "insulto/aleatorio/",
    "insulto/aleatorio",
    "ajolote/aleatorio/",
    "ajolote/aleatorio",
    "version",
    "version/"
]

h200 = 0
h503 = 0
hits = 0

def test(path):
    global h200, h503, hits
    try:
        request = requests.get("%s%s" % (base_url, path))
    except:
        return
    if request.status_code == 200 :
        h200 += 1
        hits += 1
    elif request.status_code == 503:
        h503 += 1
        hits += 1

for path in always_ok_or_503:
    t = threading.Thread(target=test, args=(path,))
    t.start()

sleep(4)
print("%d tests : %d 200 : %d 503 : %d failures" % (always_ok_or_503.__len__(), h200, h503, (always_ok_or_503.__len__() - h200 + h503)))