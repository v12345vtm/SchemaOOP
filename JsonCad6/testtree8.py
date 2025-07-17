import tkinter as tk
import re

# ---- Your class definitions and tree construction ----


class Component:
    def __init__(self, label, type,  **kwargs):
        self.label = label
        self.type = type
        self.children = []
        self.parent = None
        self.x = 0
        self.y = 0
        self._stroomrichting = "horizontal"   # "horizontal" or "vertical"
        self.COMPONENT_SIZE = 50  # Default size, can be parameterized
        self.stack_on_top_of_brother = False  # New attribute!
        self.allow_stack_on_top_of_parent  = False  # Default behavior
        self.kwargs = kwargs  # Store all extra arguments in a dict
        # Optionally extract common expected values
        self.volgorde = kwargs.get("volgorde", None)

    def draw_recursive_top_left(self, canvas, x_spacing=0, y_spacing=0):
        # Convert logical grid position to pixel position (top-left corner)
        pixel_x = self.x   + x_spacing
        pixel_y = self.y   + y_spacing
        size = self.COMPONENT_SIZE

        # Draw the rectangle for the component
        canvas.create_rectangle(pixel_x, pixel_y, pixel_x + size, pixel_y + size, fill="pink", outline="black")

        # Draw the label centered in the component
        canvas.create_text(pixel_x + size / 2, pixel_y + size / 2, text=self.label, font=("Arial", 8))

        # === RED INPUT LINE ===
        if self.connectionpoint_input and self.inputlinepoint:
            x1 = self.inputlinepoint[0] + x_spacing
            y1 = self.inputlinepoint[1]   + y_spacing
            x2 = self.connectionpoint_input[0]  + x_spacing
            y2 = self.connectionpoint_input[1]   + y_spacing
            canvas.create_line(x1, y1, x2, y2, fill="red")


        # === green output LINE ===
        if self.connectionpoint_output and self.outputlinepoint:
            x1 = self.outputlinepoint[0] + x_spacing
            y1 = self.outputlinepoint[1]   + y_spacing
            x2 = self.connectionpoint_output[0]  + x_spacing
            y2 = self.connectionpoint_output[1]   + y_spacing
            canvas.create_line(x1, y1, x2, y2, fill="green")

        # === CONNECTION TO CHILDREN ===
        for child in self.children:
            x1 = (self.x + 0.5)   + x_spacing
            y1 = (self.y + 0.5)  + y_spacing
            x2 = (child.grid_x + 0.5) + x_spacing
            y2 = (child.grid_y + 0.5) + y_spacing
            canvas.create_line(x1, y1, x2, y2, fill="black", width=2)

            # Recursively draw the child
            child.draw_recursive_top_left(canvas, x_spacing, y_spacing)

    def draw(self, canvas, offset_x=0, offset_y=80, x_spacing=80, y_spacing=80):
        canvas_height = int(canvas['height'])

        # Calculate canvas position (0,0 bottom-left)
        screen_x = offset_x + self.x * x_spacing
        screen_y = canvas_height - (offset_y + self.y * y_spacing)

        size = self.COMPONENT_SIZE

        # Draw the component rectangle
        canvas.create_rectangle(screen_x, screen_y - size, screen_x + size, screen_y,
                                fill="pink", outline="black")

        # Draw label inside
        canvas.create_text(screen_x + size / 2, screen_y - size / 2, text=self.label, font=("Arial", 8))

        # Draw connection to parent
        if self.parent:
            px = offset_x + self.parent.grid_x * x_spacing + size / 2
            py = canvas_height - (offset_y + self.parent.grid_y * y_spacing) - size / 2
            cx = screen_x + size / 2
            cy = screen_y - size / 2
            canvas.create_line(px, py, cx, cy, arrow=tk.LAST)

        # Draw all children recursively
        for child in self.children:
            child.draw(canvas, offset_x=offset_x, offset_y=offset_y, x_spacing=x_spacing, y_spacing=y_spacing)

    def limit_hoogte(self, hoogtelimiet=5):
        # 1. Collect all nodes
        nodes = []
        def collect_nodes(node):
            nodes.append(node)
            for child in node.children:
                collect_nodes(child)
        collect_nodes(self)
        # 2. Find all columns (x) with nodes above the y-limit
        # We'll process each column only once
        processed_columns = set()
        for node in nodes:
            if node.grid_y > hoogtelimiet and node.grid_x not in processed_columns:
                col_x = node.grid_x
                processed_columns.add(col_x)
                # 3. Insert new column at x+1 (do this once per column)
                self.insert_kolom_at(col_x + 1)
                # 4. Move all nodes in col_x with y > hoogtelimiet to new column (x+1)
                moved_nodes = []
                for n in nodes:
                    if n.grid_x == col_x and n.grid_y > hoogtelimiet:
                        n.grid_x += 1
                        moved_nodes.append(n)
                # 5. Find the lowest y in the previous column (col_x)
                prev_col_y = [n.grid_y for n in nodes if n.grid_x == col_x]
                if prev_col_y:
                    base_y = min(prev_col_y)
                else:
                    base_y = 0
                # 6. Stack moved nodes on top of base_y, preserving their original order
                moved_nodes.sort(key=lambda n: n.grid_y)  # Ascending order
                for i, n in enumerate(moved_nodes):
                    n.grid_y = base_y + i
        # 7. Print all coordinates for verification
        for n in nodes:
            print(f"{n.label}: x={n.grid_x}, y={n.grid_y}")

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


    def explode_coordinates_to_canvas(self, x=30, y=30):
        """Multiply logical grid coordinates and apply offset for canvas placement."""
        #hoeveel pixels moeten tussen de kaders zijn?
        if self.x is not None and self.y is not None:
            self.x = self.x *  ( x + self.COMPONENT_SIZE)
            self.y = self.y *  (y + self.COMPONENT_SIZE)

            #  all children recursively
            for child in self.children:
                child.explode_coordinates_to_canvas( x , y)



    @property
    def connectionpoint_input(self):
        if self.x is None or self.y is None:
            return None
        if self.stroomrichting == "horizontal":
            # Input is left center
            return (self.x, self.y + self.COMPONENT_SIZE // 2)
        else:
            # Input is bottom center
            return (self.x + self.COMPONENT_SIZE // 2, self.y)

    @property
    def connectionpoint_output(self):
        if self.x is None or self.y is None:
            return None
        if self.stroomrichting == "horizontal":
            # Output is right center
            return (self.x + self.COMPONENT_SIZE, self.y + self.COMPONENT_SIZE // 2)
        else:
            # Output is top center
            return (self.x + self.COMPONENT_SIZE // 2, self.y + self.COMPONENT_SIZE)

    @property
    def inputlinepoint(self):
        """Return the point from which the input line starts (slightly outside the input connector)."""
        ip = self.connectionpoint_input
        inputline_lengte = 10 #hoelang moet het lijntje zijn van ons icoon aan de ingang
        if ip is None:
            return None
        if self.stroomrichting == "horizontal":
            return (ip[0] - inputline_lengte, ip[1])
        else:
            return (ip[0], ip[1] - inputline_lengte)


    @property
    def outputlinepoint(self):
        """Return the point from which the output line ends (slightly outside the input connector)."""
        op = self.connectionpoint_output
        outputline_lengte = 10 #hoelang moet het lijntje zijn van ons icoon op de uitgang
        if op is None:
            return None
        if self.stroomrichting == "horizontal":
            return (op[0] +  outputline_lengte, op[1])  # x,y koppel
        else:
            return (op[0], op[1] + outputline_lengte)

    def add_child(self, *children):
        for child in children:
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

    @staticmethod
    def assign_coords_safe_stacking(component, depth=0, counter=[0], occupied=None):
        if occupied is None:
            occupied = set()
        if component.parent is None:
            component.grid_x = counter[0]
            component.grid_y = depth
            occupied.add((component.grid_x, component.grid_y))
            counter[0] += 1
        else:
            parent = component.parent
            siblings = parent.children
            index = siblings.index(component)
            def is_invalid_stack_on_parent():
                return (
                    component.allow_stack_on_top_of_parent and
                    parent.stroomrichting == "vertical" and
                    component.stroomrichting == "horizontal"
                )
            def is_invalid_stack_on_brother(prev_sibling):
                return (
                    component.stack_on_top_of_brother and
                    prev_sibling.stroomrichting == "vertical" and
                    component.stroomrichting == "horizontal"
                )

            if index == 0:
                if component.allow_stack_on_top_of_parent and not is_invalid_stack_on_parent():
                    component.grid_x = parent.grid_x
                    component.grid_y = parent.grid_y + 1
                    while (component.grid_x, component.grid_y) in occupied:
                        component.grid_y += 1
                    occupied.add((component.grid_x, component.grid_y))
                else:
                    component.grid_x = counter[0]
                    component.grid_y = parent.grid_y + 1
                    while (component.grid_x, component.grid_y) in occupied:
                        component.grid_y += 1
                    occupied.add((component.grid_x, component.grid_y))
                    counter[0] += 1
            else:
                prev_sibling = siblings[index - 1]
                if component.stack_on_top_of_brother and not is_invalid_stack_on_brother(prev_sibling):
                    component.grid_x = prev_sibling.grid_x
                    component.grid_y = prev_sibling.grid_y + 1
                    while (component.grid_x, component.grid_y) in occupied:
                        component.grid_y += 1
                    occupied.add((component.grid_x, component.grid_y))
                else:
                    component.grid_x = counter[0]
                    component.grid_y = parent.grid_y + 1
                    while (component.grid_x, component.grid_y) in occupied:
                        component.grid_y += 1
                    occupied.add((component.grid_x, component.grid_y))
                    counter[0] += 1

        for child in component.children:
            Component.assign_coords_safe_stacking(child, depth + 1, counter, occupied)

class Differential(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.allow_stack_on_top_of_parent  = True  # Default behavior
        self.stroomrichting = "vertical"


class CircuitBreaker(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.allow_stack_on_top_of_parent  = True  # Default behavior
        self.stroomrichting = "vertical"

class Appliance(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.stack_on_top_of_brother = True  # New attribute!
        self.stroomrichting="horizontal"


class Domomodule(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.stack_on_top_of_brother = True  # New attribute!
        self.stroomrichting = "horizontal"

class Contax(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.stack_on_top_of_brother = True  # New attribute!
        self.stroomrichting = "horizontal"

class Verlichting(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.stack_on_top_of_brother = True  # New attribute!
        self.stroomrichting = "horizontal"

class Voeding(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.stroomrichting = "horizontal"


# Example tree
cabine = Voeding("cabine", "voeding")
voeding2 = Voeding("Voeding2", "voeding")
zek1voeding2 = CircuitBreaker("voeding2Zekering1", "circuit_breaker")
voeding = Voeding("Voeding", "voeding")
diff300 = Differential("Diff300", "differential")
diff30 = Differential("Diff30", "differential")
diff3 = Differential("Diff9", "differential")
zek1 = CircuitBreaker("A", "circuit_breaker")
zek2 = CircuitBreaker("B2", "circuit_breaker")
zek3 = CircuitBreaker("B10", "circuit_breaker")
zek4 = CircuitBreaker("B1", "circuit_breaker")
vaatwas = Appliance("Vaatwas", "appliance")
keuken = Appliance("Keuken", "appliance")
dif9_3 = Appliance("3etoestel", "appliance" , tak=2 )
oven = Appliance("Oven", "appliance")
microOven = Appliance("microOven", "appliance")
contaxopvoeding = Contax("contaxvoeding" , "appliance")
domo1 = Domomodule("Domo1", "domomodule")
contax1 = Contax("Contax1", "contax", tak=5)
verlichting1 = Verlichting("Verlicht1", "verlichting")
ct1 = Contax("ct1", "contax")
ct2 = Contax("ct2", "contax")
ct3 = Contax("ct3", "contax")
ct4 = Contax("ct4", "contax")
ct5 = Contax("ct5", "contax")
ct6 = Contax("ct6", "contax")
ct7 = Contax("ct7", "contax")
ct8 = Contax("ct8", "contax")

diffa = Differential("DiffA", "differential")
diffb = Differential("DIFFB", "differential")
zekc = CircuitBreaker("Zekeringc", "circuit_breaker")
tv = Appliance("tv", "appliance")
tv2 = Appliance("tv2", "appliance")
voeding2.add_child(zek1voeding2)
cabine.add_child(voeding)
cabine.add_child(voeding2)

voeding.add_child(diffa)
diffa.add_child(diffb)
diffb.add_child(zekc)
zekc.add_child(tv)
zekc.add_child(tv2)
voeding.add_child(contaxopvoeding)
voeding.add_child(diff300)
voeding.add_child(diff30)
voeding.add_child(diff3)
voeding.add_child(verlichting1)  # example non-leaf with no children - leaf

diff300.add_child(zek1)
diff30.add_child(zek2)
zek1.add_child(vaatwas)
zek2.add_child(keuken)
zek2.add_child(oven)
diff30.add_child(zek3)
diff30.add_child(microOven)
diff30.add_child(zek4)

diff3.add_child(domo1)
diff3.add_child(contax1)
diff3.add_child(dif9_3)
diff3.add_child(ct1 , ct2 , ct3 , ct4 , ct5 )






def get_max_coords(component, max_x=[0], max_y=[0]):
    if component.grid_x > max_x[0]:
        max_x[0] = component.grid_x
    if component.grid_y > max_y[0]:
        max_y[0] = component.grid_y
    for child in component.children:
        get_max_coords(child, max_x, max_y)
        pass

# ---- Drawing on Canvas ----



####################
def print_all_coordinates(component):
    print(f"{component.label}: x={component.grid_x}, y={component.grid_y}")
    for child in component.children:
        print_all_coordinates(child)
################

class Box:
    def __init__(self, x=100, y=100, size=100, color="pink"):
        # x, y are the bottom-left coordinates in "user space"
        self.x = x
        self.y = y
        self.size = size
        self.color = color

    def draw(self, canvas):
        canvas_height = int(canvas['height'])  # Get the actual canvas height
        # Convert bottom-left origin to Tkinter's top-left origin
        x1 = self.x
        y1 = canvas_height - (self.y + self.size)
        x2 = self.x + self.size
        y2 = canvas_height - self.y
        canvas.create_rectangle(x1, y1, x2, y2, fill=self.color, outline="black")
# ---- Main ----


if __name__ == "__main__":
    te_tekenen_startpunt = cabine
    # Use the new methods
    te_tekenen_startpunt.sort_children()
    Component.assign_coords_safe_stacking(te_tekenen_startpunt)

    print_all_coordinates(te_tekenen_startpunt)
    te_tekenen_startpunt.limit_hoogte(hoogtelimiet=5)

    Component.explode_coordinates_to_canvas(te_tekenen_startpunt)








    #te_tekenen_startpunt.insert_kolom_at(3)

    # Find max x and y for canvas size
    max_x = [0]
    max_y = [0]
    get_max_coords(te_tekenen_startpunt, max_x, max_y)
    x_spacing = 80
    y_spacing = 80


    root = tk.Tk()
    root.title("Component Tree (0,0 bottom left, sorted)")
    canvas = tk.Canvas(root, width=1300, height=600, bg="white")
    canvas.pack()
    # Draw a pink square at (100, 100) with size 100
    x, y, size = 300, 300, 100
    #canvas.create_rectangle(x, y, x + size, y + size, fill="pink", outline="black")


    rodedoos = Box()  # Default at (100, 100), size 100, pink
    #rodedoos.draw(canvas )
    te_tekenen_startpunt.draw_recursive_top_left(canvas)

    root.mainloop()