import re
import copy
import drawsvg as dw  # Import drawsvg


class Component:
    show_number_label = True
    show_boundarybox = True

    def __init__(self, label, lokatie, **kwargs):
        self.pixels_tussen_kringen_H = 0
        self.pixels_tussen_takken_V = 0
        self.inputstub = 20
        self.outputstub = 20
        self.label = label
        self.lokatie = lokatie
        self.children = []
        self.parent = None
        self.x = 0  # Grid X coordinate
        self.y = 0  # Grid Y coordinate
        self.canvas_x = 0  # Canvas pixel X coordinate
        self.canvas_y = 0  # Canvas pixel Y coordinate
        self._stroomrichting = None
        # Default boundary box, can be overridden by subclasses
        self.boundarybox_hoogte = 50
        self.boundarybox_breedte = 100
        self.nulpunt = "bottom_left"
        self.kwargs = kwargs

    def print_ascii_tree_with_regel(self, prefix=" "):
        regel = getattr(self, "_regel_used", "?")
        print(f"{prefix}{self.label} SVG({self.canvas_x},{self.canvas_y})  core({self.x},{self.y})\t\t{regel}")
        for i, child in enumerate(self.children):
            connector = "└── " if i == len(self.children) - 1 else "├── "
            child_prefix = prefix + ("    " if i == len(self.children) - 1 else "│   ")
            print(f"{prefix}{connector}", end="")
            child.print_ascii_tree_with_regel(child_prefix)

    def assign_coordinates_by_rules(self):
        def deepest_descendant_x(node):
            xs = [node.x]
            for child in node.children:
                xs.append(deepest_descendant_x(child))
            return max(xs)

        def deepest_descendant_y(node):
            ys = [node.y]
            for child in node.children:
                ys.append(deepest_descendant_y(child))
            return max(ys)

        def visit(node, parent=None, prev_sibling=None):
            if parent is None:
                node.x, node.y = 0, 0
                node._regel_used = "regel 1"
            else:
                pdir = parent.stroomrichting
                ndir = node.stroomrichting
                if prev_sibling is not None:
                    prev_x = prev_sibling.x
                    prev_y = prev_sibling.y
                    prev_far_x = deepest_descendant_x(prev_sibling)
                    prev_far_y = deepest_descendant_y(prev_sibling)
                else:
                    prev_x = prev_y = prev_far_x = prev_far_y = None

                if pdir == "vertical" and ndir == "vertical":
                    if prev_sibling:
                        node.x = prev_far_x + 1
                        node.y = prev_y
                        node._regel_used = "regel 2a"
                    else:
                        node.x = parent.x
                        node.y = parent.y + 1
                        node._regel_used = "regel 2b"
                elif pdir == "vertical" and ndir == "horizontal":
                    if prev_sibling:
                        node.x = prev_x
                        node.y = prev_far_y + 1
                        node._regel_used = "regel 3a"
                    else:
                        node.x = parent.x + 1
                        node.y = parent.y + 1
                        node._regel_used = "regel 3b"
                elif pdir == "horizontal" and ndir == "horizontal":
                    if prev_sibling:
                        node.x = prev_x
                        node.y = prev_y + 1
                        node._regel_used = "regel 4a"
                    else:
                        node.x = parent.x + 1
                        node.y = parent.y
                        node._regel_used = "regel 4b"
                elif pdir == "horizontal" and ndir == "vertical":
                    if prev_sibling:
                        node.x = prev_far_x + 1
                        node.y = parent.y + 1
                        node._regel_used = "regel 5a"
                    else:
                        node.x = parent.x + 1
                        node.y = parent.y + 1
                        node._regel_used = "regel 5b"
                else:
                    node.x = parent.x + 1
                    node.y = parent.y + 1
                    node._regel_used = "fallback"

            prev = None
            for child in node.children:
                visit(child, node, prev)
                prev = child

        visit(self)

    def generate_svg(self):
        """Generates an SVG representation of the component tree using drawsvg."""
        # --- CONFIGURATION ---
        NODE_PADDING = 3  # Padding between component boundary and calculated spacing
        PADDING = 2  # Padding for the entire canvas

        # --- Find canvas dimensions and max component sizes ---
        max_x, max_y = 0, 0
        max_component_width = 0
        max_component_height = 0

        nodes_to_visit = [self]
        all_nodes = []
        while nodes_to_visit:
            node = nodes_to_visit.pop(0)
            all_nodes.append(node)
            if node.x > max_x: max_x = node.x
            if node.y > max_y: max_y = node.y
            if node.boundarybox_breedte > max_component_width: max_component_width = node.boundarybox_breedte
            if node.boundarybox_hoogte > max_component_height: max_component_height = node.boundarybox_hoogte
            nodes_to_visit.extend(node.children)

        # Calculate dynamic spacing based on max component dimensions
        H_SPACING = max_component_width + NODE_PADDING
        V_SPACING = max_component_height + NODE_PADDING

        # Canvas size is based on grid plus the maximum component size for padding
        canvas_width = (max_x * H_SPACING) + max_component_width + PADDING * 2
        canvas_height = (max_y * V_SPACING) + max_component_height + PADDING * 2

        # Create a new drawing
        d = dw.Drawing(canvas_width, canvas_height, origin=(0, 0))

        # Styles are now applied directly to elements, no <style> tag needed.

        def get_center_coords(node):
            # The grid point (node.x, node.y) determines the center of the component
            # Adjust calculation to use max_component_width/height for consistent grid alignment
            cx = (node.x * H_SPACING) + PADDING + (max_component_width / 2)
            cy = (node.y * V_SPACING) + PADDING + (max_component_height / 2)
            return cx, cy

        for node in all_nodes:
            cx, cy = get_center_coords(node)

            # Store canvas coordinates on the node object
            node.canvas_x = cx
            node.canvas_y = cy

            # Use instance-specific boundary box for width and height
            node_width = node.boundarybox_breedte
            node_height = node.boundarybox_hoogte

            # --- Draw Box and Label ---
            # Position box based on its own width/height, centered at cx, cy
            box_x = cx - node_width / 2
            box_y = cy - node_height / 2

            # Add rectangle with direct styling
            d.append(dw.Rectangle(
                box_x, box_y, node_width, node_height,
                rx=5, ry=5,
                stroke="black",  # Black border
                stroke_width=2,
                fill="#ADD8E6"  # Light Blue fill for better visibility
            ))

            # Add label with direct styling
            label_text = node.label.replace("_H", "").replace("_V", "")
            d.append(dw.Text(
                label_text, "10px", cx, cy,  # Correctly passing font_size as the second positional argument
                font_family="Arial, sans-serif",
                text_anchor="middle",
                alignment_baseline="middle",
                fill="black"  # Black text
            ))

            # --- Draw Connection to Parent ---
            if node.parent:
                pcx, pcy = get_center_coords(node.parent)

                # Create 'elbow' connectors using dw.Path with direct styling
                path = dw.Path(
                    stroke="#4682B4",  # Steel Blue stroke for connections
                    stroke_width=1.5,
                    fill="none"
                )
                if node.parent.stroomrichting == 'vertical':
                    # Vertical trunk, horizontal branch
                    path.M(pcx, pcy).L(pcx, cy).L(cx, cy)
                else:  # horizontal
                    # Horizontal trunk, vertical branch
                    path.M(pcx, pcy).L(cx, pcy).L(cx, cy)
                d.append(path)

        return d  # Return the drawsvg Drawing object

    @property
    def stroomrichting(self):
        return self._stroomrichting

    @stroomrichting.setter
    def stroomrichting(self, value):
        if value not in ("horizontal", "vertical"):
            raise ValueError("stroomrichting must be 'horizontal' or 'vertical'")
        self._stroomrichting = value

    def contains_node(self, node):
        if self is node:
            return True
        for child in self.children:
            if child.contains_node(node):
                return True
        return False

    def clone(self):
        return copy.deepcopy(self)

    def add_child(self, *children):
        for child in children:
            if self.contains_node(child):
                print(f"⚠️  WARNING: {child.label} is already present in the tree. Cloning and adding the clone.")
                child = child.clone()
            child.parent = self
            self.children.append(child)

    def sort_children(self):
        self.children.sort(key=lambda c: (Component.extract_int(c.label), c.label))
        for child in self.children:
            child.sort_children()

    @staticmethod
    def extract_int(label):
        match = re.search(r'\d+', label)
        return int(match.group()) if match else float('inf')


