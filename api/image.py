from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback
import base64
import httpagentparser

# ------------------ METADATA ------------------

__app__ = "Image Logger (Sanitized)"
__version__ = "2.0-clean"

# ------------------ CONFIG ------------------

config = {
    "image": "https://example.com/image.png",
    "imageArgument": False,

    "message": {
        "doMessage": False,
        "message": "Hello",
        "richMessage": False,
    },

    "redirect": {
        "redirect": False,
        "page": "https://example.com"
    },

    "buggedImage": False,
    "accurateLocation": False,
}

blacklistedIPs = ("27", "104", "143", "164")

# ------------------ HELPERS ------------------

def botCheck(ip: str, useragent: str):
    if ip.startswith(("34", "35")):
        return "Discord"
    if useragent and useragent.startswith("TelegramBot"):
        return "Telegram"
    return False


def safe_detect_ua(useragent: str):
    try:
        return httpagentparser.simple_detect(useragent or "")
    except Exception:
        return ("Unknown", "Unknown")


# ------------------ HANDLER ------------------

class ImageLoggerAPI(BaseHTTPRequestHandler):

    def handleRequest(self):
        try:
            # Always define path
            s = self.path

            # Safe headers
            ip = self.headers.get("x-forwarded-for", "")
            useragent = self.headers.get("user-agent", "")

            if ip.startswith(blacklistedIPs):
                return

            # Parse image
            url = config["image"]
            if config["imageArgument"]:
                dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
                if dic.get("url") or dic.get("id"):
                    encoded = dic.get("url") or dic.get("id")
                    url = base64.b64decode(encoded.encode()).decode()

            # Bot handling
            if botCheck(ip, useragent):
                self.send_response(200)
                self.send_header("Content-type", "image/jpeg")
                self.end_headers()
                return

            # Normal response
            html = f"""
            <style>
            body {{
                margin: 0;
                padding: 0;
            }}
            .img {{
                background-image: url('{url}');
                background-position: center;
                background-repeat: no-repeat;
                background-size: contain;
                width: 100vw;
                height: 100vh;
            }}
            </style>
            <div class="img"></div>
            """

            # Optional redirect
            if config["redirect"]["redirect"]:
                html = f'<meta http-equiv="refresh" content="0;url={config["redirect"]["page"]}">'

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())

        except Exception:
            self.send_response(500)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"500 - Internal Server Error\n")
            print(traceback.format_exc())

    do_GET = handleRequest
    do_POST = handleRequest


handler = app = ImageLoggerAPI
