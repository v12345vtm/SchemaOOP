import os
import re

def assign_coordinates(component, x=0, y=0):
    component.x = x
    component.y = y

    if not component.children:
        return 1  # subtree height/width = 1 grid unit

    if component.stroomrichting == "horizontal":
        # children stacked vertically upwards at x+1, increasing y
        current_y = y
        for child in component.children:
            height = assign_coordinates(child, x + 1, current_y)
            current_y += height
        return current_y - y  # total height consumed by this subtree

    else:  # stroomrichting == "vertical"
        # children stacked horizontally rightwards at y+1, increasing x
        current_x = x
        for child in component.children:
            width = assign_coordinates(child, current_x, y + 1)
            current_x += width
        return current_x - x  # total width consumed by this subtree

class Component:
    def __init__(self, label, type, stroomrichting="horizontal"):
        self.label = label
        self.type = type
        self.children = []
        self.parent = None
        self.x = 0
        self.y = 0
        self._stroomrichting = stroomrichting  # "horizontal" or "vertical"
        self.COMPONENT_SIZE = 20  # Default size, can be parameterized

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
        self.sort_children()  # Ensure children are always sorted

    def sort_children(self):
        leaves = [c for c in self.children if not c.children]
        non_leaves = [c for c in self.children if c.children]
        non_leaves_sorted = sorted(non_leaves, key=non_leaf_sort_key)
        leaves_sorted = sorted(leaves, key=leaf_sort_key)
        self.children = non_leaves_sorted + leaves_sorted

    def draw(self, c, COMPONENT_SIZE=20, font="Helvetica", font_size=6):
        """
        Draws the component as a square on the given ReportLab canvas `c`.
        """
        # Use .x_pdf and .y_pdf for actual PDF coordinates
        c.rect(self.x, self.y, COMPONENT_SIZE, COMPONENT_SIZE)
        c.setFont(font, font_size)
        c.drawCentredString(
            self.x + COMPONENT_SIZE / 2,
            self.y + COMPONENT_SIZE / 2 - font_size / 2,
            self.label
        )



    def print_connection_tree(self, path=None, prefix="", output_lines=None):
        if path is None:
            path = [1]
        if output_lines is None:
            output_lines = []

        node_path_str = ".".join(map(str, path))
        x, y = self.x, self.y
        label = f"NodePath {node_path_str} | {self.label} ({self.type}) | coord=({x},{y})"
        if not self.children:
            label += " [Leaf]"
        output_lines.append(prefix + label)

        if self.children:
            # Children are already sorted if you use sort_children after each add
            for i, child in enumerate(self.children):
                connector = "└── " if i == len(self.children) - 1 else "├── "
                new_prefix = prefix + connector
                child.print_connection_tree(path + [i + 1], new_prefix, output_lines)

        return output_lines

class Voeding(Component):
    def __init__(self, label, type):
        super().__init__(label, type, stroomrichting="horizontal")


class Differential(Component):
    def __init__(self, label, type):
        super().__init__(label, type, stroomrichting="vertical")


class CircuitBreaker(Component):
    def __init__(self, label, type):
        super().__init__(label, type, stroomrichting="vertical")



class Appliance(Component):
    def __init__(self, label, type):
        super().__init__(label, type, stroomrichting="horizontal")


class Domomodule(Component):
    def __init__(self, label, type):
        super().__init__(label, type, stroomrichting="horizontal")


class Contax(Component):
    def __init__(self, label, type):
        super().__init__(label, type, stroomrichting="horizontal")


class Verlichting(Component):
    def __init__(self, label, type):
        super().__init__(label, type, stroomrichting="horizontal")






leaf_volgorde = ["Domomodule", "Contax", "Appliance"]

def extract_int(label):
    match = re.search(r'\d+', label)
    return int(match.group()) if match else float('inf')

def non_leaf_sort_key(component):
    # Sort by integer in label, then by label as fallback
    return (extract_int(component.label), component.label.lower())

def leaf_sort_key(component):
    cls_name = type(component).__name__
    try:
        type_order = leaf_volgorde.index(cls_name)
    except ValueError:
        type_order = len(leaf_volgorde)
    return (type_order, extract_int(component.label), component.label.lower())





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


voeding.sort_children()
assign_coordinates(voeding)

lines = voeding.print_connection_tree()
print("\n".join(lines))


