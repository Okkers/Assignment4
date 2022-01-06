import argparse
import socketserver
import time
import os
import re
import shutil
import datetime
from typing import Tuple

SERVER_IP = "127.0.0.1"
SERVER_PORT = 80
MSG_MAX_SIZE = 1024


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
    
    # os.listdir(r'C:\Users\sofie\Documents\HPPS\Aflevering_4')


class MyHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:

        # Headers 
        
        Headers = {
        "head-200": "HTTP/1.1 200 OK",
        "head-404": "HTTP/1.1 404 NOT FOUND",
        "head-201": "HTTP/1.1 201 SUCCESSFULLY MOVED",
        "head-204": "HTTP/1.1 204 NO CONTENT",
        "head-date": str(datetime.datetime.now()),
        "head-connection": "close",
        "head_accept-language": "" 
        }

        # Implementation of GET 
        
        def http_get(self, url): 
            isFile = os.path.isfile(url)
            isDir = os.path.isdir(url) 
            print("getting url:", url)
            # check if empty
            if not(isFile) and not(isDir):
                self.handle_error(Headers["head-404"])
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
                self.handle_error(Headers["head-404"])
                return
            
            elif isFile:
                if os.path.getsize(destination) == 0:
                    self.handle_error(Headers["head-204"])
                else:
                    shutil.move(source, destination)
                    return destination
            elif isDir:
                if os.listdir(destination) == 0:
                    self.handle_error(Headers["head-204"])
                    return
                else:
                    shutil.move(source, destination)
                    return destination

        # Implementation of DELETE, as per RCT protocol
        
        def http_delete(self, destination):
            isFile = os.path.isfile(destination)
            isDir = os.path.isdir(destination) 
            
            if not(isFile) and not(isDir):
                self.handle_error(Headers["head-404"])
                return
            elif isFile:
                os.remove(destination)
                return destination
            
            elif isDir:
                shutil.rmtree(destination)
                return destination
            
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
        
            print(f"Server responded to '{self.client_address}'")

            # Consider extending later, if trouble 
            # Checking which protocol is issued - no tolerance for spaces
            response_info = string_message.split('\r\n')
            vals = string_message.split(' ')
            if len(vals) < 2: 
                self.handle_error(f"FIND FEJLKODEN, HVIS DER ER FOR LIDT INFO")
                return
            
            command, url = vals[0], vals[1]

            # building reponse headers
            resp_heads = Headers["head-200"] + " \r\nDate: " + Headers["head-date"] + " \r\n"

            for req in response_info:
                if "Connection" in req:
                    resp_heads += "Connection: " + Headers["head-connection"] + " \r\n"    
            # resp_heads = Headers["head-200"] + " \r\nDate: " + Headers["head-date"] + " \r\nConnection: " + Headers["head-connection"] + "\r\n"

            if command == "GET": 
                val = http_get(self, r"C:\Users\oskar\OneDrive\Skrivebord\ML\HPPS\Ass4\webstart.html")  
                length = len(val)

                resp_heads += "Content-Length: " + str(length) + "\r\n\r\n"
                resp_heads += val
                
                print(response_info)
                print(resp_heads)

                response = \
                    bytearray(resp_heads.encode())
                self.request.sendall(response)
                # self.request.sendall(val.encode())
                
            elif command == "POST":
                val = http_post(self, vals[2], url)
                msg = "Location: " + str(val) + "  201 SUCCESSFULLY MOVED"
                self.request.send(resp_heads.encode())
                self.request.sendall(msg.encode())
                
            elif command == "DELETE":
                val = http_delete(self, url)
                msg = "Location: " + str(val) + " 200 SUCCESSFULLY DELETED"
                
                self.request.sendall(resp_heads.encode())
                self.request.sendall(msg.encode())

            # response = \
            #     bytearray(f"{resp_heads}".encode())
            # self.request.sendall(response)
            # self.request.close()
            return

        except Exception as e:
            self.handle_error(f"An error was encountered in the server. {e}")

    def handle_error(self, error_msg: str) -> None:
        print(f"{error_msg}")
        self.request.send(error_msg.encode())
        response = bytearray("Internal server error".encode())
        self.request.send(response)
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