# --- Component Subclasses (as provided) ---
class Differential(Component):
    show_boundarybox = True

    def __init__(self, label, lokatie, amperage=16, polen=2, vertrekkende_kabel="XVB_3G1.5", vertrekkendelengte=None,
                 klemmen=None, millies=None, **kwargs):
        super().__init__(label, lokatie, **kwargs)
        self.stroomrichting = "vertical"
        self.amperage = amperage
        self.polen = polen
        self.millies = millies
        self.boundarybox_hoogte = 150  # User's change
        self.boundarybox_breedte = 50  # User's change
        self.vertrekkende_kabel = vertrekkende_kabel
        self.vertrekkendelengte = vertrekkendelengte
        self.klemmen = klemmen
        self.lokatie = lokatie
        self.secundary_aftakpunt = None


class CircuitBreaker(Component):
    show_boundarybox = True

    def __init__(self, label, lokatie, amperage=None, polen=None, vertrekkende_kabel=None, vertrekkendelengte=None,
                 klemmen=None, image_path=None, **kwargs):
        super().__init__(label, lokatie, **kwargs)
        self.stroomrichting = "vertical"
        self.amperage = amperage
        self.polen = polen
        self.vertrekkende_kabel = vertrekkende_kabel
        self.vertrekkendelengte = vertrekkendelengte
        self.klemmen = klemmen
        self.lokatie = lokatie
        self.secundary_aftakpunt = None


