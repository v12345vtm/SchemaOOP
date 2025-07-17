import tkinter as tk
import re



class Component:
    def __init__(self, label, type,  **kwargs):
        self.label = label
        self.type = type
        self.children = []
        self.parent = None
        self.x = 0
        self.y = 0
        self._stroomrichting = None   # "horizontal" or "vertical"
        self.COMPONENT_SIZE = 50  # Default size, can be parameterized
        self.stack_on_top_of_brother = False  # New attribute!
        self.allow_stack_on_top_of_parent  = False  # Default behavior

        self.kwargs = kwargs  # Store all extra arguments in a dict
        # Optionally extract common expected values
        self.volgorde = kwargs.get("volgorde", None)

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
        Assigns coordinates to all nodes in the tree according to the specified rules.
        Annotates each node with ._regel_used (string).
        """

        def deepest_descendant_x(node):
            """Find the largest x among all descendants, or node.x if no descendants."""
            xs = [node.grid_x]
            for child in node.children:
                xs.append(deepest_descendant_x(child))
            return max(xs)

        def visit(node, parent=None, prev_sibling=None):
            # Regel 1: Root node
            if parent is None:
                node.grid_x, node.grid_y = 0, 0
                node._regel_used = "regel 1"
            else:
                # Determine types
                pdir = parent.stroomrichting
                ndir = node.stroomrichting

                # Find the previous sibling if any
                if prev_sibling is not None:
                    prev_x = prev_sibling.grid_x
                    prev_y = prev_sibling.grid_y
                    prev_far_x = deepest_descendant_x(prev_sibling)
                else:
                    prev_x = prev_y = prev_far_x = None

                # V child with V parent
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

                # H child with V parent
                elif pdir == "vertical" and ndir == "horizontal":
                    if prev_sibling:
                        # regel 3a
                        node.grid_x = prev_x
                        node.grid_y = prev_y + 1
                        node._regel_used = "regel 3a"
                    else:
                        # regel 3b
                        node.grid_x = parent.grid_x + 1
                        node.grid_y = parent.grid_y + 1
                        node._regel_used = "regel 3b"

                # H child with H parent
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

                # V child with H parent
                elif pdir == "horizontal" and ndir == "vertical":
                    if prev_sibling:
                        # regel 5a
                        node.grid_x = parent.grid_x + 2
                        node.grid_y = parent.grid_y + 2
                        node._regel_used = "regel 5a"
                    else:
                        # regel 5b
                        node.grid_x = parent.grid_x + 3
                        node.grid_y = parent.grid_y + 2
                        node._regel_used = "regel 5b"
                else:
                    # Fallback
                    node.grid_x = parent.grid_x + 1
                    node.grid_y = parent.grid_y + 1
                    node._regel_used = "fallback"

            # Now recursively assign to children, keeping track of previous sibling
            prev = None
            for child in node.children:
                visit(child, node, prev)
                prev = child

        # Start from self (root)
        visit(self)

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
        self.stroomrichting = "vertical"

class Teller(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.stroomrichting = "vertical"

class Bord(Component):
    def __init__(self, label, type, **kwargs):
        super().__init__(label, type, **kwargs)
        self.stroomrichting = "vertical"

# Example tree
teller = Teller("Teller_V", "teller")
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
droogkast3002 = Appliance("droogkast3002_H"  , "appliance")
oven3002 = Appliance("oven3002_H", "appliance")
lamp3004 = Appliance("lamp3004_H", "appliance")
microoven3002 = Appliance("microoven3002_H", "appliance")
contaxop3004 = Contax("contaxop3004_H", "appliance")
contaxopcontax = Contax("contaxopcontax_H", "appliance")

faaropcontax = Verlichting("faaropcontax_H", "verlichting")
verlicht1 = Verlichting("Verlicht1_H", "verlichting")
verlicht2 = Verlichting("Verlicht2_H", "verlichting")
verlicht3 = Verlichting("Verlicht3_H", "verlichting")
tv = Appliance("tv_H", "appliance")
tv2 = Appliance("tv2_H", "appliance")

teller.add_child(dif300, dif30, dif3)
dif300.add_child(zek3001 , zek3002 , zek3003)
zek3001.add_child(droogkast3002  )
zek3002.add_child(oven3002 , microoven3002)
zek3003.add_child(tv , tv2)
zek3004verl.add_child(verlicht1, verlicht2   , verlicht3 , lamp3004)
zek3004verl.add_child(contaxop3004)
dif300.add_child(zek3004verl)
zek1001.add_child(vaatwas301)
dif300.add_child(dif100)
contaxop3004.add_child(contaxopcontax)
contaxopcontax.add_child(faaropcontax)

dif100.add_child(zek1001)
# ---- Drawing on Canvas ----

def assign_increasing_x(component, depth=0, counter=[0]):
    component.grid_y = depth
    component.grid_x = counter[0]
    counter[0] += 1
    for child in component.children:
        assign_increasing_x(child, depth + 1, counter)








####################
def print_all_coordinates(component):
    print(f"{component.label}: x={component.grid_x}, y={component.grid_y}")
    for child in component.children:
        print_all_coordinates(child)
################

def post_order_traversal(node, visit):
    for child in node.children:
        post_order_traversal(child, visit)
    visit(node)

def print_relationships(node, processed=None):
    if processed is None:
        processed = []
    # Parent info
    parent = node.parent
    parent_label = parent.label if parent else None
    parent_stroomrichting = parent.stroomrichting if parent else None

    # Siblings (brothers)
    brothers = []
    if parent:
        brothers = [c for c in parent.children if c is not node]
    brother_labels = [b.label for b in brothers]
    num_horizontal_brothers = sum(1 for b in brothers if b.stroomrichting == "horizontal")
    num_vertical_brothers = sum(1 for b in brothers if b.stroomrichting == "vertical")

    # Coordinates of processed elements so far
    processed.append(node)
    coords = [(n.label, n.grid_x, n.grid_y) for n in processed]

    # Print info
    print(f"{node.label}={node.stroomrichting} ; parent={parent_label}={parent_stroomrichting} ; "
          f"number of horizontal brothers={num_horizontal_brothers} ; number of vertical brothers={num_vertical_brothers} ; "
          f"xycordates of processed elements={coords} ; brothers={brother_labels}")

    # Recurse for children
    for child in node.children:
        print_relationships(child, processed)


def print_preorder_relationships(node, processed=None):
    if processed is None:
        processed = []

    # Parent info
    parent = node.parent
    parent_label = parent.label if parent else None
    parent_stroomrichting = parent.stroomrichting if parent else None

    # Siblings (brothers)
    brothers = []
    if parent:
        brothers = [c for c in parent.children if c is not node]
    brother_labels = [b.label for b in brothers]
    num_horizontal_brothers = sum(1 for b in brothers if b.stroomrichting == "horizontal")
    num_vertical_brothers = sum(1 for b in brothers if b.stroomrichting == "vertical")

    # Coordinates of processed elements so far
    processed.append(node)
    coords = [(n.label, n.grid_x, n.grid_y) for n in processed]

    # Print info in your requested format
    print(f"{node.label}={node.stroomrichting} ; parent={parent_label}={parent_stroomrichting} ; "
          f"number of horizontal brothers={num_horizontal_brothers} ; number of vertical brothers={num_vertical_brothers} ; "
          f"xycordates of processed elements={coords} ; brothers={brother_labels}")

    # Pre-order: process children after current node
    for child in node.children:
        print_preorder_relationships(child, processed)

def post_order_relationships(node, processed=None):
    if processed is None:
        processed = []

    # First process all children (post-order)
    for child in node.children:
        post_order_relationships(child, processed)

    # Now process this node
    parent = node.parent
    parent_label = parent.label if parent else None
    parent_stroomrichting = parent.stroomrichting if parent else None

    # Assign coordinates if parent exists and child is horizontal, parent is vertical
    if parent and node.stroomrichting == "horizontal" and parent.stroomrichting == "vertical":
        # Find this child's index among horizontal siblings
        horizontal_siblings = [c for c in parent.children if c.stroomrichting == "horizontal"]
        counter = horizontal_siblings.index(node)
        node.grid_x = parent.grid_x + 1
        node.grid_y = parent.grid_y + counter + 1

    # Siblings (brothers)
    brothers = []
    if parent:
        brothers = [c for c in parent.children if c is not node]
    brother_labels = [b.label for b in brothers]
    num_horizontal_brothers = sum(1 for b in brothers if b.stroomrichting == "horizontal")
    num_vertical_brothers = sum(1 for b in brothers if b.stroomrichting == "vertical")

    processed.append(node)
    coords = [(n.label, n.grid_x, n.grid_y) for n in processed]

    print(f"{node.label}={node.stroomrichting} ; parent={parent_label}={parent_stroomrichting} ; "
          f"number of horizontal brothers={num_horizontal_brothers} ; number of vertical brothers={num_vertical_brothers} ; "
          f"xycordates of processed elements={coords} ; brothers={brother_labels}")

def subtree_depth(node):
    if not node.children:
        return 1
    return 1 + max(subtree_depth(child) for child in node.children)

def count_horizontal_ancestors(node):
    count = 0
    current = node.parent
    while current and current.stroomrichting == "horizontal":
        count += 1
        current = current.parent
    return count

def post_order_deepest_first_with_assignment(node, visit):
    sorted_children = sorted(node.children, key=subtree_depth, reverse=True)
    num_children = len(sorted_children)
    # For assigning coordinates to horizontal children of vertical parent
    horizontal_counter = 0
    # For assigning coordinates to horizontal children of horizontal parent
    grandgrandchildcounter = 0
    for child in sorted_children:
        print(child.label)
        # Condition 1: child is horizontal, parent is vertical
        if child.stroomrichting == "horizontal" and node.stroomrichting == "vertical":
            child.grid_x = node.grid_x + 1
            child.grid_y = node.grid_y + horizontal_counter + 1
            horizontal_counter += 1
        # Condition 2: child is horizontal, parent is horizontal
        elif child.stroomrichting == "horizontal" and node.stroomrichting == "horizontal":
            h_ancestors = count_horizontal_ancestors(node)
            child.grid_x = node.grid_x + 1
            child.grid_y = node.grid_y + h_ancestors + 0
            grandgrandchildcounter += 1
        # Default: assign coordinates if not already set
        else:
            child.grid_x = node.grid_x
            child.grid_y = node.grid_y + 1
        post_order_deepest_first_with_assignment(child, visit)
    visit(node, num_children)

def print_node_with_children_count(node, num_children):
    parent = node.parent.label if node.parent else None
    print(f"{node.label}: x={node.grid_x}, y={node.grid_y}, parent={parent}, children={num_children}")


# Example visit function to print the node and its assigned coordinates
def print_node_with_children_count(node, num_children):
    parent = node.parent.label if node.parent else None
    print(f"{node.label}: x={node.grid_x}, y={node.grid_y}, parent={parent}, children={num_children}")


def get_nodes_deepest_first(root):
    """
    Returns a list of all nodes in the tree rooted at `root`,
    ordered from deepest to shallowest.
    """
    nodes_with_depth = []

    def collect(node, depth):
        nodes_with_depth.append((depth, node))
        for child in node.children:
            collect(child, depth + 1)

    collect(root, 0)
    # Sort by depth descending (deepest first)
    nodes_with_depth.sort(reverse=True, key=lambda x: x[0])
    # Return only the nodes, in order
    return [node for depth, node in nodes_with_depth]



if __name__ == "__main__":
    te_tekenen_startpunt = teller
    te_tekenen_startpunt.print_ascii_tree()
    print("_hierboven is de tree____")

    te_tekenen_startpunt.assign_coordinates_by_rules()
    te_tekenen_startpunt.print_ascii_tree_with_regel()




