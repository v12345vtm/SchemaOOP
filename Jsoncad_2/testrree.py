import tkinter as tk
import re

# ---- Your class definitions and tree construction ----

class Component:
    def __init__(self, label, type, stroomrichting="horizontal", stack_on_top_of_brother=False):
        self.label = label
        self.type = type
        self.children = []
        self.parent = None
        self.x = 0
        self.y = 0
        self._stroomrichting = stroomrichting  # "horizontal" or "vertical"
        self.COMPONENT_SIZE = 20  # Default size, can be parameterized
        self.stack_on_top_of_brother = stack_on_top_of_brother  # New attribute!
        self.allow_stack_on_top_of_parent  = False  # Default behavior

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

    def draw(self, c, COMPONENT_SIZE=20, font="Helvetica", font_size=6):
        c.rect(self.x, self.y, COMPONENT_SIZE, COMPONENT_SIZE)
        c.setFont(font, font_size)
        c.drawCentredString(
            self.x + COMPONENT_SIZE / 2,
            self.y + COMPONENT_SIZE / 2 - font_size / 2,
            self.label
        )



class Differential(Component):
    def __init__(self, label, type, stack_on_top_of_brother=False):
        super().__init__(label, type, stroomrichting="vertical", stack_on_top_of_brother=stack_on_top_of_brother)
        self.allow_stack_on_top_of_parent  = True  # Default behavior

class CircuitBreaker(Component):
    def __init__(self, label, type, stack_on_top_of_brother=False):
        super().__init__(label, type, stroomrichting="vertical", stack_on_top_of_brother=stack_on_top_of_brother)
        self.allow_stack_on_top_of_parent  = True  # Default behavior

class Appliance(Component):
    def __init__(self, label, type, stack_on_top_of_brother=False):
        super().__init__(label, type, stroomrichting="horizontal", stack_on_top_of_brother=stack_on_top_of_brother)
        self.stack_on_top_of_brother = True  # New attribute!


class Domomodule(Component):
    def __init__(self, label, type, stack_on_top_of_brother=False):
        super().__init__(label, type, stroomrichting="horizontal", stack_on_top_of_brother=stack_on_top_of_brother)
        self.stack_on_top_of_brother = True  # New attribute!

class Contax(Component):
    def __init__(self, label, type, stack_on_top_of_brother=False):
        super().__init__(label, type, stroomrichting="horizontal", stack_on_top_of_brother=stack_on_top_of_brother)
        self.stack_on_top_of_brother = True  # New attribute!

class Verlichting(Component):
    def __init__(self, label, type, stack_on_top_of_brother=False):
        super().__init__(label, type, stroomrichting="horizontal", stack_on_top_of_brother=stack_on_top_of_brother)
        self.stack_on_top_of_brother = True  # New attribute!

class Voeding(Component):
    def __init__(self, label, type, stack_on_top_of_brother=False):
        super().__init__(label, type, stroomrichting="horizontal", stack_on_top_of_brother=stack_on_top_of_brother)


# Example tree
voeding = Voeding("Voeding", "voeding")
diff300 = Differential("Diff300", "differential")
diff30 = Differential("Diff30", "differential")
diff3 = Differential("Diff9", "differential")
zek1 = CircuitBreaker("Zekering1", "circuit_breaker")
zek2 = CircuitBreaker("Zekering102", "circuit_breaker")
zek3 = CircuitBreaker("Zekering99", "circuit_breaker")
zek4 = CircuitBreaker("Zekering4", "circuit_breaker")
vaatwas = Appliance("Vaatwas", "appliance")
keuken = Appliance("Keuken", "appliance")
oven = Appliance("Oven", "appliance")
microOven = Appliance("microOven", "appliance")

domo1 = Domomodule("Domo1", "domomodule")
contax1 = Contax("Contax1", "contax")
verlichting1 = Verlichting("Verlicht1", "verlichting")

diffa = Differential("DiffA", "differential")
diffb = Differential("DIFFB", "differential")
zekc = CircuitBreaker("Zekeringc", "circuit_breaker")
tv = Appliance("tv", "appliance")
tv2 = Appliance("tv2", "appliance")

voeding.add_child(diffa)
diffa.add_child(diffb)
diffb.add_child(zekc)
zekc.add_child(tv)
zekc.add_child(tv2)

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

