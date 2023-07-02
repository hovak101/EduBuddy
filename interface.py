import tkinter as tk
from screeninfo import get_monitors
from PIL import Image, ImageTk
import os
from tkinter import filedialog
import TextConverter as tc
from tkinter import messagebox
import platform
import pyperclip
import config
from threading import Thread
from Speech_functions import checking, asking
import textwrap
import time
from llama_index import VectorStoreIndex, SimpleDirectoryReader, GPTVectorStoreIndex
from langchain.memory import ConversationSummaryMemory
import llama_index
import re
import openai
config.init()
from langchain.chat_models import ChatOpenAI

# import ctypes
# import objc

"""
Changes to make:
- icons for all buttons
- rounded corners
- smooth animation for expanding/compressing window
- minimize on click buddy (maybe right click for settings)
- open close button (and moving it) with messagebox to check if user really want to close

- threadings and button for memory
- show user the memory if they wish to do so
"""


class Quiz:
    def __init__(self, quiz_input_string, num_quiz_questions = 5):
        self.questions = [None for _ in range(num_quiz_questions)]
        lines = quiz_input_string.split("\n")
        for i in range(num_quiz_questions):
            self.questions[i] = {
                "question": lines[i * 6][3:],
                "alternatives": ["", "", "", ""],
                "answer": -1,
            }
            for j in range(4):
                init_string = lines[i * 6 + j + 1][3:]
                asterisk_index = init_string.find("*")

                # Create the substring based on the asterisk index
                if asterisk_index != -1:
                    init_string = init_string[:asterisk_index]
                    self.questions[i]["answer"] = j

                self.questions[i]["alternatives"][j] = init_string

        # self.questions is formatted like this: obj = [{question: "<q>", alternatives: ["alt1", "alt2", "alt3", "alt4"], answer: <0-3>}]


# quiz1 = Quiz(tc.getMultipleChoiceQuiz("""Giraffes are majestic creatures known for their towering height, distinctive features, and gentle nature. With long necks, patterned coats, and graceful movements, they symbolize the beauty of the African savanna. These tallest land animals browse treetops, feed on foliage with their prehensile tongues, and exhibit intriguing social structures. Despite their imposing size, giraffes possess a calm demeanor but can defend themselves if threatened. Conservation efforts are crucial to protect giraffes from habitat loss and poaching, ensuring their survival and the preservation of Earth's biodiversity.""", f"{num_quiz_questions}"))


