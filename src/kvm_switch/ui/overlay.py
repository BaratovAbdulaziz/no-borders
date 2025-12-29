"""
Server overlay functionality for the KVM Switch application
"""

import tkinter as tk
from typing import Optional
from ..utils.config import UI_COLORS, FONTS

class ServerOverlay:
    """
    Semi-transparent overlay for server when client has control
    
    This class creates a fullscreen overlay that appears on the server
    screen when the client has taken control of the system.
    """
    
    def __init__(self, parent_root: Optional[tk.Tk] = None):
        """
        Initialize the server overlay
        
        Args:
            parent_root: Parent tkinter root window
        """
        self.overlay: Optional[tk.Toplevel] = None
        self.parent_root = parent_root
        self.canvas: Optional[tk.Canvas] = None
        
    def show(self) -> None:
        """Show the semi-transparent overlay"""
        if self.overlay or not self.parent_root:
            return
        
        self.overlay = tk.Toplevel(self.parent_root)
        
        # Get screen dimensions for fullscreen
        screen_width = self.overlay.winfo_screenwidth()
        screen_height = self.overlay.winfo_screenheight()
        
        # Make it truly fullscreen
        self.overlay.geometry(f"{screen_width}x{screen_height}+0+0")
        self.overlay.overrideredirect(True)
        
        # Set transparency
        try:
            self.overlay.wait_visibility(self.overlay)
            self.overlay.wm_attributes('-alpha', 0.6)
        except Exception:
            pass
        
        # Create canvas with semi-transparent gray
        self.canvas = tk.Canvas(
            self.overlay, 
            width=screen_width, 
            height=screen_height, 
            bg='gray', 
            highlightthickness=0
        )
        self.canvas.pack(fill='both', expand=True)
        
        # Add status text
        self.canvas.create_text(
            screen_width // 2, 
            screen_height // 2,
            text="Server Overlay Active\nClient has control",
            font=FONTS['overlay_text'],
            fill="white"
        )
        
        self.overlay.attributes('-topmost', True)
        self.overlay.update_idletasks()
        
        # Lower below control button
        self.overlay.lower()
        
        # Keep control button on top
        if self.parent_root:
            self.parent_root.attributes('-topmost', True)
            self.parent_root.lift()
        
        self.overlay.update()
    
    def hide(self) -> None:
        """Hide and destroy the overlay"""
        if self.overlay:
            try:
                self.overlay.withdraw()
                self.overlay.destroy()
                if self.overlay:
                    self.overlay.update()
            except Exception:
                pass
            self.overlay = None
            self.canvas = None
        
        # Reset button topmost and force refresh
        if self.parent_root:
            try:
                self.parent_root.attributes('-topmost', True)
                self.parent_root.update()
            except Exception:
                pass
    
    def is_visible(self) -> bool:
        """
        Check if overlay is currently visible
        
        Returns:
            bool: True if overlay is visible, False otherwise
        """
        return self.overlay is not None
    
    def update_text(self, text: str) -> None:
        """
        Update the overlay text
        
        Args:
            text: New text to display on the overlay
        """
        if self.canvas:
            # Clear existing text and create new
            self.canvas.delete("text")
            screen_width = self.canvas.winfo_width()
            screen_height = self.canvas.winfo_height()
            
            self.canvas.create_text(
                screen_width // 2, 
                screen_height // 2,
                text=text,
                font=FONTS['overlay_text'],
                fill="white",
                tags="text"
            )