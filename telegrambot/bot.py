import pyinotify
import telebot
import signal
import sys
import os

# Config
BOT_TOKEN = 'TELEGRAM-BOT-TOKEN'

GROUP_ID = 'GROUP-ID-TO-SEND-MESSAGES'

recordingspath = '/tmp/recordings/'

# Air Band Channels Names
freq = {
    '118000000': 'SBRP TWR 118.00MHz',
    '119550000': 'APP ACADEMIA 119.55MHz',
    '119750000': 'APP ACADEMIA 119.75MHz',
    '120100000': 'APP ACADEMIA 120.10MHz',
    '121500000': 'AIR DISTRESS 121.50MHz',
    '122400000': 'APP ACADEMIA 122.40MHz',
    '122750000': 'AIR TO AIR 122.75MHz',
    '122800000': 'APP ACADEMIA 122.80MHz',
    '123025000': 'AIR TO AIR HELI 123.025MHz',
    '123450000': 'AIR TO AIR 123.45MHz',
}

# Bot instance
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

# Send stale audio files
oldfiles = [os.path.join(recordingspath, f) for f in os.listdir(recordingspath) if os.path.isfile(os.path.join(recordingspath, f))]
for fpath in oldfiles:
    try:
        filepath = fpath.strip('.tmp')
        text = freq.get(fpath.strip('.mp3').split('_')[3], '')
        with open(fpath, 'rb') as audiof:
            bot.send_audio(GROUP_ID, audiof, text)
            print(f'Old Audio {text} sent.')
    finally:
        os.remove(fpath)

# Start regular operation
bot.send_message(GROUP_ID, 'Listening to the air band...')

class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CLOSE_WRITE(self, event):
        filepath = event.pathname.strip('.tmp')
        text = freq.get(filepath.strip('.mp3').split('_')[3], '')
        with open(filepath, 'rb') as audiof:
            bot.send_audio(GROUP_ID, audiof, text)
        os.remove(filepath)
        print(f'Audio {text} sent.')

# Filesystem notify thread
wm = pyinotify.WatchManager()
mask = pyinotify.IN_CLOSE_WRITE
notifier = pyinotify.ThreadedNotifier(wm, EventHandler())
notifier.start()
wdd = wm.add_watch(recordingspath, mask)
print('Telegram Bot running...')

# Sigint capture and exit
def signal_handler(signal, frame):
    global notifier
    notifier.stop()
    print('Bye!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.pause()