# ---- Sorting helper ----
def print_ascii_tree(component, prefix=""):
    print(f"{prefix}{component.label} ({component.grid_x},{component.grid_y})")
    for i, child in enumerate(component.children):
        connector = "└── " if i == len(component.children) - 1 else "├── "
        child_prefix = prefix + ("    " if i == len(component.children) - 1 else "│   ")
        print(f"{prefix}{connector}", end="")
        print_ascii_tree(child, child_prefix)



def extract_int(label):
    """Extract the first integer found in the label, or return a large number if not found."""
    match = re.search(r'\d+', label)
    return int(match.group()) if match else float('inf')

def sort_children(component):
    # Sort children by integer in label, or by label as fallback
    component.children.sort(key=lambda c: (extract_int(c.label), c.label))
    for child in component.children:
        sort_children(child)

# ---- Assign coordinates ----

def assign_increasing_x(component, depth=0, counter=[0]):
    component.grid_y = depth
    component.grid_x = counter[0]
    counter[0] += 1
    for child in component.children:
        assign_increasing_x(child, depth + 1, counter)

def get_max_coords(component, max_x=[0], max_y=[0]):
    if component.grid_x > max_x[0]:
        max_x[0] = component.grid_x
    if component.grid_y > max_y[0]:
        max_y[0] = component.grid_y
    for child in component.children:
        get_max_coords(child, max_x, max_y)

# ---- Drawing on Canvas ----

def draw_tree(canvas, component, canvas_height, x_spacing=80, y_spacing=80):
    size = component.boundarybox_hoogte
    x = component.grid_x * x_spacing + 40
    y = canvas_height - (component.grid_y * y_spacing + 40)
    # Draw rectangle
    canvas.create_rectangle(x, y - size, x + size, y, fill="white", outline="black")
    # Draw label
    canvas.create_text(x + size / 2, y - size / 2, text=component.label, font=("Arial", 8))
    # Draw lines to children
    for child in component.children:
        child_x = child.grid_x * x_spacing + 40 + size / 2
        child_y = canvas_height - (child.grid_y * y_spacing + 40) - size / 2
        canvas.create_line(x + size / 2, y - size / 2, child_x, child_y, fill="black")
        draw_tree(canvas, child, canvas_height, x_spacing, y_spacing)



def assign_coords_with_stacking(component, depth=0, counter=[0], occupied=set()):
    """Assign x, y coordinates to components with support for stacking."""
    if component.parent is None:
        # Root node
        component.grid_x = counter[0]
        component.grid_y = depth
        occupied.add((component.grid_x, component.grid_y))
        counter[0] += 1
    else:
        # Determine x and y based on stacking logic
        parent = component.parent
        siblings = parent.children
        index = siblings.index(component)

        if index == 0:
            # First child gets a new x
            component.grid_x = counter[0]
            component.grid_y = parent.grid_y + 1
            while (component.grid_x, component.grid_y) in occupied:
                component.grid_y += 1
            occupied.add((component.grid_x, component.grid_y))
            counter[0] += 1
        else:
            prev_sibling = siblings[index - 1]
            if component.stack_on_top_of_brother:
                # Stack vertically on same x
                component.grid_x = prev_sibling.grid_x
                component.grid_y = prev_sibling.grid_y + 1
                while (component.grid_x, component.grid_y) in occupied:
                    component.grid_y += 1
                occupied.add((component.grid_x, component.grid_y))
            else:
                # Use next x and reset y
                component.grid_x = counter[0]
                component.grid_y = parent.grid_y + 1
                while (component.grid_x, component.grid_y) in occupied:
                    component.grid_y += 1
                occupied.add((component.grid_x, component.grid_y))
                counter[0] += 1

    # Recursively assign children
    for child in component.children:
        assign_coords_with_stacking(child, depth + 1, counter, occupied)



