import tkinter as tk
from components import *
from example_tree import te_tekenen_startpunt

def get_max_coords(component, max_x=[0], max_y=[0]):
    if component.x > max_x[0]:
        max_x[0] = component.x
    if component.y > max_y[0]:
        max_y[0] = component.y
    for child in component.children:
        get_max_coords(child, max_x, max_y)

def draw_tree(canvas, component, canvas_height, x_spacing=60, y_spacing=60):
    size = component.boundarybox
    x = component.x * x_spacing + 30
    y = canvas_height - (component.y * y_spacing + 30)
    canvas.create_rectangle(x, y - size, x + size, y, fill="white", outline="black")
    canvas.create_text(x + size / 2, y - size / 2, text=component.label, font=("Arial", 8))
    for child in component.children:
        child_x = child.x * x_spacing + 30 + size / 2
        child_y = canvas_height - (child.y * y_spacing + 30) - size / 2
        canvas.create_line(x + size / 2, y - size / 2, child_x, child_y, fill="black")
        draw_tree(canvas, child, canvas_height, x_spacing, y_spacing)

def draw_grid(canvas, width, height, x_spacing, y_spacing, font=("Arial", 8)):
    cols = width // x_spacing
    rows = height // y_spacing
    for col in range(cols + 1):
        x = col * x_spacing
        canvas.create_line(x, 0, x, height, fill="red")
    for row in range(rows + 1):
        y = row * y_spacing
        canvas.create_line(0, y, width, y, fill="red")
    for col in range(cols):
        for row in range(rows):
            center_x = col * x_spacing + x_spacing // 2
            center_y = row * y_spacing + y_spacing // 2
            canvas.create_text(center_x, center_y, text=f"({col},{rows - row - 1})", fill="red", font=font)

if __name__ == "__main__":
    te_tekenen_startpunt.sort_children()
    Component.assign_coords_safe_stacking(te_tekenen_startpunt)
    te_tekenen_startpunt.limit_hoogte(hoogtelimiet=6)
    te_tekenen_startpunt.print_ascii_tree()


    # Get the max x, y from the component tree
    max_x = [0]
    max_y = [0]
    get_max_coords(te_tekenen_startpunt, max_x, max_y)

    # Define maximum allowed window size
    MAX_WIDTH = 1000
    MAX_HEIGHT = 800

    # Calculate required spacing
    padding = 2  # extra columns/rows of spacing
    natural_width = (max_x[0] + padding) * 80
    natural_height = (max_y[0] + padding) * 80

    # Compute scaling factor
    scale_x = MAX_WIDTH / natural_width
    scale_y = MAX_HEIGHT / natural_height
    scale = min(1.0, scale_x, scale_y)  # never upscale, only shrink if needed

    # Apply scaling
    x_spacing = int(80 * scale)
    y_spacing = int(80 * scale)
    width = (max_x[0] + padding) * x_spacing
    height = (max_y[0] + padding) * y_spacing

    root = tk.Tk()
    root.title("Component Tree (scaled to fit window)")
    canvas = tk.Canvas(root, width=width, height=height, bg="white")
    canvas.pack()

    draw_grid(canvas, width, height, x_spacing, y_spacing)
    draw_tree(canvas, te_tekenen_startpunt, height, x_spacing, y_spacing)

    root.mainloop()
