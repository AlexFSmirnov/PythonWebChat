from tkinter import *
from gui import *
import datetime
import time
import socket
import json
import configparser


def onClosing():
    global WINDOW_EXISTS
    if True or messagebox.askokcancel("Quit", "Do you want to quit?"):
        if is_connected: disconnect()
        root.destroy()
        WINDOW_EXISTS = False  # For the correct turn-off
        
def updateUsers(active_users):
    global users
    users.delete(0, END)
    for user in active_users: users.insert(END, user)

def updateMessages(new_messages):
    for msg in new_messages: 
        addToLog(msg)   
    # TODO: nickname coloring

def updateData():
    global last_connection
    global is_connected
    global last_idx
    last_connection = time.time()
    if not is_connected:
        return
    try:  # Checking, if the client can get response from the server.
        conn = socket.socket()
        conn.connect((server_ip, server_port))
        
        send_data = ["update_data", last_idx]
        conn.send(json.dumps(send_data).encode("utf-8"))
        
        rec_data = json.loads(conn.recv(16384).decode("utf-8"))
        conn.close()
        
        new_messages = rec_data[0]
        active_users = rec_data[1]
        last_idx += len(new_messages)
        
        updateUsers(active_users)         
        updateMessages(new_messages)       
    except:  # If he can't, he disconnects.
        is_connected = False
        addToLog("System> You were disconnected.")

def sendMessage(message):    
    if not is_connected:
        addToLog("System> Connect to a server first!")
        return
    conn = socket.socket()
    conn.connect((server_ip, server_port))
    send_data = ["send_message", username + "> " + message]
    conn.send(json.dumps(send_data).encode("utf-8"))             
    conn.close()
    return

def checkServer(addr, value='', timeout=999):
    try:
        conn = socket.socket()
        conn.settimeout(timeout)
        conn.connect(addr)
        conn.send(json.dumps(["check_connection", value]).encode("utf-8"))
        response = conn.recv(4096)
        conn.close()
        return response
    except:
        return False

#COMMANDS--------------------------------------------------------------COMMANDS#
def checkCommand(*args):
    text = getText() + "  "
    if text[0] == '/':
        command = text[1:text.index(" ")]
        value   = text[text.index(" ") + 1:]
        if command not in command_list.keys():
            addToLog("System> Unknown command. Type /command_list to see" +
                                    " avaliable commands.")
            return
        command_list[command](value)        
        
    else:
        sendMessage(text)

def connectToServer(addr):
    global server_ip
    global server_port
    global server_name
    global is_connected
    if not username:
        addToLog("System> Set a username first! (/set_username)")
        return
    if ":" not in addr: 
        addr += ":" + str(server_port)
    addr = addr.replace(' ', '')
    ip = addr.split(":")
    server_ip = ip[0]
    server_port = int(ip[1])
    response = checkServer((server_ip, server_port), username)
    if response:
        is_connected = True
        server_name = response.decode("utf-8")
        addToLog("System> Connected to " + server_name + "!")
    else:
        addToLog("System> Connection error.")

def disconnect(*args):
    global is_connected
    global users
    if not is_connected:
        addToLog("System> Not connected.")
        return
    conn = socket.socket()
    conn.connect((server_ip, server_port))
    conn.send(json.dumps(["disconnect", username]).encode("utf-8"))
    conn.close()
    addToLog("System> Disconnected.")
    is_connected = False
    users.delete(0, END)
    users.insert(END, "Not connected")

def commandList(*args):
    addToLog("System> Avaliable commands: ")
    for cmd in command_list.keys():
        addToLog("    /" + cmd)

def setUsername(new_username):
    global username
    global config
    if is_connected:
        addToLog("System> Disconnect first!")
        return
    addToLog("System> Username set: " + new_username)
    username = new_username[:-2]
    config['DEFAULT']['username'] = username
    with open("config.ini", 'w') as fout: config.write(fout)
    fout.close()

