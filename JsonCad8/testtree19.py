import tkinter as tk
import re
import copy


class Component:
    def __init__(self, label, type, **kwargs):
        self.pixels_tussen_kringen_H = 40 #tussen verschikkende zekeringen horizontaal
        self.pixels_tussen_takken_V = 40 #tussen de lampenen onderling vertikaal
        self.label = label
        self.type = type
        self.children = []
        self.parent = None
        self.x = 0
        self.y = 0
        self._stroomrichting = None  # "horizontal" or "vertical"
        self.boundarybox = 50  # Default size, can be parameterized
        self.nulpunt = "top_left" # #top_left of bottom_left
        self.kwargs = kwargs  # Store all extra arguments in a dict
        # Optionally extract common expected values
        self.volgorde = kwargs.get("volgorde", None)

    def swapy(self):
        """
        Set nulpunt to 'bottom_left' and flip the y coordinate
        for this node and all children, so the grid is drawn
        with (0,0) at the bottom left.
        """
        # 1. Gather all nodes to find max_y
        all_nodes = []

        def collect(node):
            all_nodes.append(node)
            for child in node.children:
                collect(child)

        collect(self)
        max_y = max(node.grid_y for node in all_nodes)

        # 2. Recursively set nulpunt and flip y for all nodes
        def flip_nulpunt_and_y(node):
            node.nulpunt = "bottom_left"
            node.grid_y = max_y - node.grid_y
            for child in node.children:
                flip_nulpunt_and_y(child)

        flip_nulpunt_and_y(self)

    def print_ascii_tree_with_regel(self, prefix=" "):
        regel = getattr(self, "_regel_used", "?")
        print(f"{prefix}{self.label} ({self.x},{self.y})\t\t{regel}")
        for i, child in enumerate(self.children):
            connector = "└── " if i == len(self.children) - 1 else "├── "
            child_prefix = prefix + ("    " if i == len(self.children) - 1 else "│   ")
            print(f"{prefix}{connector}", end="")
            child.print_ascii_tree_with_regel(child_prefix)

    def assign_coordinates_by_rules(self):
        """
        Wijs coördinaten toe aan alle nodes volgens de aangepaste regels.
        Annotatie: node._regel_used (string).
        """


        def deepest_descendant_x(node):
            """Grootste x in de subboom."""
            xs = [node.grid_x]
            for child in node.children:
                xs.append(deepest_descendant_x(child))
            return max(xs)

        def deepest_descendant_y(node):
            """Grootste y in de subboom."""
            ys = [node.grid_y]
            for child in node.children:
                ys.append(deepest_descendant_y(child))
            return max(ys)

        def visit(node, parent=None, prev_sibling=None):
            # Regel 1: root
            if parent is None:
                node.grid_x, node.grid_y = 0, 0
                node._regel_used = "regel 1"
            else:
                pdir = parent.stroomrichting
                ndir = node.stroomrichting

                # vorige broer info
                if prev_sibling is not None:
                    prev_x = prev_sibling.grid_x
                    prev_y = prev_sibling.grid_y
                    prev_far_x = deepest_descendant_x(prev_sibling)
                    prev_far_y = deepest_descendant_y(prev_sibling)
                else:
                    prev_x = prev_y = prev_far_x = prev_far_y = None

                # Regel 2: V kind met V ouder
                if pdir == "vertical" and ndir == "vertical":
                    if prev_sibling:
                        # regel 2a
                        node.grid_x = prev_far_x + 1
                        node.grid_y = prev_y
                        node._regel_used = "regel 2a"
                    else:
                        # regel 2b
                        node.grid_x = parent.grid_x
                        node.grid_y = parent.grid_y + 1
                        node._regel_used = "regel 2b"

                # Regel 3: H kind met V ouder
                elif pdir == "vertical" and ndir == "horizontal":
                    if prev_sibling:
                        # regel 3a
                        node.grid_x = prev_x
                        node.grid_y = prev_far_y + 1  # aangepaste regel!
                        node._regel_used = "regel 3a"
                    else:
                        # regel 3b
                        node.grid_x = parent.grid_x + 1
                        node.grid_y = parent.grid_y + 1
                        node._regel_used = "regel 3b"

                # Regel 4: H kind met H ouder
                elif pdir == "horizontal" and ndir == "horizontal":
                    if prev_sibling:
                        # regel 4a
                        node.grid_x = prev_x
                        node.grid_y = prev_y + 1
                        node._regel_used = "regel 4a"
                    else:
                        # regel 4b
                        node.grid_x = parent.grid_x + 1
                        node.grid_y = parent.grid_y
                        node._regel_used = "regel 4b"

                # Regel 5: V kind met H ouder
                elif pdir == "horizontal" and ndir == "vertical":
                    if prev_sibling:
                        # regel 5a
                        node.grid_x = prev_far_x + 1
                        node.grid_y = parent.grid_y + 1
                        node._regel_used = "regel 5a"
                    else:
                        # regel 5b
                        node.grid_x = parent.grid_x + 1
                        node.grid_y = parent.grid_y + 1
                        node._regel_used = "regel 5b"
                else:
                    # fallback
                    node.grid_x = parent.grid_x + 1
                    node.grid_y = parent.grid_y + 1
                    node._regel_used = "fallback"

            # Recursief voor kinderen, met bijhouden van vorige broer
            prev = None
            for child in node.children:
                visit(child, node, prev)
                prev = child

        visit(self)

    def multiply_coordinates(self, factor):
        """
        Vermenigvuldig alle x- en y-coördinaten in de boom met de opgegeven factor.
        """
        self.x *= factor
        self.y *= factor
        for child in self.children:
            child.multiply_coordinates(factor)



    def draw_recursive_top_left(self, canvas, x_spacing=0, y_spacing=0 , swapy=False):
        if swapy:
            self.swapy()  # flips y, updates self.nulpunt to "bottom_left"

        # Component's top-left pixel position
        pixel_x = self.x + x_spacing
        pixel_y = self.y + y_spacing
        size = self.boundarybox

        # Draw the rectangle for the component
        canvas.create_rectangle(pixel_x, pixel_y, pixel_x + size, pixel_y + size, fill="pink", outline="black")
        # Draw the label
        canvas.create_text(pixel_x + size / 2, pixel_y + size / 2, text=self.label, font=("Arial", 8))

        # ----- Draw input/output dots -----
        dot_radius = 5
        # Draw input dot (red)
        if self.connectionpoint_input:
            in_cx, in_cy = self.connectionpoint_input
            canvas.create_oval(
                pixel_x + in_cx - dot_radius, pixel_y + in_cy - dot_radius,
                pixel_x + in_cx + dot_radius, pixel_y + in_cy + dot_radius,
                fill="red", outline=""
            )
            canvas.create_text(pixel_x + in_cx, pixel_y + in_cy, text="IN", font=("Arial", 15))

        # Draw output dot (green)
        if self.connectionpoint_output:
            out_cx, out_cy = self.connectionpoint_output
            canvas.create_oval(
                pixel_x + out_cx - dot_radius, pixel_y + out_cy - dot_radius,
                pixel_x + out_cx + dot_radius, pixel_y + out_cy + dot_radius,
                fill="green", outline=""
            )
            canvas.create_text(pixel_x + out_cx, pixel_y + out_cy, text="OUT", font=("Arial", 15))

        # ----- Draw connections/lines to children -----
        stub_length_H = self.pixels_tussen_kringen_H // 2
        stub_length_V = self.pixels_tussen_takken_V // 2


        for child in self.children:
            # Parent output
            out_cx, out_cy = self.connectionpoint_output
            out_abs_x = pixel_x + out_cx
            out_abs_y = pixel_y + out_cy

            # Child input
            child_pixel_x = child.grid_x + x_spacing
            child_pixel_y = child.grid_y + y_spacing
            in_cx, in_cy = child.connectionpoint_input
            in_abs_x = child_pixel_x + in_cx
            in_abs_y = child_pixel_y + in_cy

            # ----- Parent output stub -----
            if self.stroomrichting == "horizontal":
                stub1_end_x = out_abs_x + stub_length_H
                stub1_end_y = out_abs_y
            else:  # vertical
                if self.nulpunt == "top_left":
                    stub1_end_x = out_abs_x
                    stub1_end_y = out_abs_y + stub_length_V
                else:  # bottom_left
                    stub1_end_x = out_abs_x
                    stub1_end_y = out_abs_y - stub_length_V

            canvas.create_line(out_abs_x, out_abs_y, stub1_end_x, stub1_end_y, fill="black", width=2)

            # ----- Child input stub -----
            if child.stroomrichting == "horizontal":
                stub2_end_x = in_abs_x - stub_length_H
                stub2_end_y = in_abs_y
            else:  # vertical
                if child.nulpunt == "top_left":
                    stub2_end_x = in_abs_x
                    stub2_end_y = in_abs_y - stub_length_V
                else:  # bottom_left
                    stub2_end_x = in_abs_x
                    stub2_end_y = in_abs_y + stub_length_V

            canvas.create_line(in_abs_x, in_abs_y, stub2_end_x, stub2_end_y, fill="black", width=2)

            parent_stub_end = (stub1_end_x, stub1_end_y)
            child_stub_end = (stub2_end_x, stub2_end_y)

            # If not already connected, connect with orthogonal lines via crossing point
            if parent_stub_end != child_stub_end:
                # First, try horizontal-then-vertical "elbow"
                crossing_point1 = (child_stub_end[0], parent_stub_end[1])
                # Draw from parent stub end straight horizontally/vertically to crossing
                canvas.create_line(parent_stub_end[0], parent_stub_end[1], crossing_point1[0], crossing_point1[1],
                                   fill="black", width=2)
                # Draw from crossing point straight to child stub end
                canvas.create_line(crossing_point1[0], crossing_point1[1], child_stub_end[0], child_stub_end[1],
                                   fill="black", width=2)
                # If you want vertical-then-horizontal instead, swap x/y in crossing_point1

        # Recurse for children
        for child in self.children:
            child.draw_recursive_top_left(canvas, x_spacing, y_spacing)

    def limit_hoogte(self, hoogtelimiet=5):
        pass

    def insert_kolom_at(self, kolom_index):
        """
        Increase x by 1 for all nodes with x >= kolom_index.
        Prints all nodes with their new x and y values.
        """

        def update_x(component):
            if component.grid_x >= kolom_index:
                component.grid_x += 1
            for child in component.children:
                update_x(child)

        update_x(self)

    @property
    def stroomrichting(self):
        return self._stroomrichting

    @stroomrichting.setter
    def stroomrichting(self, value):
        if value not in ("horizontal", "vertical"):
            raise ValueError("stroomrichting must be 'horizontal' or 'vertical'")
        self._stroomrichting = value

    def explode_coordinates_to_canvas(self, x=None, y=None):
        if y is None:
            y = self.pixels_tussen_takken_V
        if x is None:
            x = self.pixels_tussen_kringen_H
        if self.x is not None and self.y is not None:
            self.x = self.x * (x + self.boundarybox)
            self.y = self.y * (y + self.boundarybox)
            for child in self.children:
                child.explode_coordinates_to_canvas(x, y)

    @property
    def connectionpoint_input(self):
        size = self.boundarybox
        ref = self.nulpunt
        HofV = self.stroomrichting
        if self.stroomrichting == "horizontal":
            # Input always at left center (0,50)
            return (0, size // 2)  # INPUT  0,50 horizonataal altijd 0,50 Linkerkant
        else:
            if self.nulpunt == "top_left":
                # Bottom center (default)
                return (size // 2, 0) # IN vertikaal 50,0 , Bovenaan
            elif self.nulpunt == "bottom_left":
                # Top center for bottom-up logic
                return (size // 2, size) #50,100 = input langs onderkant
            else:
                return (size // 2, 0)

    @property
    def connectionpoint_output(self):
        size = self.boundarybox
        ref = self.nulpunt
        HofV = self.stroomrichting

        if self.stroomrichting == "horizontal":
            # Always right center
            return (size, size // 2) # Horizontaal OUTPUT altijd 100,50 rechterkant
        else:
            if self.nulpunt == "top_left":
                # Output is at bottom center (default)
                return (size // 2, size) #vertikaal OUT = 50,100 onderkant
            elif self.nulpunt == "bottom_left":
                # Output is at top center (for bottom-up layouts)
                return (size // 2, 0)  # 50,0 bovenkant
            else:
                # Default to top_left logic if something else
                return (size // 2, size)




    def contains_node(self, node):
        if self is node:
            return True
        for child in self.children:
            if child.contains_node(node):
                return True
        return False

    def clone(self):
        return copy.deepcopy(self)

    def oudadd_child(self, *children):
        for child in children:
            child.parent = self
            self.children.append(child)

    def add_child(self, *children):
        for child in children:
            if self.contains_node(child):
                print(f"⚠️  WARNING: {child.label} is already present in the tree. Cloning and adding the clone.")
                child = child.clone()  # Use the clone instead
            child.parent = self
            self.children.append(child)

    def sort_children(self):
        """Sort children by number in label, fallback to alphabetical."""
        self.children.sort(key=lambda c: (Component.extract_int(c.label), c.label))
        for child in self.children:
            child.sort_children()

    def print_ascii_tree(self, prefix=" "):
        print(f"{prefix}{self.label} ({self.x},{self.y})")
        for i, child in enumerate(self.children):
            connector = "└── " if i == len(self.children) - 1 else "├── "
            child_prefix = prefix + ("    " if i == len(self.children) - 1 else "│   ")
            print(f"{prefix}{connector}", end="")
            child.print_ascii_tree(child_prefix)

    @staticmethod
    def extract_int(label):
        """Extract the first integer found in the label, or return inf if not found."""
        match = re.search(r'\d+', label)
        return int(match.group()) if match else float('inf')


class Differential(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.stroomrichting = "vertical"


class CircuitBreaker(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.stroomrichting = "vertical"


class Appliance(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.stroomrichting = "horizontal"


class Hoofddifferentieel(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.stroomrichting = "horizontal"


class HoofdAutomaat(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.stroomrichting = "horizontal"


class Domomodule(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.stroomrichting = "horizontal"


class Contax(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.stroomrichting = "horizontal"


class Verlichting(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.stroomrichting = "horizontal"


class Voeding(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.stroomrichting = "vertical"


class Teller(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.stroomrichting = "horizontal"


class Bord(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.stroomrichting = "vertical"


# Example tree
kopkwhmeter = Appliance("kopkwhmeter_H", "appliance")
teller = Teller("Teller_H", "teller")
bord1 = Bord("Bord1_V", "bord")
bord1 = Bord("bord1_V", "bord")
dif300 = Differential("Diff300_V", "differential")
dif30 = Differential("Diff30_V", "differential")
dif100 = Differential("Diff100_V", "differential")
dif3 = Differential("Diff3_V", "differential")

zek3001 = CircuitBreaker("zek3001_V", "circuit_breaker")
zek3002 = CircuitBreaker("zek3002_V", "circuit_breaker")
zek1001 = CircuitBreaker("zek1001_V", "circuit_breaker")
zek3003 = CircuitBreaker("zek3003_V", "circuit_breaker")
zek3004verl = CircuitBreaker("zek3004verl_V", "circuit_breaker")
vaatwas301 = Appliance("vaatwas301_H", "appliance")
droogkast3002 = Appliance("droogkast3002_H", "appliance")
oven3002 = Appliance("oven3002_H", "appliance")
lamp3004 = Appliance("lamp3004_H", "appliance")
microoven3002 = Appliance("microoven3002_H", "appliance")
contaxop3004 = Contax("contaxop3004_H", "appliance")
contaxopcontax = Contax("contaxopcontax_H", "appliance")
domo = Domomodule("Domomodule_H", "domomodule")
verlH = Verlichting("Verlichting_H", "verlichting")
verlH2 = Verlichting("Verlichting2_H", "verlichting")
verlH3 = Verlichting("Verlichting3_H", "verlichting")
verlH4 = Verlichting("Verlichting4_H", "verlichting")
verlH5 = Verlichting("Verlichting5_H", "verlichting")
zonnepaneelopdif3 = Appliance("zonnepaneelopdif3_H", "appliance")
faaropcontax = Verlichting("faaropcontax_H", "verlichting")
verlicht1 = Verlichting("Verlicht1_H", "verlichting")
verlicht2 = Verlichting("Verlicht2_H", "verlichting")
verlicht3 = Verlichting("Verlicht3_H", "verlichting")
tv = Appliance("tv_H", "appliance")
domo2 = Appliance("domo2_H", "appliance")
domo.add_child(verlH)
teller.add_child(dif300, dif30, dif3)
dif300.add_child(zek3001, zek3002, zek3003)
zek3001.add_child(droogkast3002)
zek3002.add_child(oven3002, microoven3002)
zek3003.add_child(tv, domo2, domo)
domo2.add_child(verlH2, verlH3, verlH4, verlH5)
zek3004verl.add_child(verlicht1, verlicht2, verlicht3, lamp3004)
zek3004verl.add_child(contaxop3004)
dif300.add_child(zek3004verl)
zek1001.add_child(vaatwas301)
dif300.add_child(dif100)
contaxop3004.add_child(contaxopcontax)
contaxopcontax.add_child(faaropcontax)
dif3.add_child(zonnepaneelopdif3)
dif100.add_child(zek1001)
kopkwhmeter.add_child(teller)
# ---- Drawing on Canvas ----


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
            cell = tk.Label(grid_frame, text="", width=10, height=4, borderwidth=1, relief="solid", bg="#f8f8f8")
            cell.grid(row=y, column=x, sticky="nsew")

    # 5. Zet objecten in de juiste cellen
    for node in all_nodes:
        info = f"{node.label}\n({node.grid_x},{node.grid_y})"
        if hasattr(node, "_regel_used"):
            info += f"\n{node._regel_used}"
        lbl = tk.Label(grid_frame, text=info, width=9, height=4, borderwidth=2, relief="groove", bg="#ffe0e0")
        lbl.grid(row=node.grid_y, column=node.grid_x, sticky="nsew")

    # 6. Zorg dat cellen zich uitrekken
    for x in range(max_x + 1):
        grid_frame.grid_columnconfigure(x, weight=1)
    for y in range(max_y + 1):
        grid_frame.grid_rowconfigure(y, weight=1)

    # 7. Scrollregion instellen
    grid_frame.update_idletasks()
    bbox = canvas.bbox("all")
    canvas.config(scrollregion=bbox, width=min(1400, (max_x + 1) * cell_size), height=min(700, (max_y + 1) * cell_size))

    root.mainloop()




if __name__ == "__main__":
    te_tekenen_startpunt = kopkwhmeter

    te_tekenen_startpunt.sort_children()
    te_tekenen_startpunt.assign_coordinates_by_rules()
    te_tekenen_startpunt.multiply_coordinates(1)

    te_tekenen_startpunt.print_ascii_tree_with_regel()
    # te_tekenen_startpunt.insert_kolom_at(5)
    # te_tekenen_startpunt.insert_kolom_at(8)

    # draw_grid_with_objects(te_tekenen_startpunt)  ##ookmooi


    #exit()
    # --- Create a Tkinter window and canvas ---
    root = tk.Tk()
    root.title("Component Tree Drawing")

    # Determine canvas size (example: 2000x1200)
    canvas = tk.Canvas(root, width=2000, height=1200, bg="white")
    canvas.pack(fill="both", expand=True)

    # Optionally, explode coordinates to canvas pixels
    te_tekenen_startpunt.explode_coordinates_to_canvas() #tak en kring tussenruimte

    # Draw the tree
    #te_tekenen_startpunt.swapy()
    #te_tekenen_startpunt.draw_recursive_top_left(canvas)

    te_tekenen_startpunt.draw_recursive_top_left(canvas  , 30 , 30 ,swapy=True)


    root.mainloop()

