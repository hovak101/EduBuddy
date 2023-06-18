import tkinter as tk
from screeninfo import get_monitors
from PIL import Image, ImageTk
import os
from tkinter import filedialog
import TextConverter as tc

import platform
import pyperclip
import config
from threading import Thread
import textwrap
import time

config.init()
# import ctypes
# import objc


"""
Changes to make:
- icons for all buttons
- rounded corners
- smooth animation for expanding/compressing window
- minimize on click buddy (maybe right click for settings)

"""


num_quiz_questions = 5

class Quiz():
    def __init__(self, quiz_input_string):
        self.questions = [None for _ in range(num_quiz_questions)]
        lines = quiz_input_string.split("\n")
        for i in range(num_quiz_questions):
            self.questions[i] = {
                "question": lines[i * 6][3:],
                "alternatives": ["","","",""],
                "answer": -1
            }
            for j in range(4):
                init_string = lines[i * 6 + j + 1][3:]
                asterisk_index = init_string.find('*')
                
                # Create the substring based on the asterisk index
                if asterisk_index != -1:
                    init_string = init_string[:asterisk_index]
                    self.questions[i]["answer"] = j

                self.questions[i]["alternatives"][j] = init_string

        #self.questions is formatted like this: obj = [{question: "<q>", alternatives: ["alt1", "alt2", "alt3", "alt4"], answer: <0-3>}]



