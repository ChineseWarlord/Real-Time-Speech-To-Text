import tkinter as tk
import threading
import queue
import signal
import sys
import time
import keyboard
import random

# Function to generate random text to test subtitle display
def generate_text(num_sentences):
    # list of possible sentence structures
    structures = ["Subject Verb Object",
                  "Subject Verb Adjective",
                  "Subject Verb Adverb",
                  "Subject Verb",
                  "Subject Adverb Verb",
                  "Subject Adjective Noun",
                  "Subject Noun Verb",
                  "Subject Noun Adjective",
                  "Subject Adverb Verb Object",
                  "Subject Verb Adjective Noun"]

    # list of possible subjects, verbs, adjectives, adverbs, and objects
    subjects = ["I", "You", "He", "She", "It", "We", "They"]
    verbs = ["run", "jump", "swim", "dance", "sing", "read", "write", "eat", "sleep", "talk"]
    adjectives = ["happy", "sad", "angry", "excited", "bored", "tired", "hungry", "thirsty"]
    adverbs = ["quickly", "slowly", "happily", "sadly", "angrily", "excitedly"]
    objects = ["the ball", "the book", "the car", "the house", "the tree", "the sky", "the ocean"]

    # generate the specified number of sentences
    for i in range(num_sentences):
        # choose a random sentence structure
        structure = random.choice(structures)

        # split the structure into its component parts
        parts = structure.split()

        # generate a random word for each part of the sentence
        subject = random.choice(subjects)
        verb = random.choice(verbs)
        adjective = random.choice(adjectives)
        adverb = random.choice(adverbs)
        obj = random.choice(objects)

        # construct the sentence using the chosen structure and words
        sentence = ""
        for part in parts:
            if part == "Subject":
                sentence += subject
            elif part == "Verb":
                sentence += verb
            elif part == "Adjective":
                sentence += adjective
            elif part == "Adverb":
                sentence += adverb
            elif part == "Object":
                sentence += obj
            sentence += " "
        sentence = sentence.strip()
        sentence += "."
        return sentence


def create_root():
    root = tk.Tk()
    root.attributes("-alpha", 0.0) # set the window to be completely transparent
    root.overrideredirect(True) # remove window decorations
    root.attributes("-topmost", True) # make the window always on top
    label = tk.Label(root, text='', font=("Helvetica", 32), bg='black', fg='white')
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

def show_subtitle(x, y, q):
    root, label = create_root()
    width = label.winfo_reqwidth() # Get the required width of the label
    height = label.winfo_reqheight() # Get the required height of the label
    screen_width = root.winfo_screenwidth() # Get the width of the screen
    screen_height = root.winfo_screenheight() # Get the height of the screen
    x = screen_width - width - x # Calculate the x coordinate
    y = screen_height - height - y # Calculate the y coordinate
    root.geometry('+{}+{}'.format(x, y)) # Position the window
    root.attributes("-alpha", 1.0) # Make the window visible
    root.lift() # Bring the window to the top
    make_window_movable(label, root)
    
    while True:
        text = q.get()
        label.config(text=text)
        if text == "q":
            break
        root.update()
        
    root.destroy()

def close_app():
    print('Closing subtitler.')
    sys.exit(0)

if __name__ == '__main__':
    q = queue.Queue()
    subtitle_thread = threading.Thread(target=show_subtitle,args=(100, 100, q),daemon=True)
    subtitle_thread.start()

    while True:
        text = generate_text(1)
        q.put(text)
        if text == "q":
            close_app()
        # Catch keyboard interrupt to stop main thread
        signal.signal(signal.SIGINT, close_app)
        if keyboard.is_pressed("esc"):
            close_app()
        time.sleep(0.05)
