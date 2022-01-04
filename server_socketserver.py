import argparse
import socketserver
import time
import os
import re
import shutil

from typing import Tuple

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5678
MSG_MAX_SIZE = 256


# Here we have created a custom server type. Currently it just calls the parent
# class ThreadingTCPServer. If we wanted to add any specific functionality to
# the server itself, we would modify this class
class MyServer(socketserver.ThreadingTCPServer):
    def __init__(self, server_address: Tuple[str, int], name: str,
                 request_handler_class):
        """
        Constructor for MyServer
        :param server_address: IP address and Port number to host server at
        :param request_handler_class: Handler for responding to requests
        """
        super().__init__(server_address, request_handler_class)
        self.name = name
        print(f"MyServer '{name}' has started")
    
    os.listdir(r'C:\Users\oskar\OneDrive\Skrivebord\ML\HPPS\Ass4')


class MyHandler(socketserver.StreamRequestHandler):
    """
    A handler class to process all messages sent to the server
    """
    def handle(self) -> None:

        # Implementation of GET 
        
        def http_get(self, url): 
            isFile = os.path.isfile(url)
            isDir = os.path.isdir(url) 

            if not(isFile) and not(isDir):
                self.handle_error(f"404 file not found")
                return
            elif isFile:
                content = open(url, 'r')
                val = content.read()
                content.close()
                return val
            elif isDir:
                if 'index.html' in os.listdir(url):
                    content = open(url + '/index.html')
                    val = content.read()
                    content.close()
                    return val
                else:
                    return str(os.listdir(url))
        # Implementation of POST, as per RCT protocol
        
        def http_post(self, source, destination):
            isFile = os.path.isfile(destination)
            isDir = os.path.isdir(destination) 
            
            if not(isFile) and not(isDir):
                print(f"404 File not found")
                return
            elif isFile:
                if os.path.getsize(destination) == 0:
                    print(f"204 No content")
                else:
                    shutil.move(source, destination)
                    msg = "Location: " + str(destination) + "  201, Successfully moved"
                    self.request.sendall(msg.encode())
                    return
            elif isDir:
                if os.listdir(destination) == 0:
                    print(f"204 No content")
                    return
                else:
                    shutil.move(source, destination)
                    msg = "Location: " + str(destination) + "  201, Successfully moved"
                    self.request.sendall(msg.encode())
                    return

        # We use a try/except here to make sure that even if something goes
        # wrong in our server, we always return a response
        try:
            print(f"Server messaged by {self.client_address}")

            if not isinstance(self.server, MyServer):
                self.handle_error("Invalid server type to handle this request")
                return

            bytes_message = self.request.recv(MSG_MAX_SIZE)

            if not bytes_message:
                self.handle_error(f"No bytes received.")
                return

            string_message = bytes_message.decode('utf-8')
        
            # print(string_message)

            response = \
                bytearray(f"Message '{string_message}' received".encode())
            # self.request.sendall(response)

            # Uncomment this line to add a delay to message processing
            # time.sleep(10)
            print(f"Server responded to '{self.client_address}'")


            # Consider extending later, if trouble 
            # Checking which protocol is issued - no tolerance for spaces
            vals = string_message.split(' ')
            if len(vals) < 2: 
                self.handle_error(f"FIND FEJLKODEN, HVIS DER ER FOR LIDT INFO")
                return


            command, url = vals[0], vals[1]

            if command == "GET": 
                resp = http_get(self, url)  
                self.request.sendall(resp.encode())
            if command == "POST":
                http_post(self, vals[2], url)

                # self.request.sendall(resp.encode())
            return

        except Exception as e:
            self.handle_error(f"An error was encountered in the server. {e}")

    def handle_error(self, error_msg: str) -> None:
        print(f"{error_msg}")

        response = bytearray("Internal server error".encode())
        self.request.sendall(response)
        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "name",
        help="Name of the server, e.g.: TestServer")
    args = parser.parse_args()

    # Here we start a server running on the localhost at port 5678
    with MyServer((SERVER_IP, SERVER_PORT), args.name, MyHandler) as my_server:
        try:
            # Run this server until we specifically tell it to shutdown
            my_server.serve_forever()
        finally:
            # Shutdown our server if we ever call this script by hitting Ctrl+C
            my_server.server_close()