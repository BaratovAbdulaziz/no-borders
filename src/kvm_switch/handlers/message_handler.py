"""
Message processing and communication handling
"""

import json
from typing import Dict, Any, Callable, Optional
from .input_handler import InputHandler

class MessageHandler:
    """
    Handles processing of messages received from peer
    
    This class processes incoming control messages and delegates
    actions to appropriate handlers.
    """
    
    def __init__(self, mode: str, input_handler: InputHandler,
                 control_state_callback: Optional[Callable] = None,
                 show_overlay_callback: Optional[Callable] = None,
                 hide_overlay_callback: Optional[Callable] = None):
        """
        Initialize the message handler
        
        Args:
            mode: Operating mode ('server' or 'client')
            input_handler: Input handler instance for simulating input
            control_state_callback: Callback for control state changes
            show_overlay_callback: Callback for showing overlay
            hide_overlay_callback: Callback for hiding overlay
        """
        self.mode = mode
        self.input_handler = input_handler
        self.control_state_callback = control_state_callback
        self.show_overlay_callback = show_overlay_callback
        self.hide_overlay_callback = hide_overlay_callback
        
        self.has_control = False
        
    def process_message(self, data: bytes) -> None:
        """
        Process incoming message from peer
        
        Args:
            data: Raw message data as bytes
        """
        try:
            msg = json.loads(data.decode())
            self._handle_message(msg)
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass  # Ignore invalid messages
    
    def _handle_message(self, msg: Dict[str, Any]) -> None:
        """
        Handle parsed message
        
        Args:
            msg: Parsed message dictionary
        """
        msg_type = msg.get('type')
        
        if msg_type == 'control_request':
            self._handle_control_request()
        elif msg_type == 'control_release':
            self._handle_control_release()
        elif msg_type == 'mouse_move':
            self._handle_mouse_move(msg)
        elif msg_type == 'mouse_click':
            self._handle_mouse_click(msg)
        elif msg_type == 'mouse_scroll':
            self._handle_mouse_scroll(msg)
        elif msg_type == 'key':
            self._handle_key_action(msg)
    
    def _handle_control_request(self) -> None:
        """Handle control request from peer"""
        if self.mode == "client":
            self.has_control = True  # Client now has control
        else:
            self.has_control = False
            
        if self.mode == "server" and self.show_overlay_callback:
            self.show_overlay_callback()
            
        if self.control_state_callback:
            self.control_state_callback(self.has_control)
    
    def _handle_control_release(self) -> None:
        """Handle control release from peer"""
        if self.mode == "server":
            self.has_control = True
            if self.hide_overlay_callback:
                self.hide_overlay_callback()
        else:
            self.has_control = False
            
        if self.control_state_callback:
            self.control_state_callback(self.has_control)
    
    def _handle_mouse_move(self, msg: Dict[str, Any]) -> None:
        """
        Handle remote mouse movement
        
        Args:
            msg: Message containing mouse movement data
        """
        if self.mode == "client" and self.has_control:
            # Client has control, so apply server's movements
            x = msg.get('x', 0)
            y = msg.get('y', 0)
            self.input_handler.simulate_mouse_move(x, y)
    
    def _handle_mouse_click(self, msg: Dict[str, Any]) -> None:
        """
        Handle remote mouse click
        
        Args:
            msg: Message containing mouse click data
        """
        if self.mode == "client" and self.has_control:
            button = msg.get('button', 'left')
            pressed = msg.get('pressed', False)
            self.input_handler.simulate_mouse_click(button, pressed)
    
    def _handle_mouse_scroll(self, msg: Dict[str, Any]) -> None:
        """
        Handle remote mouse scroll
        
        Args:
            msg: Message containing mouse scroll data
        """
        if self.mode == "client" and self.has_control:
            dx = msg.get('dx', 0)
            dy = msg.get('dy', 0)
            self.input_handler.simulate_mouse_scroll(dx, dy)
    
    def _handle_key_action(self, msg: Dict[str, Any]) -> None:
        """
        Handle remote keyboard action
        
        Args:
            msg: Message containing keyboard action data
        """
        if self.mode == "client" and self.has_control:
            key = msg.get('key', '')
            pressed = msg.get('pressed', False)
            self.input_handler.simulate_key_action(key, pressed)
    
    def set_control_state(self, has_control: bool) -> None:
        """
        Update the control state
        
        Args:
            has_control: Whether local instance has control
        """
        self.has_control = has_control
        self.input_handler.set_state(True, has_control)