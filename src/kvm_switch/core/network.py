"""
Network discovery, broadcasting, and connection handling
"""

import socket
import threading
import json
import time
from typing import Optional, Callable, Tuple, Dict, Any
from ..utils.config import BROADCAST_PORT, COMM_PORT, BROADCAST_INTERVAL, MAGIC_MESSAGE

class NetworkManager:
    """
    Handles network communication for the KVM Switch application
    
    This class manages peer discovery, connection establishment,
    and message passing between server and client instances.
    """
    
    def __init__(self, mode: str, on_message_callback: Optional[Callable] = None):
        """
        Initialize the NetworkManager
        
        Args:
            mode: Operating mode ('server' or 'client')
            on_message_callback: Callback function for handling received messages
        """
        self.mode = mode
        self.on_message_callback = on_message_callback
        self.running = True
        self.connected = False
        self.peer_addr: Optional[str] = None
        self.sock: Optional[socket.socket] = None
        
    def start_discovery(self) -> None:
        """Start network discovery process"""
        if self.mode == "server":
            threading.Thread(target=self._broadcast_presence, daemon=True).start()
        threading.Thread(target=self._listen_for_peers, daemon=True).start()
    
    def _broadcast_presence(self) -> None:
        """Broadcast presence on network (server only)"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        while self.running and not self.connected:
            try:
                sock.sendto(MAGIC_MESSAGE, ('<broadcast>', BROADCAST_PORT))
                time.sleep(BROADCAST_INTERVAL)
            except Exception:
                pass
        
        sock.close()
    
    def _listen_for_peers(self) -> None:
        """Listen for peer discovery messages"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', BROADCAST_PORT))
        sock.settimeout(1.0)
        
        while self.running and not self.connected:
            try:
                data, addr = sock.recvfrom(1024)
                if data == MAGIC_MESSAGE and self.mode == "client":
                    # Client found server
                    from ..ui.control_panel import show_connection_approval_dialog
                    if show_connection_approval_dialog(addr[0]):
                        self.peer_addr = addr[0]
                        self.establish_connection()
                        break
            except socket.timeout:
                continue
            except Exception:
                pass
        
        sock.close()
    
    def establish_connection(self) -> bool:
        """
        Establish TCP connection with peer
        
        Returns:
            bool: True if connection was successful, False otherwise
        """
        try:
            if self.mode == "server":
                # Server listens
                server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_sock.bind(('', COMM_PORT))
                server_sock.listen(1)
                server_sock.settimeout(10.0)
                
                self.sock, addr = server_sock.accept()
                self.peer_addr = addr[0]
                server_sock.close()
            else:
                # Client connects
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.peer_addr, COMM_PORT))
            
            self.sock.settimeout(1.0)
            self.connected = True
            
            # Start communication thread
            threading.Thread(target=self._handle_communication, daemon=True).start()
            
            return True
            
        except Exception:
            self.connected = False
            return False
    
    def exchange_screen_info(self, screen_width: int, screen_height: int) -> Tuple[int, int]:
        """
        Exchange screen dimensions with peer
        
        Args:
            screen_width: Local screen width
            screen_height: Local screen height
            
        Returns:
            Tuple[int, int]: Peer's screen dimensions (width, height)
        """
        try:
            # Send our dimensions
            dims = {"width": screen_width, "height": screen_height}
            self.sock.sendall(json.dumps(dims).encode() + b'\n')
            
            # Receive peer dimensions
            data = b''
            while b'\n' not in data:
                chunk = self.sock.recv(1024)
                if not chunk:
                    break
                data += chunk
            
            peer_dims = json.loads(data.decode().strip())
            return peer_dims['width'], peer_dims['height']
        except Exception:
            return 1920, 1080  # Default fallback
    
    def _handle_communication(self) -> None:
        """Handle incoming messages from peer"""
        buffer = b''
        while self.running and self.connected:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    raise ConnectionError("Connection lost")
                
                buffer += chunk
                while b'\n' in buffer:
                    line, buffer = buffer.split(b'\n', 1)
                    if self.on_message_callback:
                        self.on_message_callback(line)
                        
            except socket.timeout:
                continue
            except Exception:
                self.connected = False
                break
    
    def send_message(self, msg: Dict[str, Any]) -> bool:
        """
        Send message to peer
        
        Args:
            msg: Message dictionary to send
            
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        try:
            if self.sock and self.connected:
                self.sock.sendall(json.dumps(msg).encode() + b'\n')
                return True
        except Exception:
            self.connected = False
        return False
    
    def disconnect(self) -> None:
        """Close connection and cleanup resources"""
        self.running = False
        self.connected = False
        
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None
    
    def reconnect(self) -> None:
        """Attempt to reconnect to peer"""
        if not self.running:
            return
        
        self.disconnect()
        time.sleep(2)
        self.start_discovery()
    
    def wait_for_client(self) -> None:
        """Wait for client connection (server only)"""
        while self.running and not self.connected:
            try:
                self.establish_connection()
            except Exception:
                time.sleep(1)