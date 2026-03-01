import tkinter as tk
from tkinter import messagebox
import cv2
import numpy as np
import os
import random
import time
from datetime import datetime

NUM_PHOTOS = 4
COUNTDOWN = 3
STICKER_FOLDER = "stickers"

# ===== LOAD STICKERS =====
def load_stickers(folder):
    stickers = []
    for file in os.listdir(folder):
        if file.endswith(".png"):
            path = os.path.join(folder, file)
            img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if img is not None and img.shape[2] == 4:
                stickers.append(img)
    return stickers


# ===== ADD STICKER =====
def add_sticker(frame, sticker, x, y):
    h, w = sticker.shape[:2]
    if y + h > frame.shape[0] or x + w > frame.shape[1]:
        return frame
    alpha = sticker[:, :, 3:4] / 255.0
    frame[y:y+h, x:x+w] = (
        alpha * sticker[:, :, :3] +
        (1 - alpha) * frame[y:y+h, x:x+w]
    )
    return frame


# ===== COUNTDOWN =====
def smooth_countdown(cap, seconds, sticker=None):
    start_time = time.time()
    while True:
        ret, frame = cap.read()
        if not ret:
            return None
        elapsed = time.time() - start_time
        if elapsed >= seconds:
            return frame
        display = frame.copy()
        if sticker is not None:
            display = add_sticker(display, sticker, display.shape[1] - 170, display.shape[0] - 170)
        cv2.imshow("PhotoBooth", display)
        if cv2.waitKey(1) == 27:
            return None


# ===== CAPTURE SEQUENCE =====
def capture_sequence(cap, stickers, layout="1x4"):
    photos = []
    thumb_h, thumb_w = 120, 160
    blank_thumb = np.zeros((thumb_h, thumb_w, 3), dtype=np.uint8)

    for i in range(NUM_PHOTOS):
        sticker = random.choice(stickers)
        sticker_resized = cv2.resize(sticker, (150, 150))
        frame = smooth_countdown(cap, COUNTDOWN, sticker_resized)
        if frame is None:
            break
        frame = add_sticker(frame, sticker_resized, frame.shape[1] - 170, frame.shape[0] - 170)
        photos.append(frame)

        thumbs = [cv2.resize(p, (thumb_w, thumb_h)) for p in photos]
        if layout == "2x2":
            grid_rows = []
            for r in range(2):
                row_imgs = []
                for c in range(2):
                    idx = r * 2 + c
                    row_imgs.append(thumbs[idx] if idx < len(thumbs) else blank_thumb)
                grid_rows.append(np.hstack(row_imgs))
            preview = np.vstack(grid_rows)
        else:
            stacked = thumbs + [blank_thumb] * (NUM_PHOTOS - len(thumbs))
            preview = np.vstack(stacked)

        cv2.imshow("Preview", preview)
        cv2.imshow("PhotoBooth", frame)
        cv2.waitKey(300)

    if cv2.getWindowProperty("Preview", cv2.WND_PROP_VISIBLE) > 0:
        cv2.destroyWindow("Preview")
    return photos


