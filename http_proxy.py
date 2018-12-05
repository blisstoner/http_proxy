
import sys
import socket
import re
from concurrent.futures import ThreadPoolExecutor

test_response = 'HTTP/1.1 200 OK\r\nContent-Length:2\r\n\r\nHi\r\n'

class Client:
  def __init__(self,host,port):
    self.host = host
    self.port = port
    
  def __connection__(self):    
    response = self.sock.recv(10000)
    if not response:
      print("[!] Connection {} failed".format(self.host))
      return None
    self.sock.close()
    return response

  def client_response(self, request):
    self.sock = socket.socket()
    self.sock.connect((self.host, self.port))
    self.sock.send(request)
    return self.__connection__()

class Server:
  def __init__(self, port):
    self.port = port
    self.host = 'localhost'
  
  def server_start(self):
    MAX_CLIENT = 100
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
      pool = ThreadPoolExecutor(MAX_CLIENT)
    except:
      print("[!] Failed to create thread pool. Terminated")
      exit(-1)
    try:
      self.socket.bind((self.host, self.port))
      self.socket.listen(MAX_CLIENT)
    except:
      print("[!] Failed to bind socket. Terminated")
      exit(-1)
    print("[+] Thread pool created and Socket binded")
    while True:   
      sock, addr = self.socket.accept()
      print("[Server] Connection established from {}".format(addr))
      pool.submit(self.__communicate__,sock,addr)

  def __communicate__(self, sock, addr):
    while True:
      request = sock.recv(10000).decode()
      if not request:
        print("[Server] Connection from {} closed".format(addr))
        sock.close()
        break
      if len(request) < 3 or request[:3] != "GET":
        print("[!] Not supported request")
        sock.send(test_response.encode())
        continue
      url_port = re.search('Host: (.*)\r',request).group(1).split(':')
      if len(url_port) > 2:
        print("[!] Not supported request")
        sock.send(test_response.encode())
        continue
      if len(url_port) == 1:
        url_port.append(80)
      else:
        url_port[1] = int(url_port[1])
      url,port = url_port
      port = int(port)
      print("[+] Request : ", url, port)
      C = Client(url,port)
      response = C.client_response(request.encode())
      sock.send(response)
      print("[+] Relay an data")


def usage():
  print("syntax : python http_proxy.py <port>")
  print("sample : python http_proxy.py 8080")


if __name__== "__main__":
  if len(sys.argv) != 2:
    usage()
    exit(-1)
  try:
    port = int(sys.argv[1])
  except:
    usage()
    exit(-1)
  S = Server(port)
  S.server_start()
