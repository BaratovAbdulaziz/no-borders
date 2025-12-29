"""
Animated splash screen for the KVM Switch application
"""

import tkinter as tk
from typing import Optional
from ..utils.config import (SPLASH_WIDTH, SPLASH_HEIGHT, UI_COLORS, FONTS)

class SplashScreen:
    """
    Animated No-Borders brand splash screen
    
    This class creates and displays an animated splash screen
    with the No-Borders branding and Connect Without Limits tagline.
    """
    
    def __init__(self):
        """Initialize the splash screen"""
        self.splash: Optional[tk.Tk] = None
        self.canvas: Optional[tk.Canvas] = None
        
    def show(self) -> None:
        """Show the animated splash screen"""
        self.splash = tk.Tk()
        self.splash.title("No-Borders")
        self.splash.attributes('-topmost', True)
        self.splash.overrideredirect(True)

        screen_width = self.splash.winfo_screenwidth()
        screen_height = self.splash.winfo_screenheight()

        x = (screen_width - SPLASH_WIDTH) // 2
        y = (screen_height - SPLASH_HEIGHT) // 2
        self.splash.geometry(f"{SPLASH_WIDTH}x{SPLASH_HEIGHT}+{x}+{y}")

        self.canvas = tk.Canvas(
            self.splash, 
            width=SPLASH_WIDTH, 
            height=SPLASH_HEIGHT, 
            bg=UI_COLORS['splash_bg'], 
            highlightthickness=0
        )
        self.canvas.pack()

        center_x = SPLASH_WIDTH // 2
        center_y = SPLASH_HEIGHT // 2

        # Create border lines
        border_lines = []
        for i in range(4):
            line = self.canvas.create_line(
                0, 0, 0, 0, 
                fill=UI_COLORS['splash_border'], 
                width=3
            )
            border_lines.append(line)

        # Create text elements
        brand_text = self.canvas.create_text(
            center_x, center_y, 
            text="No-Borders",
            font=FONTS['splash_title'], 
            fill=UI_COLORS['splash_text']
        )
        tagline_text = self.canvas.create_text(
            center_x, center_y + 60,
            text="Connect Without Limits",
            font=FONTS['splash_tagline'], 
            fill=UI_COLORS['splash_tagline']
        )

        # Initially hide text
        self.canvas.itemconfig(brand_text, state='hidden')
        self.canvas.itemconfig(tagline_text, state='hidden')

        # Start animation
        self._animate(border_lines, brand_text, tagline_text, center_x, center_y)
        
        self.splash.mainloop()
        
    def _animate(self, border_lines, brand_text, tagline_text, center_x, center_y):
        """
        Animate the splash screen elements
        
        Args:
            border_lines: List of border line canvas items
            brand_text: Brand text canvas item
            tagline_text: Tagline text canvas item
            center_x: Center X coordinate
            center_y: Center Y coordinate
        """
        animation_step = [0]
        total_steps = 60

        def animate():
            step = animation_step[0]

            if step < total_steps:
                if step < 20:
                    # Animate border lines
                    fade_progress = step / 20
                    border_length = 200 * fade_progress

                    self.canvas.coords(border_lines[0], 
                                     center_x - border_length, center_y - 100,
                                     center_x + border_length, center_y - 100)
                    self.canvas.coords(border_lines[1], 
                                     center_x + border_length, center_y - 100,
                                     center_x + border_length, center_y + 100)
                    self.canvas.coords(border_lines[2], 
                                     center_x + border_length, center_y + 100,
                                     center_x - border_length, center_y + 100)
                    self.canvas.coords(border_lines[3], 
                                     center_x - border_length, center_y + 100,
                                     center_x - border_length, center_y - 100)

                elif step == 20:
                    # Show text
                    self.canvas.itemconfig(brand_text, state='normal')
                    self.canvas.itemconfig(tagline_text, state='normal')

                elif 20 < step < 40:
                    # Fade in text
                    text_fade = (step - 20) / 20
                    color = int(255 * text_fade)
                    self.canvas.itemconfig(brand_text, 
                                         fill=f'#{color:02x}{color:02x}{color:02x}')

                    tag_color = int(136 * text_fade)
                    self.canvas.itemconfig(tagline_text, 
                                         fill=f'#{tag_color:02x}{tag_color:02x}{tag_color:02x}')

                elif 40 <= step < 55:
                    # Dissolve borders
                    dissolve_progress = (step - 40) / 15
                    border_length = 200 * (1 - dissolve_progress)
                    opacity = int(255 * (1 - dissolve_progress))
                    
                    border_color = f'#{0:02x}{opacity:02x}{opacity:02x}'
                    for line in border_lines:
                        self.canvas.itemconfig(line, fill=border_color)

                    if border_length > 0:
                        self.canvas.coords(border_lines[0], 
                                         center_x - border_length, center_y - 100,
                                         center_x + border_length, center_y - 100)
                        self.canvas.coords(border_lines[1], 
                                         center_x + border_length, center_y - 100,
                                         center_x + border_length, center_y + 100)
                        self.canvas.coords(border_lines[2], 
                                         center_x + border_length, center_y + 100,
                                         center_x - border_length, center_y + 100)
                        self.canvas.coords(border_lines[3], 
                                         center_x - border_length, center_y + 100,
                                         center_x - border_length, center_y - 100)

                animation_step[0] += 1
                self.splash.after(50, animate)
            else:
                # End animation
                self.splash.after(500, self.splash.destroy)

        self.splash.after(100, animate)