import tkinter as tk
import sys

def create_root():
    root = tk.Tk()
    root.attributes("-alpha", 0.0) # set the window to be completely transparent
    root.overrideredirect(True) # remove window decorations
    root.attributes("-topmost", True) # make the window always on top
    label = tk.Label(root, text='TEST', font=("Helvetica", 32), bg='black', fg='white')
    label.pack()
    return root, label

def make_window_movable(label, root):
    def move_window(event):
        x, y = event.x_root, event.y_root
        x_offset = x - root.winfo_x()
        y_offset = y - root.winfo_y()

        def update_position(event):
            x, y = event.x_root, event.y_root
            root.geometry('+{0}+{1}'.format(x - x_offset, y - y_offset))
        label.bind('<B1-Motion>', update_position)
    label.bind('<Button-1>', move_window)

def show_subtitle(x, y, q, stop_event):
    root, label = create_root()
    width = label.winfo_reqwidth() # get the required width of the label
    height = label.winfo_reqheight() # get the required height of the label
    screen_width = root.winfo_screenwidth() # get the width of the screen
    screen_height = root.winfo_screenheight() # get the height of the screen
    x = screen_width - width - x # calculate the x coordinate
    y = screen_height - height - y # calculate the y coordinate
    root.geometry('+{}+{}'.format(x, y)) # position the window
    root.attributes("-alpha", 1.0) # make the window visible
    root.lift() # bring the window to the top
    make_window_movable(label, root)
    
    while not stop_event.is_set():
        try:
            text = q.get()
            label.config(text=text)
            if text == "q":
                break
            root.update()
        except Exception as e:
            print(f"No subtitles! {e}")
        
    root.destroy()
    close_app()

def close_app():
    print('Closing subtitler.')
    sys.exit(0)