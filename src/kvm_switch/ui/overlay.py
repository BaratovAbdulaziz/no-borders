"""
Overlay manager for No-Borders KVM Switch
Handles overlay display when not in control
"""
import tkinter as tk
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.kvm_switch import KVMSwitch


class OverlayManager:
    """
    Manages overlay display for client control indication
    """
    
    def __init__(self, kvm_instance: 'KVMSwitch') -> None:
        """Initialize overlay manager"""
        self.kvm = kvm_instance
        self.overlay: Optional[tk.Toplevel] = None
    
    def show_overlay(self) -> None:
        """Show overlay when not in control"""
        if self.overlay:
            return
        
        try:
            self.overlay = tk.Toplevel()
            self.overlay.attributes('-fullscreen', True)
            self.overlay.attributes('-alpha', 0.85)
            self.overlay.configure(bg='#0f0f0f')
            
            w = self.overlay.winfo_screenwidth()
            h = self.overlay.winfo_screenheight()
            
            # Lightning icon
            tk.Label(self.overlay, text="⚡", font=("Arial", 100),
                    bg="#0f0f0f", fg="#818cf8").place(relx=0.5, rely=0.4, anchor="center")
            
            # Status text
            tk.Label(self.overlay, text="Client Has Control", font=("Arial", 32, "bold"),
                    bg="#0f0f0f", fg="white").place(relx=0.5, rely=0.55, anchor="center")
        except Exception as e:
            print(f"Failed to create overlay: {e}")
    
    def hide_overlay(self) -> None:
        """Hide overlay"""
        if self.overlay:
            try:
                self.overlay.destroy()
                self.overlay = None
            except:
                pass