def assign_coords_allow_stack_on_parent(root, counter=[0], occupied=set()):
    """
    Assign coordinates to components:
    - Children with allow_stack_on_top_of_parent=True can align with parent's column (x), y+1.
    - Other children are placed at the next available x column.
    - Avoid collisions with already-placed components and their subtrees.
    """
    root.grid_x = 0
    root.grid_y = 0
    occupied.add((root.grid_x, root.grid_y))

    def get_subtree_width(node):
        """Returns the number of columns used by the subtree rooted at this node."""
        if not node.children:
            return 1
        return sum(get_subtree_width(child) for child in node.children)

    def recurse(parent):
        current_x = parent.grid_x + 1  # Start from one column to the right of parent
        for i, child in enumerate(parent.children):
            if i == 0 and child.allow_stack_on_top_of_parent:
                # Stack first child directly under parent
                child.grid_x = parent.grid_x
                child.grid_y = parent.grid_y + 1
                while (child.grid_x, child.grid_y) in occupied:
                    child.grid_y += 1
            else:
                # Find next available x position for this child
                while any((current_x + dx, parent.grid_y + 1) in occupied for dx in range(get_subtree_width(child))):
                    current_x += 1

                child.grid_x = current_x
                child.grid_y = parent.grid_y + 1
                occupied.add((child.grid_x, child.grid_y))
                current_x += get_subtree_width(child)

            occupied.add((child.grid_x, child.grid_y))
            recurse(child)

    recurse(root)

def assign_coords_combined(component, depth=0, counter=[0], occupied=set()):
    """Assign x, y coordinates combining stacking rules and parent-aligned stacking."""
    if component.parent is None:
        # Root node
        component.grid_x = counter[0]
        component.grid_y = depth
        occupied.add((component.grid_x, component.grid_y))
        counter[0] += 1
    else:
        parent = component.parent
        siblings = parent.children
        index = siblings.index(component)

        if index == 0:
            if component.allow_stack_on_top_of_parent:
                # Stack directly under parent (reuse x)
                component.grid_x = parent.grid_x
                component.grid_y = parent.grid_y + 1
                while (component.grid_x, component.grid_y) in occupied:
                    component.grid_y += 1
                occupied.add((component.grid_x, component.grid_y))
            else:
                # First child in new x column
                component.grid_x = counter[0]
                component.grid_y = parent.grid_y + 1
                while (component.grid_x, component.grid_y) in occupied:
                    component.grid_y += 1
                occupied.add((component.grid_x, component.grid_y))
                counter[0] += 1
        else:
            prev_sibling = siblings[index - 1]
            if component.stack_on_top_of_brother:
                # Stack vertically on same x
                component.grid_x = prev_sibling.grid_x
                component.grid_y = prev_sibling.grid_y + 1
                while (component.grid_x, component.grid_y) in occupied:
                    component.grid_y += 1
                occupied.add((component.grid_x, component.grid_y))
            else:
                # Use new x column
                component.grid_x = counter[0]
                component.grid_y = parent.grid_y + 1
                while (component.grid_x, component.grid_y) in occupied:
                    component.grid_y += 1
                occupied.add((component.grid_x, component.grid_y))
                counter[0] += 1

    # Recurse on children
    for child in component.children:
        assign_coords_combined(child, depth + 1, counter, occupied)







def assign_coords_safe_stacking(component, depth=0, counter=[0], occupied=set()):
    """Assign x, y coordinates combining stacking logic with safety checks for stroomrichting."""
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
        assign_coords_safe_stacking(child, depth + 1, counter, occupied)










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


# ---- Main ----

if __name__ == "__main__":
    # Sort all children as whole numbers ascending

    sort_children(voeding)
    #assign_increasing_x(voeding)

    #print_ascii_tree(voeding)

    #assign_coords_combined(voeding) #assign_coords_combined is al zeer goed
    assign_coords_safe_stacking(voeding)

    print_ascii_tree(voeding)

    # Find max x and y for canvas size
    max_x = [0]
    max_y = [0]
    get_max_coords(voeding, max_x, max_y)
    x_spacing = 80
    y_spacing = 80
    width = (max_x[0] + 2) * x_spacing
    height = (max_y[0] + 2) * y_spacing

    root = tk.Tk()
    root.title("Component Tree (0,0 bottom left, sorted)")
    canvas = tk.Canvas(root, width=width, height=height, bg="white")
    canvas.pack()

    draw_grid(canvas, width, height, x_spacing, y_spacing)
    draw_tree(canvas, voeding, height, x_spacing, y_spacing)

    root.mainloop()