import socket
import ssl
import os
import gzip
import tkinter

class Browser:
    def __init__(self):
        WIDTH, HEIGHT = 800, 600

        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT)
        self.canvas.pack()
    
    def load(self, url):
        body = url.request()          
        show(body)
    
        self.canvas.create_rectangle(10, 20, 400, 300)
        self.canvas.create_oval(100, 100, 150, 150)
        self.canvas.create_text(100, 150, text="Hi!")
    
class URL:
    def __init__(self, url):
        
        self.scheme, rest = url.split("://", 1)
        assert self.scheme in ["http", "https", "file", "data"]
            
        if self.scheme == "file":
            self.path = rest
            self.port = None
            self.host = None
        else:
            if self.scheme == "http":
                self.port = 80
            elif self.scheme == "https":
                self.port = 443
        
        if "/" not in rest:
            rest += "/"
        self.host, path = rest.split("/", 1)
        self.path = "/" + path
        
        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)
            
        self.headers = {
            "Host": self.host if self.host else "",
            "Connection": "close",
            "User-Agent": "me",
            "Accept-Encoding": "gzip"
        }
        
    def add_header(self, key, value):
        self.headers[key] = value        
        
    def request(self):
        if self.scheme == "file":
            try:
                with open(self.path, 'r') as file:
                    return file.read()
            except FileNotFoundError:
                return "File not found!"
            except PermissionError:
                return "Permission Denied"
        
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP
        )
        
        s.connect((self.host, self.port))
        
        if self.port == -1:
            return
        
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)
        
        request = "GET {} HTTP/1.0\r\n".format(self.path)
        for key, value in self.headers.items():
            request += "{}:{}\r\n".format(key, value)
        request += "\r\n"
        
        s.send(request.encode("utf8"))
        
        response = s.makefile(mode = "rb", newline = "\r\n")
        
        statusline = response.readline().decode("utf-8")
        version, status, explanation = statusline.split(" ", 2)
        response_headers = {}
        
        while True:
            line = response.readline()
            line = line.decode('utf-8')
            if line == '\r\n': break
            header, val = line.split(":", 1)
            response_headers[header.casefold()] = val.strip()
            
        assert "transfer-encoding" not in response_headers
        
        content = response.read()
        s.close()
        
        if "content-encoding" in response_headers and response_headers["content-encoding"] == "gzip":
            content = gzip.decompress(content)
            
        return content.decode("utf-8")
    
def show(body):
    in_tag = False
    entity = ""
    entity_dict = {"&lt;":"<", "&gt;":">"}
    
    for c in body: 
        if entity:
            entity += c
            if c == ";":
                if entity in entity_dict:
                    print(entity_dict[entity], end="")
                else:
                    print(entity, end="")
                entity = ""
            continue
                
        if c == "&":
            entity = c              
        elif c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            print(c, end="")
    
# Main Function

if __name__ == "__main__":
    import sys
    
    browser = Browser()
    if len(sys.argv) < 2:
        default_file = 'file:///Users/aryan/Desktop/browser_eng/browser.py'
        browser.load(URL(default_file))
    else:
        browser.load(URL(sys.argv[1]))
    
    tkinter.mainloop()
                
            
        
        
        
        
        
        
        
    