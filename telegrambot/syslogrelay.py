from threading import Thread
from time import sleep
import socket
import json



class SyslogServer(Thread):
    def __init__(self, bot, oid):
        super(SyslogServer, self).__init__()
        self.bot = bot
        self.owner_id = int(oid)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udp_ip = '127.0.0.1'
        self.udp_port = 1433
        self.running = False
    
    def run(self):
        self.sock.bind((self.udp_ip, self.udp_port))
        self.sock.settimeout(1)
        self.running = True
        while self.running:
            try:
                line = self.sock.recv(1024)
                self.send(line)
            except socket.timeout:
                continue
            except:
                self.running = False
        self.sock.close()
    
    def stop(self):
        self.running = False

    def sanitize(self, line):
        try:
            jsontext = line.decode('UTF-8').split(' - - - ')[1]
            jsontext = json.loads(jsontext)
            text = f"{jsontext.pop('time')}\n\n"
            for key in jsontext.keys():
                if key == 'enabled':
                    return False
                text += f"{key}: {jsontext[key]}\n"
            return text
        except:
            return False

    def send(self, line):
        text = self.sanitize(line)
        if text:
            self.bot.send_message(self.owner_id, text)
            sleep(2)
