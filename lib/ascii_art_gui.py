import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

from lib.image_utils import convert_to_edges, convert_to_terminal_art, high_contrast_overlay, load_image


class AsciiArtGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ASCII Art Generator")

        # Create a main frame to hold the three columns
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create the three columnar frames
        self.image_frame = tk.Frame(
            main_frame, bd=2, relief=tk.GROOVE)
        self.ascii_frame = tk.Frame(main_frame, bd=2, relief=tk.GROOVE)
        self.control_frame = tk.Frame(main_frame, bd=2, relief=tk.GROOVE)

        # Lay them out horizontally
        self.image_frame.pack(side=tk.LEFT, fill=tk.BOTH,
                              expand=True, padx=5, pady=5)
        self.ascii_frame.pack(side=tk.LEFT, fill=tk.BOTH,
                              expand=True, padx=5, pady=5)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        self.setup_image_area()
        self.setup_ascii_area()
        self.setup_controls()

        # Theming
        fg_color = "white"
        frame_bg_color = "#222222"
        label_color = "#737373"
        bg_main = "#353535"
        action_color = "#676767"
        main_frame.configure(background=frame_bg_color)
        self.image_frame.configure(background=frame_bg_color)
        self.ascii_frame.configure(background=frame_bg_color)
        self.control_frame.configure(background=frame_bg_color)
        self.original_image_label.configure(
            background=frame_bg_color, fg=fg_color)
        self.original_image.configure(background=bg_main)
        self.ascii_text_label.configure(background=frame_bg_color, fg=fg_color)
        self.ascii_text.configure(background=bg_main, fg=fg_color)
        self.controls_label.configure(background=frame_bg_color, fg=fg_color)
        self.load_button.configure(background=action_color, fg=fg_color)
        self.scale_label.configure(background=label_color, fg=fg_color)
        self.scale.configure(background=action_color, fg=fg_color)
        self.blur_diameter_label.configure(background=label_color, fg=fg_color)
        self.blur_diameter.configure(background=action_color, fg=fg_color)
        self.canny_low_label.configure(background=label_color, fg=fg_color)
        self.canny_low.configure(background=action_color, fg=fg_color)
        self.canny_high.configure(background=action_color, fg=fg_color)
        self.dark_threshold_label.configure(
            background=label_color, fg=fg_color)
        self.dark_threshold.configure(background=action_color, fg=fg_color)
        self.invert_color.configure(background=action_color, fg=fg_color)

        self.image_path = None

    def setup_image_area(self):
        # Placeholder for image
        self.original_image_label = tk.Label(
            self.image_frame, text="Original Image")
        self.original_image_label.pack()
        self.original_image = tk.Label(self.image_frame)
        self.original_image.pack(fill=tk.BOTH, expand=True)

    def setup_ascii_area(self):
        # Placeholder for ASCII art
        self.ascii_text_label = tk.Label(self.ascii_frame, text="ASCII Art")
        self.ascii_text_label.pack()
        self.ascii_text = tk.Text(
            self.ascii_frame, wrap='none', font=("Courier", 8))
        self.ascii_text.pack(fill=tk.BOTH, expand=True)

    def setup_controls(self):
        """Initialize all controls on the control panel"""
        # Title
        self.controls_label = tk.Label(self.control_frame, text="Controls")
        self.controls_label.pack(pady=5)

        # Load button
        self.load_button = tk.Button(
            self.control_frame, text="Load Image", command=self.load_image)
        self.load_button.pack(pady=5)

        # Scale
        self.scale_label = tk.Label(self.control_frame, text="Scale (%)")
        self.scale_label.pack(pady=1)
        self.scale = tk.Scale(
            self.control_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=self.generate_ascii)
        self.scale.set(50)
        self.scale.pack(pady=3)

        # Gaussian blur radius
        self.blur_diameter_label = tk.Label(
            self.control_frame, text="Blur Diameter")
        self.blur_diameter_label.pack(pady=1)
        self.blur_diameter = tk.Scale(
            self.control_frame, from_=3, to=16, resolution=2, orient=tk.HORIZONTAL, command=self.generate_ascii)
        self.blur_diameter.set(5)
        self.blur_diameter.pack(pady=3)

        # Canny Thresholds
        self.canny_low_label = tk.Label(
            self.control_frame, text="Canny Thresholds")
        self.canny_low_label.pack(pady=1)
        self.canny_low = tk.Scale(
            self.control_frame, from_=0, to=255, resolution=5, orient=tk.HORIZONTAL, command=self.generate_ascii)
        self.canny_low.set(50)
        self.canny_low.pack(pady=3)
        self.canny_high = tk.Scale(
            self.control_frame, from_=0, to=255, resolution=5, orient=tk.HORIZONTAL, command=self.generate_ascii)
        self.canny_high.set(150)
        self.canny_high.pack(pady=3)

        # Darkness Thresholds
        self.dark_threshold_label = tk.Label(
            self.control_frame, text="Dark Threshold")
        self.dark_threshold_label.pack(pady=1)
        self.dark_threshold = tk.Scale(
            self.control_frame, from_=0, to=255, resolution=5, orient=tk.HORIZONTAL, command=self.generate_ascii)
        self.dark_threshold.set(50)
        self.dark_threshold.pack(pady=3)

        # Invert
        self.checkbox_var = tk.BooleanVar(value=True)
        self.invert_color = tk.Checkbutton(
            self.control_frame, text="Invert Color", variable=self.checkbox_var, command=self.generate_ascii)
        self.invert_color.pack(pady=3)

    def load_image(self):
        # This function will open a file dialog and load the image
        self.image_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.webp")]
        )
        if not self.image_path:
            return

        img = Image.open(self.image_path)
        img.thumbnail((300, 300))  # Resize for display
        img_tk = ImageTk.PhotoImage(img)
        self.original_image.configure(image=img_tk)
        self.original_image.image = img_tk  # Keep a reference

        # Initialize the render
        self.generate_ascii()

    def generate_ascii(self, *args):
        if not self.image_path:
            return

        # Get settings from controls
        scale = self.scale.get() / 100.0
        blur_diameter = self.blur_diameter.get()
        canny_low = self.canny_low.get()
        canny_high = self.canny_high.get()
        dark_threshold = self.dark_threshold.get()
        invert_color = self.checkbox_var.get()

        # Generate
        image = load_image(self.image_path)
        edges = convert_to_edges(image, blur_kernel=(
            blur_diameter, blur_diameter), threshold1=canny_low, threshold2=canny_high)
        image_hc = high_contrast_overlay(
            edges, image, threshold=dark_threshold)
        art = convert_to_terminal_art(
            image_hc, scale=scale, invert_color=invert_color)

        # Draw
        self.ascii_text.delete("1.0", tk.END)
        self.ascii_text.insert(tk.END, art)
