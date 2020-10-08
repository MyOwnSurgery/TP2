# -*- coding: utf-8 -*-
import tkinter
import messages

from tkinter import messagebox, simpledialog


CLOSING_PROTOCOL = "WM_DELETE_WINDOW"
END_OF_LINE = "\n"
KEY_RETURN = "<Return>"
TEXT_STATE_DISABLED = "disabled"
TEXT_STATE_NORMAL = "normal"


class EzChatUI(object):

    def __init__(self, application):
        self.application = application
        self.gui = None
        self.frame = None
        self.input_field = None
        self.message = None
        self.message_list = None
        self.scrollbar = None
        self.send_button = None
        self.button1 = None
        self.button2 = None
        self.start_label = None
        self.turn_label = None

    def show(self):
        self.gui = tkinter.Tk()
        self.gui.title(messages.TITLE)
        self.fill_frame()
        self.gui.protocol(CLOSING_PROTOCOL, self.on_closing)
        return self.input_dialogs()

    def loop(self):
        self.gui.mainloop()

    def fill_frame(self):
        self.frame = tkinter.Frame(self.gui)
        self.scrollbar = tkinter.Scrollbar(self.frame)
        self.message_list = tkinter.Text(self.frame, state=TEXT_STATE_DISABLED)
        self.scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.message_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
        self.message = tkinter.StringVar()
        self.frame.pack()
        self.button1 = tkinter.Radiobutton(self.gui, variable = self.message, value = messages.BYBUS, text = messages.BYBUS, command = self.message.set(messages.BYBUS))
        self.button2 = tkinter.Radiobutton(self.gui, variable=self.message, value=messages.ONFOOT, text=messages.ONFOOT,
                                           command=self.message.set(messages.ONFOOT))
        self.button1.pack()
        self.button2.pack()
        self.send_button = tkinter.Button(self.gui, text=messages.SEND, command=self.application.send)
        self.send_button.pack()
        self.start_label = tkinter.Label(self.gui, text="You can pick now or wait")
        self.start_label.pack()
        self.turn_label = tkinter.Label(self.gui, text="Now your turn")


    def input_dialogs(self):
        self.gui.lower()
        self.application.username = simpledialog.askstring(messages.USERNAME, messages.INPUT_USERNAME, parent=self.gui)
        if self.application.username is None:
            return False
        self.application.host = simpledialog.askstring(messages.SERVER_HOST, messages.INPUT_SERVER_HOST,
                parent=self.gui)
        if self.application.host is None:
            return False
        self.application.port = simpledialog.askinteger(messages.SERVER_PORT, messages.INPUT_SERVER_PORT,
                parent=self.gui)
        if self.application.port is None:
            return False
        return True

    def alert(self, title, message):
        messagebox.showerror(title, message)

    def show_message(self, message):
        if message.username != self.application.username:
            self.start_label.pack_forget()
            self.turn_label.pack()
            self.send_button.pack()
            self.button1.pack()
            self.button2.pack()
            self.message.set(messages.BYBUS)
        if message.username == "Server":
            self.turn_label.pack_forget()
            self.start_label.pack()
        self.message_list.configure(state=TEXT_STATE_NORMAL)
        self.message_list.insert(tkinter.END, str(message) + END_OF_LINE)
        self.message_list.configure(state=TEXT_STATE_DISABLED)

    def on_closing(self):
        self.application.exit()
        self.gui.destroy()

    def wait(self):
        self.start_label.pack_forget()
        self.send_button.pack_forget()
        self.button1.pack_forget()
        self.button2.pack_forget()