class Window(tk.Tk):
    NUM_QUIZ_QUESTIONS = 5

    def __init__(self, threads : list):
        super().__init__()
        # self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.configure(bg = "white")
        # Check windows
        self.addedDistance = 30
        llm = ChatOpenAI(model_name = "gpt-4", temperature = 0.9)
        self.memory = ConversationSummaryMemory(llm = llm)
        # memory.save_context({"input": "Hi!"}, {"output": "Hello there!"})
        if (platform.system()) == "Windows":
            self.addedDistance = 80
        self.save = ""
        self.title("EduBuddy")
        self.before_text = 0
        # self.overrideredirect(
        #     True
        # )  # Remove window decorations (title, borders, exit & minimize buttons)
        self.attributes("-topmost", True)
        self.messagebox_opening = False
        # screen info
        screen = get_monitors()[0]  # number can be changed ig
        self.screen_w = screen.width
        self.screen_h = screen.height

        # Set the window's initial position
        self.padding = 0
        self.w = 400  # was 200
        self.h = 500  # was 300
        self.x = int(self.screen_w * 0.995) - self.w - self.padding  # X coordinate
        self.y = int(self.screen_h * 0.995) - self.h - self.padding  # Y coordinate

        self.geometry(f"+{self.x}+{self.y-self.addedDistance}")
        self.geometry(f"{self.w}x{self.h}")
        sq_button_height = 45

        # summarize button
        summarize_button = tk.Button(self, text = "Summarize", command = self.summarize_button_press)
        summarize_button.place(x = 0, y = 0, width = self.w / 5, height = sq_button_height)
        
        # erase the screen
        erase_button = tk.Button(self, text = "Erase", command = lambda ind: self.output_box.delete("1.0", tk.END))
        erase_button.place(x = self.w / 5, y = 0, width = self.w / 5, height = sq_button_height)

        # show memory
        show_button = tk.Button(self, text = "Show", command = self.show_button_press)
        show_button.place(x = self.w * 2 / 5, y = 0, width = self.w / 5, height = sq_button_height)

        # save memory
        save_button = tk.Button(self, text = "Save", command = self.save_button_click)
        save_button.place(x = self.w * 3 / 5, y = 0, width = self.w / 5, height = sq_button_height)

        # quiz button
        quiz_button = tk.Button(self, text = "Quiz", command = self.quiz_button_press)
        quiz_button.place(x = self.w * 4 / 5, y = 0, width = self.w / 5, height = sq_button_height)

        # button get from microphone
        mic_button = tk.Button(self, text = "From Mic", command = asking)
        # micButton.place(x = self.w / 2 - 45 / 2, y = self.h - 48, w = 45, h = 45)
        mic_button.place(x = self.w / 5, y = self.h - 50, width = self.w / 5, height = sq_button_height)

        # button get from local file
        file_button = tk.Button(self, text = "From File", command = self.file_button_click)
        # file_button.place(x = self.w * 3 / 4 - 135 / 4, y = self.h - 48, w = 45, h = 45)
        file_button.place(x = self.w * 2 / 5, y = self.h - 50, width = self.w / 5, height = sq_button_height)

        # button get from text
        text_button = tk.Button(self, text = "From Text", command = self.text_button_press)
        # text_button.place(x = self.w / 4 - 10, y = self.h - 48, w = 45, h = 45)
        text_button.place(x = self.w * 3 / 5, y = self.h - 50, width = self.w / 5, height = sq_button_height)

        # Context title box
        self.context_title = tk.Label(self, text = "Context", bg = "lightblue")
        self.context_title.place(x = 3, y = 45, w = self.w - 6, h = 25)

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
        self.img_label = tk.Label(self, image = self.image_tk)
        self.img_label.place(x = self.w - self.icon_size, y = self.h - self.icon_size)

        # Text output
        self.output_box = tk.Text(self, borderwidth = 0, highlightthickness = 0)
        # self.output_box.insert(tk.END, "")
        # self.output_box.configure(state="disabled")
        # self.output_box.place(x = 3, y = self.h - 125 - 60, w = self.w - 6, h = 325)
        self.output_box.place(x = 3, y = 65, w = self.w - 6, h = 310)

        # # Text input field
        # self.text_box = tk.Text(self, borderwidth = 0, highlightthickness = 0)
        self.output_box.delete("1.0", tk.END)
        # self.text_box.place(x = 3, y = self.h - 65 - 60, w = self.w - 6, h = 65)
        # self.text_box.bind("<Return>", self.text_button_press)
        # self.output_box.bind("<Return>", self.text_button_press)

        # Bind mouse events
        self.bind("<ButtonPress-1>", self.on_button_press)
        self.bind("<B1-Motion>", self.on_button_motion)
        self.bind("<ButtonRelease-1>", self.on_button_release)
        
        # Quiz variables
        self.current_quiz_ans = -1
        self.current_quiz_score = 0
        self.current_quiz_questions = []
        self.quiz_obj = None
        self.quiz_alternative_buttons = [None, None, None, None]

    def on_closing(self):
        self.messagebox_opening = True
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()
        self.messagebox_opening = False

    def file_button_click(self):
        self.context_title.config(text = "Read from file(s)")
        self.output_box.configure(state = "disabled")
        file_path = filedialog.askopenfilenames(
            parent = self, title = "Choose one or multiple file(s)"
        )
        self.output_box.configure(state = "normal")
        # file_path = filedialog.askopenfilenames(parent = self, title='Choose a file', filetypes = [('All files', '*.*')])
        # folder_path = filedialog.askdirectory(parent = self, title='Choose a folder')
        if len(file_path) != 0:
            # Do something with the selected file path, such as printing it
            documents = SimpleDirectoryReader(input_files = file_path).load_data()
            # index = VectorStoreIndex.from_documents(documents)
            index = GPTVectorStoreIndex.from_documents(documents)
            # query index
            query_engine = index.as_query_engine()
            self.context_title.config(
                text = "Enter your question about the file anywhere below"
            )
            summary = query_engine.query("Summarize all!")
            print("\n", summary, end = "\n\n")
            self.save += "(Summary from documents: " + summary + "), "
            # response = query_engine.query("Explain me The Schrodinger equation")
            # result = query_engine.query("Why do we need quantum mechanics")
            # answer = query_engine.query("Who is Julia Cook")
            # random = query_engine.query("Who is Leo Messi")
            # print("Count:", index., "\n\n\n\n")
            # for doc_id in index.document_ids():
            #     embedding = index.embedding_for_document(doc_id)
            #     print(f"Embedding for document {doc_id}: {embedding}")
            # print("\n", response, end = "\n\n")
            # print("\n", result, end = "\n\n")
            # print("\n", answer, end = "\n\n")
            # print("\n", random, end = "\n\n")
            # # print("Selected file:", file_path)
            # print(len(documents))

    def on_button_press(self, event):
        if not self.messagebox_opening:
            # Capture the initial mouse position and window position
            self.x = event.x_root
            self.y = event.y_root
            self.offset_x = self.winfo_x()
            self.offset_y = self.winfo_y()

    def on_button_motion(self, event):
        if not self.messagebox_opening:
            # Calculate the new window position based on mouse movement
            new_x = self.offset_x + (event.x_root - self.x)
            new_y = self.offset_y + (event.y_root - self.y)
            self.geometry(f"+{new_x}+{new_y}")

    def on_button_release(self, event):
        if not self.messagebox_opening:
            is_left = event.x_root - event.x + self.w / 2 < self.screen_w / 2
            is_up = event.y_root - event.y + self.h / 2 < self.screen_h / 2

            new_x = self.padding if (is_left) else self.screen_w - self.w - self.padding
            new_y = (
                self.padding + self.addedDistance
                if (is_up)
                else self.screen_h - self.h - self.padding - self.addedDistance
            )

            # Move back to each side (vertical and horizontal) and maybe swap
            if is_left:
                if self.was_right:
                    self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT)
                    self.image_tk = ImageTk.PhotoImage(self.image)
                    self.img_label = tk.Label(self, image = self.image_tk)
                    self.was_right = not self.was_right
                self.img_label.place(x = 0, y = self.h - self.icon_size)
            elif not is_left:
                if not self.was_right:
                    self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT)
                    self.image_tk = ImageTk.PhotoImage(self.image)
                    self.img_label = tk.Label(self, image = self.image_tk)
                    self.was_right = not self.was_right
                self.img_label.place(x = self.w - self.icon_size, y = self.h - self.icon_size)

            self.geometry(f"+{new_x}+{new_y}")

    def waitAndReturnNewText(self):
        while True:
            config.text = pyperclip.waitForNewPaste()

    def summarize_button_press(self):
        self.output_box.configure(state = "disabled")
        # Destroy old canvas
        try:
            self.canvas.destroy()
        except:
            pass
        text = ' '.join(re.split(" \t\n", config.text))
        # print(len(text), text[:100], )
        if text != "":
            if len(text.split(" ")) >= 30:
                # generate title
                title = tc.getTitleFromText(text)
                # print(title.split('"')[1])
                self.context_title.config(
                    text = textwrap.fill(title.split('"')[1], width = self.w - 20)
                )
                # generate summary
                minimumWords = 0
                maximumWords = tc.getResponseLengthFromText(text)
                response = tc.generateSummaryFromText(
                    text, minimumWords, maximumWords
                )
                # print(response)
                # print(response[:100])
                self.output_box.configure(state = "normal")
                self.output_box.insert(tk.END, f"\nSummary:\n{response}\n")
                self.before_text = len(self.output_box.get("1.0", tk.END))
                self.save += "(Summary: " + response + "), "
            else:
                self.output_box.configure(state = "normal")
                self.context_title.config(
                    text = "Please choose a longer text to summarize"
                )
        else:
            self.output_box.configure(state = "normal")
            self.context_title.config(
                text = "No text found! Choose a new text if this keep happens"
            )

    def quiz_button_press(self):
        # generate title
        # messagebox.showinfo("Information", "This is an information messagebox")
        self.messagebox_opening = True
        print(self.output_box.get("1.0", tk.END))
        if messagebox.askyesno("Quiz", "Are you sure you are ready for the quiz? Also, if you want to save this conversation, click cancel and click 'Save'"):
            self.messagebox_opening = False
            self.output_box.delete("1.0", tk.END)
            self.output_box.configure(state = "disabled")
            # self.geometry("800x1200")
            text = ' '.join(re.split(" \t\n", config.text))
            print(len(text), text[:100], )
            if text != "":
                if len(text.split(" ")) >= 50:
                    title = tc.getTitleFromText(text)
                    # print(title.split('"')[1])
                    self.context_title.config(
                        text = textwrap.fill(title.split('"')[1], width = self.w - 20)
                    )
                    # generate quiz
                    # print(self.output_box.get("1.0", "end"))
                    response = tc.getMultipleChoiceQuiz(text, 5)
                    self.quiz_obj = Quiz(response, Window.NUM_QUIZ_QUESTIONS)
                    self.quiz_iteration(self.quiz_obj)
                else:
                    self.context_title.config(
                        text = "Please choose a longer text to make quiz"
                    )
            else:
                self.context_title.config(
                    text = "No text found! Choose a new text if this keep happens"
                )
            self.output_box.configure(state = "normal")

    def show_button_press(self):
        messagebox.showinfo(title = "Memory", message = f"Unsaved: {self.save}\nSaved: {self.memory.load_memory_variables({})}")

    def text_button_press(self):
        # print("YOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
        # print(self.text_box.get("1.0", "end-1c"))
        text = ' '.join(re.split(" \t\n", self.output_box.get("1.0", "end-1c")[self.before_text:]))
        print(text)
        # self.output_box.insert(tk.END, '\n')
        # self.text_input = txt
        # self.output_box.delete("1.0", tk.END)
        str1 = tc.sendGptRequest(text, config.text)#, self.memory)
        try:
            output ='\n'.join(str1.split('\n\n')[1:])
            self.save += "(Q: " + text + " and A: " + str1 + "), "
            if output == '':
                raise ValueError
        except:
            output = str1
        # print(output)
        # print(len(str1), len(str1.split('\n\n')), len(str1.split('\n')))
        self.output_box.insert(tk.END, '\n\n' + output + '\n')
        self.before_text = len(self.output_box.get("1.0", tk.END))
        return 'break'
        # Run your function here. And then with the gpt output, run insert it into output box

    def quiz_iteration(self, quiz_obj):
        if len(quiz_obj.questions) == 0:
            self.canvas.destroy()
            self.display_quiz_results()
            return

        # Destroy old canvas
        try:
            self.canvas.destroy()
        except:
            pass

        # make quiz question and button element from Quiz obj
        self.canvas = tk.Canvas(self, width = self.w, height = 300)
        wrapped_text = textwrap.fill(
            quiz_obj.questions[0]["question"], width = self.w - 20
        )
        self.question = self.canvas.create_text(
            self.w // 2, 30, text = wrapped_text, width = self.w - 40
        )
        self.quiz_alternative_buttons = []
        for i in range(4):
            x1, y1, x2, y2 = 10, 65 + i * 45, self.w - 10, 110 + i * 45
            rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill = "white")
            text = self.canvas.create_text(
                (x1 + x2) // 2,
                (y1 + y2) // 2,
                text = textwrap.fill(
                    f"""{i+1}. {quiz_obj.questions[0]["alternatives"][i]}""",
                    width = self.w - 20,
                ),
                width = self.w - 40,
            )
            self.canvas.tag_bind(
                rect,
                "<Button-1>",
                lambda event, choice = i: self.quiz_button_click(event, choice),
            )
            self.canvas.tag_bind(
                text,
                "<Button-1>",
                lambda event, choice = i: self.quiz_button_click(event, choice),
            )
            self.quiz_alternative_buttons.append((rect, text))

        self.current_quiz_ans = quiz_obj.questions[0]["answer"]
        self.current_quiz_questions.append([wrapped_text])
        quiz_obj.questions.pop(0)
        self.canvas.place(x = 0, y = (-100 + 45 * (i + 1)), w = self.w, h = 300)

    def quiz_button_click(self, event, choice):
        if choice == self.current_quiz_ans:
            self.current_quiz_score += 1
        for rect, text in self.quiz_alternative_buttons:
            self.canvas.itemconfig(rect, fill = "white")
        self.canvas.itemconfig(self.quiz_alternative_buttons[choice][0], fill = "red")
        self.canvas.itemconfig(
            self.quiz_alternative_buttons[self.current_quiz_ans][0], fill = "green"
        )
        self.current_quiz_questions[-1].append(
            self.canvas.itemcget(self.quiz_alternative_buttons[choice][1], "text")
            .strip()
            .split(maxsplit = 1)[1]
        )
        self.current_quiz_questions[-1].append(
            self.canvas.itemcget(
                self.quiz_alternative_buttons[self.current_quiz_ans][1], "text"
            )
            .strip()
            .split(maxsplit = 1)[1]
        )
        self.after(ms = 2000, func = lambda: self.quiz_iteration(self.quiz_obj))

    def display_quiz_results(self):
        output = (
            f"Quiz results: {self.current_quiz_score}/{Window.NUM_QUIZ_QUESTIONS}:\n\n"
        )
        # print(self.current_quiz_questions)
        for id, vals in enumerate(self.current_quiz_questions):
            try:
                output += f"Question {id + 1}: {vals[0]}\nResult: {'Correct' if vals[1] == vals[2] else 'Incorrect'}!\nYour choice: {vals[1]}\nAnswer: {vals[2]}\n\n"
            except:
                # print(id, vals)
                pass
        self.save += "(Quiz:" + ' '.join(re.split(" \t\n", str(self.current_quiz_questions))) + "), "
        self.output_box.insert(tk.END, f"\n{output}")
        self.before_text = len(self.output_box.get("1.0", tk.END))

    def save_button_click(self, event):
        self.memory.save_context({"input": f"""Here is a context for your next request: {self.save}"""},
                                         {"output": f"""Thank you, I will remember and be here for you!"""})
        print(self.memory.load_memory_variables({}))
        self.save = ""

threads = []
window = Window(threads)

thread = Thread(target = window.waitAndReturnNewText)
threads.append(thread)
thread.start()

window.mainloop()
for t in threads:
    t.join()
