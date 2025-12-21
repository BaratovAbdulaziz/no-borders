#!/usr/bin/env python3
"""
tinyKVM – bullet-proof single-file software KVM
Linux (X11/Wayland) & Windows, no evdev, no driver, one file only.

-------------------------------------------------
ENVIRONMENT
-------------------------------------------------
# Python ≥ 3.8
# Linux:
sudo apt install python3-tk python3-pip
python3 -m pip install pynput>=1.7

# Windows:
py -3 -m pip install pynput>=1.7

# Run:
python3 tinyKVM.py          (or  py tinyKVM.py)
-------------------------------------------------
Click the coloured dot (top-right) to switch keyboard/mouse.
Author: public domain / MIT-0
"""

import json, socket, threading, time, os, sys, struct, random, hashlib
from contextlib import suppress
from pynput import keyboard
from pynput.keyboard import Key, Listener as KListener
from pynput.mouse import Listener as MListener, Button, Controller as MouseCtl

# ---------- CONFIG ---------- #
UDP_PORT   = 50000
TCP_PORT   = 50001
MAGIC      = b"TINYKVM"
TOKEN      = "changeMe"
BIND_IFACE = ""
RECV_BUFSZ = 1024
BTN_SIZE   = 40
OVERLAY_ALPHA = 0.3
# ---------------------------- #

OS = sys.platform
WIN = OS.startswith("win")
if WIN:
    import ctypes
    user32 = ctypes.windll.user32
    SWP_NOMOVE = 0x0002; SWP_NOSIZE = 0x0001
    HWND_TOPMOST = -1

def log(msg): print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def get_own_ip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        log(f"Own IP detected: {ip}")
        return ip

def gen_id():
    return hashlib.sha256(str(random.random()).encode()).digest()[:4]

# ---------- NETWORK ---------- #
class Discovery:
    def __init__(self):
        self.peers = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("", UDP_PORT))          # listen on all interfaces
        self.running = True
        self.own_id = gen_id()
        self.own_ip = get_own_ip()
        # start listener and cyclic sender
        threading.Thread(target=self._listen, daemon=True).start()
        threading.Thread(target=self._send_loop, daemon=True).start()
        # send unicast beacons to the whole /24 every 2 s
        threading.Thread(target=self._unicast_loop, daemon=True).start()

    # ---------- sender ---------- #
    def _send_loop(self):
        """Plain broadcast."""
        msg = MAGIC + self.own_id + struct.pack("!H", TCP_PORT) + TOKEN.encode()
        while self.running:
            self.sock.sendto(msg, ("255.255.255.255", UDP_PORT))
            time.sleep(1)

    def _unicast_loop(self):
        """/24 unicast – works even when broadcast is dropped."""
        base = self.own_ip.rsplit(".", 1)[0] + "."
        msg  = MAGIC + self.own_id + struct.pack("!H", TCP_PORT) + TOKEN.encode()
        while self.running:
            for host in range(1, 255):
                ip = base + str(host)
                if ip == self.own_ip:
                    continue
                self.sock.sendto(msg, (ip, UDP_PORT))
            time.sleep(2)

    # ---------- receiver ---------- #
    def _listen(self):
        log("Discovery: listener ready")
        while self.running:
            r, a = self.sock.recvfrom(RECV_BUFSZ)
            ip = a[0]
            if len(r) < len(MAGIC)+6+len(TOKEN): continue
            if not r.startswith(MAGIC): continue
            peer_id = r[8:12]
            if ip == self.own_ip and peer_id == self.own_id:  # self
                continue
            if not r.endswith(TOKEN.encode()): continue
            tcp_port = struct.unpack("!H", r[12:14])[0]
            self.peers[ip] = (tcp_port, peer_id)
            log(f"Discovery: peer recorded {ip}:{tcp_port}")

    def close(self):
        self.running = False
        self.sock.close()

