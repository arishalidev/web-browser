import socket
import ssl
import tkinter

from browser import Browser

class URL:
    def __init__(self, url):

        if not url:
            url = "file:///Users/arisha/Documents/browserTest.txt"

        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https", "file", "view-source:http", "view-source:https"]

        match self.scheme:
            case "http" | "https" | "view-source:http" | "view-source:https":
                if self.scheme == "http" or self.scheme == "view-source:http":
                    self.port = 80
                elif self.scheme == "https" or self.scheme == "view-source:https":
                    self.port = 443

                if self.scheme.split(":", 1)[0] == "view-source":
                    self.view_source = True
                else:
                    self.view_source = False

                if "/" not in url:
                    url = url + "/"

                self.host, url = url.split("/", 1)

                if ":" in self.host:
                    self.host, port = self.host.split(":", 1)
                    self.port = int(port)

                self.path = "/" + url

            case "file":
                if "/" not in url:
                    url = "/" + url

                self.file_path = url
                self.view_source = True




    def request(self):
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP
        )

        s.connect((self.host, self.port))
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        request = "GET {} HTTP/1.1\r\n".format(self.path)
        request += "Host: {}\r\n".format(self.host)
        request += "Connection: {}\r\n".format("close")
        request += "User-Agent: {}\r\n".format("Best Browser")
        request += "\r\n"

        s.send(request.encode("utf8"))

        response = s.makefile("r", encoding="utf8", newline="\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)

        response_headers = {}

        while True:
            line = response.readline()
            if line == "\r\n": break

            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

        assert  "transfer-encoding" not in response_headers
        assert  "content-encoding" not in response_headers

        content = response.read()
        s.close()

        return content

    def getfile(self):
        try:
            with open(self.file_path, "r") as file:
                content = file.read()
                return content
        except FileNotFoundError:
            print("File not found!")
            exit(1)
        except PermissionError:
            print("You do not have permission to access this file!")
            exit(1)
        except IsADirectoryError:
            print("File is a directory!")
            exit(1)
        except (UnicodeDecodeError, OSError):
            print("Error opening file!")
            exit(1)




if __name__ == "__main__":
    Browser().load(URL("view-source:http://example.org/"))
    tkinter.mainloop()

