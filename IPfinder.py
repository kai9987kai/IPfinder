import socket
import tkinter as tk
from tkinter import *
import webbrowser
from tkinter import messagebox

def callback():
    webbrowser.open_new(r"https://github.com/kai9987kai/IPfinder/wiki")


def callback2():
    webbrowser.open_new(r"https://github.com/kai9987kai/IPfinder")


def callback3():
    webbrowser.open_new(r"https://autoclicker.webstarts.com/index.html?r=20181122215206")

def clicked():
    messagebox.showinfo('CONTACT', 'Email: kai9987kai@gmail.com')

def getIp(input_url):
    ip_info = socket.gethostbyname(input_url)
    ip.config(text=ip_info)
def EXITME():
    exit(0)  # crashed prog so it closes
        # strtoint("crashmE!")

root = tk.Tk()
# optionally give it a title
root.title("IP Fetcher")
# set the root window's height, width and x,y position
# x and y are the coordinates of the upper left corner
w = 450
h = 330
x = 50
y = 100
# use width x height + x_offset + y_offset (no spaces!)
root.geometry("%dx%d+%d+%d" % (w, h, x, y))

# use a colorful frame
frame = tk.Frame(root, bg='#F5F5F5')
frame.pack(fill='both', expand='yes')

# position a label on the frame using place(x, y)
# place(x=0, y=0) would be the upper left frame corner
label = tk.Label(frame, text="Enter Url Below & Click GET IP "  ,fg="black" , bg = '#F5F5F5' )
label.place(x=10, y=10)
label.config(font=("Times", 18))

label = tk.Label(frame, text="URL :  "  ,fg="black", bg = '#F5F5F5' )
label.place(x=10, y=100)
label.config(font=("Times", 18))

label = tk.Label(frame, text="IP: "  ,fg="black", bg = '#F5F5F5' )
label.place(x=10, y=200)
label.config(font=("Times", 18,'bold'))

ip= tk.Label(frame, text="0.0.0.0"  ,fg="black", bg = '#F5F5F5')
ip.place(x=150, y=200)
ip.config(font=("Times", 26))

input_url = tk.Entry(frame)
input_url.place(x=150, y=100)
input_url.config(font=("Times", 18,'bold'))

#Get IP
button = tk.Button(frame, text="GET IP", bg='#456bbc',fg="white",command=lambda:getIp(input_url.get()))
button.place(x=10, y=280 , width=180)
button.config(font=("Times", 16))

menu = Menu(root)
new_item = Menu(menu)
new_item.add_command(label='ABOUT', command=callback)
new_item.add_command(label='GITHUB PAGE', command=callback2)
new_item.add_separator()
new_item.add_command(label='GET IP', command=lambda:getIp(input_url.get()))
new_item.add_command(label='EXIT', command=EXITME)
menu.add_cascade(label='Menu', menu=new_item)
new_item2 = Menu(menu)
new_item2.add_command(label='CONTACT', command=clicked)
menu.add_cascade(label='Help', menu=new_item2)
root.config(menu=menu)

root.resizable(False, False)
root.iconbitmap('favicon.ico')
root.mainloop()