# quiz1 = Quiz(tc.getMultipleChoiceQuiz("""Giraffes are majestic creatures known for their towering height, distinctive features, and gentle nature. With long necks, patterned coats, and graceful movements, they symbolize the beauty of the African savanna. These tallest land animals browse treetops, feed on foliage with their prehensile tongues, and exhibit intriguing social structures. Despite their imposing size, giraffes possess a calm demeanor but can defend themselves if threatened. Conservation efforts are crucial to protect giraffes from habitat loss and poaching, ensuring their survival and the preservation of Earth's biodiversity.""", f"{num_quiz_questions}"))



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
        self.w = 400 #was 200
        self.h = 500 #was 300
        self.x = self.screen_w - self.w - self.padding  # X coordinate
        self.y = self.screen_h - self.h - self.padding  # Y coordinate

        self.geometry(f"+{self.x}+{self.y-self.addedDistance}")
        self.geometry(f"{self.w}x{self.h}")

        #quiz/submit button
        sq_button1 = tk.Button(self, text="S")
        sq_button2 = tk.Button(self, text="Q")
        sq_button_height = 45
        sq_button1.place(x=0, y=0, width=self.w/2, height=sq_button_height)
        sq_button2.place(x=self.w/2, y=0, width=self.w/2, height=sq_button_height)

        sq_button1.bind("<ButtonPress-1>", self.sq_button1_press)
        sq_button2.bind("<ButtonPress-1>", self.sq_button2_press)

        # Context title box
        self.context_title = tk.Label(self, text="Context", bg="lightblue")
        self.context_title.place(x=3, y=45, w=self.w - 6, h=20)

        # add icon
        self.icon_size = 60
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(script_dir, "media", "buddy.png")
        # print(image_path)
        self.image = Image.open(image_path)
        self.image = self.image.resize((self.icon_size, self.icon_size))
        self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT)
        self.was_right = True
        self.image_tk = ImageTk.PhotoImage(self.image)
        self.img_label = tk.Label(self, image=self.image_tk)
        self.img_label.place(x=self.w-self.icon_size, y=self.h-self.icon_size)

        # Text output
        self.output_box = tk.Text(self, borderwidth=0, highlightthickness=0)
        # self.output_box.insert(tk.END, "")
        self.output_box.configure(state="disabled")
        # self.output_box.place(x=3, y=self.h - 125 - 60, w=self.w - 6, h=325)
        self.output_box.place(x=3, y=65, w=self.w - 6, h=310)

        # Text input field
        self.text_box = tk.Text(self, borderwidth=0, highlightthickness=0)
        self.text_box.place(x=3, y=self.h - 65 - 60, w=self.w - 6, h=65)
        self.text_box.bind("<Return>", self.submit_input)

        # Bind mouse events
        self.bind("<ButtonPress-1>", self.on_button_press)
        self.bind("<B1-Motion>", self.on_button_motion)
        self.bind("<ButtonRelease-1>", self.on_button_release)

        # get local file
        file_button = tk.Button(self, text="File", command=self.open_file_dialog)
        file_button.place(x=self.w/2 - 45/2, y=self.h - 48, w=45, h=45)

        # Quiz variables
        self.current_quiz_ans = -1
        self.current_quiz_score = 0
        self.current_quiz_questions = []
        self.quiz_obj = None
        self.quiz_alternative_buttons = [None, None, None, None]

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
  
    def waitAndReturnNewText(self):
        while True:
            config.text = pyperclip.waitForNewPaste()
        
    def sq_button1_press(self, event):
        # generate title
        text1 = tc.getTitleFromText(config.text)
        self.context_title.config(text=text1)

        # generate summary
        minimumWords = 0
        maximumWords = tc.getResponseLengthFromText(config.text)
        response = tc.generateSummaryFromText(config.text, minimumWords, maximumWords)
        # print(response)
        self.updateOutput(response)

    def sq_button2_press(self, event):
        # generate title
        text1 = tc.getTitleFromText(config.text)
        self.context_title.config(text=text1)

        # generate quiz
        response = tc.generateQuizFromText(config.text, 5)
        print(response)
        self.updateOutput(response)

    def updateOutput(self, text_input):
        # self.output_box.config(text=text_input)
        self.output_box.configure(state="normal")
        self.output_box.delete('1.0', tk.END)
        self.output_box.insert(tk.END, text_input)

    def submit_input(self, event):
        self.text_input = self.text_box.get("1.0", "end-1c")
        self.output_box.delete('1.0', tk.END)
        str1 = tc.sendGptRequest(self.text_input,config.text)
        self.updateOutput(str1)
        #Run your function here. And then with the gpt output, run updateOutput function above this function

    def quiz_iteration(self, quiz_obj):
        if (len(quiz_obj.questions) == 0):
            self.question.destroy()
            for i in self.quiz_alternative_buttons:
                i.destroy()
            self.display_quiz_results()
            return
        # make quiz question and button element from Quiz obj
        wrapped_text = textwrap.fill(quiz_obj.questions[0]["question"], width=self.w)
        self.question = tk.Label(self, text=wrapped_text, bg="gray")
        self.quiz_alternative_buttons = [
            tk.Button(self, text="1." + quiz_obj.questions[0]["alternatives"][0]),
            tk.Button(self, text="2." + quiz_obj.questions[0]["alternatives"][1]),
            tk.Button(self, text="3." + quiz_obj.questions[0]["alternatives"][2]),
            tk.Button(self, text="4." + quiz_obj.questions[0]["alternatives"][3])
        ]
        self.current_quiz_ans = quiz_obj.questions[0]["answer"]

        # place on window
        self.question.place(x=0, y=65, w=self.w, h=60)
        for i in range(4):
            self.quiz_alternative_buttons[i].place(x=0, y=(125 + 45*(i+1)), w=self.w, h=45)

            self.quiz_alternative_buttons[i].bind("<ButtonPress-1>", self.quiz_button_click)

        # add to list of questions for this quiz only
        self.current_quiz_questions.append([wrapped_text, quiz_obj.questions[0]["alternatives"][self.current_quiz_ans]])

        quiz_obj.questions.pop(0)
        
    def quiz_button_click(self, event):
        answered = int(event.widget.cget("text")[0]) - 1
        print(answered == self.current_quiz_ans)
        if (answered == self.current_quiz_ans):
            self.current_quiz_score += 1
        print(self.current_quiz_ans)
        self.quiz_alternative_buttons[answered].configure(bg="red")
        self.quiz_alternative_buttons[self.current_quiz_ans].configure(bg="green")

        self.quiz_iteration(self.quiz_obj)

    def display_quiz_results(self):
        self.updateOutput(f"Quiz results: {self.current_quiz_score}/{num_quiz_questions} - {self.current_quiz_questions}")


        
        
window = Window()

thread = Thread(target=window.waitAndReturnNewText)
thread.start()

window.mainloop()
thread.join()