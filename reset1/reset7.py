import re
import copy
import drawsvg as dw


# --- Component Classes ---

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
        self.x = 0
        self.y = 0
        self.canvas_x = 0
        self.canvas_y = 0
        self._stroomrichting = None
        self.boundarybox_hoogte = 50
        self.boundarybox_breedte = 50
        self.nulpunt = "bottom_left"
        self.kwargs = kwargs
        self.tussenruimte_H = 50
        self.tussenruimte_V = 50

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
            xs = [node.x] + [deepest_descendant_x(child) for child in node.children]
            return max(xs) if xs else node.x

        def deepest_descendant_y(node):
            ys = [node.y] + [deepest_descendant_y(child) for child in node.children]
            return max(ys) if ys else node.y

        def visit(node, parent=None, prev_sibling=None):
            if parent is None:
                node.x, node.y = 0, 0
                node._regel_used = "regel 1"
            else:
                pdir = parent.stroomrichting
                ndir = node.stroomrichting

                if prev_sibling:
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

    @property
    def stroomrichting(self):
        return self._stroomrichting

    @stroomrichting.setter
    def stroomrichting(self, value):
        if value not in ("horizontal", "vertical"):
            raise ValueError("stroomrichting must be 'horizontal' or 'vertical'")
        self._stroomrichting = value

    def contains_node(self, node):
        if self is node: return True
        return any(child.contains_node(node) for child in self.children)

    def clone(self):
        return copy.deepcopy(self)

    def add_child(self, *children):
        for child in children:
            if self.contains_node(child):
                print(f"⚠️  WARNING: {child.label} is already in the tree. Cloning.")
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

    def get_all_nodes(self):
        nodes = [self]
        for child in self.children:
            nodes.extend(child.get_all_nodes())
        return nodes

    def compute_column_widths(self):
        """
        Returns a dict mapping each unique x (column) to the maximum required width in that column,
        based on all nodes’ 'tussenruimte_H'.
        """
        nodes = self.get_all_nodes()
        col_widths = {}
        for node in nodes:
            width = 60 + getattr(node, 'tussenruimte_H', 0)
            col_widths[node.x] = max(width, col_widths.get(node.x, 0))
        return col_widths


class Differential(Component):
    show_boundarybox = True

    def __init__(self, label, lokatie, amperage=16, polen=2, vertrekkende_kabel="XVB_3G1.5", vertrekkendelengte=None,
                 klemmen=None, millies=None, **kwargs):
        super().__init__(label, lokatie, **kwargs)
        self.stroomrichting = "vertical"
        self.amperage = amperage
        self.polen = polen
        self.millies = millies
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
        self.tussenruimte_H = 50
        self.tussenruimte_V = 100


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
        self.boundarybox_hoogte = 50
        self.boundarybox_breedte = 100
        self.bediening = bediening
        self.hydro = hydro
        self.verlichteknop = verlichteknop
        self.soort = soort
        self.aantal = aantal
        self.ALLOWED_BEDIENINGEN = {None, "dim", "domo", "tele", "wissel", "bewegingmelder", "dubbel", "domodim"}
        self.ALLOWED_SOORTEN = {"led", "gloei", "halogeen", "tl", "ledstrip"}
        self.tussenruimte_H = 100
        self.tussenruimte_V = 0


class Voeding(Component):
    def __init__(self, label, lokatie, **kwargs):
        super().__init__(label, lokatie, **kwargs)
        self.stroomrichting = "vertical"


class Teller(Component):
    show_number_label = False

    def __init__(self, label, lokatie, **kwargs):
        super().__init__(label, lokatie, **kwargs)
        self.stroomrichting = "horizontal"
        self.tussenruimte_H = 100


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

def increment_y_for_circuitbreaker_descendants(node):
    if isinstance(node, CircuitBreaker):
        for child in node.children:
            # Increment y position of this child and all its descendants
            def increment_y(subnode):
                subnode.y += 2 #hier kan je de kabel langer tekenen na een circuitbreaker
                for c in subnode.children:
                    increment_y(c)
            increment_y(child)
    for child in node.children:
        increment_y_for_circuitbreaker_descendants(child)



