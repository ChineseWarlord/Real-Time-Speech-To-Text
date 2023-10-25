import tkinter as tk
import threading
import signal
import queue
import time
import sys

import keyboard


def show_subtitle(x, y, q):
    root = tk.Tk()
    root.attributes("-alpha", 0.0) # set the window to be completely transparent
    root.overrideredirect(True) # remove window decorations
    root.attributes("-topmost", True) # make the window always on top
    label = tk.Label(root, text=q.get(), font=("Helvetica", 32), bg='black', fg='white')
    label.pack()
    width = label.winfo_reqwidth() # get the required width of the label
    height = label.winfo_reqheight() # get the required height of the label
    screen_width = root.winfo_screenwidth() # get the width of the screen
    screen_height = root.winfo_screenheight() # get the height of the screen
    x = screen_width - width - x # calculate the x coordinate
    y = screen_height - height - y # calculate the y coordinate
    root.geometry('+{}+{}'.format(x, y)) # position the window
    root.attributes("-alpha", 1.0) # make the window visible
    root.lift() # bring the window to the top
    
    # make the window moveable
    def move_window(event):
        x, y = event.x_root, event.y_root
        x_offset = x - root.winfo_x()
        y_offset = y - root.winfo_y()

        def update_position(event):
            x, y = event.x_root, event.y_root
            root.geometry('+{0}+{1}'.format(x - x_offset, y - y_offset))
        label.bind('<B1-Motion>', update_position)
    label.bind('<Button-1>', move_window)
    
    root.mainloop()

def setup_overlay():
    root = tk.Tk()
    root.overrideredirect(True) # remove window decorations
    screen_width = root.winfo_screenwidth() # get the width of the screen
    screen_height = root.winfo_screenheight() # get the height of the screen
    x = screen_width - 100 # calculate the x coordinate
    y = screen_height - 100 # calculate the y coordinate
    root.geometry('+{}+{}'.format(x, y)) # position the window
    root.lift() # bring the window to the top
    root.attributes("-alpha", 0.0) # set the window to be completely transparent
    root.attributes("-topmost", True) # make the window always on top
    #root.attributes("-alpha", 1.0) # make the window visible
    #label = tk.Label(root, text="TEST TEST TEST SET SETSETTSETT", font=("Helvetica", 32), bg='black', fg='white')
    #label.pack()
    #width = label.winfo_reqwidth() # get the required width of the label
    #height = label.winfo_reqheight() # get the required height of the label
    
    ## make the window moveable
    #def move_window(event):
    #    x, y = event.x_root, event.y_root
    #    x_offset = x - root.winfo_x()
    #    y_offset = y - root.winfo_y()

    #    def update_position(event):
    #        x, y = event.x_root, event.y_root
    #        root.geometry('+{0}+{1}'.format(x - x_offset, y - y_offset))
    #    label.bind('<B1-Motion>', update_position)
    #label.bind('<Button-1>', move_window)
    
    #root.mainloop()
    root.withdraw()
    
    return root

def move_window(root,label):
    # make the window moveable
    def move_window(event):
        x, y = event.x_root, event.y_root
        x_offset = x - root.winfo_x()
        y_offset = y - root.winfo_y()

        def update_position(event):
            x, y = event.x_root, event.y_root
            root.geometry('+{0}+{1}'.format(x - x_offset, y - y_offset))
        label.bind('<B1-Motion>', update_position)
    label.bind('<Button-1>', move_window)
        
def close_app():
    print('Closing subtitler.')
    sys.exit(0)

if __name__ == '__main__':
    q = queue.Queue()
    signal.signal(signal.SIGINT, close_app)
    
    overlay = setup_overlay()
    subtitle = tk.Label()
    label = tk.Label(overlay, text="TEST TEST TEST SET SETSETTSETT", font=("Helvetica", 32), bg='black', fg='white')
    label.pack()
    overlay.mainloop()
    #subtitle_thread = threading.Thread(target=show_subtitle,args=(100, 100,q),daemon=True).start()
    
    #while True:
    #    text = str(input("Write text: "))
    #    q.put(text)
    #    if text == "q":
    #        close_app()
    #    # catch keyboard interrupt to stop main thread
    #    signal.signal(signal.SIGINT, close_app)
    #    if keyboard.is_pressed("esc"):
    #        close_app()
    #    time.sleep(0.05)




#def show_subtitle(x, y, q):
#    global root
#    global label
#    while True:
#        text = q.get()
#        if text == "q":
#            break
#        qsize = q.qsize()
#        if qsize > 1: # If there are more messages in the queue, discard them and only show the latest one
#            q.get()
#        root.after(50, label.config, {'text': text}) # update the label with the new text using the after method
#        width = label.winfo_reqwidth() # get the required width of the label
#        height = label.winfo_reqheight() # get the required height of the label
#        screen_width = root.winfo_screenwidth() # get the width of the screen
#        screen_height = root.winfo_screenheight() # get the height of the screen
#        x = screen_width - width - x # calculate the x coordinate
#        y = screen_height - height - y # calculate the y coordinate
#        root.geometry('+{}+{}'.format(x, y)) # position the window
#        time.sleep(0.05)

#    root.destroy()

#def close_app():
#    print('Closing subtitler.')
#    sys.exit(0)

#if __name__ == '__main__':
#    q = queue.Queue()
#    root = tk.Tk()
#    root.attributes("-alpha", 0.0) # set the window to be completely transparent
#    root.overrideredirect(True) # remove window decorations
#    root.attributes("-topmost", True) # make the window always on top
#    label = tk.Label(root, text='', font=("Helvetica", 32), bg='black', fg='white')
#    label.pack()

#    subtitle_thread = threading.Thread(target=show_subtitle,args=(100, 100,q),daemon=True)
#    subtitle_thread.start()

#    while True:
#        text = input("Write text: ")
#        q.put(text)
#        if text == "q":
#            q.put("q") # add a sentinel to signal the end of the thread
#            subtitle_thread.join() # wait for the thread to finish
#            close_app()
#        # catch keyboard interrupt to stop main thread
#        signal.signal(signal.SIGINT, close_app)
#        if keyboard.is_pressed("esc"):
#            q.put("q") # add a sentinel to signal the end of the thread
#            subtitle_thread.join() # wait for the thread to finish
#            close_app()
#        time.sleep(0.05)