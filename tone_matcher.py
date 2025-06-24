import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import numpy as np
import os

def match_histograms(source, reference):
    matched = np.zeros_like(source)
    for c in range(3):  # RGB channels
        src = source[:, :, c].flatten()
        ref = reference[:, :, c].flatten()

        s_values, bin_idx, s_counts = np.unique(src, return_inverse=True, return_counts=True)
        r_values, r_counts = np.unique(ref, return_counts=True)

        s_quantiles = np.cumsum(s_counts).astype(np.float64) / s_counts.sum()
        r_quantiles = np.cumsum(r_counts).astype(np.float64) / r_counts.sum()

        interp_r_values = np.interp(s_quantiles, r_quantiles, r_values)
        matched[:, :, c] = interp_r_values[bin_idx].reshape(source[:, :, c].shape)

    return np.clip(matched, 0, 1)

def select_reference():
    file_path = filedialog.askopenfilename()
    if file_path:
        reference_path.set(file_path)

def select_target():
    file_path = filedialog.askopenfilename()
    if file_path:
        target_path.set(file_path)

def select_output_folder():
    folder = filedialog.askdirectory()
    if folder:
        output_folder.set(folder)

def process_images():
    try:
        ref = Image.open(reference_path.get()).convert("RGB")
        tgt = Image.open(target_path.get()).convert("RGB")

        ref_arr = np.array(ref).astype(np.float32) / 255.0
        tgt_arr = np.array(tgt).astype(np.float32) / 255.0

        matched_arr = match_histograms(tgt_arr, ref_arr)
        matched_img = Image.fromarray((matched_arr * 255).astype(np.uint8))

        out_path = os.path.join(output_folder.get(), "matched_" + os.path.basename(target_path.get()))
        matched_img.save(out_path)
        messagebox.showinfo("Success", f"Saved to:\n{out_path}")

    except Exception as e:
        messagebox.showerror("Error", str(e))

# GUI setup
root = tk.Tk()
root.title("Texture Tone Matcher")
root.geometry("500x300")

reference_path = tk.StringVar()
target_path = tk.StringVar()
output_folder = tk.StringVar()

tk.Label(root, text="Reference Image:").pack(pady=5)
tk.Entry(root, textvariable=reference_path, width=60).pack()
tk.Button(root, text="Browse", command=select_reference).pack()

tk.Label(root, text="Target Image:").pack(pady=5)
tk.Entry(root, textvariable=target_path, width=60).pack()
tk.Button(root, text="Browse", command=select_target).pack()

tk.Label(root, text="Output Folder:").pack(pady=5)
tk.Entry(root, textvariable=output_folder, width=60).pack()
tk.Button(root, text="Browse", command=select_output_folder).pack()

tk.Button(root, text="Match Tone and Save", command=process_images, bg="gold", fg="black").pack(pady=20)

root.mainloop()
