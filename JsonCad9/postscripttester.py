import tkinter as tk
import subprocess
import os

# --- Drawing parameters ---
canvas_width, canvas_height = 1200, 800

# --- 1. Draw your content on a Tkinter Canvas ---
root = tk.Tk()
root.title("Tkinter Canvas PDF Export Example")
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="white")
canvas.pack()

# <--- Example vector drawing --->
canvas.create_rectangle(100, 100, 1100, 700, outline='black', width=5)
canvas.create_line(100, 700, 1100, 100, fill='blue', width=8)
canvas.create_oval(400, 200, 800, 600, outline="red", width=7)
canvas.create_text(600, 400, text="True Vector PDF Export", font=("Arial", 40), fill="forest green")
# <---- Add your own lines, shapes, and text as needed ---->

root.update()  # Ensure the canvas is rendered

# --- 2. Export to PostScript (true vector) ---
ps_file = "drawing_output.ps"
canvas.postscript(
    file=ps_file,
    colormode='color',
    x=0, y=0,
    width=canvas_width,
    height=canvas_height,
    pagewidth=canvas_width,
    pageheight=canvas_height
)
print(f"Exported PostScript vector file as {ps_file}")

# --- 3. Convert PostScript to PDF (true vector) ---
pdf_file = "drawing_output.pdf"
# ps2pdf is likely the easiest; add Ghostscript to PATH if needed
try:
    result = subprocess.run(["ps2pdf", ps_file, pdf_file], check=True)
    print(f"Vector PDF written as {pdf_file}")
    # Optionally, remove the temporary .ps file
    os.remove(ps_file)
except Exception as e:
    print("Could not convert to PDF automatically. Run this command manually:")
    print(f"ps2pdf {ps_file} {pdf_file}")
    print(f"Error: {e}")

root.mainloop()
