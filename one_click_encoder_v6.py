import os
import subprocess
import threading
import re
from tkinter import Tk, Label, Button, filedialog, ttk, StringVar, messagebox

SUPPORTED = (".mp4", ".mov", ".mkv", ".avi", ".m4v", ".flv", ".wmv", ".webm")

class EncoderApp:
    def __init__(self, root):
        self.root = root
        root.title("One-Click Video Encoder")
        root.geometry("500x620")
        root.minsize(450, 580)

        self.input_folder = ""
        self.output_folder = ""
        self.abort_flag = False
        self.current_process = None

        self.status = StringVar(value="Select folders to begin")
        self.resolution_choice = StringVar(value="1080")

        # Title
        Label(root, text="One-Click Video Encoder", font=("Arial", 16, "bold")).pack(pady=15)
        
        # Instructions
        Label(root, text="Simple video re-encoder for TV/Computer playback", 
              font=("Arial", 9)).pack(pady=5)
        
        # Status
        Label(root, textvariable=self.status, wraplength=400, fg="blue").pack(pady=5)

        # Folder selection
        Button(root, text="Select Input Folder (Videos to Encode)", 
               command=self.select_input, width=35, height=2, bg="#4CAF50", fg="white",
               font=("Arial", 10, "bold")).pack(pady=5)
        
        Button(root, text="Select Output Folder (Where to Save)", 
               command=self.select_output, width=35, height=2, bg="#2196F3", fg="white",
               font=("Arial", 10, "bold")).pack(pady=5)

        # Resolution selection
        Label(root, text="Maximum Resolution:", font=("Arial", 10)).pack(pady=(10, 0))
        ttk.Combobox(
            root,
            textvariable=self.resolution_choice,
            values=["1080", "720"],
            state="readonly",
            width=10,
            font=("Arial", 10)
        ).pack(pady=5)

        # Current file progress
        Label(root, text="Current File Progress", font=("Arial", 9)).pack(pady=(10, 0))
        self.file_progress = ttk.Progressbar(root, length=350, mode='determinate')
        self.file_progress.pack()
        self.file_percent = Label(root, text="0%", font=("Arial", 9))
        self.file_percent.pack()

        # Overall progress
        Label(root, text="Overall Progress", font=("Arial", 9)).pack(pady=(10, 0))
        self.total_progress = ttk.Progressbar(root, length=350, mode='determinate')
        self.total_progress.pack()
        self.total_percent = Label(root, text="0%", font=("Arial", 9))
        self.total_percent.pack()

        # Action buttons
        Button(root, text="START ENCODING", command=self.start, width=20, height=2,
               bg="#FF9800", fg="white", font=("Arial", 12, "bold")).pack(pady=10)
        
        Button(root, text="STOP", command=self.abort, width=15,
               fg="white", bg="red", font=("Arial", 10, "bold")).pack(pady=5)

    def select_input(self):
        folder = filedialog.askdirectory(title="Select Input Folder with Videos")
        if folder:
            self.input_folder = folder
            self.status.set(f"Input: {os.path.basename(folder)}")

    def select_output(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder = folder
            self.status.set(f"Output: {os.path.basename(folder)}")

    def abort(self):
        self.abort_flag = True
        if self.current_process:
            try:
                self.current_process.terminate()
            except:
                pass
        self.status.set("Stopping...")

    def get_video_info(self, filepath):
        """Get video dimensions and duration"""
        try:
            cmd = [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height,duration",
                "-of", "csv=p=0",
                filepath
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return None, None, None
            
            output = result.stdout.strip()
            parts = output.split(',')
            
            if len(parts) >= 3:
                width = int(parts[0])
                height = int(parts[1])
                duration = float(parts[2]) if parts[2] else 0
                return width, height, duration
            
            return None, None, None
        except Exception as e:
            print(f"Error getting video info: {e}")
            return None, None, None

    def calculate_scale(self, width, height):
        """Calculate target dimensions - maintains aspect ratio"""
        max_res = int(self.resolution_choice.get())
        
        # If video is already small enough, keep original size
        if height <= max_res and width <= max_res:
            return width, height
        
        # Calculate scaling based on longest dimension
        if width >= height:  # Landscape or square
            if height > max_res:
                # Scale down to max resolution
                scale_factor = max_res / height
                new_height = max_res
                new_width = int(width * scale_factor)
                # Make sure width is even (required by some codecs)
                new_width = new_width if new_width % 2 == 0 else new_width - 1
                new_height = new_height if new_height % 2 == 0 else new_height - 1
                return new_width, new_height
            else:
                return width, height
        else:  # Portrait
            if width > max_res:
                # Scale down to max resolution
                scale_factor = max_res / width
                new_width = max_res
                new_height = int(height * scale_factor)
                # Make sure dimensions are even
                new_width = new_width if new_width % 2 == 0 else new_width - 1
                new_height = new_height if new_height % 2 == 0 else new_height - 1
                return new_width, new_height
            else:
                return width, height

    def encode(self, input_path, output_path):
        """Encode video with progress tracking"""
        width, height, duration = self.get_video_info(input_path)
        
        if width is None or height is None:
            # If we can't get video info, try encoding anyway with no scaling
            print(f"Could not get video info for {input_path}, encoding without scaling")
            duration = 0
            target_w, target_h = None, None
        else:
            target_w, target_h = self.calculate_scale(width, height)

        # Build ffmpeg command
        cmd = ["ffmpeg", "-y", "-i", input_path]

        # Add scaling if needed and dimensions are known
        if target_w and target_h:
            cmd += ["-vf", f"scale={target_w}:{target_h}"]

        # Video codec settings - compatible with most devices
        cmd += [
            "-c:v", "libx264",      # H.264 video codec (universal compatibility)
            "-preset", "medium",     # Good balance of speed and quality
            "-crf", "23",            # Quality setting (18-28 is good, 23 is default)
            "-profile:v", "high",    # H.264 profile
            "-level", "4.1",         # H.264 level (compatible with most devices)
            "-pix_fmt", "yuv420p",   # Pixel format for compatibility
            "-c:a", "aac",           # AAC audio codec
            "-b:a", "128k",          # Audio bitrate
            "-movflags", "+faststart",  # Enable streaming
            output_path
        ]

        try:
            self.current_process = subprocess.Popen(
                cmd,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True
            )

            time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.?\d*)")

            for line in self.current_process.stderr:
                if self.abort_flag:
                    break

                match = time_pattern.search(line)
                if match and duration > 0:
                    h, m, s = map(float, match.groups())
                    current_time = h * 3600 + m * 60 + s
                    percent = min(100, (current_time / duration) * 100)

                    self.file_progress["value"] = percent
                    self.file_percent.config(text=f"{percent:.0f}%")
                    self.root.update_idletasks()

            self.current_process.wait()
            
            # Check if output file was created successfully
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                success = True
            else:
                success = False
                
        except Exception as e:
            print(f"Error encoding {input_path}: {e}")
            success = False
        finally:
            self.file_progress["value"] = 0
            self.file_percent.config(text="0%")
            self.current_process = None
        
        return success

    def start(self):
        if not self.input_folder or not self.output_folder:
            messagebox.showwarning("Missing Folders", 
                                 "Please select both input and output folders!")
            return

        # Check if ffmpeg is available
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        except:
            messagebox.showerror("FFmpeg Not Found", 
                               "FFmpeg is not installed or not in system PATH.\n\n"
                               "Please install FFmpeg to use this program.\n"
                               "Download from: https://ffmpeg.org/download.html")
            return

        self.abort_flag = False
        threading.Thread(target=self.process, daemon=True).start()

    def process(self):
        """Main processing loop"""
        files = [
            f for f in os.listdir(self.input_folder)
            if f.lower().endswith(SUPPORTED)
        ]
        
        total = len(files)

        if total == 0:
            self.status.set("No video files found in input folder!")
            messagebox.showinfo("No Videos Found", 
                              f"No supported video files found.\n\n"
                              f"Supported formats: {', '.join(SUPPORTED)}")
            return

        self.total_progress["maximum"] = total
        successful = 0
        failed = 0

        for i, file in enumerate(files, 1):
            if self.abort_flag:
                break

            inp = os.path.join(self.input_folder, file)
            # Always output as .mp4 for maximum compatibility
            out = os.path.join(
                self.output_folder,
                os.path.splitext(file)[0] + "_encoded.mp4"
            )

            self.status.set(f"Encoding {i}/{total}: {file}")
            
            success = self.encode(inp, out)
            
            if success:
                successful += 1
            else:
                failed += 1

            self.total_progress["value"] = i
            total_pct = (i / total) * 100
            self.total_percent.config(text=f"{total_pct:.0f}%")
            self.root.update_idletasks()

        # Final status
        if self.abort_flag:
            self.status.set("Stopped by user.")
            messagebox.showinfo("Stopped", f"Encoding stopped.\n\n"
                                         f"Completed: {successful}\nFailed: {failed}")
        else:
            self.status.set(f"Complete! {successful} videos encoded.")
            messagebox.showinfo("Complete!", 
                              f"All videos processed!\n\n"
                              f"Successfully encoded: {successful}\n"
                              f"Failed: {failed}\n\n"
                              f"Output folder: {self.output_folder}")


if __name__ == "__main__":
    root = Tk()
    app = EncoderApp(root)
    root.mainloop()
