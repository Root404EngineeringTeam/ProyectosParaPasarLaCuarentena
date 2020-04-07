#!/usr/bin/env python3
import ErinaBot
import requests
import discord
import time

from datetime import datetime

def notifications_cron(unix_time):
    notifications = ErinaBot.db.notifications.find()

    for notification in notifications:
        if notification['expiration'] <= unix_time:
            ErinaBot.webhook.send("Recordatorio por parte de %s: %s" %(notification['author'], notification['message']))
            ErinaBot.db.notifications.delete_one({'_id':notification['_id']})

try:
    while True:
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        time_array = time_str.split(":")
        unix_time = time.time()

        hour = time_array[0]
        minute = time_array[1]

        print("%s - Running cron jobs" %(time_str))

        notifications_cron(unix_time)

        time.sleep(60)

except KeyboardInterrupt:
    pass
