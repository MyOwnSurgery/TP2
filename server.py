# -*- coding: utf-8 -*-
import json
import socket
import sys
import threading
import model
import random
import client
import messages

BUFFER_SIZE = 2 ** 10
CLOSING = "Application closing..."
CONNECTION_ABORTED = "Connection aborted"
CONNECTED_PATTERN = "Client connected: {}:{}"
ERROR_ARGUMENTS = "Provide port number as the first command line argument"
ERROR_OCCURRED = "Error Occurred"
EXIT = "exit"
JOIN_PATTERN = "{username} has joined"
RUNNING = "Server is running..."
SERVER = "SERVER"
SHUTDOWN_MESSAGE = "shutdown"
TYPE_EXIT = "Type 'exit' to exit>"


##Идти - 30 минут, ехать - 15
class Server(object):

    def __init__(self):
        self.clients = set()
        self.listen_thread = None
        self.port = 8080
        self.sock = None
        self.day = 1
        self.timetable = self.rand()
        self.count = 0
        self.message = model.Message()
        self.message.username = "Server"
        self.first_client = client.Client()
        self.second_client = client.Client()

    def rand(self):
        return random.randint(0, 30)

    def decide(self):
        if self.first_client.last_message == self.second_client.last_message:
            return
        if self.timetable == 15:
            return
        elif self.timetable < 15:
            if self.first_client.last_message == "By bus":
                self.first_client.points += 1
            else:
                self.second_client.points += 1
        else:
            if self.first_client.last_message == "On foot":
                self.first_client.points += 1
            else:
                self.second_client.points += 1

    def start_new(self):
        self.first_client = client.Client()
        self.second_client = client.Client()
        self.day = 1
        self.count = 0

    def finish(self):
        if self.first_client.points > self.second_client.points:
            self.message.message = self.first_client.name + " is a winner!"
        elif self.first_client.points < self.second_client.points:
            self.message.message = self.second_client.name + " is a winner!"
        else:
            self.message.message = "It`s a draw!"
        self.message.message += messages.FIRST_DAY
        self.broadcast(self.message)
        self.start_new()

    def listen(self):
        a = True
        self.sock.listen(1)
        while True:
            try:
                client, address = self.sock.accept()
            except OSError:
                print(CONNECTION_ABORTED)
                return
            print(CONNECTED_PATTERN.format(*address))
            print(self.clients)
            if len(self.clients) < 2:
                self.clients.add(client)
            if a and len(self.clients) == 2:
                self.message.message = messages.FIRST_DAY
                self.broadcast(self.message)
                a = False
            threading.Thread(target=self.handle, args=(client,)).start()

    def handle(self, client):
        while True:
            try:
                message = model.Message(**json.loads(self.receive(client)))
            except (ConnectionAbortedError, ConnectionResetError):
                print(CONNECTION_ABORTED)
                return
            if message.quit:
                client.close()
                self.clients.remove(client)
                return
            print(str(message))
            if SHUTDOWN_MESSAGE.lower() == message.message.lower():
                self.exit()
                return
            self.check(message)
            if self.first_client.last_message is None:
                self.first_client.last_message = message.message
            else:
                self.second_client.last_message = message.message
                self.decide()
            self.broadcast(message)
            self.count += 1
            if self.count == 2:
                if self.day != 5:
                    self.start_new_day()
                else:
                    self.finish()

    def check(self, message):
        if self.first_client.name is None:
            self.first_client.name = message.username
        elif self.second_client.name is None:
            self.second_client.name = message.username

    def start_new_day(self):
        self.count = 0
        self.day += 1
        self.timetable = self.rand()
        self.message.message = "Day " + str(self.day) + ", 9:00 AM"
        self.broadcast(self.message)
        self.first_client.last_message = None
        self.second_client.last_message = None

    def broadcast(self, message):
        for client in self.clients:
            client.sendall(message.marshal())

    def receive(self, client):
        buffer = ""
        while not buffer.endswith(model.END_CHARACTER):
            buffer += client.recv(BUFFER_SIZE).decode(model.TARGET_ENCODING)
        return buffer[:-1]

    def run(self):
        print(RUNNING)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("", self.port))
        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.start()

    def exit(self):
        self.sock.close()
        for client in self.clients:
            client.close()
        print(CLOSING)


if __name__ == "__main__":
    try:
        Server().run()
    except RuntimeError as error:
        print(ERROR_OCCURRED)
        print(str(error))
