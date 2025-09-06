"""TBD"""
import tkinter as tk
from lib.ascii_art_gui import AsciiArtGUI


def main():
    """Main entry point"""
    root = tk.Tk()
    app = AsciiArtGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
