"""
Network manager for No-Borders KVM Switch
Handles discovery, broadcasting, and connections
"""
import socket
import threading
import time
import os
from typing import Optional, TYPE_CHECKING

from ..utils.config import (
    BROADCAST_PORT, COMM_PORT, MAGIC_MESSAGE,
    BROADCAST_INTERVAL, DISCOVERY_TIMEOUT
)

if TYPE_CHECKING:
    from .kvm_switch import KVMSwitch


class NetworkManager:
    """
    Manages network discovery and connections
    """
    
    def __init__(self, kvm_instance: 'KVMSwitch') -> None:
        """Initialize network manager"""
        self.kvm = kvm_instance
        self.broadcast_socket: Optional[socket.socket] = None
        self.listen_socket: Optional[socket.socket] = None
        self.server_socket: Optional[socket.socket] = None
        self.running = False
    
    def start(self) -> None:
        """Start network services"""
        self.running = True
        
        if self.kvm.mode == "server":
            threading.Thread(target=self._broadcast, daemon=True).start()
        
        threading.Thread(target=self._listen, daemon=True).start()
    
    def stop(self) -> None:
        """Stop network services"""
        self.running = False
        
        if self.broadcast_socket:
            try:
                self.broadcast_socket.close()
            except:
                pass
        
        if self.listen_socket:
            try:
                self.listen_socket.close()
            except:
                pass
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
    
    def _broadcast(self) -> None:
        """Broadcast presence for server mode"""
        try:
            self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        except Exception as e:
            print(f"Failed to create broadcast socket: {e}")
            return
        
        while self.running and not self.kvm.connected:
            try:
                self.broadcast_socket.sendto(MAGIC_MESSAGE, ('<broadcast>', BROADCAST_PORT))
                time.sleep(BROADCAST_INTERVAL)
            except Exception as e:
                print(f"Broadcast error: {e}")
                break
        
        if self.broadcast_socket:
            try:
                self.broadcast_socket.close()
            except:
                pass
    
    def _listen(self) -> None:
        """Listen for broadcasts from peers"""
        try:
            self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.listen_socket.bind(('', BROADCAST_PORT))
            self.listen_socket.settimeout(DISCOVERY_TIMEOUT)
        except Exception as e:
            print(f"Failed to create listen socket: {e}")
            return
        
        while self.running and not self.kvm.connected:
            try:
                data, addr = self.listen_socket.recvfrom(1024)
                print(f"Received from {addr[0]}: {data}")
                
                if data == MAGIC_MESSAGE and self.kvm.mode == "client":
                    print(f"Client found server at {addr[0]}")
                    self.kvm.peer_addr = addr[0]
                    threading.Thread(target=self._connect_as_client, daemon=True).start()
                    break
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Listen error: {e}")
                break
        
        if self.listen_socket:
            try:
                self.listen_socket.close()
            except:
                pass
    
    def start_server(self) -> None:
        """Start server and wait for client connection"""
        from ..utils.config import SERVER_TIMEOUT
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Add Windows-specific socket options
            if os.name == 'nt':
                self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            
            self.server_socket.bind(('', COMM_PORT))
            self.server_socket.listen(1)
            self.server_socket.settimeout(SERVER_TIMEOUT)
            
            print(f"Server: Listening on port {COMM_PORT}")
            self.kvm.sock, addr = self.server_socket.accept()
            self.kvm.peer_addr = addr[0]
            print(f"Server: Connected to client at {addr[0]}")
            
            # Set socket options for better reliability
            self.kvm.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.kvm.sock.settimeout(1.0)
            
        except Exception as e:
            raise Exception(f"Server setup failed: {e}")
        finally:
            if self.server_socket:
                try:
                    self.server_socket.close()
                except:
                    pass
    
    def connect_to_server(self, server_addr: str) -> None:
        """Connect to server as client"""
        from ..utils.config import CONNECTION_TIMEOUT
        
        try:
            self.kvm.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Add Windows-specific socket options
            if os.name == 'nt':
                self.kvm.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            
            self.kvm.sock.settimeout(CONNECTION_TIMEOUT)
            self.kvm.sock.connect((server_addr, COMM_PORT))
            print(f"Client: Connected to server!")
            
            # Set socket options for better reliability
            self.kvm.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.kvm.sock.settimeout(1.0)
            
        except Exception as e:
            raise Exception(f"Client connection failed: {e}")
    
    def _connect_as_client(self) -> None:
        """Handle client connection establishment"""
        try:
            if self.kvm.peer_addr is not None:
                self.connect_to_server(self.kvm.peer_addr)
            self.kvm.connected = True
            
            print(f"✓ Connection established! Mode: {self.kvm.mode}, Has control: {self.kvm.has_control}")
            
            # Start message handling
            if self.kvm.message_handler:
                threading.Thread(target=self.kvm.message_handler.handle_messages, daemon=True).start()
                
        except Exception as e:
            print(f"Connection error: {e}")
            self.kvm.connected = False
            if self.kvm.running:
                time.sleep(3)
                threading.Thread(target=self._connect_as_client, daemon=True).start()