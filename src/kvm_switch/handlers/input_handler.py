"""
Input handling for mouse and keyboard events
"""

from typing import Optional, Callable, Dict, Any, Union
from pynput import mouse, keyboard
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key

class InputHandler:
    """
    Handles mouse and keyboard input capture and simulation
    
    This class manages both local input capture for sending to remote
    systems and remote input simulation for received commands.
    """
    
    def __init__(self, mode: str, send_message_callback: Optional[Callable] = None):
        """
        Initialize the input handler
        
        Args:
            mode: Operating mode ('server' or 'client')
            send_message_callback: Callback function for sending messages
        """
        self.mode = mode
        self.send_message_callback = send_message_callback
        self.connected = False
        self.has_control = False
        
        # Controllers for simulating input
        self.mouse_controller = MouseController()
        self.keyboard_controller = KeyboardController()
        
        # Listeners for capturing input
        self.mouse_listener: Optional[mouse.Listener] = None
        self.keyboard_listener: Optional[keyboard.Listener] = None
        
        # Screen dimensions
        self.screen_width = 1920
        self.screen_height = 1080
        self.peer_screen_width = 1920
        self.peer_screen_height = 1080
        
    def set_screen_dimensions(self, width: int, height: int, 
                            peer_width: int, peer_height: int) -> None:
        """
        Set screen dimensions for coordinate scaling
        
        Args:
            width: Local screen width
            height: Local screen height
            peer_width: Peer screen width
            peer_height: Peer screen height
        """
        self.screen_width = width
        self.screen_height = height
        self.peer_screen_width = peer_width
        self.peer_screen_height = peer_height
        
    def set_state(self, connected: bool, has_control: bool) -> None:
        """
        Update the current connection and control state
        
        Args:
            connected: Whether connected to peer
            has_control: Whether local instance has control
        """
        self.connected = connected
        self.has_control = has_control
        
    def start_input_capture(self) -> None:
        """Start capturing input events"""
        # Never suppress - handle blocking in the callbacks
        self.mouse_listener = mouse.Listener(
            on_move=self._on_mouse_move,
            on_click=self._on_mouse_click,
            on_scroll=self._on_mouse_scroll,
            suppress=False
        )
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release,
            suppress=False
        )
        
        self.mouse_listener.start()
        self.keyboard_listener.start()
        
    def stop_input_capture(self) -> None:
        """Stop capturing input events"""
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
            
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
    
    def _on_mouse_move(self, x: int, y: int) -> bool:
        """
        Handle mouse movement
        
        Args:
            x: Mouse X coordinate
            y: Mouse Y coordinate
            
        Returns:
            bool: True to allow movement, False to block
        """
        if not self.connected:
            return True
            
        if self.mode == "server":
            if not self.has_control:
                # Server with gray overlay - control client
                norm_x = x / self.screen_width
                norm_y = y / self.screen_height
                if self.send_message_callback:
                    self.send_message_callback({
                        'type': 'mouse_move', 
                        'x': norm_x, 
                        'y': norm_y
                    })
                return True  # Allow cursor to move on overlay
            else:
                # Server has control - work normally
                return True
        else:  # Client
            if self.has_control:
                # Client has control - allow normal movement
                return True
            else:
                # Client doesn't have control - FREEZE
                return False
    
    def _on_mouse_click(self, x: int, y: int, button: Button, pressed: bool) -> bool:
        """
        Handle mouse click
        
        Args:
            x: Click X coordinate
            y: Click Y coordinate
            button: Mouse button that was clicked
            pressed: True if pressed, False if released
            
        Returns:
            bool: True to allow click, False to block
        """
        if not self.connected:
            return True
            
        if self.mode == "server":
            if not self.has_control:
                # Server controlling client
                btn = 'left' if button == Button.left else 'right'
                if self.send_message_callback:
                    self.send_message_callback({
                        'type': 'mouse_click', 
                        'button': btn, 
                        'pressed': pressed
                    })
                return True
            else:
                return True
        else:  # Client
            if self.has_control:
                return True
            else:
                return False
    
    def _on_mouse_scroll(self, x: int, y: int, dx: float, dy: float) -> bool:
        """
        Handle mouse scroll
        
        Args:
            x: Scroll X coordinate
            y: Scroll Y coordinate
            dx: Horizontal scroll amount
            dy: Vertical scroll amount
            
        Returns:
            bool: True to allow scroll, False to block
        """
        if not self.connected:
            return True
            
        if self.mode == "server":
            if not self.has_control:
                # Server controlling client
                if self.send_message_callback:
                    self.send_message_callback({
                        'type': 'mouse_scroll', 
                        'dx': dx, 
                        'dy': dy
                    })
                return True
            else:
                return True
        else:  # Client
            if self.has_control:
                return True
            else:
                return False
    
    def _on_key_press(self, key: Union[Key, str]) -> bool:
        """
        Handle key press
        
        Args:
            key: Key that was pressed
            
        Returns:
            bool: True to allow key, False to block
        """
        if not self.connected:
            return True
            
        if self.mode == "server":
            if not self.has_control:
                # Server controlling client
                try:
                    k = key.char if hasattr(key, 'char') and key.char else key.name
                    if self.send_message_callback:
                        self.send_message_callback({
                            'type': 'key', 
                            'key': k, 
                            'pressed': True
                        })
                except AttributeError:
                    pass
                return True
            else:
                return True
        else:  # Client
            if self.has_control:
                return True
            else:
                return False
    
    def _on_key_release(self, key: Union[Key, str]) -> bool:
        """
        Handle key release
        
        Args:
            key: Key that was released
            
        Returns:
            bool: True to allow key, False to block
        """
        if not self.connected:
            return True
            
        if self.mode == "server":
            if not self.has_control:
                # Server controlling client
                try:
                    k = key.char if hasattr(key, 'char') and key.char else key.name
                    if self.send_message_callback:
                        self.send_message_callback({
                            'type': 'key', 
                            'key': k, 
                            'pressed': False
                        })
                except AttributeError:
                    pass
                return True
            else:
                return True
        else:  # Client
            if self.has_control:
                return True
            else:
                return False
    
    def simulate_mouse_move(self, norm_x: float, norm_y: float) -> None:
        """
        Simulate mouse movement from remote input
        
        Args:
            norm_x: Normalized X coordinate (0-1)
            norm_y: Normalized Y coordinate (0-1)
        """
        x = int(norm_x * self.screen_width)
        y = int(norm_y * self.screen_height)
        self.mouse_controller.position = (x, y)
    
    def simulate_mouse_click(self, button_name: str, pressed: bool) -> None:
        """
        Simulate mouse click from remote input
        
        Args:
            button_name: Name of the button ('left' or 'right')
            pressed: True to press, False to release
        """
        button = Button.left if button_name == 'left' else Button.right
        if pressed:
            self.mouse_controller.press(button)
        else:
            self.mouse_controller.release(button)
    
    def simulate_mouse_scroll(self, dx: float, dy: float) -> None:
        """
        Simulate mouse scroll from remote input
        
        Args:
            dx: Horizontal scroll amount
            dy: Vertical scroll amount
        """
        self.mouse_controller.scroll(dx, dy)
    
    def simulate_key_action(self, key_name: str, pressed: bool) -> None:
        """
        Simulate keyboard action from remote input
        
        Args:
            key_name: Name of the key
            pressed: True to press, False to release
        """
        try:
            if len(key_name) == 1:
                # Single character key
                key = key_name
            else:
                # Special key
                key = getattr(Key, key_name, key_name)
            
            if pressed:
                self.keyboard_controller.press(key)
            else:
                self.keyboard_controller.release(key)
        except Exception:
            pass  # Ignore invalid keys