# --- Main execution block ---
if __name__ == "__main__":
    # 1. Build the component tree
    reserve = Appliance("reserve_H", "geen")
    kopkwhmeter = Appliance("kop", "appliance")
    teller = Teller("Teller_H", "teller")
    bord1 = Bord("Bord1_V", "bord")
    dif300 = Differential("Diff300_V", "differential", amperage=630, polen=3, millies=300)
    dif30 = Differential("Diff30_V", "differential")
    dif100 = Differential("Diff100_V", "differential")
    dif3 = Differential("Diff3_V", "differential", polen=7, millies=206)
    prieze = Prieze("prieze", "prieze", aantal=1)
    priezedub = Prieze("priezedub", "prieze", aantal=2)
    zek3001 = CircuitBreaker("zek3001_V", "circuit_breaker")
    zek3002 = CircuitBreaker("zek3002_V", "circuit_breaker")
    zek1001 = CircuitBreaker("zek1001_V", "vb", 20, 2, "vob_3x2.5", 36, None)
    zek3003 = CircuitBreaker("zek3003_V", "circuit_breaker")
    zek3004verl = CircuitBreaker("zek3004verl_V", "circuit_breaker")
    vaatwas301 = Appliance("vaatwas301_H met een langenaam", "keuken")
    droogkast3002 = Appliance("droogkast3002_H", "appliance")
    oven3002 = Appliance("oven3002_H", "keuken")
    lamp3004 = Appliance("lamp3004_H", "appliance")
    microoven3002 = Appliance("microoven3002_H", "appliance")
    contaxop3004 = Contax("contaxop3004_H", "appliance")
    contaxopcontax = Contax("contaxopcontax_H", "appliance")
    domo = Domomodule("Domomodule_H", "domomodule")
    verlH6 = Verlichting("centraal", "slpk2", bediening="dim", hydro=False, verlichteknop=False, soort="led", aantal=15)
    verlH = Verlichting("eettafel", "living", bediening="wissel", hydro=False, verlichteknop=False, soort="led",
                        aantal=3)
    verlH2 = Verlichting("phaar", "tuin", bediening="domo", hydro=False, verlichteknop=False, soort="ledstrip",
                         aantal=3)
    verlH3 = Verlichting("dressoir", "living", bediening="tele", hydro=False, verlichteknop=False, soort="led",
                         aantal=3)
    verlH4 = Verlichting("centraal", "garage", bediening="dubbel", hydro=True, verlichteknop=True, soort="gloei",
                         aantal=3)
    verlH5 = Verlichting("kot", "kot", bediening="bewegingmelder", hydro=False, verlichteknop=False, soort="spot",
                         aantal=1)
    zonnepaneelopdif3 = Appliance("zonnepaneelopdif3_H", "appliance")
    faaropcontax = Verlichting("faaropcontax_H", "verlichting", bediening="domodim", hydro=False, verlichteknop=False,
                               soort="led", aantal=3)
    verlicht1 = Verlichting("inkom", "inkom", aantal=2, bediening="domo")
    verlicht2 = Verlichting("Verlicht2_H", "verlichting")
    verlicht3 = Verlichting("Verlicht3_H", "verlichting")
    tv = Appliance("tv_H", "appliance")
    dompelpomp = Appliance("dompelpomp_H", "appliance")
    domo2 = Appliance("domo2_H", "appliance")

    # Establish parent-child relationships
    domo.add_child(verlH)
    prieze.add_child(dompelpomp)
    teller.add_child(dif300, dif30, dif3)
    dif300.add_child(zek3001, zek3002, zek3003)
    zek3001.add_child(droogkast3002)
    zek3002.add_child(oven3002, microoven3002)
    zek3003.add_child(tv, domo2, domo)
    domo2.add_child(verlH2, verlH3, verlH4, verlH5)
    zek3004verl.add_child(verlicht2, verlicht3, lamp3004)
    zek3004verl.add_child(contaxop3004)
    dif300.add_child(zek3004verl)
    zek1001.add_child(vaatwas301, prieze, priezedub, verlH6, verlicht1)
    dif30.add_child(reserve)
    dif300.add_child(dif100)
    contaxop3004.add_child(contaxopcontax)
    contaxopcontax.add_child(faaropcontax)
    dif3.add_child(zonnepaneelopdif3)
    dif100.add_child(zek1001)
    kopkwhmeter.add_child(teller)

    # 2. Set the root and process the tree
    te_tekenen_startpunt = kopkwhmeter
    te_tekenen_startpunt.sort_children()
    te_tekenen_startpunt.assign_coordinates_by_rules()
    increment_y_for_circuitbreaker_descendants(te_tekenen_startpunt)  # Adjustments

    print("--- ASCII Tree with Calculated Coordinates ---")
    te_tekenen_startpunt.print_ascii_tree_with_regel()

    # 3. --- SVG Drawing Logic ---
    print("\n--- Generating SVG file: tree_grid.svg ---")

    # Drawing constants
    CELL_HEIGHT = 80
    H_PADDING = 10
    V_PADDING = 0

    # Get all nodes to determine canvas size
    all_nodes = te_tekenen_startpunt.get_all_nodes()
    max_x = max(node.x for node in all_nodes)
    max_y = max(node.y for node in all_nodes)

    # Use the new logic for per-column widths
    column_widths = te_tekenen_startpunt.compute_column_widths()
    col_x_starts = {}
    x_offset = H_PADDING
    for col_x in range(0, max_x + 1):
        col_x_starts[col_x] = x_offset
        x_offset += column_widths.get(col_x, 60)  # fallback base width

    canvas_width = x_offset + H_PADDING
    canvas_height = (max_y + 1) * CELL_HEIGHT + V_PADDING

    # Create the drawing canvas
    d = dw.Drawing(canvas_width, canvas_height, origin=(0, 0))
    d.append(dw.Rectangle(0, 0, canvas_width, canvas_height, fill='#f5f5f5'))  # Light grey background

    # Iterate through all nodes and draw them
    for node in all_nodes:
        x_pos = col_x_starts[node.x]
        y_pos = node.y * CELL_HEIGHT + V_PADDING
        rect_width = column_widths[node.x]

        cell = dw.Group(id=node.label)
        cell.append(dw.Rectangle(x_pos, y_pos, rect_width - H_PADDING, CELL_HEIGHT - V_PADDING,
                                 fill='lightblue', stroke='black', rx=5, ry=5))
        cell.append(dw.Text(node.label, 15, x_pos + 10, y_pos + 25,
                            font_family="Arial", fill="black"))
        cell.append(dw.Text(f"Grid (x,y): ({node.x}, {node.y})", 12, x_pos + 10, y_pos + 50,
                            font_family="monospace", fill="#444"))
        d.append(cell)

    # Save the SVG file
    d.save_svg("tree_grid.svg")
    print("--- SVG file saved successfully! ---")
