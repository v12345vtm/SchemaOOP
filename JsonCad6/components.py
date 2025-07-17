# components.py
import re

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
            pass
            #print(f"{n.label}: x={n.x}, y={n.y}")

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
        # Print all nodes with their new coordinates
        def print_all(component):
            print(f"{component.label}: x={component.grid_x}, y={component.grid_y}")
            for child in component.children:
                print_all(child)
        #print_all(self)


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



    def add_child(self, *children):
        for child in children:
            child.parent = self
            self.children.append(child)

    def sort_children(self):
        """Sort children by number in label, fallback to alphabetical."""
        self.children.sort(key=lambda c: (Component.extract_int(c.label), c.label))
        for child in self.children:
            child.sort_children()

    def print_ascii_tree(self, prefix=""):
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

# Subclasses
class Differential(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.allow_stack_on_top_of_parent  = True
        self.stroomrichting = "vertical"

class CircuitBreaker(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.allow_stack_on_top_of_parent  = True
        self.stroomrichting = "vertical"

class Appliance(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.stack_on_top_of_brother = True
        self.stroomrichting="horizontal"

class Domomodule(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.stack_on_top_of_brother = True
        self.stroomrichting = "horizontal"

class Contax(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.stack_on_top_of_brother = True
        self.stroomrichting = "horizontal"

class Verlichting(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.stack_on_top_of_brother = True
        self.stroomrichting = "horizontal"

class Voeding(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.stroomrichting = "horizontal"
