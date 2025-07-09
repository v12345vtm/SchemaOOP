import os
import re

class Component:
    def __init__(self, label, type):
        self.label = label
        self.type = type
        self.children = []
        self.parent = None

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

class Voeding(Component): pass
class Differential(Component): pass
class CircuitBreaker(Component): pass
class Verlichting(Component): pass
class Contax(Component): pass
class Domomodule(Component): pass
class Appliance(Component): pass

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

def assign_coordinates(component, y=0, x_counter=None, coords=None):
    """
    Assigns (x, y) coordinates to each node.
    - x: strictly increasing column number (global, not per row)
    - y: depth (row)
    """
    if x_counter is None:
        x_counter = [0]  # Use a list for mutability in recursion
    if coords is None:
        coords = {}

    x = x_counter[0]
    coords[id(component)] = (x, y)
    x_counter[0] += 1  # Increment for the next node

    # Sort children as before
    leaves = [c for c in component.children if not c.children]
    non_leaves = [c for c in component.children if c.children]
    non_leaves_sorted = sorted(non_leaves, key=non_leaf_sort_key)
    leaves_sorted = sorted(leaves, key=leaf_sort_key)
    combined_children = non_leaves_sorted + leaves_sorted

    for child in combined_children:
        assign_coordinates(child, y + 1, x_counter, coords)

    return coords


def print_connection_tree(component, coords, path=None, prefix="", output_lines=None):
    if path is None:
        path = [1]
    if output_lines is None:
        output_lines = []

    node_path_str = ".".join(map(str, path))
    x, y = coords[id(component)]
    label = f"NodePath {node_path_str} | {component.label} ({component.type}) (x={x}, y={y})"
    if not component.children:
        label += " [Leaf]"
    output_lines.append(prefix + label)

    if component.children:
        leaves = [c for c in component.children if not c.children]
        non_leaves = [c for c in component.children if c.children]
        non_leaves_sorted = sorted(non_leaves, key=non_leaf_sort_key)
        leaves_sorted = sorted(leaves, key=leaf_sort_key)
        combined_children = non_leaves_sorted + leaves_sorted

        for i, child in enumerate(combined_children):
            connector = "└── " if i == len(combined_children) - 1 else "├── "
            new_prefix = prefix + connector
            print_connection_tree(child, coords, path + [i + 1], new_prefix, output_lines)

    return output_lines

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

# Assign unique coordinates
coords = assign_coordinates(voeding)

# Print tree with coordinates
output_lines = print_connection_tree(voeding, coords)
output_text = "\n".join(output_lines)

output_filename = "component_tree_nodepaths_sorted_by_leaftype_with_coordinates.txt"
with open(output_filename, "w", encoding="utf-8") as f:
    f.write(output_text)

try:
    os.startfile(output_filename)
except AttributeError:
    try:
        os.system(f"open {output_filename}")
    except:
        try:
            os.system(f"xdg-open {output_filename}")
        except:
            print(f"Saved as {output_filename} but could not auto-open.")

print(output_text)
