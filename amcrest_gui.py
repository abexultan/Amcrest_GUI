import tkinter as tk
import cv2
from PIL import Image, ImageTk
from amcrest import AmcrestCamera
from tkinter import messagebox
from typing import Tuple
from datetime import datetime
import time

connection = False
cap = None
manipulate = False
scale = 100
camera = None

# Creating the main loop for the interface
root = tk.Tk()
root.bind('<Escape>', lambda e: root.quit())
root.title("Amcrest view.")

# Image widget
lmain = tk.Label(root)
lmain.grid(column=3, sticky='SW')

# Hinting fields
ip_label = tk.Label(root, text="Enter IP Adress:", borderwidth=1,
              relief="raised")
login_label = tk.Label(root, text="Enter login:", borderwidth=1,
                 relief="raised")
password_label = tk.Label(root, text="Enter password:", borderwidth=1,
                    relief="raised")
scale_label = tk.Label(root, text="Scale in %:", borderwidth=1,
                       relief="raised")

ip_label.grid(row=0, sticky='NW', column=0)
login_label.grid(row=1, sticky='NW', column=0)
password_label.grid(row=2, sticky='NW', column=0)
scale_label.grid(row=5, sticky='NW', column=0)

# Default values
ip_default = tk.StringVar(root, value="192.168.1.103")
login_default = tk.StringVar(root, value="admin")
password_default = tk.StringVar(root, value="passwd0000")

# User input fields
ip_field = tk.Entry(root, textvariable=ip_default)
login_field = tk.Entry(root, textvariable=login_default)
password_field = tk.Entry(root, textvariable=password_default)
scale_field = tk.Entry(root)
timer_field = tk.Entry(root)

ip_field.grid(row=0, column=1, rowspan=1, sticky='NW')
login_field.grid(row=1, column=1, rowspan=1, sticky='NW')
password_field.grid(row=2, column=1, rowspan=1, sticky='NW')
scale_field.grid(row=5, column=1, rowspan=1, sticky='NW')
timer_field.grid(row=6, column=1, rowspan=1, sticky='NW')


def show_frame():
    '''
    Main function, shows the frame of the stream captured from
    rtsp url of the provided Amcrest camera
    '''
    global connection
    global cap
    global scale
    
    if not connection:
        connection, cap = connect()
        
    if connection:
        _, frame = cap.read()
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Resizing to the 20% of the original resolution
        try:
            scale_percent = int(scale_field.get())
        except:
            scale_percent = 20
            
        w = (cv2image.shape[1] * scale_percent) // 100
        h = (cv2image.shape[0] * scale_percent) // 100
        cv2image_resized = cv2.resize(cv2image, (w, h),
                                      interpolation=cv2.INTER_AREA)

        # Converting to the Image object in order to use with tk interface
        img = Image.fromarray(cv2image_resized)
        
        if manipulate:
            img = img.convert('LA')
            img = img.transpose(Image.ROTATE_90)


        imgtk = ImageTk.PhotoImage(image=img)
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)
        lmain.after(10, show_frame)
    else:
        # In case if connection is unsuccessfull, raises the messagebox
        messagebox.showerror("Connection error.", 
                             "Check IP, admin and password information.")


def connect() -> Tuple[bool, cv2.VideoCapture]:
    '''
    Function used to connect and set up global variables
    '''
    global camera
    global cap
    try:
        camera = AmcrestCamera(ip_field.get(), 80, login_field.get(), password_field.get()).camera
        rstp_url = camera.rtsp_url()
        cap = cv2.VideoCapture(rstp_url)
        connection = True
        return connection, cap
    except:
        return False, None
    
def snapshot():
    '''
    Saves the snapshot from the stream
    '''
    global camera
    current_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    camera.snapshot(0, "./" + current_time + ".jpeg")
    
def record_stream():
    '''
    Records the stream from the camera into a videofile
    for the given period of time
    '''
    current_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    out = cv2.VideoWriter('./' + current_time + '.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 10,
                          (frame_width, frame_height))
    try:
        timer = int(timer_field.get())
        difference = 0
        now = time.time()
        while(difference <= timer):
            _, frame = cap.read()
            out.write(frame)
            later = time.time()
            difference = int(later-now)
        out.release()
    except:
        messagebox.showerror("Innapropriate time", 
                             "Please, check the timer value")
            
def exit():
    global cap
    if cap:
        cap.release()
    root.destroy()
    

# Buttons to initiate the interface changes, connect shows the frame
# exit, as the name suggests, exits the interface
connect_button = tk.Button(root, text="Connect", command=show_frame,
                    borderwidth=3)
connect_button.grid(row=3, column=0, sticky='NW', rowspan=1, columnspan=1)

exit_button = tk.Button(root, text="Quit", command=exit,
                 borderwidth=3)
exit_button.grid(row=3, column=1, sticky='NW', rowspan=1, columnspan=1)

# Snapshot and record:
snapshot_button = tk.Button(root, text="Snapshot", command=snapshot,
                     borderwidth=3)
snapshot_button.grid(row=4, column=0, sticky="NW", rowspan=1, columnspan=1)

record_button = tk.Button(root, text="Record stream", command=record_stream,
                         borderwidth=3)
record_button.grid(row=6 , column=0, sticky="NW", rowspan=1, columnspan=1)


# Start of the main loop
root.mainloop()