# ===== BUILD STRIP =====
def build_strip(photos, layout="1x4"):
    # Resize photos to smaller size for output (400px width)
    max_width = 400
    h, w = photos[0].shape[:2]
    scale = max_width / w
    new_h = int(h * scale)
    new_w = max_width
    
    photos = [cv2.resize(p, (new_w, new_h)) for p in photos]

    if layout == "2x2":
        top = np.hstack((photos[0], photos[1]))
        bottom = np.hstack((photos[2], photos[3]))
        strip = np.vstack((top, bottom))
    else:
        strip = np.vstack(photos)

    border_size = 20
    strip = cv2.copyMakeBorder(
        strip, border_size, border_size, border_size, border_size,
        cv2.BORDER_CONSTANT, value=[255, 255, 255]
    )

    header_height = 80
    header = np.ones((header_height, strip.shape[1], 3), dtype=np.uint8) * 255
    cv2.putText(header, "PHOTOBOOTH 2026", (strip.shape[1] // 6, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)

    return np.vstack((header, strip))


class PhotoBoothApp:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  # hide main window
        
        self.cap = None
        self.stickers = []
        self.layout = "1x4"
        
        self.init_resources()
        self.create_modal()
    
    def init_resources(self):
        self.stickers = load_stickers(STICKER_FOLDER)
        if len(self.stickers) == 0:
            messagebox.showerror("Error", "No stickers found in folder!")
            self.root.destroy()
            return
        
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Cannot open camera!")
            self.root.destroy()
            return
    
    def create_modal(self):
        self.dlg = tk.Toplevel(self.root)
        self.dlg.title("📸 PhotoBooth App v2.0")
        self.dlg.geometry("400x580")
        self.dlg.configure(bg="#2c3e50")
        self.dlg.resizable(False, False)
        self.dlg.grab_set()
        self.dlg.protocol("WM_DELETE_WINDOW", self.quit_app)
        
        # Header
        header = tk.Frame(self.dlg, bg="#e74c3c", height=80)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)
        tk.Label(header, text="📸 PhotoBooth", font=("Arial", 24, "bold"), 
                bg="#e74c3c", fg="white").pack(pady=15)
        
        # Content
        content = tk.Frame(self.dlg, bg="#2c3e50")
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Layout section
        layout_frame = tk.LabelFrame(content, text="Layout", font=("Arial", 11, "bold"),
                                     bg="#34495e", fg="white", padx=15, pady=15)
        layout_frame.pack(fill=tk.X, pady=10)
        
        self.layout_var = tk.StringVar(value="1x4")
        
        tk.Radiobutton(layout_frame, text="📋 1 × 4 Vertical", 
                      variable=self.layout_var, value="1x4",
                      font=("Arial", 10), bg="#34495e", fg="white",
                      activebackground="#34495e", activeforeground="#e74c3c",
                      selectcolor="#34495e").pack(anchor="w", pady=8)
        
        tk.Radiobutton(layout_frame, text="🔲 2 × 2 Square",
                      variable=self.layout_var, value="2x2",
                      font=("Arial", 10), bg="#34495e", fg="white",
                      activebackground="#34495e", activeforeground="#e74c3c",
                      selectcolor="#34495e").pack(anchor="w", pady=8)
        
        # Status section
        status_frame = tk.LabelFrame(content, text="Status", font=("Arial", 11, "bold"),
                                    bg="#34495e", fg="white", padx=15, pady=15)
        status_frame.pack(fill=tk.X, pady=10)
        
        self.status_label = tk.Label(status_frame, text="🟢 Ready to capture", 
                                     font=("Arial", 10), bg="#34495e", fg="#2ecc71",
                                     wraplength=300, justify="left")
        self.status_label.pack(anchor="w", pady=5)
        
        # Info section
        info_frame = tk.Frame(content, bg="#34495e", relief=tk.FLAT, bd=1)
        info_frame.pack(fill=tk.X, pady=10, padx=5)
        tk.Label(info_frame, text="💡 Press Start Capture to begin\nSelect layout above, save or retake after capture",
                font=("Arial", 8), bg="#34495e", fg="#bdc3c7",
                justify="left").pack(anchor="w", padx=10, pady=5)
        
        # Controls
        button_frame = tk.Frame(content, bg="#2c3e50")
        button_frame.pack(fill=tk.X, pady=20)
        
        self.start_btn = tk.Button(button_frame, text="🚀 Start Capture", 
                                   command=self.start_capture,
                                   font=("Arial", 11, "bold"), bg="#e74c3c", fg="white",
                                   padx=15, pady=10, relief=tk.RAISED, cursor="hand2")
        self.start_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        quit_btn = tk.Button(button_frame, text="❌ Quit",
                            command=self.quit_app,
                            font=("Arial", 10), bg="#95a5a6", fg="white",
                            padx=10, pady=8, relief=tk.RAISED, cursor="hand2")
        quit_btn.pack(side=tk.RIGHT, padx=5)
        
        # Footer
        footer = tk.Frame(self.dlg, bg="#1a252f", height=30)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        tk.Label(footer, text="💾 Photos saved in: output/", font=("Arial", 8),
                bg="#1a252f", fg="#bdc3c7").pack(pady=5)
    
    def update_status(self, msg, color="#2ecc71"):
        self.status_label.config(text=msg, fg=color)
        self.root.update_idletasks()
    
    def start_capture(self):
        self.start_btn.config(state=tk.DISABLED)
        self.layout = self.layout_var.get()
        self.update_status("⏳ Capturing photos...", "#f39c12")
        self.dlg.update_idletasks()
        
        try:
            photos = capture_sequence(self.cap, self.stickers, self.layout)
            
            if len(photos) != NUM_PHOTOS:
                self.update_status("❌ Capture cancelled", "#e74c3c")
                self.start_btn.config(state=tk.NORMAL)
                return
            
            final_image = build_strip(photos, self.layout)
            cv2.imshow("PhotoBooth Result", final_image)
            
            result = messagebox.askyesnocancel("Save Photo",
                                              "Do you want to save this photo?\n\nYes: Save\nNo: Retake\nCancel: Discard")
            
            if result is True:
                os.makedirs("output", exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"output/photobooth_{timestamp}.jpg"
                cv2.imwrite(filename, final_image)
                self.update_status(f"✅ Saved to output/", "#2ecc71")
            elif result is False:
                cv2.destroyWindow("PhotoBooth Result")
                self.update_status("🔄 Retaking...", "#f39c12")
                self.start_capture()
                return
            else:
                self.update_status("⏹️ Discarded", "#e74c3c")
            
            cv2.destroyWindow("PhotoBooth Result")
        
        except Exception as e:
            self.update_status(f"❌ Error: {str(e)}", "#e74c3c")
            messagebox.showerror("Error", str(e))
        
        finally:
            self.start_btn.config(state=tk.NORMAL)
    
    def quit_app(self):
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        self.root.destroy()


if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    root = tk.Tk()
    app = PhotoBoothApp(root)
    root.mainloop()
