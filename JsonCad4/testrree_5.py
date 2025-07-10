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
        self.COMPONENT_SIZE = 20  # Default size, can be parameterized
        self.stack_on_top_of_brother = False  # New attribute!
        self.allow_stack_on_top_of_parent  = False  # Default behavior
        self.kwargs = kwargs  # Store all extra arguments in a dict

        # Optionally extract common expected values
        self.volgorde = kwargs.get("volgorde", None)

    @property
    def stroomrichting(self):
        return self._stroomrichting

    @stroomrichting.setter
    def stroomrichting(self, value):
        if value not in ("horizontal", "vertical"):
            raise ValueError("stroomrichting must be 'horizontal' or 'vertical'")
        self._stroomrichting = value

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

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

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
            component.x = counter[0]
            component.y = depth
            occupied.add((component.x, component.y))
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
                    component.x = parent.x
                    component.y = parent.y + 1
                    while (component.x, component.y) in occupied:
                        component.y += 1
                    occupied.add((component.x, component.y))
                else:
                    component.x = counter[0]
                    component.y = parent.y + 1
                    while (component.x, component.y) in occupied:
                        component.y += 1
                    occupied.add((component.x, component.y))
                    counter[0] += 1
            else:
                prev_sibling = siblings[index - 1]
                if component.stack_on_top_of_brother and not is_invalid_stack_on_brother(prev_sibling):
                    component.x = prev_sibling.x
                    component.y = prev_sibling.y + 1
                    while (component.x, component.y) in occupied:
                        component.y += 1
                    occupied.add((component.x, component.y))
                else:
                    component.x = counter[0]
                    component.y = parent.y + 1
                    while (component.x, component.y) in occupied:
                        component.y += 1
                    occupied.add((component.x, component.y))
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




def print_all_coordinates(component):
    print(f"{component.label}: x={component.x}, y={component.y}")
    for child in component.children:
        print_all_coordinates(child)




def get_max_coords(component, max_x=[0], max_y=[0]):
    if component.x > max_x[0]:
        max_x[0] = component.x
    if component.y > max_y[0]:
        max_y[0] = component.y
    for child in component.children:
        get_max_coords(child, max_x, max_y)
        pass

# ---- Drawing on Canvas ----

def draw_tree(canvas, component, canvas_height, x_spacing=80, y_spacing=80):
    size = component.COMPONENT_SIZE
    x = component.x * x_spacing + 40
    y = canvas_height - (component.y * y_spacing + 40)
    # Draw rectangle
    canvas.create_rectangle(x, y - size, x + size, y, fill="white", outline="black")
    # Draw label
    canvas.create_text(x + size / 2, y - size / 2, text=component.label, font=("Arial", 8))
    # Draw lines to children
    for child in component.children:
        child_x = child.x * x_spacing + 40 + size / 2
        child_y = canvas_height - (child.y * y_spacing + 40) - size / 2
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

    # Draw coordinate labels in the center of each grid cell
    for col in range(cols):
        for row in range(rows):
            center_x = col * x_spacing + x_spacing // 2
            center_y = row * y_spacing + y_spacing // 2
            canvas.create_text(center_x, center_y, text=f"({col},{rows - row - 1})", fill="red", font=font)

####################
def print_all_coordinates(component):
    print(f"{component.label}: x={component.x}, y={component.y}")
    for child in component.children:
        print_all_coordinates(child)
################


# ---- Main ----


if __name__ == "__main__":
    te_tekenen_startpunt = cabine
    # Use the new methods
    te_tekenen_startpunt.sort_children()
    Component.assign_coords_safe_stacking(te_tekenen_startpunt)

    print_all_coordinates(cabine)

    te_tekenen_startpunt.print_ascii_tree()



    print_all_coordinates(te_tekenen_startpunt)



    # Find max x and y for canvas size
    max_x = [0]
    max_y = [0]
    get_max_coords(te_tekenen_startpunt, max_x, max_y)
    x_spacing = 80
    y_spacing = 80
    width = (max_x[0] + 2) * x_spacing
    height = (max_y[0] + 2) * y_spacing

    root = tk.Tk()
    root.title("Component Tree (0,0 bottom left, sorted)")
    canvas = tk.Canvas(root, width=width, height=height, bg="white")
    canvas.pack()

    draw_grid(canvas, width, height, x_spacing, y_spacing)
    draw_tree(canvas, te_tekenen_startpunt, height, x_spacing, y_spacing)

    root.mainloop()