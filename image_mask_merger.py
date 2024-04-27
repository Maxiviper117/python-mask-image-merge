import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import threading
import json
from functools import partial

class ImageMaskMergerApp:
    def __init__(self, root):
        self.root = root
        root.title('Image Mask Merger Tool')

        # Set the initial window size and enable resizing
        root.geometry("800x600")
        root.resizable(True, True)

        # Configure resizing behavior for rows and columns
        root.grid_rowconfigure(4, weight=1)  # Row containing the log_console
        root.grid_columnconfigure(0, weight=1)  # First column containing the log_console

        # Labels and Entry widgets for directories
        tk.Label(root, text="Image Directory:").grid(row=0, column=0)
        self.image_dir = tk.Entry(root, width=50)
        self.image_dir.grid(row=0, column=1)
        tk.Button(root, text="Browse", command=self.browse_image_dir).grid(row=0, column=2)
        self.image_dir.bind('<KeyRelease>', partial(self.save_input_values, entry=self.image_dir))

        tk.Label(root, text="Mask Directory:").grid(row=1, column=0)
        self.mask_dir = tk.Entry(root, width=50)
        self.mask_dir.grid(row=1, column=1)
        tk.Button(root, text="Browse", command=self.browse_mask_dir).grid(row=1, column=2)
        self.mask_dir.bind('<KeyRelease>', partial(self.save_input_values, entry=self.mask_dir))

        tk.Label(root, text="Output Directory:").grid(row=2, column=0)
        self.output_dir = tk.Entry(root, width=50)
        self.output_dir.grid(row=2, column=1)
        tk.Button(root, text="Browse", command=self.browse_output_dir).grid(row=2, column=2)
        self.output_dir.bind('<KeyRelease>', partial(self.save_input_values, entry=self.output_dir))

        # Button to start processing
        tk.Button(root, text="Merge Images and Masks", command=self.process_images).grid(row=3, column=1)

        # Stop button
        tk.Button(root, text="Stop Processing", command=self.stop_processing).grid(row=3, column=2)

        # Text widget for logging
        self.log_console = tk.Text(root, height=10, width=75)
        self.log_console.grid(row=4, column=0, columnspan=3, sticky="nsew")  # Make the console fill the entire row/column
        self.log_console.config(state='disabled')

        # Thread management
        self.process_thread = None
        self.stop_event = threading.Event()

        # Load input values from file
        self.load_input_values()

        # Save input values on window close
        root.protocol("WM_DELETE_WINDOW", self.on_window_close)

        # Debounce timer
        self.debounce_timer = None

        # Configure resizing behavior for the log_console
        root.grid_rowconfigure(4, weight=1)
        root.grid_columnconfigure(0, weight=1)


    def log_message(self, message):
        self.log_console.config(state='normal')
        self.log_console.insert(tk.END, message + "\n")
        self.log_console.config(state='disabled')
        self.log_console.see(tk.END)
        self.root.update_idletasks()  # Update the GUI to show the message immediately

    def browse_image_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.image_dir.delete(0, tk.END)
            self.image_dir.insert(0, directory)
            self.save_settings()  # Save settings after selecting a directory

    def browse_mask_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.mask_dir.delete(0, tk.END)
            self.mask_dir.insert(0, directory)
            self.save_settings()  # Save settings after selecting a directory

    def browse_output_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir.delete(0, tk.END)
            self.output_dir.insert(0, directory)
            self.save_settings()  # Save settings after selecting a directory

    def process_images(self):
        if self.process_thread is not None and self.process_thread.is_alive():
            messagebox.showwarning("Process Running", "Please wait or stop the current process before starting a new one.")
            return

        self.stop_event.clear()
        self.process_thread = threading.Thread(target=self.run_processing)
        self.process_thread.start()

    def run_processing(self):
        image_dir = self.image_dir.get()
        mask_dir = self.mask_dir.get()
        output_dir = self.output_dir.get()

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        images = [f for f in os.listdir(image_dir) if f.endswith('.JPG')]

        for image_name in images:
            if self.stop_event.is_set():
                self.log_message("Processing was stopped by user.")
                break

            image_path = os.path.join(image_dir, image_name)
            mask_name = image_name + '.mask.png'
            mask_path = os.path.join(mask_dir, mask_name)

            image = cv2.imread(image_path)
            mask = cv2.imread(mask_path, 0)

            if image is None or mask is None:
                self.log_message(f"Error loading {image_name}. Skipping.")
                continue

            if image.shape[:2] != mask.shape:
                self.log_message(f"Skipping {image_name} due to mismatch in dimensions.")
                continue

            binary_mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)[1]
            black_background = np.zeros_like(image)
            result = np.where(binary_mask[:, :, np.newaxis] == 255, image, black_background)

            result_path = os.path.join(output_dir, f'{os.path.splitext(image_name)[0]}_black_background.png')
            cv2.imwrite(result_path, result)
            self.log_message(f"Processed and saved: {result_path}")

        if not self.stop_event.is_set():
            self.log_message("All images have been successfully merged and saved.")


    def stop_processing(self):
        if self.process_thread is not None and self.process_thread.is_alive():
            self.stop_event.set()
            self.process_thread.join()
            self.log_message("Stopped processing at user's request.")
        
        self.root.after(100, self.root.destroy)  # Schedule the window to be destroyed




    def save_input_values(self, event=None, entry=None):
        if self.debounce_timer is not None:
            self.root.after_cancel(self.debounce_timer)

        self.debounce_timer = self.root.after(2000, self.save_settings)

    def save_settings(self):
        settings = {
            "image_dir": self.image_dir.get(),
            "mask_dir": self.mask_dir.get(),
            "output_dir": self.output_dir.get(),
        }
        with open("settings.json", "w") as file:
            json.dump(settings, file)

    def load_input_values(self):
        try:
            with open("settings.json", "r") as file:
                settings = json.load(file)
                self.image_dir.delete(0, tk.END)
                self.image_dir.insert(0, settings.get("image_dir", ""))
                self.mask_dir.delete(0, tk.END)
                self.mask_dir.insert(0, settings.get("mask_dir", ""))
                self.output_dir.delete(0, tk.END)
                self.output_dir.insert(0, settings.get("output_dir", ""))
        except FileNotFoundError:
            pass

    def on_window_close(self):
        self.save_settings()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageMaskMergerApp(root)
    root.mainloop()