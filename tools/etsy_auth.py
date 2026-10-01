"""One-time Etsy login. Run this on your own computer (Python 3, no installs needed):

    python3 etsy_auth.py YOUR_KEYSTRING

In your Etsy developer app, set the callback URL to  http://localhost:3003/callback
A browser window opens, you approve access, and the script prints ETSY_REFRESH_TOKEN
and ETSY_SHOP_ID. Paste those into the cloud environment's settings (not into chat).
"""
import base64, hashlib, http.server, json, os, secrets, sys, urllib.parse, urllib.request, webbrowser

REDIRECT = "http://localhost:3003/callback"
SCOPES = "listings_r listings_w transactions_r shops_r"

key = sys.argv[1] if len(sys.argv) > 1 else sys.exit(__doc__)
verifier = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b"=").decode()
challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
state = secrets.token_urlsafe(16)
url = "https://www.etsy.com/oauth/connect?" + urllib.parse.urlencode({
    "response_type": "code", "redirect_uri": REDIRECT, "scope": SCOPES, "client_id": key,
    "state": state, "code_challenge": challenge, "code_challenge_method": "S256"})
result = {}


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if q.get("state", [""])[0] == state and "code" in q:
            result["code"] = q["code"][0]
        self.send_response(200); self.end_headers()
        self.wfile.write(b"Done - you can close this tab and go back to the terminal.")

    def log_message(self, *a):
        pass


print("Opening Etsy in your browser. If it doesn't open, visit:\n" + url)
webbrowser.open(url)
server = http.server.HTTPServer(("localhost", 3003), Handler)
while "code" not in result:
    server.handle_request()

tok = json.load(urllib.request.urlopen("https://api.etsy.com/v3/public/oauth/token", urllib.parse.urlencode({
    "grant_type": "authorization_code", "client_id": key, "redirect_uri": REDIRECT,
    "code": result["code"], "code_verifier": verifier}).encode()))
user_id = tok["access_token"].split(".")[0]
print("\nETSY_REFRESH_TOKEN=" + tok["refresh_token"])
print("ETSY_USER_ID=" + user_id)
print("(Your shop id is shown in the Etsy developer portal, or ask Claude to look it up from the user id.)")
