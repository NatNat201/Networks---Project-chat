#!/usr/bin/env python3
import threading
import socket
import argparse
import os
import datetime
from datetime import *
import sqlite3
from sqlite3 import Error

SEPARATOR = "<SEPARATOR>"

def create_connection():
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect("userdb.db")
    except Error as e:
        print(e)

    return conn


def create_table(conn):
    try:
        c = conn.cursor()
        c.execute(""" CREATE TABLE IF NOT EXISTS users (
                                        username text PRIMARY KEY NOT NULL,
                                        password text NOT NULL
                                    ); """)
    except Error as e:
        print(e)

def create_user(conn, user):
    sql = "INSERT INTO users(username,password) VALUES(?,?)"
    cur = conn.cursor()
    print(user)
    cur.execute(sql, user)
    conn.commit()
    print("user inserted")


def select_user(conn, username, password):
    cur = conn.cursor()
    user=(str(username),str(password))
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", user)

    rows = cur.fetchall()

    if len(rows)>=1:
        return True

    return False



def database():
    # create a database connection
    conn = create_connection()

    # create table
    if conn is not None:
        print("create users table")
        # create users table
        create_table(conn)

    else:
        print("Error! cannot create the database connection.")

    # insert users
    user_1 = ('plako','eau_plate')
    user_2 = ('banto22', 'nilon.2020')
    user_3 = ('Bob', 'bob')
    user_4 = ('test','test')
    user_5 = ('John','coucou')

    try:
        create_user(conn, user_1)
        create_user(conn, user_2)
        create_user(conn, user_3)
        create_user(conn, user_4)
        create_user(conn, user_5)

    except:
        print("users already exist")

    return conn


class Server(threading.Thread):

    def __init__(self, host, port):
        super().__init__()
        self.connections = []
        self.host = host
        self.port = port
        self.clients = []

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(1)
        print('Listening at', sock.getsockname())
        while True:
                # Accept new connection
                sc, sockname= sock.accept()
                print('Accepted a new connection from {} to {}'.format(sc.getpeername(), sc.getsockname()))
                # Create new thread
                server_socket = ServerSocket(sc, sockname, self)
                # Start new thread
                server_socket.start()
                # Add thread to active connections
                self.connections.append(server_socket)
                print('Ready to receive messages from', sc.getpeername())

                print('Enter Q to shut down the server and all the connections it has.\n')
                print('Enter K to disconnect only one client.\n')


    def broadcast(self, message, source):

        for connection in self.connections:
            # Send to all connected clients except the source client
            if connection.sockname != source:
                try:
                    connection.send(message)
                except:
                    self.connections.remove(connection)

class ServerSocket(threading.Thread):

    def __init__(self, sc, sockname, server):
        super().__init__()
        self.sc = sc
        self.sockname = sockname
        self.server = server


    def run(self):
        while True:
            try:
                message = self.sc.recv(1024).decode('utf8')
                '''message0 = self.sc.recv(1024)
                clef=AES.new('This is a key456'.encode('utf8'), AES.MODE_EAX, 'This is an IV789'.encode('utf8'))
                messagecode=clef.decrypt(message0)
                message=messagecode.decode('utf8')'''
                if message:
                    l=message.split(";")
                    if(len(l)>=2):
                        username=l[0]
                        password=l[1].split(":")[0]
                        print("checking user...")
                        if(select_user(create_connection(),username,password)):
                            self.server.clients.append([username, self.sockname])
                            print('{} is registered in the database'.format(self.sockname))

                        else:
                            print('{} is not registered in the database'.format(self.sockname))
                            self.sc.close()
                            return
                    else:
                        print('{} : {} says {!r}'.format(str(datetime.now()),self.sockname, message))
                        self.server.broadcast(message, self.sockname)

            except:
                # Client has closed the socket, exit the thread
                print('{} has closed the connection'.format(self.sockname))
                self.sc.close()
                #server.remove_connection(self)
                return


    def send(self, message):
        print(message)
        self.sc.sendall(message.encode('utf8'))

def kill_exit(server):

    while True:
        ipt2 = input('')
        if ipt2 == 'K':
            for client in server.clients:
                print(client)
            name=input("Who do you want to disconnect? \n")
            socket=None
            for client in server.clients:
                if name==client[0]:
                    socket=client[1]
                    break

            for connection in server.connections:
                if str(connection.sockname)==str(socket):
                    connection.sc.close()
                    print ('{} have been disconnected'.format(name))
                    break
        if ipt2 == 'Q':
            print('Closing all connections...')
            for connection in server.connections:
                connection.sc.close()
            print('Shutting down the server...')
            os._exit(0)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Chatroom Server')
    parser.add_argument('host', help='Interface the server listens at')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060,
                        help='TCP port (default 1060)')
    args = parser.parse_args()

    # Create database
    conn = database()
    #conn.close()
    # Create and start server thread
    server = Server(args.host, args.p)
    server.start()
    kill_exit = threading.Thread(target = kill_exit, args = (server,))
    kill_exit.start()
    #exit = threading.Thread(target = exit, args = (server,))
    #exit.start()