class Link:
    def __init__(self, ip, port):
        log(f"Link: trying {ip}:{port}")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for attempt in range(10):
            try:
                self.sock.connect((ip, port))
                log("Link: TCP connected")
                break
            except (ConnectionRefusedError, TimeoutError) as e:
                log(f"Link: connect failed ({e}) – retry {attempt+1}")
                time.sleep(0.5)
        else:
            raise
        self.lock = threading.Lock()

    def send(self, typ, **kw):
        with self.lock:
            payload = json.dumps({"t": typ, **kw}) + "\n"
            self.sock.sendall(payload.encode())
            log(f"Sent {typ} event")

    def recv_loop(self, handler):
        buf = b""
        log("Link: receive loop started")
        while True:
            try:
                data = self.sock.recv(RECV_BUFSZ)
                if not data:
                    log("Link: socket closed by peer")
                    break
                buf += data
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    msg = json.loads(line)
                    log(f"Received {msg['t']} event")
                    handler(msg)
            except Exception as e:
                log(f"Link: recv error – {e}")
                break

# ---------- INPUT ---------- #
class InputCapture:
    def __init__(self, forward_fn):
        self.forward = forward_fn
        self.active = False
        self.klistener = None
        self.mlistener = None
        log("InputCapture created")

    def start(self):
        if self.active: return
        self.active = True
        log("InputCapture STARTED")
        self.klistener = KListener(on_press=self._kp, on_release=self._kr)
        self.mlistener = MListener(on_move=self._mm, on_click=self._mc, on_scroll=self._ms)
        self.klistener.start(); self.mlistener.start()

    def stop(self):
        if not self.active: return
        self.active = False
        log("InputCapture STOPPED")
        if self.klistener: self.klistener.stop()
        if self.mlistener: self.mlistener.stop()

    def _kp(self, key):
        log(f"CAPTURE kp: {key}")
        self.forward("kp", key=str(key))
    def _kr(self, key):
        log(f"CAPTURE kr: {key}")
        self.forward("kr", key=str(key))
    def _mm(self, x, y):
        log(f"CAPTURE mm: {x},{y}")
        self.forward("mm", x=x, y=y)
    def _mc(self, x, y, btn, pressed):
        log(f"CAPTURE mc: {btn} {pressed} @ {x},{y}")
        self.forward("mc", x=x, y=y, b=str(btn), p=pressed)
    def _ms(self, x, y, dx, dy):
        log(f"CAPTURE ms: {dx},{dy} @ {x},{y}")
        self.forward("ms", x=x, y=y, dx=dx, dy=dy)

class InputInject:
    def __init__(self):
        self.k = keyboard.Controller()
        self.m = MouseCtl()
        self.key_map = {str(k): k for k in Key}
        self.btn_map = {str(b): b for b in (Button.left, Button.right, Button.middle)}
        log("InputInject ready")

    def handle(self, msg):
        t = msg["t"]
        log(f"INJECT {t}")
        if t == "kp":
            with suppress(Exception): self.k.press(self._key(msg["key"]))
        elif t == "kr":
            with suppress(Exception): self.k.release(self._key(msg["key"]))
        elif t == "mm":
            self.m.position = (msg["x"], msg["y"])
        elif t == "mc":
            btn = self.btn_map.get(msg["b"], Button.left)
            if msg["p"]: self.m.press(btn)
            else: self.m.release(btn)
        elif t == "ms":
            self.m.scroll(msg["dx"], msg["dy"])

    def _key(self, name):
        return self.key_map.get(name, name.strip("'"))

# ---------- GUI ---------- #
try:
    import tkinter as tk
except ImportError:
    log("tkinter missing – install python3-tk"); sys.exit(1)

class ButtonWidget:
    def __init__(self, parent, click_cb):
        self.click_cb = click_cb
        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", 0.8)
        self.btn = tk.Button(self.win, text="●", width=2, height=1,
                             bg="#444", fg="#fff", activebackground="#0af",
                             command=self._toggle)
        self.btn.pack()
        self._place()
        self.win.bind("<ButtonPress-1>", self._start_drag)
        self.win.bind("<B1-Motion>", self._drag)
        self.drag_xy = None
        log("ButtonWidget created")

    def _place(self):
        sw = self.win.winfo_screenwidth()
        self.win.geometry(f"+{sw - BTN_SIZE - 5}+5")

    def _toggle(self):
        log("Button clicked – toggle control")
        self.click_cb()

    def set_color(self, has_control):
        self.btn.config(bg="#0f0" if has_control else "#f00")

    def _start_drag(self, e):
        self.drag_xy = (e.x_root, e.y_root)

    def _drag(self, e):
        if self.drag_xy:
            dx = e.x_root - self.drag_xy[0]
            dy = e.y_root - self.drag_xy[1]
            x = self.win.winfo_x() + dx
            y = self.win.winfo_y() + dy
            self.win.geometry(f"+{x}+{y}")
            self.drag_xy = (e.x_root, e.y_root)