class Appliance(Component):
    show_boundarybox = True

    def __init__(self, label, lokatie, **kwargs):
        super().__init__(label, lokatie, **kwargs)
        self.stroomrichting = "horizontal"
        self.lijsttoestellen = ["vaatwas", "droogkast", "oven", "reserve"]


class Hoofddifferentieel(Component):
    def __init__(self, label, lokatie, **kwargs):
        super().__init__(label, lokatie, **kwargs)
        self.stroomrichting = "horizontal"


class HoofdAutomaat(Component):
    def __init__(self, label, lokatie, **kwargs):
        super().__init__(label, lokatie, **kwargs)
        self.stroomrichting = "horizontal"


class Domomodule(Component):
    def __init__(self, label, lokatie, **kwargs):
        super().__init__(label, lokatie, **kwargs)
        self.stroomrichting = "horizontal"


class Contax(Component):
    def __init__(self, label, lokatie, **kwargs):
        super().__init__(label, lokatie, **kwargs)
        self.stroomrichting = "horizontal"


class Verlichting(Component):
    show_boundarybox = True

    def __init__(self, label, lokatie, bediening=None, hydro=False, verlichteknop=False, soort="gloei", aantal=1,
                 **kwargs):
        super().__init__(label, lokatie, **kwargs)
        self.stroomrichting = "horizontal"
        # This class has a different default size
        self.boundarybox_hoogte = 50
        self.boundarybox_breedte = 150  # Made it wider to demonstrate the change
        self.bediening = bediening
        self.hydro = hydro
        self.verlichteknop = verlichteknop
        self.soort = soort
        self.aantal = aantal
        self.ALLOWED_BEDIENINGEN = {None, "dim", "domo", "tele", "wissel", "bewegingmelder", "dubbel", "domodim"}
        self.ALLOWED_SOORTEN = {"led", "gloei", "halogeen", "tl", "ledstrip"}


class Voeding(Component):
    def __init__(self, label, lokatie, **kwargs):
        super().__init__(label, lokatie, **kwargs)
        self.stroomrichting = "vertical"


class Teller(Component):
    show_number_label = False

    def __init__(self, label, lokatie, **kwargs):
        super().__init__(label, lokatie, **kwargs)
        self.stroomrichting = "horizontal"


class Prieze(Component):
    show_boundarybox = True

    def __init__(self, label, lokatie, hydro=False, kinderveiligheid=True,
                 aarding=True, aantal=1, image_path=None, **kwargs):
        super().__init__(label, lokatie, **kwargs)
        self.stroomrichting = "horizontal"
        self.hydro = hydro
        self.kinderveiligheid = kinderveiligheid
        self.aarding = aarding
        self.aantal = aantal


class Bord(Component):
    def __init__(self, label, lokatie, **kwargs):
        super().__init__(label, lokatie, **kwargs)
        self.stroomrichting = "vertical"


