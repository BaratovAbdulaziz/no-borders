"""
Splash screen for No-Borders KVM Switch
Animated startup screen
"""
import tkinter as tk
from typing import Optional

from ..utils.config import SPLASH_WIDTH, SPLASH_HEIGHT, APP_NAME


class SplashScreen:
    """
    Animated splash screen for the application
    """
    
    def __init__(self) -> None:
        """Initialize splash screen"""
        self.splash: Optional[tk.Tk] = None
        self.alpha = 0.0
    
    def show(self) -> None:
        """Display the animated splash screen"""
        self.splash = tk.Tk()
        self.splash.title(APP_NAME)
        self.splash.overrideredirect(True)
        self.splash.attributes('-topmost', True)
        
        # Center the splash screen
        x = (self.splash.winfo_screenwidth() - SPLASH_WIDTH) // 2
        y = (self.splash.winfo_screenheight() - SPLASH_HEIGHT) // 2
        self.splash.geometry(f"{SPLASH_WIDTH}x{SPLASH_HEIGHT}+{x}+{y}")
        self.splash.configure(bg='#0f0f0f')
        
        # Create UI elements
        self._create_ui()
        
        # Start animation
        self._animate()
        
        # Run the splash
        self.splash.mainloop()
    
    def _create_ui(self) -> None:
        """Create UI elements for splash screen"""
        # Animated lightning icon
        title = tk.Label(self.splash, text="⚡", font=("Arial", 80),
                        bg="#0f0f0f", fg="#818cf8")
        title.pack(pady=(60, 10))
        
        # Application name
        name = tk.Label(self.splash, text=APP_NAME, font=("Arial", 32, "bold"),
                       bg="#0f0f0f", fg="white")
        name.pack(pady=10)
        
        # Subtitle
        subtitle = tk.Label(self.splash, text="Seamless Multi-Computer Control",
                          font=("Arial", 11), bg="#0f0f0f", fg="#6b7280")
        subtitle.pack()
    
    def _animate(self) -> None:
        """Handle fade-in animation"""
        if self.splash and self.alpha < 1.0:
            self.alpha += 0.05
            try:
                self.splash.attributes('-alpha', self.alpha)
            except:
                pass
            self.splash.after(20, self._animate)
        else:
            # Show splash for a moment then close
            if self.splash:
                self.splash.after(1500, self._close)
    
    def _close(self) -> None:
        """Close the splash screen"""
        if self.splash:
            try:
                self.splash.quit()  # Properly quit the mainloop
                self.splash.destroy()
            except:
                pass
            self.splash = None