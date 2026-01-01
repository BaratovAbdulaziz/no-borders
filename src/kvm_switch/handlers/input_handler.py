"""
Input handler for No-Borders KVM Switch
Handles mouse and keyboard input capture and forwarding
"""
import threading
import time
from typing import Optional, TYPE_CHECKING

from pynput import mouse, keyboard
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key

if TYPE_CHECKING:
    from ..core.kvm_switch import KVMSwitch


class InputHandler:
    """
    Handles mouse and keyboard input capture and forwarding
    """
    
    def __init__(self, kvm_instance: 'KVMSwitch') -> None:
        """Initialize input handler"""
        self.kvm = kvm_instance
        self.mouse_controller = MouseController()
        self.keyboard_controller = KeyboardController()
        self.mouse_listener: Optional[mouse.Listener] = None
        self.keyboard_listener: Optional[keyboard.Listener] = None
        self.running = False
    
    def start(self) -> None:
        """Start input capture"""
        self.running = True
        
        def on_move(x, y):
            if self.kvm.mode == "server" and not self.kvm.has_control and self.kvm.connected:
                nx = x / self.kvm.screen_width
                ny = y / self.kvm.screen_height
                self.kvm.message_handler.send_message({'type': 'mouse_move', 'x': nx, 'y': ny})
        
        def on_click(x, y, button, pressed):
            if self.kvm.mode == "server" and not self.kvm.has_control and self.kvm.connected:
                btn = 'left' if button == Button.left else 'right'
                self.kvm.message_handler.send_message({'type': 'mouse_click', 'button': btn, 'pressed': pressed})
        
        def on_press(key):
            # Check hotkey
            if self.kvm.control_method == "hotkey" and self.kvm.mode == "server":
                try:
                    k = key.char if hasattr(key, 'char') and key.char else key.name
                    self.kvm.current_keys.add(k)
                    
                    if set(self.kvm.hotkey_combo).issubset(self.kvm.current_keys):
                        print(f"Hotkey triggered! {self.kvm.hotkey_combo}")
                        threading.Thread(target=self.kvm.toggle_control, daemon=True).start()
                except:
                    pass
            
            if self.kvm.mode == "server" and not self.kvm.has_control and self.kvm.connected:
                try:
                    k = key.char if hasattr(key, 'char') and key.char else key.name
                    self.kvm.message_handler.send_message({'type': 'key', 'key': k, 'pressed': True})
                except:
                    pass
        
        def on_release(key):
            if self.kvm.control_method == "hotkey":
                try:
                    k = key.char if hasattr(key, 'char') and key.char else key.name
                    self.kvm.current_keys.discard(k)
                except:
                    pass
            
            if self.kvm.mode == "server" and not self.kvm.has_control and self.kvm.connected:
                try:
                    k = key.char if hasattr(key, 'char') and key.char else key.name
                    self.kvm.message_handler.send_message({'type': 'key', 'key': k, 'pressed': False})
                except:
                    pass
        
        self.mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click)
        self.keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        
        self.mouse_listener.start()
        self.keyboard_listener.start()
        print("Input capture started")
    
    def stop(self) -> None:
        """Stop input capture"""
        self.running = False
        
        if self.mouse_listener:
            try:
                self.mouse_listener.stop()
            except:
                pass
        
        if self.keyboard_listener:
            try:
                self.keyboard_listener.stop()
            except:
                pass
    
    def process_input_message(self, msg: dict) -> None:
        """Process received input message (for client mode)"""
        if msg['type'] == 'mouse_move' and self.kvm.mode == "client" and self.kvm.has_control:
            x = int(msg['x'] * self.kvm.screen_width)
            y = int(msg['y'] * self.kvm.screen_height)
            self.mouse_controller.position = (x, y)
        
        elif msg['type'] == 'mouse_click' and self.kvm.mode == "client" and self.kvm.has_control:
            btn = Button.left if msg['button'] == 'left' else Button.right
            if msg['pressed']:
                self.mouse_controller.press(btn)
            else:
                self.mouse_controller.release(btn)
        
        elif msg['type'] == 'key' and self.kvm.mode == "client" and self.kvm.has_control:
            k = msg['key']
            try:
                if len(k) == 1:
                    key_obj = k
                else:
                    key_obj = getattr(Key, k, k)
                
                if msg['pressed']:
                    self.keyboard_controller.press(key_obj)
                else:
                    self.keyboard_controller.release(key_obj)
            except:
                pass