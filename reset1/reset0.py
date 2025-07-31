import re
import copy
import drawsvg as dw  # Import drawsvg

class Component:
    show_number_label = True  # Default: de nummer van de takken ,
    show_boundarybox = True

    def __init__(self, label, lokatie, **kwargs):
        self.pixels_tussen_kringen_H = 0  # tussen verschikkende zekeringen horizontaal
        self.pixels_tussen_takken_V = 0  # tussen de lampenen onderling vertikaal
        self.inputstub = 20  # niet langer dan de parameter hierboven doen
        self.outputstub = 20
        self.label = label
        self.lokatie = lokatie
        self.children = []
        self.parent = None
        self.x = 0  # initieel staan ze alllemaal op 0  xy
        self.y = 0
        self.canvas_x = 0  # initieel staan ze alllemaal op 0  xy
        self.canvas_y = 0
        self._stroomrichting = None  # "horizontal" or "vertical"
        self.boundarybox_hoogte = 50  # Default size, can be parameterized
        self.boundarybox_breedte = 50  # Default size, can be parameterized
        self.nulpunt = "bottom_left"  # #top_left of bottom_left
        self.kwargs = kwargs  # Store all extra arguments in a dict
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
        """
        Wijs coördinaten toe aan alle nodes volgens de aangepaste regels.
        Annotatie: node._regel_used (string).
        """

        def deepest_descendant_x(node):
            """Grootste x in de subboom."""
            xs = [node.x]
            for child in node.children:
                xs.append(deepest_descendant_x(child))
            return max(xs)

        def deepest_descendant_y(node):
            """Grootste y in de subboom."""
            ys = [node.y]
            for child in node.children:
                ys.append(deepest_descendant_y(child))
            return max(ys)

        def visit(node, parent=None, prev_sibling=None):
            # Regel 1: root
            if parent is None:
                node.x, node.y = 0, 0
                node._regel_used = "regel 1"
            else:
                pdir = parent.stroomrichting
                ndir = node.stroomrichting

                # vorige broer info
                if prev_sibling is not None:
                    prev_x = prev_sibling.x
                    prev_y = prev_sibling.y
                    prev_far_x = deepest_descendant_x(prev_sibling)
                    prev_far_y = deepest_descendant_y(prev_sibling)
                else:
                    prev_x = prev_y = prev_far_x = prev_far_y = None

                # Regel 2: V kind met V ouder
                if pdir == "vertical" and ndir == "vertical":
                    if prev_sibling:
                        # regel 2a
                        node.x = prev_far_x + 1
                        node.y = prev_y
                        node._regel_used = "regel 2a"
                    else:
                        # regel 2b
                        node.x = parent.x
                        node.y = parent.y + 1
                        node._regel_used = "regel 2b"

                # Regel 3: H kind met V ouder
                elif pdir == "vertical" and ndir == "horizontal":
                    if prev_sibling:
                        # regel 3a
                        node.x = prev_x
                        node.y = prev_far_y + 1  # aangepaste regel!
                        node._regel_used = "regel 3a"
                    else:
                        # regel 3b
                        node.x = parent.x + 1
                        node.y = parent.y + 1
                        node._regel_used = "regel 3b"

                # Regel 4: H kind met H ouder
                elif pdir == "horizontal" and ndir == "horizontal":
                    if prev_sibling:
                        # regel 4a
                        node.x = prev_x
                        node.y = prev_y + 1
                        node._regel_used = "regel 4a"
                    else:
                        # regel 4b
                        node.x = parent.x + 1
                        node.y = parent.y
                        node._regel_used = "regel 4b"

                # Regel 5: V kind met H ouder
                elif pdir == "horizontal" and ndir == "vertical":
                    if prev_sibling:
                        # regel 5a
                        node.x = prev_far_x + 1
                        node.y = parent.y + 1
                        node._regel_used = "regel 5a"
                    else:
                        # regel 5b
                        node.x = parent.x + 1
                        node.y = parent.y + 1
                        node._regel_used = "regel 5b"
                else:
                    # fallback
                    node.x = parent.x + 1
                    node.y = parent.y + 1
                    node._regel_used = "fallback"

            # Recursief voor kinderen, met bijhouden van vorige broer
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
                child = child.clone()  # Use the clone instead
            child.parent = self
            self.children.append(child)

    def sort_children(self):
        """Sort children by number in label, fallback to alphabetical."""
        self.children.sort(key=lambda c: (Component.extract_int(c.label), c.label))
        for child in self.children:
            child.sort_children()

    @staticmethod
    def extract_int(label):
        """Extract the first integer found in the label, or return inf if not found."""
        match = re.search(r'\d+', label)
        return int(match.group()) if match else float('inf')


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
        self.secundary_aftakpunt = None  # als je zeer veel elementen op u zekering hebt aangesloten


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
        self.secundary_aftakpunt = None  # als je zeer veel elementen op u zekering hebt aangesloten
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
    def __init__(self, label, lokatie, bediening=None, hydro=False, verlichteknop=False, soort="gloei", aantal=1,                 **kwargs):
        super().__init__(label, lokatie, **kwargs)
        self.stroomrichting = "horizontal"
        self.boundarybox_hoogte = 50  # Default size, can be parameterized
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


# Example tree
reserve = Appliance("reserve_H", "geen")
kopkwhmeter = Appliance("kop", "appliance")
teller = Appliance("Teller_H", "teller")
bord1 = Bord("Bord1_V", "bord")
bord1 = Bord("bord1_V", "bord")
dif300 = Differential("Diff300_V", "differential", amperage=630, polen=3, millies=300)
dif30 = Differential("Diff30_V", "differential")
dif100 = Differential("Diff100_V", "differential")
dif3 = Differential("Diff3_V", "differential", polen=7, millies=206)
prieze = Prieze("prieze", "prieze", aantal=1)
priezedub = Prieze("priezedub", "prieze", aantal=2)
zek3001 = CircuitBreaker("zek3001_V", "circuit_breaker")
zek3002 = CircuitBreaker("zek3002_V", "circuit_breaker")
zek1001 = CircuitBreaker("zek1001_V", "vb", 20, 2, "vob_3x2.5", 36,
                         None)  # (self, label, lokatie, amperage=16, polen=2, vertrekkende_kabel=1.5, klemmen=None, image_path=None, **kwargs):
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
domo2 = Appliance("domo2_H", "appliance")
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

if __name__ == "__main__":
    te_tekenen_startpunt = kopkwhmeter
    te_tekenen_startpunt.sort_children()  # Sort children first

    te_tekenen_startpunt.assign_coordinates_by_rules()  # Assign initial (x, y) grid coords
    te_tekenen_startpunt.print_ascii_tree_with_regel()
