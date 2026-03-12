import os
import subprocess
import threading
from tkinter import Tk, Label, Button, filedialog, ttk, StringVar

SUPPORTED = (".mp4", ".mov", ".mkv", ".avi", ".m4v")

class EncoderApp:
    def __init__(self, root):
        self.root = root
        root.title("One-Click Video Encoder")

        self.input_folder = ""
        self.output_folder = ""

        self.status = StringVar(value="Drop a folder or select one")

        Label(root, text="One-Click Video Encoder", font=("Arial", 14)).pack(pady=10)
        Label(root, textvariable=self.status).pack()

        Button(root, text="Select Input Folder", command=self.select_input).pack(pady=5)
        Button(root, text="Select Output Folder", command=self.select_output).pack(pady=5)

        self.progress = ttk.Progressbar(root, length=300)
        self.progress.pack(pady=10)

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
            "-show_entries", "stream=width,height",
            "-of", "csv=p=0", filepath
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        width, height = map(int, result.stdout.strip().split(","))
        return width, height

    def encode(self, input_path, output_path):
        width, height = self.get_resolution(input_path)

        # Decide orientation
        if width >= height:
            target = "1920:1080"
        else:
            target = "1080:1920"

        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vf", f"scale={target}:force_original_aspect_ratio=decrease,"
                   f"pad={target}:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac",
            output_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

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

        self.progress["maximum"] = total

        for i, file in enumerate(files, 1):
            inp = os.path.join(self.input_folder, file)
            out = os.path.join(self.output_folder, os.path.splitext(file)[0] + ".mp4")

            self.status.set(f"Encoding: {file}")
            self.encode(inp, out)
            self.progress["value"] = i

        self.status.set("Done!")

if __name__ == "__main__":
    root = Tk()
    app = EncoderApp(root)
    root.mainloop()
