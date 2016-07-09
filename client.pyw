from tkinter import *
from tkinter import messagebox
import datetime
import time
import socket
from multiprocessing.dummy import Pool

def setStatus(text):
    statusbar.config(text=str(text))

def addToLog(text):
    log.insert(END, text + "\n")

def update():
    time.sleep(1 / 60)
    root.update()

def on_closing():
    global WINDOW_EXISTS
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()
        WINDOW_EXISTS = False  # For the correct turn-off

def receiveMessages():
    global start
    start = time.time()

def sendMessage(*args):
    global conn
    
    message = getText()
    addToLog(message)  # Temporary.
    print(message.encode("utf-8"))
    
    conn = socket.socket()
    conn.connect(("localhost", 14000))
    conn.send(message.encode("utf-8"))
    
    data = conn.recv(1024)
    addToLog(data.decode("utf-8"))
             
    conn.close()
    
    return

def getText(*args):
    text = message_entry.get()
    message_entry.delete(0, END)
    return text

pool = Pool(15)

root = Tk()
root.wm_title("Python Chat")
root.protocol("WM_DELETE_WINDOW", on_closing)

WIDTH = 15  # Divisible by 15.

log = Text(root)
log.insert(END, '''Welcome to Fullmetal Chat v0.0!\n''')  # Welcome message.
log.grid(row=0, column=0, columnspan=WIDTH // 15 * 14, padx=1, pady=1)

users = Listbox(root)
users.grid(row=0, column=WIDTH // 15 * 14, columnspan=WIDTH // 15, 
                                                sticky=N+S+W+E, padx=1, pady=1)
for i in range(5):
    users.insert(END, "User #-" + str(i))

message_entry = Entry(root)
message_entry.bind("<Return>", sendMessage)
message_entry.grid(row=1, sticky=N+S+E+W, padx=1, pady=2, 
                                                   columnspan=WIDTH // 15 * 14)

message_button = Button(root, command=sendMessage, text="Send")
message_button.grid(row=1, sticky=E+W+S+N, padx=1, pady=2, 
                               columnspan=WIDTH // 15, column=WIDTH // 15 * 14)

statusbar = Label(root, text="Nothing happened", border=1, 
                                                        relief=RIDGE, anchor=W)
statusbar.grid(sticky=E+W, columnspan=WIDTH, pady=(2, 0))

start = time.time()
WINDOW_EXISTS = True  # For the correct turn-off.
while WINDOW_EXISTS:  # Mainloop.
    setStatus("Ping: " + str(int((time.time() - start) * 1000)) + " ms.")
    update()

# root.mainloop() doesn't work, so we need to update the window
# manually with root.update().