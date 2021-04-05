#!/usr/bin/env python3
import os
#import tqdm
import threading
import socket
import argparse
import base64


SEPARATOR = "<SEPARATOR>"

class Send(threading.Thread):
    def __init__(self, sock, name, password):
        super().__init__()
        self.sock = sock
        self.name = name
        self.password = password

    def run(self):
        while True:
            message = input('{}: '.format(self.name))

            # Type 'QUIT' to leave the chatroom
            if message == 'QUIT':
                self.sock.sendall('Server: {} has left the chat.'.format(self.name).encode('utf8'))
                break
            if message == 'FILE':
                filename = input('enter the name of the file and its type (.jpeg for example): ')
                filesize = os.path.getsize(filename)
                self.sock.send(f"{filename}{SEPARATOR}{filesize}".encode('utf8'))
                #progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
                with open(filename, "rb") as f:
                    #for _ in progress:
                    # read the bytes from the file
                    bytes_read = f.read(1024)
                    if not bytes_read:
                        # file transmitting is done
                        break
                    # we use sendall to assure transimission in
                    # busy networks
                    self.sock.sendall(bytes_read)
                    self.sock.sendall('\n'.encode('utf8'))
                    #progress.update(len(bytes_read))
                print('Sending Complete')

            if message=='IMAGE':
                filename = input('enter the name of the file and its type (.jpeg for example): ')
                self.sock.sendall('Sending a file...'.format(self.name).encode('utf8'))
                import base64
                image = open(filename, 'rb') #open binary file in read mode
                image_read = image.read()
                image_64_encode = base64.encodebytes(image_read)
                # import cv2
                #
                # im = cv2.imread(filename)
                # size=im.shape[0]*im.shape[1]
                # self.sock.sendall('SIZE:'.encode('utf8')+size.encode('utf8'))
                self.sock.sendall('FILE:'.encode('utf8')+image_64_encode)
            else:
                try:
                    self.sock.sendall('{}: {}'.format(self.name, message).encode('utf8'))
                except:
                    print("you have been kicked from the server")
                    print('\nQuitting...')
                    self.sock.close()
                    os._exit(0)


        print('\nQuitting...')
        self.sock.close()
        os._exit(0)

    def check_user(self):
        self.sock.sendall('{};{}'.format(self.name, self.password).encode('utf8'))

class Receive(threading.Thread):
    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name

    def run(self):
        size=1
        while True:

            try:
                if size==1 :
                    message = self.sock.recv(1024)

                else:
                    message = self.sock.recv(size)

                code=str('File:'.encode('utf8'))
                message_in_str = str(message)
                #print(code)
                #print(message_in_str[0:50])

                if message:
                    print('\r{}\n{}: '.format(message.decode('utf8'), self.name), end = '')
                    if message_in_str.startswith('SIZE:'):
                        size=int(message[5:])
                    elif message_in_str.startswith('FILE:'):
                        message=message[5:]
                        image_64_decode = base64.decodestring(message)
                        image_name = input('Enter the name under which you want to save the received file and its type (.jpeg for example): ')
                        image_result = open(image_name, 'wb') # create a writable image and write the decoding result
                        image_result.write(image_64_decode)


                    elif message_in_str.startswith('IMAGE:'):
                        message=message[6:]
                        image_64_decode = base64.decodestring(message)
                        image_name = input('Enter the name under which you want to save the received file and its type (.jpeg for example): ')
                        image_result = open(image_name, 'wb') # create a writable image and write the decoding result
                        image_result.write(image_64_decode)

                    elif message_in_str.startswith('FINI'):
                        SIZE_IMAGE=1024


                    else:
                        message=self.sock.recv(1024)

                    #else:
                        #message=self.sock.recv(1024)

                else:
                    # Server has closed the socket, exit the program
                    print('\nwe have lost connection to the server!')
                    print('\nQuitting...')
                    self.sock.close()
                    os._exit(0)
            except:
                return


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        print('Trying to connect to {}:{}...'.format(self.host, self.port))
        self.sock.connect((self.host, self.port))
        print('Successfully connected to {}:{}'.format(self.host, self.port))

        print()
        username = input('Your name: ')
        print()
        password = input('Your password: ')
        print()
        print('Welcome, {}! Getting ready to send and receive messages...'.format(username))
        # Create send and receive threads
        send = Send(self.sock, username, password)
        receive = Receive(self.sock, username)
        send.check_user()
        # Start send and receive threads
        send.start()
        receive.start()
        self.sock.sendall('Server: {} has joined the chat.'.format(username).encode('utf8'))
        print("\rAll set! Leave the chatroom anytime by typing 'QUIT'\n")
        print("\rAll set! Send a file in the chatroom by typing 'FILE'\n")
        print("\rAll set! Send an image in the chatroom by typing 'IMAGE'\n")
        print('{}: '.format(username), end = '')



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Chatroom Server')
    parser.add_argument('host', help='Interface the server listens at')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060,help='TCP port (default 1060)')
    args = parser.parse_args()

client = Client(args.host, args.p)
client.start()