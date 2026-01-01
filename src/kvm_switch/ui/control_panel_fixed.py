"""
Control panel for No-Borders KVM Switch setup
Handles mode selection and configuration
"""
import tkinter as tk
from tkinter import messagebox
import threading
import time
from typing import Optional

from ..utils.config import SETUP_WIDTH, SETUP_HEIGHT, APP_NAME


class ControlPanel:
    """
    Setup dialog for mode selection and configuration
    """
    
    def __init__(self, kvm_instance) -> None:
        """Initialize control panel"""
        self.kvm = kvm_instance
        self.root = None
        self.hotkey_display = None
        self.recording = False
    
    def show(self) -> None:
        """Display the setup dialog"""
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} Setup")
        self.root.geometry(f"{SETUP_WIDTH}x{SETUP_HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg="#0f0f0f")
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - SETUP_WIDTH) // 2
        y = (self.root.winfo_screenheight() - SETUP_HEIGHT) // 2
        self.root.geometry(f"+{x}+{y}")
        
        # Create UI
        self._create_ui()
        
        # Setup protocol
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Run the dialog
        self.root.mainloop()
    
    def _create_ui(self) -> None:
        """Create UI elements"""
        # Main container
        main_container = tk.Frame(self.root, bg="#0f0f0f")
        main_container.pack(fill="both", expand=True)
        
        # Header
        self._create_header(main_container)
        
        # Mode selection
        mode_var = tk.StringVar(value="server")
        self._create_mode_selection(main_container, mode_var)
        
        # Control method (for server)
        control_var = tk.StringVar(value="button")
        self._create_control_method(main_container, control_var)
        
        # Hotkey configuration
        self._create_hotkey_config(main_container)
        
        # Update visibility functions
        def update_ui(*args):
            if mode_var.get() == "server":
                # Show control method
                control_frame = main_container.winfo_children()[2]
                control_frame.pack(fill="x", padx=40, pady=(10, 10))
                
                # Show/hide hotkey settings based on control method
                if control_var.get() == "hotkey":
                    hotkey_frame = main_container.winfo_children()[3]
                    hotkey_frame.pack(fill="x", padx=40, pady=(10, 10))
                else:
                    try:
                        hotkey_frame = main_container.winfo_children()[3]
                        hotkey_frame.pack_forget()
                    except:
                        pass
            else:
                # Client mode - hide both
                try:
                    control_frame = main_container.winfo_children()[2]
                    control_frame.pack_forget()
                    hotkey_frame = main_container.winfo_children()[3]
                    hotkey_frame.pack_forget()
                except:
                    pass
            
            self.root.update_idletasks()
        
        mode_var.trace('w', update_ui)
        control_var.trace('w', update_ui)
        
        # Initial UI state
        update_ui()
        
        # Start button
        def start():
            self.kvm.mode = mode_var.get()
            self.kvm.control_method = control_var.get()
            
            if self.kvm.mode == "server" and self.kvm.control_method == "hotkey" and not self.kvm.hotkey_combo:
                messagebox.showerror("Error", "Please record a hotkey first!\n\nClick the red RECORD button.")
                return
            
            self.root.destroy()
        
        btn_frame = tk.Frame(main_container, bg="#0f0f0f")
        btn_frame.pack(fill="x", padx=40, pady=(20, 30))
        
        start_btn = tk.Button(btn_frame, text="START", command=start,
                             bg="#818cf8", fg="white", font=("Arial", 16, "bold"),
                             bd=0, pady=15, cursor="hand2", relief="flat")
        start_btn.pack(fill="x")
        
        tk.Label(btn_frame, text="v0.2.1 • MIT License", font=("Arial", 9),
                bg="#0f0f0f", fg="#4b5563").pack(pady=(10, 0))
    
    def _create_header(self, parent) -> None:
        """Create header section"""
        header = tk.Frame(parent, bg="#0f0f0f")
        header.pack(fill="x", padx=40, pady=(30, 20))
        
        tk.Label(header, text="⚡ No-Borders", font=("Arial", 28, "bold"),
                bg="#0f0f0f", fg="white").pack()
        tk.Label(header, text="Setup Your Connection", font=("Arial", 12),
                bg="#0f0f0f", fg="#6b7280").pack(pady=(5, 0))
    
    def _create_mode_selection(self, parent, mode_var) -> None:
        """Create mode selection section"""
        mode_frame = tk.Frame(parent, bg="#0f0f0f")
        mode_frame.pack(fill="x", padx=40, pady=(10, 10))
        
        tk.Label(mode_frame, text="Select Mode:", font=("Arial", 14, "bold"),
                bg="#0f0f0f", fg="white").pack(anchor="w", pady=(0, 10))
        
        # Server option
        server_frame = tk.Frame(mode_frame, bg="#1a1a1a", highlightbackground="#818cf8",
                               highlightthickness=2)
        server_frame.pack(fill="x", pady=(0, 10))
        
        tk.Radiobutton(server_frame, text="🖥️  SERVER - Control other computers",
                                   variable=mode_var, value="server",
                                   font=("Arial", 11), bg="#1a1a1a", fg="white",
                                   selectcolor="#1a1a1a", activebackground="#1a1a1a").pack(anchor="w", padx=15, pady=15)
        
        # Client option
        client_frame = tk.Frame(mode_frame, bg="#1a1a1a", highlightbackground="#2a2a2a",
                               highlightthickness=1)
        client_frame.pack(fill="x")
        
        tk.Radiobutton(client_frame, text="💻  CLIENT - Be controlled by others",
                                   variable=mode_var, value="client",
                                   font=("Arial", 11), bg="#1a1a1a", fg="white",
                                   selectcolor="#1a1a1a", activebackground="#1a1a1a").pack(anchor="w", padx=15, pady=15)
    
    def _create_control_method(self, parent, control_var) -> None:
        """Create control method section"""
        control_frame = tk.Frame(parent, bg="#0f0f0f")
        
        tk.Label(control_frame, text="Control Method:", font=("Arial", 14, "bold"),
                bg="#0f0f0f", fg="white").pack(anchor="w", pady=(0, 10))
        
        method_frame = tk.Frame(control_frame, bg="#1a1a1a")
        method_frame.pack(fill="x")
        
        tk.Radiobutton(method_frame, text="📘  Toggle Button",
                      variable=control_var, value="button",
                      font=("Arial", 11), bg="#1a1a1a", fg="white",
                      selectcolor="#1a1a1a").pack(anchor="w", padx=15, pady=(10, 5))
        
        tk.Radiobutton(method_frame, text="🔥  Custom Hotkey",
                      variable=control_var, value="hotkey",
                      font=("Arial", 11), bg="#1a1a1a", fg="white",
                      selectcolor="#1a1a1a").pack(anchor="w", padx=15, pady=(5, 10))
    
    def _create_hotkey_config(self, parent) -> None:
        """Create hotkey configuration section"""
        hotkey_frame = tk.Frame(parent, bg="#0f0f0f")
        
        tk.Label(hotkey_frame, text="Hotkey Configuration:", font=("Arial", 14, "bold"),
                bg="#0f0f0f", fg="white").pack(anchor="w", pady=(0, 10))
        
        hk_container = tk.Frame(hotkey_frame, bg="#1a1a1a", highlightbackground="#818cf8",
                               highlightthickness=2)
        hk_container.pack(fill="x")
        
        hk_inner = tk.Frame(hk_container, bg="#1a1a1a")
        hk_inner.pack(fill="x", padx=20, pady=20)
        
        tk.Label(hk_inner, text="Current Hotkey:", font=("Arial", 11, "bold"),
                bg="#1a1a1a", fg="white").pack(anchor="w", pady=(0, 8))
        
        self.hotkey_display = tk.Label(hk_inner, text="Not set - Click RECORD below",
                                      font=("Arial", 12),
                                      bg="#1a1a1a", fg="#818cf8")
        self.hotkey_display.pack(anchor="w", pady=(0, 15))
        
        # Button frame
        button_frame = tk.Frame(hk_inner, bg="#1a1a1a")
        button_frame.pack(fill="x", pady=(10, 0))
        
        # Clear button
        clear_btn = tk.Button(button_frame, text="CLEAR HOTKEY", command=self._clear_hotkey,
                             bg="#4b5563", fg="white", font=("Arial", 14, "bold"),
                             bd=0, padx=30, pady=20, cursor="hand2", relief="flat")
        clear_btn.pack(fill="x", pady=(0, 10))
        
        # Record button
        record_btn = tk.Button(button_frame, text="🔴 RECORD", command=self._record_hotkey,
                               bg="#ef4444", fg="white", font=("Arial", 12, "bold"),
                               bd=0, padx=25, pady=12, cursor="hand2", relief="flat")
        record_btn.pack(fill="x")
        
        # Tip label
        tk.Label(hk_inner, text="💡 Tip: Press 2-3 keys together (e.g., Ctrl+Shift+Space)",
                font=("Arial", 9), bg="#1a1a1a", fg="#6b7280").pack(anchor="w", pady=(10, 0))
    
    def _record_hotkey(self) -> None:
        """Start recording hotkey"""
        if self.recording:
            return
        
        self.recording = True
        self.hotkey_display.config(text="⏺️ Recording... Press keys!", fg="#fbbf24")
        self.root.update()
        threading.Thread(target=self._record_hotkey_thread, daemon=True).start()
    
    def _record_hotkey_thread(self) -> None:
        """Record hotkey in background thread"""
        from pynput import keyboard
        
        recorded = []
        recording = [True]
        
        def on_press(key):
            if not recording[0]:
                return
            try:
                k = key.char if hasattr(key, 'char') and key.char else key.name
                if k and k not in recorded:
                    recorded.append(k)
                    self.hotkey_display.config(text=f"Recording: {' + '.join(recorded)}")
            except:
                pass
        
        def on_release(key):
            if len(recorded) >= 2:
                time.sleep(0.5)
                recording[0] = False
                return False
        
        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()
        listener.join()
        
        if recorded:
            self.kvm.hotkey_combo = recorded
            self.hotkey_display.config(text=f"{' + '.join(recorded)} ✓", fg="#10b981")
        else:
            self.hotkey_display.config(text="Not set - Click RECORD below", fg="#818cf8")
        
        self.recording = False
    
    def _clear_hotkey(self) -> None:
        """Clear recorded hotkey"""
        self.kvm.hotkey_combo = []
        self.hotkey_display.config(text="Not set - Click RECORD below", fg="#818cf8")
    
    def _on_close(self) -> None:
        """Handle window close"""
        if self.root:
            try:
                self.root.destroy()
            except:
                pass
            self.root = None
        
        # Signal cancellation rather than hard exit
        import sys
        sys.exit(0)