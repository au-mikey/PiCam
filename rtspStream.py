#import RPi.GPIO as GPIO
import os
from time import sleep
from http.server import BaseHTTPRequestHandler, HTTPServer
import configparser
import socket

host_name = ''  # Change this to your Raspberry Pi IP address
#host_port = 8000

global conf
conf = "config.ini"

config = configparser.ConfigParser()
config.read(conf)
host_port = int(config.get("WEB", "Port"))

class MyServer(BaseHTTPRequestHandler):
    """ A special implementation of BaseHTTPRequestHander for reading data from
        and control GPIO of a Raspberry Pi
    """

    def do_HEAD(self):
        """ do_HEAD() can be tested use curl command
            'curl -I http://server-ip-address:port'
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _redirect(self, path):
        self.send_response(303)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', path)
        self.end_headers()

    def do_GET(self):
        if self.path == "/":
            self.path = "index.html"
        if self.path == "favico.ico":
            return

        temp = os.popen("/opt/vc/bin/vcgencmd measure_temp").read().split("=")[1].split("'")[0]
        #temp = "temp=44.4'C".split("=")[1].split("'")[0]

        config = configparser.ConfigParser()
        config.read(conf)
        confWidth = config.get("VIDEO", "Width")
        confHeight = config.get("VIDEO", "Height")
        confRotation = int(config.get("VIDEO", "Rotation"))
        confFPS = int(config.get("VIDEO", "FPS"))
        confBitrate = int(config.get("VIDEO", "Bitrate"))
        confPort = config.get("STREAM", "Port")
        confDirectory = config.get("STREAM", "Directory")
        confProtocol = config.get("STREAM", "Protocol")
        confRes = f"{confWidth}x{confHeight}"
        link0 = f"rtsp://{address0}:{confPort}/{confDirectory}"
        link1 = f"rtsp://{address1}:{confPort}/{confDirectory}"

        resOpts = "640x480", "800x600", "1024x768", "1280x960", "1400x1050", "1600x1200", "1920x1080"
        bitrateOpts = "400000", "800000", "1200000", "1500000", "4000000"
        rotationOpts = "0", "90", "180", "270"
        protocolOpts = "udp", "tcp"

        resMenu = bitrateMenu = rotationMenu = protocolMenu = ""

        for res in resOpts:
            if res == confRes:
                resSelect = "selected"
            else:
                resSelect = ""
            resMenu += f'						<option value="{res}" {resSelect}>{res}</value>\n'

        for bitrate in bitrateOpts:
            if bitrate == str(confBitrate):
                bitrateSelect = "selected"
            else:
                bitrateSelect = ""
            bitrateMenu += f'						<option value="{bitrate}" {bitrateSelect}>{int(bitrate)/1000:.0f} kbps</value>\n'

        for rotation in rotationOpts:
            if rotation == str(confRotation):
                rotationSelect = "selected"
            else:
                rotationSelect = ""
            rotationMenu += f'						<option value="{rotation}" {rotationSelect}>{rotation}&#186</value>\n'

        for protocol in protocolOpts:
            if protocol == confProtocol:
                protocolSelect = "selected"
            else:
                protocolSelect = ""
            protocolMenu += f'						<option value="{protocol}" {protocolSelect}>{protocol}</value>\n'

        if self.path.endswith(".html"):
            f = open(self.path)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f.read().format(\
            fps = confFPS,\
            port = confPort,\
            directory = confDirectory,\
            resMenu = resMenu, \
            bitrateMenu = bitrateMenu, \
            rotationMenu = rotationMenu, \
            protocolMenu = protocolMenu, \
            link0 = link0, \
            link1 = link1, \
            temp = temp\
            ).encode("utf-8"))
            f.close()
        elif self.path.endswith(".css"):
            self.path = self.path[1:]
            f = open(self.path)
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            self.wfile.write(f.read().encode("utf-8"))
            f.close()
            return

    def do_POST(self):
        """ do_POST() can be tested using curl command
            'curl -d "submit=On" http://server-ip-address:port'
        """
        #conf = "conf.ini"
        content_length = int(self.headers['Content-Length'])  # Get the size of data
        post_data = self.rfile.read(content_length).decode("utf-8")  # Get the data
        post_data = post_data.split("&")
        data = dict(s.split("=") for s in post_data)

        if "submit" in data:
            print(f"Will now update {conf}")

            width = data['resolution'].split("x")[0]
            height = data['resolution'].split("x")[1]

            config = configparser.ConfigParser()
            config.read(conf)
            config.set("VIDEO", "Width", width)
            config.set("VIDEO", "Height", height)
            config.set("VIDEO", "Rotation", data['rotation'])
            config.set("VIDEO", "FPS", data['fps'])
            config.set("VIDEO", "Bitrate", data['br'])
            config.set("STREAM", "Port", data['port'])
            config.set("STREAM", "Directory", data['directory'])
            config.set("STREAM", "Protocol", data['protocol'])

            with open(conf, "w") as configfile:
                config.write(configfile)
            os.system("sudo systemctl restart initCam.service")
        elif "reboot" in data:
            print(f"Will now reboot")
            os.system("sudo reboot")

        self._redirect('/')  # Redirect back to the root url

if __name__ == '__main__':
    http_server = HTTPServer((host_name, host_port), MyServer)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    myip = s.getsockname()[0]
    s.close()
    fqdn = socket.gethostbyaddr(myip)[0]

    if host_name != '':
        address0 = host_name
        address1 = fqdn
    else:
        address0 = myip
        address1 = fqdn
    print("Starting web server - %s:%s" % (address0, host_port))
    print("                    - %s:%s" % (address1, host_port))

    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()
