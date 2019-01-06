import time
import socket
import sys
import os
from threading import Thread

class Barotrauma:
    def __init__(self, stdinpath, udspath, writetimeout=0.1, responsetime=0.1):
        self.stdinpath = stdinpath
        self.udspath = udspath
        self.writetimeout = writetimeout
        self.responsetime = 0.3
        self.udsbuffer = Udsbuffer()
        self.__start_uds_thread()

    def __uds_thread(self):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            sock.connect(self.udspath)
        except Exception as error:
            raise Exception("Error connecting to unix domain socket: " + repr(error))
        while True:
            data = []
            data = ""
            while True:
                data = data + sock.recv(1).decode()
                if data.endswith("\n"):
                    break
            self.udsbuffer.add(data.strip("\n"))

    def __start_uds_thread(self):
        thread = Thread(target=self.__uds_thread)
        thread.start()

    def send_command(self, command, args=[], followup=[]):
        try:
            with open(self.stdinpath, "w") as file:
                file.write(command + " ".join(args))
                time.sleep(self.writetimeout)
                for string in followup:
                    file.write(string)
                    time.sleep(self.writetimeout)
        except Exception as error:
            raise Exception("Error on writing to pipefile: " + repr(error))

    def response(self, command, args=[]):
        self.udsbuffer.flush()
        self.send_command(command, args)

        time.sleep(self.responsetime)

        response = self.udsbuffer.buffer

        index = [i for i, s in enumerate(response) if command in s][0]

        response = response[index+1:]

        return response

    def ban_name(self, name, reason, duration):
        self.send_command("ban", [name], [reason, duration])

    def ban_ip(self, ip, reason, duration):
        self.send_command("banip", [ip], [reason, duration])

    def get_clients(self):
        responses = self.response("clientlist")
        responses = [i for i in responses if i.startswith("-")]
        clients = []
        for response in responses:
            response = response[2:]
            if(response.find("playing") == -1):
                name = response[response.find(":")+2:response.rfind(",")]
            else:
                name = response[response.find(":")+2:response.find("playing")-1]
            id = response[:response.find(":")]
            ip = response[response.rfind(",")+2:].strip()
            clients.append(Player(name, id, ip))

        return clients

class Udsbuffer:
    def __init__(self, size=128):
        self.buffer = []
        self.size = 128

    def add(self, data):
        self.buffer.append(data)
        if len(self.buffer) > self.size:
            del self.buffer[self.size:]

    def flush(self):
        self.buffer.clear()

class Player:
    def __init__(self, name, id, ip):
        self.name = name
        self.id = id
        self.ip = ip
