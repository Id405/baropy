# Baropy
Python library for interfacing with barotrauma
Only unix compatible

# Setting Up Barotrauma To Work With Baropy
Barotrauma must be run so that a pipefile pipes into it and it pipes out to a tcp server pointing to a unix domain socket, ideally this tcp server should be able to accept multiple connections so multiple scripts can interface with barotrauma. Both ncat from nmap and netcat-openbsd cannot accept multiple connections while pointing to a unix domain socket and I cannot find a tool that can do this so I wrote my own with the help of tazial

```python
#!/usr/bin/python3
# pipe2net
# forwards stdin to a tcp server that allows multiple connections
# written by 8o7wer and tazial
import socket
import sys 
import os
import threading

clients = []
def forwarder():
    for line in sys.stdin:
        i = 0 
        while i < len(clients):
            client = clients[i]
            try:
                client.sendall(line.encode())
                i += 1
            except:
                del clients[i]
    

s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
address = sys.argv[1]

try:
    os.remove(address)
except:
    pass

s.bind(address)
s.listen(10)

t = threading.Thread(target=forwarder)
t.start()

while True:
    c, addr = s.accept()
    clients.append(c)
```

# Examples

List currently connected players

```python
from baropy import Barotrauma

baro = Barotrauma("/tmp/testin", "/tmp/testsock")

players = baro.get_clients()

for player in players:
    print("name: " + player.name)
    print("id: " + player.id)
    print("ip: " + player.ip)
```

# Classes

## Barotrauma class

Note: this may not be up to date, at all

**Barotrauma(path_to_barotrauma_pipefile, path_to_unix_domain_socket, writetimeout=0.1, responsetime=0.1)**

constructor for Barotrauma

**send_command(command, args=[], followup=[])**

Returns: none

send_command sends a command with args to barotrauma then follows up with commands in followup with a delay of writetimeout between each command

**response(command, args=[])**

Returns: list of lines (as strings) of command response

response sends a command with args to barotrauma then waits for responsetime. It then returns barotraumas response. Keep in mind there may be extra text after response that is not barotraumas response to the command as it only trims off the lines in udsbuffer before the command. It does not include the command as the first line of the response

**ban_name(name, reason, duration)**

Returns: none

bans user by name

**ban_ip(ip, reason, duration)**

Returns: none

bans user by ip

**get_clients()**

Returns: list of Player objects

gets all clients connected to the server

**udsbuffer**

Variable, holds the udsbuffer object

**get_player_by_name(name) get_player_by_id(id) get_player_by_ip(ip)**

Returns: Player or -1 if the player couldnt be found

# Udsbuffer

Udsbuffer holds the buffer for incoming logs from barotrauma, dont make your own of this

**Udsbuffer(size=128)**

Constructor for Udsbuffer

**add(data)**

Returns: none

appends data to the buffer

**flush()**

Returns: none

flushes buffer

**buffer**

Variable, holds the data sent from the server in a list of lines

## Player

**name**

Variable, the players name

**id**

Variable, the players id

**ip**

Variable, the players ip

**ban_ip(reason, duration) and ban_name(reason, duration)**

Returns: none

**give_rank(rank) and give_permission(permission)**

Returns: none
