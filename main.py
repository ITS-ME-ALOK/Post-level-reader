"""
Application entry point.
"""
import sys
import os

# Ensure the root directory is on the path so absolute imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from ui.main_window import MainWindow
from utils.logger import logger

def main():
    """
    Initializes and runs the main application loop.
    """
    logger.info("Starting PDF to Excel Converter application")
    
    # Set appearance mode and color theme for CustomTkinter
    ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
    
    try:
        app = MainWindow()
        app.mainloop()
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        logger.info("Application closed")

if __name__ == "__main__":
    main()
