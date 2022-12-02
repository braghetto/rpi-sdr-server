from telebot.handler_backends import BaseMiddleware, CancelUpdate
from tokens import BOT_TOKEN, GROUP_ID, OWNER_ID
from syslogrelay import SyslogServer
from telebot import types
from airband import freq
from time import sleep
import subprocess
import pyinotify
import telebot
import signal
import psutil
import os


recordingspath = '/var/recordings/'


# SDR Services disable and stop helper functions
def stop_all_sdr_services():
    subprocess.call(['sudo', 'systemctl', 'stop', 'spyserver.service'])
    subprocess.call(['sudo', 'systemctl', 'stop', 'soapyserver.service'])
    subprocess.call(['sudo', 'systemctl', 'stop', 'rtlairband.service'])
    subprocess.call(['sudo', 'systemctl', 'stop', 'rtltcp.service'])
    subprocess.call(['sudo', 'systemctl', 'stop', 'rtl433.service'])
    return None

def disable_all_sdr_services():
    subprocess.call(['sudo', 'systemctl', 'disable', 'spyserver.service'])
    subprocess.call(['sudo', 'systemctl', 'disable', 'soapyserver.service'])
    subprocess.call(['sudo', 'systemctl', 'disable', 'rtlairband.service'])
    subprocess.call(['sudo', 'systemctl', 'disable', 'rtltcp.service'])
    subprocess.call(['sudo', 'systemctl', 'disable', 'rtl433.service'])
    return None


# Bot instance
bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None, use_class_middlewares=True)

# Bot owner authentication
class OwnerMiddleware(BaseMiddleware):
    def __init__(self):
        self.update_types = ['message']
    def pre_process(self, message, data):
        if message.from_user.id != int(OWNER_ID):
            return CancelUpdate()
    def post_process(self, message, data, exception=None):
        pass

bot.setup_middleware(OwnerMiddleware())


# Send stale audio files
oldfiles = [os.path.join(recordingspath, f) for f in os.listdir(recordingspath) if os.path.isfile(os.path.join(recordingspath, f))]
for fpath in oldfiles:
    try:
        filepath = fpath.strip('.tmp')
        text = freq.get(fpath.strip('.mp3').split('_')[3], '')
        sleep(1)
        with open(fpath, 'rb') as audiof:
            bot.send_audio(GROUP_ID, audiof, text)
            print(f'Old Audio {text} sent.')
    finally:
        os.remove(fpath)


# Syslog server for rtl433 messages
syslogsrv = SyslogServer(bot, OWNER_ID)
syslogsrv.start()


# File system events handler
class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CLOSE_WRITE(self, event):
        filepath = event.pathname.strip('.tmp')
        text = freq.get(filepath.strip('.mp3').split('_')[3], '')
        sleep(1)
        with open(filepath, 'rb') as audiof:
            bot.send_audio(GROUP_ID, audiof, text)
        os.remove(filepath)
        print(f'Audio {text} sent.')

# File system notify thread
wm = pyinotify.WatchManager()
mask = pyinotify.IN_CLOSE_WRITE
notifier = pyinotify.ThreadedNotifier(wm, EventHandler())
notifier.start()
wdd = wm.add_watch(recordingspath, mask)


# Bot commands handlers
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    text = 'My commands are:'
    keyboard = types.ReplyKeyboardMarkup()
    btn_start = types.KeyboardButton('/start')
    btn_help = types.KeyboardButton('/help')
    btn_info = types.KeyboardButton('/info')
    btn_services = types.KeyboardButton('/services')
    btn_usbreset = types.KeyboardButton('/usbreset')
    btn_calibrate = types.KeyboardButton('/calibrate')
    btn_restart = types.KeyboardButton('/restart')
    btn_shutdown = types.KeyboardButton('/shutdown')
    btn_cancel = types.KeyboardButton('/cancel')
    keyboard.add(btn_start, btn_help, btn_info)
    keyboard.add(btn_services, btn_usbreset, btn_calibrate)
    keyboard.add(btn_restart, btn_shutdown)
    keyboard.add(btn_cancel)
    bot.reply_to(message, text, reply_markup=keyboard)

