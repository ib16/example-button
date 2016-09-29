# -*- coding: utf-8 -*-

#
# IoT Button
#
#   usage:
#   $ python -u main.py
#

GMAIL_ADDRESS = "iotbutton2016@gmail.com"
GMAIL_PASSWORD = "Button2016"
EMAIL_SENDTO = "nohara@xshell.io"

TWITTER_CONSUMER_KEY = "UoZIinYJfxqBj37Psqeq08Isb"
TWITTER_CONSUMER_SECRET = "AHYjeg7gHa91CbStLJ5hZovekFfTKCyr7Uho9je18P92VSNQyF"
TWITTER_ACCESS_TOKEN = "774677219784491008-wYdWiQe65VAk66liZggWIZisjxW4PvW"
TWITTER_ACCESS_TOKEN_SECRET = "Ch68qvj8Tts8be0f3b9ADe8ZfUegagsVUfkKGSyeVtblF"

TOGGL_API_TOKEN = "416800af1ae414b0e9a71b31c13c18e3"


import os
import sys
import time
import threading
import json
from datetime import datetime, timedelta, tzinfo
import smtplib
from email.mime.text import MIMEText
from email.header import Header

import requests
from twitter import *

import iot_button

#if 'API_TOKEN' in os.environ:
#    API_TOKEN = os.environ['API_TOKEN']
#else:
#    raise "API_TOKEN is not set"

class JST(tzinfo):
    def utcoffset(self, dt):
        return timedelta(hours=9)

    def dst(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return 'JST'

def stamp_text():
    now_datetime = datetime.now(tz=JST())
    time_string = now_datetime.strftime("%Y-%m-%d %H:%M:%S")
    message = time_string + " IoT Button から送信"
    return message


# gmail

def send_gmail():
    print("send_gmail")
    host, port = 'smtp.gmail.com', 465
    msg = MIMEText(stamp_text(), 'plain', 'utf-8')
    msg['Subject'] = Header("IoT Button から送信", 'utf-8')
    msg['From'] = GMAIL_ADDRESS
    msg['To'] = EMAIL_SENDTO

    smtp = smtplib.SMTP_SSL(host, port)
    smtp.ehlo()
    smtp.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
    smtp.mail(GMAIL_ADDRESS)
    smtp.rcpt(EMAIL_SENDTO)
    smtp.data(msg.as_string())
    smtp.quit()



# Twitter

auth = OAuth(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET, TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
twitter = Twitter(auth=auth)

tweeting = False

def tweet():
    global tweeting
    print("tweet")
    print(threading.current_thread())
    if not tweeting:
    #if True:
        tweeting = True
        print(tweeting)
        message = stamp_text()
        print("message: " + message)
        twitter.statuses.update(status=message)
        print 'tweeted'
        tweeting = False

# toggl

def start_toggl():
    print("start_toggl")
    payload = {"time_entry":{"description":"Started by Knob", "created_with":"Knob"}}
    res = requests.post("https://www.toggl.com/api/v8/time_entries/start", auth=(TOGGL_API_TOKEN, 'api_token'), headers={"Content-Type": "application/json"}, data=json.dumps(payload))
    print(res)

def stop_toggl(current_time_entry):
    print("stop_toggl")
    #current_id = get_current_time_entry_id()
    current_id = get_current_time_entry_id(current_time_entry)
    print("current_id: %d" % (current_id))
    res = requests.put("https://www.toggl.com/api/v8/time_entries/%d/stop" % (current_id), auth=(TOGGL_API_TOKEN, 'api_token'))
    print(res.json())

def get_current_time_entry():
    res = requests.get("https://www.toggl.com/api/v8/time_entries/current", auth=(TOGGL_API_TOKEN, 'api_token'))
    return res.json()['data']

def get_current_time_entry_id(current_time_entry):
    return current_time_entry['id']

def toggle_toggl():
    print("toggle_toggl")
    current_time_entry = get_current_time_entry()
    if current_time_entry is None:
        start_toggl()
    else:
        stop_toggl(current_time_entry)


def on_position_change_callback(position):
    print("on_position_change: %d" % (position))
    if position == 2 or position == 4:
        print("starts toggl")
        start_toggl()
    else:
        print("stops toggl")
        stop_toggl()

def on_press(button, knob):
    print("button pressed")
    try:
        print("knob position: %d" % (knob.get_position()))
        position = knob.get_position()
        if position == 1:
            send_gmail()
        elif position == 2:
            tweet()
        elif position == 3:
            toggle_toggl()
        elif position == 4:
            pass
        #toggle_toggl()
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    k = iot_button.Knob()
    #k.on_position_change = on_position_change_callback

    b = iot_button.Button(k)
    b.on_press = on_press

    while True:
        time.sleep(1)
        #print(threading.current_thread())
        print("knob position: %d" % (k.get_position()))
        print("button state: %d" % (b.get_status()))