class Overlay:
    def __init__(self, parent, on_click):
        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", OVERLAY_ALPHA)
        self.win.configure(bg="black")
        self.win.geometry(f"{self.win.winfo_screenwidth()}x{self.win.winfo_screenheight()}+0+0")
        self.win.bind("<Button-1>", lambda e: on_click())
        self.win.bind("<Key>", lambda e: "break")
        self.win.withdraw()
        log("Overlay created")

    def show(self):
        self.win.deiconify()
        log("Overlay SHOWN")
        if WIN:
            hwnd = ctypes.windll.user32.GetParent(self.win.winfo_id())
            user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)

    def hide(self):
        self.win.withdraw()
        log("Overlay HIDDEN")

# ---------- CORE ---------- #
class Node:
    def __init__(self):
        self.role = None
        self.link = None
        self.server_sock = None
        self.discovery = Discovery()
        self.inject = InputInject()
        self.capture = InputCapture(self._send_input)
        self.root = tk.Tk()
        self.root.withdraw()
        self.btn = ButtonWidget(self.root, self.toggle)
        self.overlay = Overlay(self.root, self.toggle)
        self.has_control = True
        self._update_gui()
        log("Node init complete – starting peer-watch thread")
        threading.Thread(target=self._peer_watch, daemon=True).start()
        self.root.mainloop()

    def _peer_watch(self):
        log("Peer-watch thread running")
        while True:
            peers = list(self.discovery.peers.items())
            if peers and self.role is None:
                ip, (port, _) = peers[0]
                own = self.discovery.own_ip
                if ip == own:                                   # remove self
                    del self.discovery.peers[ip]
                    log("Removed self from peer list")
                    continue
                # ----- ASK INSTEAD OF AUTO-PICK -----
                print(f"Peer found: {ip}   Own IP: {own}")
                ans = input("Act as (s)erver or (c)lient?  > ").strip().lower()
                self.role = "server" if ans.startswith("s") else "client"
                # ------------------------------------
                log(f"Role chosen: {self.role}")
                if self.role == "server":
                    self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    self.server_sock.bind(("", TCP_PORT))
                    self.server_sock.listen(1)
                    log("Server socket listening")
                    threading.Thread(target=self._accept_client, daemon=True).start()
                elif self.role == "client":
                    self.link = Link(ip, port)
                    threading.Thread(target=self.link.recv_loop,
                                     args=(self.inject.handle,), daemon=True).start()
                self._apply_control()
            time.sleep(1)

    def _send_input(self, typ, **kw):
        if self.role == "server" and not self.has_control and self.link:
            log(f"Forward {typ} to client")
            self.link.send(typ, **kw)

    def _accept_client(self):
        log("Server: waiting for incoming client...")
        while self.server_sock:
            try:
                client_sock, addr = self.server_sock.accept()
                log(f"Server: client connected from {addr}")
                self.link = Link.__new__(Link)
                self.link.sock = client_sock
                self.link.lock = threading.Lock()
                threading.Thread(target=self.link.recv_loop,
                                 args=(self.inject.handle,), daemon=True).start()
                break
            except Exception as e:
                log(f"Server: accept error – {e}")
                if self.server_sock:
                    time.sleep(0.1)
                else:
                    break

    def toggle(self, *_):
        if self.role is None: return
        self.has_control = not self.has_control
        log(f"Control toggled → has_control={self.has_control}")
        self._apply_control()
        if self.link:
            self.link.send("ctrl", has=self.has_control)

    def _apply_control(self):
        if self.role == "server":
            if self.has_control:
                self.capture.stop(); self.overlay.hide()
            else:
                self.capture.start(); self.overlay.show()
        else:
            self.capture.stop(); self.overlay.hide()
        self._update_gui()
        if self.link:
            self.link.send("ctrl", has=self.has_control)

    def _update_gui(self):
        self.btn.set_color(self.has_control)

# ---------- ENTRY ---------- #
if __name__ == "__main__":
    try:
        Node()
    except KeyboardInterrupt:
        log("bye")
