import socket
import ssl
import tkinter
import gzip

from browser import Browser

class URL:
    def __init__(self, url):

        self.socket = None

        if not url:
            url = "file:///Users/arisha/Documents/browserTest.txt"

        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https", "file", "view-source:http", "view-source:https"]

        match self.scheme:
            case "http" | "https" | "view-source:http" | "view-source:https":

                if self.scheme.split(":", 1)[0] == "view-source":
                    self.view_source = True
                else:
                    self.view_source = False

                if self.scheme == "http" or self.scheme == "view-source:http":
                    self.port = 80
                    self.scheme = "http"
                elif self.scheme == "https" or self.scheme == "view-source:https":
                    self.port = 443
                    self.scheme = "https"


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


    def request(self, established = False, established_socket = None):

        # create a new connection if not currently connected to the server
        if not established:
            s = socket.socket(
                family=socket.AF_INET,
                type=socket.SOCK_STREAM,
                proto=socket.IPPROTO_TCP
            )

            s.connect((self.host, self.port))
            if self.scheme == "https":
                ctx = ssl.create_default_context()
                s = ctx.wrap_socket(s, server_hostname=self.host)

        # if already connected to server, use previously established connection
        else:
            s = established_socket

        request = "GET {} HTTP/1.1\r\n".format(self.path)
        request += "Host: {}\r\n".format(self.host)
        request += "Connection: {}\r\n".format("keep-alive")
        request += "Accept-Encoding: {}\r\n".format("gzip")
        request += "User-Agent: {}\r\n".format("Best Browser")
        request += "\r\n"

        s.send(request.encode("utf8"))

        response = s.makefile("rb", encoding="utf8", newline="\r\n")
        statusline = response.readline().decode("utf-8")

        version, status, explanation = statusline.split(" ", 2)

        response_headers = {}

        while True:
            line = response.readline().decode("utf-8")
            if line == "\r\n": break

            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

        self.socket = s

        # Error code in 300 range, needs a redirect
        if str(status)[0] == "3":
            redirect_location = response_headers["location"]
            if redirect_location[0] == "/":
                redirect_location = self.scheme + self.host + redirect_location
            if self.view_source:
                redirect_location += "view-source:"

            return URL(redirect_location).request(True, s)


        if "transfer-encoding" in response_headers:
            if response_headers.get("transfer-encoding") == "chunked":

                raw_body = b""

                while True:

                    response_length = response.readline().decode("utf-8").strip()
                    response_length = int(response_length, 16)

                    if response_length == 0:
                        break

                    raw_body += response.read(response_length)
                    response.read(2)

                if "content-encoding" in response_headers:
                    if response_headers.get("content-encoding") == "gzip":
                        return gzip.decompress(raw_body).decode("utf-8")

                return raw_body.decode("utf-8")

            else:
                return "Unsupported transfer encoding method!"
        else:
            response_length = int(response_headers.get("content-length"))
            raw_content = response.read(response_length)

            if "content-encoding" in response_headers:
                if response_headers.get("content-encoding") == "gzip":
                    return gzip.decompress(raw_content).decode("utf-8")
                else:
                    return "Unsupported content encoding method!"

            else:
                return raw_content.decode("utf-8")


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
    b = Browser()
    b.load(URL("http://bit.ly/3SaF39o"))
    tkinter.mainloop()

