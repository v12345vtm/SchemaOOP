import tkinter as tk
from components import *
from example_tree import te_tekenen_startpunt



import tkinter as tk

def draw_grid_with_objects(root_component):
    # 1. Verzamel alle nodes en bepaal grid-afmetingen
    all_nodes = []
    def collect(node):
        all_nodes.append(node)
        for child in node.children:
            collect(child)
    collect(root_component)
    max_x = max(node.grid_x for node in all_nodes)
    max_y = max(node.grid_y for node in all_nodes)

    # 2. Maak hoofdvenster en canvas met scrollbars
    root = tk.Tk()
    root.title("Scrollable Grid of Components")

    # Canvas + scrollbars
    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(frame, bg="white")
    hbar = tk.Scrollbar(frame, orient="horizontal", command=canvas.xview)
    vbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)

    hbar.pack(side="bottom", fill="x")
    vbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # 3. Frame in canvas voor grid
    grid_frame = tk.Frame(canvas, bg="white")
    canvas.create_window((0, 0), window=grid_frame, anchor="nw")

    # 4. Vul grid met lege cellen
    cell_size = 120
    for y in range(max_y + 1):
        for x in range(max_x + 1):
            cell = tk.Label(grid_frame, text="", width=14, height=4, borderwidth=1, relief="solid", bg="#f8f8f8")
            cell.grid(row=y, column=x, sticky="nsew")

    # 5. Zet objecten in de juiste cellen
    for node in all_nodes:
        info = f"{node.label}\n({node.grid_x},{node.grid_y})"
        if hasattr(node, "_regel_used"):
            info += f"\n{node._regel_used}"
        lbl = tk.Label(grid_frame, text=info, width=14, height=4, borderwidth=2, relief="groove", bg="#ffe0e0")
        lbl.grid(row=node.grid_y, column=node.grid_x, sticky="nsew")

    # 6. Zorg dat cellen zich uitrekken
    for x in range(max_x + 1):
        grid_frame.grid_columnconfigure(x, weight=1)
    for y in range(max_y + 1):
        grid_frame.grid_rowconfigure(y, weight=1)

    # 7. Scrollregion instellen
    grid_frame.update_idletasks()
    bbox = canvas.bbox("all")
    canvas.config(scrollregion=bbox, width=min(900, (max_x+1)*cell_size), height=min(700, (max_y+1)*cell_size))

    root.mainloop()



if __name__ == "__main__":
    te_tekenen_startpunt.sort_children()
    te_tekenen_startpunt.assign_coordinates_by_rules()
    te_tekenen_startpunt.print_ascii_tree_with_regel()


    draw_grid_with_objects(te_tekenen_startpunt)