# --- Tree Definition (as provided) ---
reserve = Appliance("reserve_H", "geen")
kopkwhmeter = Appliance("kop", "appliance")
teller = Teller("Teller_H", "teller")
bord1 = Bord("Bord1_V", "bord")
dif300 = Differential("Diff300_V", "differential", amperage=63, polen=4, millies=300)
dif30 = Differential("Diff30_V", "differential", amperage=40, polen=4, millies=30)
dif100 = Differential("dif100", "differential", amperage=40, polen=2, millies=100)
dif3 = Differential("Diff3_V", "differential", polen=2, millies=30)
prieze = Prieze("prieze", "prieze", aantal=1)
priezedub = Prieze("priezedub", "prieze", aantal=2)
zek3001 = CircuitBreaker("zek3001_V", "circuit_breaker", amperage=20, polen=4)
zek3002 = CircuitBreaker("zek3002_V", "circuit_breaker", amperage=20, polen=2)
zek1001 = CircuitBreaker("zek1001_V", "vb", 20, 2, "vob_3x2.5", 36, None)
zek3003 = CircuitBreaker("zek3003_V", "circuit_breaker", amperage=16, polen=2)
zek3004verl = CircuitBreaker("zek3004verl_V", "circuit_breaker", amperage=16, polen=2)
vaatwas301 = Appliance("vaatwas301_H met een langenaam", "keuken")
droogkast3002 = Appliance("droogkast3002_H", "appliance")
oven3002 = Appliance("oven3002_H", "keuken")
lamp3004 = Appliance("lamp3004_H", "appliance")
microoven3002 = Appliance("microoven3002_H", "appliance")
contaxop3004 = Contax("contaxop3004_H", "appliance")
contaxopcontax = Contax("contaxopcontax_H", "appliance")
domo = Domomodule("Domomodule_H", "domomodule")
verlH6 = Verlichting("centraal", "slpk2", bediening="dim", hydro=False, verlichteknop=False, soort="led", aantal=15)
verlH = Verlichting("eettafel", "living", bediening="wissel", hydro=False, verlichteknop=False, soort="led", aantal=3)
verlH2 = Verlichting("phaar", "tuin", bediening="domo", hydro=False, verlichteknop=False, soort="ledstrip", aantal=3)
verlH3 = Verlichting("dressoir", "living", bediening="tele", hydro=False, verlichteknop=False, soort="led", aantal=3)
verlH4 = Verlichting("centraal", "garage", bediening="dubbel", hydro=True, verlichteknop=True, soort="gloei", aantal=3)
verlH5 = Verlichting("kot", "kot", bediening="bewegingmelder", hydro=False, verlichteknop=False, soort="spot", aantal=1)
zonnepaneelopdif3 = Appliance("zonnepaneelopdif3_H", "appliance")
faaropcontax = Verlichting("faaropcontax_H", "verlichting", bediening="domodim", hydro=False, verlichteknop=False,
                           soort="led", aantal=3)
verlicht1 = Verlichting("inkom", "inkom", aantal=2, bediening="domo")
verlicht2 = Verlichting("Verlicht2_H", "verlichting")
verlicht3 = Verlichting("Verlicht3_H", "verlichting")
tv = Appliance("tv_H", "appliance")
dompelpomp = Appliance("dompelpomp_H", "appliance")
domo2 = Domomodule("domo2_H", "appliance")

domo.add_child(verlH)
prieze.add_child(dompelpomp)
teller.add_child(dif3, dif30, dif300)
dif300.add_child(zek3001, zek3002, zek3003, zek3004verl, dif100)
zek3001.add_child(droogkast3002)
zek3002.add_child(oven3002, microoven3002)
zek3003.add_child(tv, domo2, domo)
domo2.add_child(verlH2, verlH3, verlH4, verlH5)
zek3004verl.add_child(verlicht2, verlicht3, contaxop3004, lamp3004)
contaxop3004.add_child(contaxopcontax)
contaxopcontax.add_child(faaropcontax)
dif100.add_child(zek1001)
zek1001.add_child(vaatwas301, prieze, priezedub, verlH6, verlicht1)
dif30.add_child(reserve)
dif3.add_child(zonnepaneelopdif3)
kopkwhmeter.add_child(teller)

if __name__ == "__main__":
    te_tekenen_startpunt = kopkwhmeter
    te_tekenen_startpunt.sort_children()
    te_tekenen_startpunt.assign_coordinates_by_rules()

    # Generate the SVG content using drawsvg
    drawing = te_tekenen_startpunt.generate_svg()

    # Save the SVG content to a file
    # Use drawing.save_svg() for drawsvg objects
    drawing.save_svg("out.svg")

    print("✅ SVG file 'out.svg' has been created successfully using drawsvg.")

    # You can also print the ASCII tree with canvas coordinates
    print("\n--- ASCII Tree with Grid and Canvas Coordinates ---")
    te_tekenen_startpunt.print_ascii_tree_with_regel()