@bot.message_handler(commands=['cancel'])
def send_cancel(message):
    text = 'Done.'
    remove_keyboard = types.ReplyKeyboardRemove(selective=False)
    bot.reply_to(message, text, reply_markup=remove_keyboard)

@bot.message_handler(commands=['restart'])
def send_restart(message):
    text = 'Restarting system...'
    remove_keyboard = types.ReplyKeyboardRemove(selective=False)
    bot.reply_to(message, text, reply_markup=remove_keyboard)
    subprocess.call(['sudo', 'shutdown', '-r', '+1'])
    sleep(5)
    signal.signal_raise(signal.SIGTERM)

@bot.message_handler(commands=['shutdown'])
def send_shutdown(message):
    text = 'Shutting down system...'
    remove_keyboard = types.ReplyKeyboardRemove(selective=False)
    bot.reply_to(message, text, reply_markup=remove_keyboard)
    subprocess.call(['sudo', 'shutdown', '-h', '+1'])
    sleep(5)
    signal.signal_raise(signal.SIGTERM)

@bot.message_handler(commands=['calibrate'])
def send_calibrate(message):
    text = 'Calibration in progress...'
    remove_keyboard = types.ReplyKeyboardRemove(selective=False)
    bot.reply_to(message, text, reply_markup=remove_keyboard)
    out = subprocess.check_output(['/usr/local/bin/calibrate'])
    try:
        out = out.decode('utf-8').replace('\x1b[0;32m', ' ').replace('\x1b[0m\n', ' ').strip().split('  ')
        text = 'Calibration results:\n'
        for l in out:
            text += l + '\n'
    except:
        return None
    bot.reply_to(message, text)

@bot.message_handler(commands=['usbreset'])
def send_usbreset(message):
    text = 'USB Bus power cycling in progress...'
    remove_keyboard = types.ReplyKeyboardRemove(selective=False)
    bot.reply_to(message, text, reply_markup=remove_keyboard)
    subprocess.call(['sudo', '/usr/bin/usbreset', '001/002'])

@bot.message_handler(commands=['info'])
def send_info(message):
    text = []
    services = [
        'spyserver.service',
        'soapyserver.service',
        'telegrambot.service',
        'rtlairband.service',
        'rtltcp.service',
        'rtl433.service'
    ]
    enableds = []
    actives = []
    for service in services:
        enabled = subprocess.call(['sudo', 'systemctl', 'is-enabled', service])
        active = subprocess.call(['sudo', 'systemctl', 'is-active', service])
        if enabled == 0:
            enableds.append(service)
        if active == 0:
            actives.append(service)
    if enableds:
        text.append('\nEnabled services:')
        for s in enableds:
            text.append(s)
    if actives:
        text.append('\nActive services:')
        for s in actives:
            text.append(s)
    ram_used_mb = round(psutil.virtual_memory()[3]/1000000)
    ram_used_p = round(psutil.virtual_memory()[2])
    cpu_freq_g = round(psutil.cpu_freq()[0]/1000, 2)
    cpu_use_p = round(psutil.cpu_percent(1))
    disk_usage_p = round(psutil.disk_usage('/')[3])
    disk_usage_g = round(psutil.disk_usage('/')[1]/1000000000, 2)
    uptime = subprocess.check_output(['uptime', '-p']).decode('utf-8').strip().removeprefix('up ')
    temp_c = round(int(subprocess.check_output(['cat', '/sys/class/thermal/thermal_zone0/temp']).decode('utf-8').strip())/1000, 1)
    degree = u"\N{DEGREE SIGN}"
    text.append('\nHardware:')
    text.append(f'Uptime: {uptime}')
    text.append(f'RAM usage: {ram_used_p}% {ram_used_mb}MB')
    text.append(f'Disk usage: {disk_usage_p}% {disk_usage_g}GB')
    text.append(f'CPU usage: {cpu_use_p}%')
    text.append(f'CPU temp: {temp_c}{degree}C')
    text.append(f'CPU freq: {cpu_freq_g}GHz')
    newtext = '- System Status -\n'
    for l in text:
        newtext = newtext + l + '\n'
    text = newtext
    remove_keyboard = types.ReplyKeyboardRemove(selective=False)
    bot.reply_to(message, text, reply_markup=remove_keyboard)

