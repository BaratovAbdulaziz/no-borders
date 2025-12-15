# KVM No Borders

**KVM No Borders** is a lightweight, open‑source tool that lets you control multiple computers (Linux / Windows) using a **single keyboard and mouse**, just like a software KVM switch — **no physical hardware required**.

Think of it as *Mouse Without Borders / Barrier*, but focused on simplicity, low latency, and cross‑platform setups.

---

## ✨ Features

* 🖱️ Share **keyboard & mouse** across multiple PCs
* 🖥️ Works over **local network (LAN)**
* 🔁 Seamless cursor movement between screens
* 🐧 Linux & 🪟 Windows support
* ⚡ Lightweight & fast
* 🔐 No cloud, no tracking — local only

---

## 🧠 How It Works

One machine acts as the **server (host)** and captures keyboard/mouse input.
Other machines run as **clients**, receiving input over the network.

```
[ Keyboard + Mouse ]
          │
      (Server PC)
          │  LAN
 ┌────────┴────────┐
(Client PC)   (Client PC)
```

Move your cursor to the edge of one screen and it appears on the next machine.

---

## 📦 Installation

### Requirements

* Same local network (Wi‑Fi or Ethernet)
* Python 3.x *(if applicable)*
* Linux (X11 / Wayland*) or Windows

> ⚠️ Wayland support may be limited depending on compositor.

### Clone the repository

```bash
git clone https://github.com/BaratovAbdulaziz/no-borders/tree/main
cd no-borders
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

### Start server (host machine)

1. Fork the repo
2. start the script
3. choose the options weather it is server or client
4. use it
---

```bash
python KVM.py
```

### Start client (secondary machine)

```bash
python client.py --server-ip 192.168.1.10
```

> Replace the IP with your server machine’s local IP address.

---

## ⚙️ Configuration

You can configure:

* Screen layout (left / right / top / bottom)
* Hotkeys
* Port number
* Sensitivity & delay

---

## 🔒 Security Notes

* Designed for **trusted local networks only**
* No encryption by default
* Do **not expose ports to the internet**

---

## 🐞 Known Issues

- In windows it has some problems for upgrading pip
- inslling packages in windows
- some wrong prompting users while using powershell

---

## 🚀 Roadmap

* [ ] Clipboard sharing
* [ ] Encrypted communication
* [ ] Auto‑discovery on LAN
* [ ] Wayland‑native input support
* [ ] GUI configuration

---

## 📄 License

MIT License

---

## 💬 Inspiration

Inspired by:

* Mouse Without Borders
* Barrier / Synergy

But built to be **simpler, lighter, and hackable**.

---

## ⭐ Support

If you find this project useful, please ⭐ the repository and share it!

Happy hacking 🚀
