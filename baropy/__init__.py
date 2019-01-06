import time
import socket
import sys
import os
from threading import Thread

class Barotrauma:
    def __init__(self, stdinpath, udspath, writetimeout=0.1, responsetime=0.1, buffersize=128):
        self.stdinpath = stdinpath
        self.udspath = udspath
        self.writetimeout = writetimeout
        self.responsetime = 0.3
        self.udsbuffer = Udsbuffer(size = buffersize)
        self.__start_uds_thread()

    def __uds_thread(self):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            sock.connect(self.udspath)
        except Exception as error:
            raise Exception("Error connecting to unix domain socket: " + repr(error))
        while True:
            data = ""
            while True: # Recieve exactly one line of data
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
                for string in followup:
                    time.sleep(self.writetimeout)
                    file.write(string)
        except Exception as error:
            raise Exception("Error on writing to pipefile: " + repr(error))

    def response(self, command, args=[]):
        self.udsbuffer.flush()
        self.send_command(command, args)

        time.sleep(self.responsetime)

        response = self.udsbuffer.buffer

        index = [i for i, s in enumerate(response) if command in s][0] #Get index of command in game output

        response = response[index+1:] #trim buffer array so that its only text after the command in game output

        return response

    def ban_name(self, name, reason, duration):
        self.send_command("ban", [name], [reason, duration])

    def ban_ip(self, ip, reason, duration):
        self.send_command("banip", [ip], [reason, duration])

    def get_players(self):
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
            clients.append(Player(self, name, id, ip))

        return clients

    def get_player_by_name(self, name): #returns -1 if a client cant be found
        clients = self.get_players()
        for client in clients:
            if client.name.lower() == name.lower():
                return client
        return -1

    def get_player_by_ip(self, ip): #same as above
        clients = self.get_players()
        for client in clients:
            if client.ip == ip:
                return ip
        return -1

    def get_player_by_id(self, id): #Id must be a string
        clients = self.get_players()
        for client in clients:
            if client.id == id:
                return client
        return -1



class Udsbuffer: #Holds the buffer for incoming lines of data from the game server
    def __init__(self, size=128):
        self.buffer = []
        self.size = size

    def add(self, data): #Please use this function insteada of udsbuffer.append.(Data) as this function limits the size of the list
        self.buffer.append(data)
        if len(self.buffer) > self.size:
            del self.buffer[self.size:]

    def flush(self):
        self.buffer.clear()

class Player:
    def __init__(self, barotrauma, name, id, ip):
        self.name = name
        self.id = id
        self.ip = ip
        self.barotrauma = barotrauma

    def ban_name(self, reason, duration):
        barotrauma.ban_name(self.name, reason, duration)

    def ban_ip(self, reason, duration):
        barotrauma.ban_name(self.ip, reason, duration)

    def give_rank(self, rank):
        barotrauma.send_command(give_rank, [id], [rank])

    def give_permission(self, permission):
        barotrauma.send_command(give_rank, [id], [permission])