@bot.message_handler(commands=['services'])
def send_services(message):
    text = 'Available services:'
    services_keyboard = types.ReplyKeyboardMarkup()
    btn_telegrambot = types.KeyboardButton('/telegrambot')
    btn_spyserver = types.KeyboardButton('/spyserver')
    btn_rtl433 = types.KeyboardButton('/rtl433')
    btn_soapyserver = types.KeyboardButton('/soapyserver')
    btn_airbandserver = types.KeyboardButton('/airbandserver')
    btn_tcpserver = types.KeyboardButton('/tcpserver')
    btn_cancel = types.KeyboardButton('/cancel')
    services_keyboard.add(btn_airbandserver, btn_rtl433)
    services_keyboard.add(btn_soapyserver, btn_spyserver)
    services_keyboard.add(btn_tcpserver, btn_telegrambot)
    services_keyboard.add(btn_cancel)
    bot.reply_to(message, text, reply_markup=services_keyboard)

# Bot services handle - telegrambot
@bot.message_handler(commands=['telegrambot'])
def service_telegrambot(message):
    text = 'Telegram Bot Service:'
    unitname = 'telegrambot.service'
    cmdname = '/telegrambot'
    remove_keyboard = types.ReplyKeyboardRemove(selective=False)
    action = message.text.removeprefix(f'{cmdname} ').upper()
    if action == 'START':
        bot.reply_to(message, 'Starting service...', reply_markup=remove_keyboard)
        subprocess.call(['sudo', 'systemctl', 'start', unitname])
        return None
    elif action == 'STATUS':
        enabled = subprocess.call(['sudo', 'systemctl', 'is-enabled', unitname])
        active = subprocess.call(['sudo', 'systemctl', 'is-active', unitname])
        if enabled == 0:
            enabled = 'enabled'
        else:
            enabled = 'disabled'
        if active == 0:
            active = 'active'
        else:
            active = 'inactive'
        bot.reply_to(message, f'Service is {enabled} and {active}.', reply_markup=remove_keyboard)
        return None
    elif action == 'STOP':
        bot.reply_to(message, 'Stoping service...', reply_markup=remove_keyboard)
        subprocess.call(['sudo', 'systemctl', 'stop', unitname])
        return None
    elif action == 'ENABLE':
        bot.reply_to(message, 'Enabling service...', reply_markup=remove_keyboard)
        subprocess.call(['sudo', 'systemctl', 'enable', unitname])
        return None
    elif action == 'DISABLE':
        bot.reply_to(message, 'Disabling service...', reply_markup=remove_keyboard)
        subprocess.call(['sudo', 'systemctl', 'disable', unitname])
        return None
    service_keyboard = types.ReplyKeyboardMarkup()
    btn_start = types.KeyboardButton(f'{cmdname} start')
    btn_stop = types.KeyboardButton(f'{cmdname} stop')
    btn_enable = types.KeyboardButton(f'{cmdname} enable')
    btn_disable = types.KeyboardButton(f'{cmdname} disable')
    btn_status = types.KeyboardButton(f'{cmdname} status')
    btn_cancel = types.KeyboardButton('/cancel')
    service_keyboard.add(btn_start, btn_stop) 
    service_keyboard.add(btn_enable, btn_disable)
    service_keyboard.add(btn_status)
    service_keyboard.add(btn_cancel)
    bot.reply_to(message, text, reply_markup=service_keyboard)