def scanServers(timeout):
    global saved_servers
    global config
    global stop_scan
    stop_scan = False
    self_ip = socket.gethostbyname(socket.gethostname()).split('.')
    addToLog("System> Scaning the network for avaliable servers...")
    addToLog("System> You can see the progress in the status bar below.")
    update()
    
    progress_str = list("[=========================], Done: ")
    i = -1
    for s in saved_servers:
        i += 1
        prc = round(i / len(saved_servers) * 100)
        progress_str[1:round(prc / 100 * 25) + 1] = "#" * round(prc / 100 * 25)
        setStatus("Scaning saved servers: " + 
                  ''.join(progress_str) + str(s) + " (" + str(prc) + "%)")        
        self_ip[-1] = str(s)
        str_ip = '.'.join(self_ip)
        try:
            conn = socket.socket()
            conn.settimeout(float(timeout))
            conn.connect((str_ip, server_port))
            conn.send(b'0')
            addToLog("  " + str_ip + " - " + conn.recv(4096).decode("utf-8"))
            conn.close()
        except:
            pass     
        update()
    progress_str = list("[=========================], Done: ")
    found_server = False    
    for s in range(256):
        if stop_scan: 
            addToLog("System> Stopped.")
            break
        if s in saved_servers: continue
        prc = round(s / 255 * 100)
        progress_str[round(prc / 100 * 25) + 1] = "#"
        setStatus("Scaning the network: " + 
                  ''.join(progress_str) + str(s) + " (" + str(prc) + "%)")
        
        self_ip[-1] = str(s)
        str_ip = '.'.join(self_ip)
        try:
            conn = socket.socket()
            conn.settimeout(float(timeout))
            conn.connect((str_ip, server_port))
            conn.send(b'0')
            addToLog("  " + str_ip + " - " + conn.recv(4096).decode("utf-8"))
            conn.close()
            if i not in saved_servers:
                saved_servers.add(i)
                found_server = True
        except:
            pass
        if found_server:
            u_list = list(saved_servers)
            config['SAVED DATA']['saved_servers'] = json.dumps(u_list)
            with open("config.ini", 'w') as fout: config.write(fout)
            fout.close()
        update()      

def stopScan(*args):
    global stop_scan
    stop_scan = True
        
command_list = {
    "connect"      : connectToServer,
    "disconnect"   : disconnect,
    "command_list" : commandList,
    "set_username" : setUsername,
    "scan_servers" : scanServers,
    "stop_scan"    : stopScan
    }
#COMMANDS_END------------------------------------------------------COMMANDS_END#


root.wm_title("Python Chat")
root.protocol("WM_DELETE_WINDOW", onClosing)
message_field.bind("<Return>", checkCommand)
message_button.config(command=checkCommand)

config = configparser.ConfigParser()
config.read('config.ini')

server_ip = "localhost"
server_port = int(config['DEFAULT']['default_port'])
server_name = ""
is_connected = False
last_idx = -1
username = config['DEFAULT']['username']
stop_scan = False  # If it is true, the server scaning will stop.
saved_servers = set(json.loads(config['SAVED DATA']['saved_servers']))
 
welcome_message = '''  Welcome to Fullmetal Chat v0.0!
  Type /connect [ip]:[port] to connect to a chat room.
'''
if username != 'None': welcome_message = username + ',\n' + welcome_message
log.insert(END, welcome_message) 
users.insert(END, "Not connected")

last_connection = time.time()
WINDOW_EXISTS = True  # For the correct turn-off.
while WINDOW_EXISTS:  # Mainloop.
    updateData()
    if is_connected:
        setStatus("Connected to " + server_name + " (" + server_ip + ":" + 
                  str(server_port) + ")  Ping: " + 
                  str(int((time.time() - last_connection) * 1000)) + " ms.")
    else:
        setStatus("Not connected")
    update()

# root.mainloop() doesn't work, so we need to update the window
# manually with root.update().