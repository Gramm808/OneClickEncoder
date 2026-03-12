import os
import subprocess
import threading
import re
from tkinter import Tk, Label, Button, filedialog, ttk, StringVar

SUPPORTED = (".mp4", ".mov", ".mkv", ".avi", ".m4v")

class EncoderApp:
    def __init__(self, root):
        self.root = root
        root.title("One-Click Video Encoder")

        self.input_folder = ""
        self.output_folder = ""

        self.status = StringVar(value="Select folders to begin")
        self.resolution_choice = StringVar(value="1080")

        Label(root, text="One-Click Video Encoder", font=("Arial", 14)).pack(pady=10)
        Label(root, textvariable=self.status).pack()

        Button(root, text="Select Input Folder", command=self.select_input).pack(pady=5)
        Button(root, text="Select Output Folder", command=self.select_output).pack(pady=5)

        # Resolution dropdown
        Label(root, text="Max Resolution:").pack()
        ttk.Combobox(root, textvariable=self.resolution_choice,
                     values=["1080", "720"], state="readonly").pack(pady=5)

        # Current file progress
        Label(root, text="Current File Progress").pack()
        self.file_progress = ttk.Progressbar(root, length=300)
        self.file_progress.pack()
        self.file_percent = Label(root, text="0%")
        self.file_percent.pack()

        # Overall progress
        Label(root, text="Overall Progress").pack(pady=(10,0))
        self.total_progress = ttk.Progressbar(root, length=300)
        self.total_progress.pack()
        self.total_percent = Label(root, text="0%")
        self.total_percent.pack()

        Button(root, text="GO", command=self.start).pack(pady=10)

    def select_input(self):
        self.input_folder = filedialog.askdirectory()
        self.status.set(f"Input: {self.input_folder}")

    def select_output(self):
        self.output_folder = filedialog.askdirectory()
        self.status.set(f"Output: {self.output_folder}")

    def get_resolution(self, filepath):
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,duration",
            "-of", "default=noprint_wrappers=1:nokey=1", filepath
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        width, height, duration = result.stdout.strip().split("\n")
        return int(width), int(height), float(duration)

    def calculate_scale(self, width, height):
        max_res = int(self.resolution_choice.get())

        # Determine orientation
        if width >= height:
            target_w, target_h = max_res, int(max_res * 9 / 16)
        else:
            target_w, target_h = int(max_res * 9 / 16), max_res

        # Prevent upscaling
        target_w = min(target_w, width)
        target_h = min(target_h, height)

        return target_w, target_h

    def encode(self, input_path, output_path):
        width, height, duration = self.get_resolution(input_path)
        target_w, target_h = self.calculate_scale(width, height)

        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vf", f"scale={target_w}:{target_h}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac",
            output_path
        ]

        process = subprocess.Popen(cmd, stderr=subprocess.PIPE, text=True)

        time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")

        for line in process.stderr:
            match = time_pattern.search(line)
            if match:
                h, m, s = map(float, match.groups())
                current_time = h*3600 + m*60 + s
                percent = min(100, (current_time / duration) * 100)

                self.file_progress["value"] = percent
                self.file_percent.config(text=f"{percent:.1f}%")
                self.root.update_idletasks()

        process.wait()
        self.file_progress["value"] = 0
        self.file_percent.config(text="0%")

    def start(self):
        if not self.input_folder or not self.output_folder:
            self.status.set("Select both folders first")
            return
        threading.Thread(target=self.process).start()

    def process(self):
        files = [f for f in os.listdir(self.input_folder) if f.lower().endswith(SUPPORTED)]
        total = len(files)

        if total == 0:
            self.status.set("No videos found")
            return

        self.total_progress["maximum"] = total

        for i, file in enumerate(files, 1):
            inp = os.path.join(self.input_folder, file)
            out = os.path.join(self.output_folder, os.path.splitext(file)[0] + ".mp4")

            self.status.set(f"Encoding: {file}")
            self.encode(inp, out)

            self.total_progress["value"] = i
            total_pct = (i / total) * 100
            self.total_percent.config(text=f"{total_pct:.1f}%")
            self.root.update_idletasks()

        self.status.set("Done!")