# Bot services handle - sdr servers
@bot.message_handler(commands=['spyserver', 'rtl433', 'soapyserver', 'airbandserver', 'tcpserver'])
def service_sdrservers(message):
    if message.text.lower().strip().startswith('/spyserver'):
        text = 'Spyserver Service:'
        unitname = 'spyserver.service'
        cmdname = '/spyserver'
    elif message.text.lower().strip().startswith('/rtl433'):
        text = 'Rtl433 Service:'
        unitname = 'rtl433.service'
        cmdname = '/rtl433'
    elif message.text.lower().strip().startswith('/soapyserver'):
        text = 'SoapyServer Service:'
        unitname = 'soapyserver.service'
        cmdname = '/soapyserver'
    elif message.text.lower().strip().startswith('/airbandserver'):
        text = 'AirbandServer Service:'
        unitname = 'rtlairband.service'
        cmdname = '/airbandserver'
    elif message.text.lower().strip().startswith('/tcpserver'):
        text = 'TcpServer Service:'
        unitname = 'rtltcp.service'
        cmdname = '/tcpserver'
    remove_keyboard = types.ReplyKeyboardRemove(selective=False)
    action = message.text.removeprefix(f'{cmdname} ').upper()
    if action == 'START':
        bot.reply_to(message, 'Starting service...', reply_markup=remove_keyboard)
        stop_all_sdr_services()
        subprocess.call(['sudo', 'systemctl', 'start', unitname])
        return None
    elif action == 'STATUS':
        enabled = subprocess.call(['sudo', 'systemctl', 'is-enabled', unitname])
        active = subprocess.call(['sudo', 'systemctl', 'is-active', unitname])
        if enabled == 0:
            enabled = 'enabled'
        else:
            enabled = 'disabled'
        if active == 0:
            active = 'active'
        else:
            active = 'inactive'
        bot.reply_to(message, f'Service is {enabled} and {active}.', reply_markup=remove_keyboard)
        return None
    elif action == 'STOP':
        bot.reply_to(message, 'Stoping service...', reply_markup=remove_keyboard)
        subprocess.call(['sudo', 'systemctl', 'stop', unitname])
        return None
    elif action == 'ENABLE':
        bot.reply_to(message, 'Enabling service...', reply_markup=remove_keyboard)
        disable_all_sdr_services()
        subprocess.call(['sudo', 'systemctl', 'enable', unitname])
        return None
    elif action == 'DISABLE':
        bot.reply_to(message, 'Disabling service...', reply_markup=remove_keyboard)
        subprocess.call(['sudo', 'systemctl', 'disable', unitname])
        return None
    service_keyboard = types.ReplyKeyboardMarkup()
    btn_start = types.KeyboardButton(f'{cmdname} start')
    btn_stop = types.KeyboardButton(f'{cmdname} stop')
    btn_enable = types.KeyboardButton(f'{cmdname} enable')
    btn_disable = types.KeyboardButton(f'{cmdname} disable')
    btn_status = types.KeyboardButton(f'{cmdname} status')
    btn_cancel = types.KeyboardButton('/cancel')
    service_keyboard.add(btn_start, btn_stop) 
    service_keyboard.add(btn_enable, btn_disable)
    service_keyboard.add(btn_status)
    service_keyboard.add(btn_cancel)
    bot.reply_to(message, text, reply_markup=service_keyboard)


# Exit signal capture
def signal_handler(signal, frame):
    global bot
    global syslogsrv
    bot.stop_polling()
    bot.stop_bot()
    syslogsrv.stop()
    syslogsrv.join()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGQUIT, signal_handler)
signal.signal(signal.SIGABRT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


# Bot start polling
bot.infinity_polling(interval=1, timeout=60)

# Exit
notifier.stop()
print("Bye!")
