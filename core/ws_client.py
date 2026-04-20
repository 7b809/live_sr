import websocket, json, threading

class WSClient:
    def __init__(self, url, sec, callback):
        self.url = f"{url}/{sec}/quote"
        self.cb = callback

    def start(self):
        t = threading.Thread(target=self._run)
        t.daemon = True
        t.start()

    def _run(self):
        ws = websocket.WebSocketApp(
            self.url,
            on_message=self.on_msg
        )
        ws.run_forever()

    def on_msg(self, ws, msg):
        try:
            data = json.loads(msg)
            self.cb(data)
        except:
            pass