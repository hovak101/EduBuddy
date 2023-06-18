import tkinter as tk
from screeninfo import get_monitors
from PIL import Image, ImageTk
import os
from tkinter import filedialog
import TextConverter as tc
import platform
# import ctypes
# import objc


"""
Changes to make:
- icons for all buttons
- rounded corners
- smooth animation for expanding/compressing window
- minimize on click buddy (maybe right click for settings)

"""

class Window(tk.Tk):
    def __init__(self):
        super().__init__()

        # Check windows
        self.addedDistance = 0
        if (platform.system()) == "Windows":
            self.addedDistance = 80

        self.title("EduBuddy")
        self.overrideredirect(True) # Remove window decorations (title, borders, exit & minimize buttons)
        self.attributes("-topmost", True)

        #screen info
        screen = get_monitors()[0] #number can be changed ig
        self.screen_w = screen.width
        self.screen_h = screen.height

        # Set the window's initial position
        self.padding = 15
        self.w = 200
        self.h = 300
        self.x = self.screen_w - self.w - self.padding  # X coordinate
        self.y = self.screen_h - self.h - self.padding  # Y coordinate

        self.geometry(f"+{self.x}+{self.y-self.addedDistance}")
        self.geometry(f"{self.w}x{self.h}")

        #quiz/submit button
        qs_button1 = tk.Button(self, text="S")
        qs_button2 = tk.Button(self, text="Q")
        qs_button_height = 45
        qs_button1.place(x=0, y=0, width=self.w/2, height=qs_button_height)
        qs_button2.place(x=self.w/2, y=0, width=self.w/2, height=qs_button_height)

        qs_button1.bind("<ButtonPress-1>", self.qs_button1_pres)

        # Context title box
        context_title = tk.Label(self, text="<QQQQQQQQQQQQQQQQQ>", bg="lightblue")
        context_title.place(x=3, y=45, w=self.w - 6, h=20)

        # add icon
        self.icon_size = 60
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, "media", "buddy.png")
        print(image_path)
        self.image = Image.open(image_path)
        self.image = self.image.resize((self.icon_size, self.icon_size))
        self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT)
        self.was_right = True
        self.image_tk = ImageTk.PhotoImage(self.image)
        self.img_label = tk.Label(self, image=self.image_tk)
        self.img_label.place(x=self.w-self.icon_size, y=self.h-self.icon_size)

        # Text output
        output_box = tk.Text(self, borderwidth=0, highlightthickness=0)
        output_box.place(x=3, y=65, w=self.w - 6, h=125)

        # Text input field
        text_box = tk.Text(self, borderwidth=0, highlightthickness=0)
        text_box.place(x=3, y=self.h - 50 - 65, w=self.w - 6, h=65)

        # Bind mouse events
        self.bind("<ButtonPress-1>", self.on_button_press)
        self.bind("<B1-Motion>", self.on_button_motion)
        self.bind("<ButtonRelease-1>", self.on_button_release)

        # get local file
        file_button = tk.Button(self, text="File", command=self.open_file_dialog)
        file_button.place(x=self.w/2 - 45/2, y=self.h - 48, w=45, h=45)

    def open_file_dialog(event):
        file_path = filedialog.askopenfilename()
        # Do something with the selected file path, such as printing it
        print("Selected file:", file_path)
    
    def on_button_press(self, event):
        # Capture the initial mouse position and window position
        self.x = event.x_root
        self.y = event.y_root
        self.offset_x = self.winfo_x()
        self.offset_y = self.winfo_y()

    def on_button_motion(self, event):
        # Calculate the new window position based on mouse movement
        new_x = self.offset_x + (event.x_root - self.x)
        new_y = self.offset_y + (event.y_root - self.y)
        self.geometry(f"+{new_x}+{new_y}")


    def on_button_release(self, event):
        is_left = (event.x_root - event.x + self.w/2 < self.screen_w/2)
        is_up = (event.y_root - event.y + self.h/2 < self.screen_h/2)

        new_x = self.padding if (is_left) else self.screen_w - self.w - self.padding
        new_y = self.padding + self.addedDistance if (is_up) else self.screen_h - self.h - self.padding - self.addedDistance

        # Move back to each side (vertical and horizontal) and maybe swap
        if (is_left):
            if (self.was_right):
                self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT)
                self.image_tk = ImageTk.PhotoImage(self.image)
                self.img_label = tk.Label(self, image=self.image_tk)
                self.was_right = not self.was_right
            self.img_label.place(x=0, y=self.h - self.icon_size)
        elif (not is_left):
            if (not self.was_right):
                self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT)
                self.image_tk = ImageTk.PhotoImage(self.image)
                self.img_label = tk.Label(self, image=self.image_tk)
                self.was_right = not self.was_right
            self.img_label.place(x=self.w - self.icon_size, y=self.h - self.icon_size)

        self.geometry(f"+{new_x}+{new_y}")

    def qs_button1_pres(self, event):
        minimumWords = 0
        maximumWords = tc.getResponseLengthFromText()
        # tc.generateSummaryFromText(text, minimumWords, maximumWords)
        text = "Lorem ipsum"
        

window = Window()
window.mainloop()