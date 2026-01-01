"""
Message handler for No-Borders KVM Switch
Handles message processing and communication
"""
import json
import time
import threading
import socket
from typing import Optional, TYPE_CHECKING

from ..utils.config import MESSAGE_TIMEOUT, RECONNECT_DELAY

if TYPE_CHECKING:
    from ..core.kvm_switch import KVMSwitch


class MessageHandler:
    """
    Handles message processing and network communication
    """
    
    def __init__(self, kvm_instance: 'KVMSwitch') -> None:
        """Initialize message handler"""
        self.kvm = kvm_instance
        self.running = False
    
    def send_message(self, msg: dict) -> None:
        """Send message to peer"""
        try:
            if hasattr(self.kvm, 'sock') and self.kvm.sock and self.kvm.connected:
                data = json.dumps(msg).encode() + b'\n'
                self.kvm.sock.sendall(data)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError) as e:
            print(f"Send error (connection lost): {e}")
            self.kvm.connected = False
            if self.kvm.running:
                threading.Thread(target=self._reconnect, daemon=True).start()
        except Exception as e:
            print(f"Send error: {e}")
            self.kvm.connected = False
    
    def handle_messages(self) -> None:
        """Handle incoming messages"""
        buffer = b''
        
        while self.kvm.running and self.kvm.connected:
            try:
                if hasattr(self.kvm, 'sock') and self.kvm.sock:
                    self.kvm.sock.settimeout(MESSAGE_TIMEOUT)
                    chunk = self.kvm.sock.recv(4096)
                    if not chunk:
                        raise ConnectionError("Connection closed")
                    
                    buffer += chunk
                    while b'\n' in buffer:
                        line, buffer = buffer.split(b'\n', 1)
                        self._process_message(line)
                else:
                    time.sleep(0.1)
                    
            except socket.timeout:
                continue
            except ConnectionError:
                print("Connection lost - attempting reconnect...")
                self.kvm.connected = False
                time.sleep(RECONNECT_DELAY)
                if self.kvm.running:
                    threading.Thread(target=self._reconnect, daemon=True).start()
                break
            except Exception as e:
                print(f"Message handling error: {e}")
                self.kvm.connected = False
                time.sleep(RECONNECT_DELAY)
                if self.kvm.running:
                    threading.Thread(target=self._reconnect, daemon=True).start()
                break
    
    def _process_message(self, data: bytes) -> None:
        """Process received message"""
        try:
            msg = json.loads(data.decode())
            
            if msg['type'] == 'toggle':
                self.kvm.has_control = not self.kvm.has_control
                print(f"Control toggled - Has control: {self.kvm.has_control}")
                
                if not self.kvm.has_control and self.kvm.mode == "server":
                    if self.kvm.overlay_manager:
                        self.kvm.overlay_manager.show_overlay()
                elif self.kvm.has_control and self.kvm.mode == "server":
                    if self.kvm.overlay_manager:
                        self.kvm.overlay_manager.hide_overlay()
            
            else:
                # Handle input messages
                if self.kvm.input_handler:
                    self.kvm.input_handler.process_input_message(msg)
                    
        except Exception as e:
            print(f"Message processing error: {e}")
    
    def _reconnect(self) -> None:
        """Attempt to reconnect"""
        if hasattr(self.kvm, 'network_manager') and self.kvm.network_manager:
            try:
                if self.kvm.mode == "server":
                    self.kvm.network_manager.start_server()
                else:
                    self.kvm.network_manager.connect_to_server(self.kvm.peer_addr)
                
                self.kvm.connected = True
                print(f"✓ Reconnection established!")
                
            except Exception as e:
                print(f"Reconnection failed: {e}")
                self.kvm.connected = False