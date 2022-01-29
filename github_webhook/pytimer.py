import threading
from time import sleep


event = None
on_going_timer = None

#TODO: SEPARATE THREADS BY CRITICAL SECTION

def refresh(latest_event, wait_for, *args, **kwargs):
    global event, on_going_timer
    t = threading.Thread(target=__wait__, args=(wait_for, *args), kwargs=kwargs)
    t.start()
    event = latest_event
    on_going_timer = t.native_id

def __wait__(t, *args, **kwargs):
    sleep(t)
    if not threading.get_ident() == on_going_timer:
        return
    __run__(*args, **kwargs)

def __run__(*args, **kwargs):
    global event, on_going_timer
    on_going_timer = None
    event(*args, **kwargs)
    event = None
