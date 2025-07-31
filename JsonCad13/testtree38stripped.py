import tkinter as tk
import re
import copy
from PIL import Image, ImageTk
import os
import drawsvg as draw

DEBUG = True  # Set to False for normal operation


class Component:
    show_number_label = True  # Default: de nummer van de takken ,
    show_boundarybox = True
    def __init__(self, label, lokatie, **kwargs):
        self.pixels_tussen_kringen_H = 50 #tussen verschikkende zekeringen horizontaal
        self.pixels_tussen_takken_V = 50 #tussen de lampenen onderling vertikaal
        self.inputstub = 15 #niet langer dan de parameter hierboven doen
        self.outputstub = 15
        self.label = label
        self.lokatie = lokatie
        self.children = []
        self.parent = None
        self.x = 0 #initieel staan ze alllemaal op 0  xy
        self.y = 0

        self.grid_x = 0 #initieel staan ze alllemaal op 0  xy
        self.grid_y = 0

        self.taknummer_x = 0 #initieel staan ze alllemaal op 0  xy
        self.taknummer_y = 0 # dit is lokatie in de svg waar achter een circuitbreaker de nummers staan 8priezen max
        self.allowed_cuts_x =  [] # waarmogenweknippen mutiipage
        self._stroomrichting = None  # "horizontal" or "vertical"
        self.boundarybox_hoogte = 50  # Default size, can be parameterized
        self.boundarybox_breedte = 50  # Default size, can be parameterized
        self.nulpunt = "top_left" # #top_left of bottom_left
        self.kwargs = kwargs  # Store all extra arguments in a dict




    def draw_svg(self, drawing, x_spacing=0, y_spacing=0, swapy=False):
        if swapy:
            self.swapy()
        pixel_x = self.grid_x + x_spacing
        pixel_y = self.grid_y + y_spacing
        sizex = self.boundarybox_breedte
        sizey = self.boundarybox_hoogte

        # Draw the rectangle boundarybox for the component
        if getattr(self, "show_boundarybox", True):
            rect = draw.Rectangle(pixel_x, pixel_y, sizex, sizey, fill='pink', stroke='black', stroke_width=1)
            drawing.append(rect)

        # Draw input/output dots
        dot_radius = 5
        # Input dot (red)
        if self.connectionpoint_input and DEBUG:
            in_cx, in_cy = self.connectionpoint_input
            in_x = pixel_x + in_cx
            in_y = pixel_y + in_cy
            drawing.append(draw.Circle(in_x, in_y, dot_radius, fill='red'))
            #drawing.append(draw.Text("IN", 12, in_x, in_y + 15, center=True, fill='black', valign='top'))
            label_IN = f"IN{in_x} , {in_y}  ,   {self.label}"
            drawing.append(draw.Text(label_IN, 12, in_x, in_y + 15, center=True, fill='black', valign='top'))

        # Output dot (green)
        if self.connectionpoint_output and DEBUG:
            out_cx, out_cy = self.connectionpoint_output
            out_x = pixel_x + out_cx
            out_y = pixel_y + out_cy
            drawing.append(draw.Circle(out_x, out_y, dot_radius, fill='green'))
            #drawing.append(draw.Text("OUT", 12, out_x, out_y + 15, center=True, fill='black', valign='top'))

        # CUT dot (yellow) if vertical
        if self.connectionpoint_input and self.stroomrichting == "vertical":
            in_cx, in_cy = self.connectionpoint_input
            waarmogenweknippen = sizex // 2 + 7
            cut_x = pixel_x + in_cx - waarmogenweknippen
            cut_y = pixel_y + in_cy
            self.allowed_cuts_x.append(cut_x)
            if DEBUG :
                drawing.append(draw.Circle(cut_x, cut_y, dot_radius, fill='yellow'))
                drawing.append(draw.Text("CUT", 12, cut_x, cut_y + 15, center=True, fill='yellow', valign='top'))

        # Draw connections/lines to children
        child_stub_coords = []
        for child in self.children:
            # output coordinate from parent
            out_cx, out_cy = self.connectionpoint_output
            out_abs_x = pixel_x + out_cx
            out_abs_y = pixel_y + out_cy
            # input coordinate for child
            child_px = child.grid_x + x_spacing
            child_py = child.grid_y + y_spacing
            in_cx, in_cy = child.connectionpoint_input
            in_abs_x = child_px + in_cx
            in_abs_y = child_py + in_cy

            # bereken the output stub
            if self.stroomrichting == "horizontal":
                stub1_end_x = out_abs_x + self.outputstub
                stub1_end_y = out_abs_y
            else:
                if self.nulpunt == "top_left":
                    stub1_end_x = out_abs_x
                    stub1_end_y = out_abs_y + self.outputstub
                else:
                    stub1_end_x = out_abs_x
                    stub1_end_y = out_abs_y - self.outputstub
            # bereken de input stub
            if child.stroomrichting == "horizontal":
                stub2_end_x = in_abs_x - child.inputstub
                stub2_end_y = in_abs_y
            else:
                if child.nulpunt == "top_left":
                    stub2_end_x = in_abs_x
                    stub2_end_y = in_abs_y - child.inputstub
                else:
                    stub2_end_x = in_abs_x
                    stub2_end_y = in_abs_y + child.inputstub

            # Draw the INPUT stub
            drawing.append(draw.Line(in_abs_x, in_abs_y, stub2_end_x, stub2_end_y, stroke='red', stroke_width=12))
            # Draw the output stub
            drawing.append(draw.Line(out_abs_x, out_abs_y, stub1_end_x, stub1_end_y, stroke='green', stroke_width=12))
            drawing.save_svg('out.svg')  # Save your vector

            # Store for bus crossing
            child_stub_coords.append((stub2_end_x, stub2_end_y))
            child._parent_stub_end = (stub1_end_x, stub1_end_y)
            child._parent_out_abs_x = out_abs_x
            child._parent_out_abs_y = out_abs_y

        # Bus/bend lines between stubs and children
        if False :
            for idx, child in enumerate(self.children):
                parent_stub_end = child._parent_stub_end
                child_stub_end = child_stub_coords[idx]
                use_secondary = (
                        isinstance(self, CircuitBreaker)
                        and child.stroomrichting == "horizontal"
                        and (child.x - self.x > 1)
                        and getattr(self, "secundary_aftakpunt", None) is not None
                )
                if self.stroomrichting == "vertical":
                    if use_secondary:
                        bus_x, bus_y0 = self.secundary_aftakpunt
                        # Go horizontally first, then vertically to child
                        drawing.append(draw.Line(bus_x, bus_y0, child_stub_end[0], bus_y0, stroke='black', stroke_width=2))
                        drawing.append(draw.Line(child_stub_end[0], bus_y0, child_stub_end[0], child_stub_end[1], stroke='black', stroke_width=2))
                        self.taknummer_x = child_stub_end[0] #waar de 8priezen per kiring nummerstaat
                        self.taknummer_y = child_stub_end[1]

                    else:
                        bus_x = parent_stub_end[0]
                        bus_y0 = parent_stub_end[1]
                        bus_y1 = child_stub_end[1]
                        drawing.append(draw.Line(bus_x, bus_y0, bus_x, bus_y1, stroke='black', stroke_width=2))
                        van = f"van({bus_x},{bus_y0})>"
                        naar = f"naar({bus_x},{bus_y1})>"
                        self.taknummer_x = bus_x #de positie waar de blauwe nummer komt ( max 8 priezen bijvoorbeeld
                        self.taknummer_y = bus_y1
                        drawing.append(draw.Line(bus_x, bus_y1, child_stub_end[0], bus_y1, stroke='black', stroke_width=2))
                        if (child_stub_end[0], bus_y1) != (child_stub_end[0], child_stub_end[1]):
                            drawing.append(draw.Line(child_stub_end[0], bus_y1, child_stub_end[0], child_stub_end[1], stroke='black',stroke_width=2))
                else:
                    # Horizontal parent: default simple elbow logic
                    if parent_stub_end != child_stub_end:
                        crossing_point1 = (child_stub_end[0], parent_stub_end[1])
                        drawing.append(
                            draw.Line(parent_stub_end[0], parent_stub_end[1], crossing_point1[0], crossing_point1[1],
                                      stroke='black', stroke_width=2))
                        drawing.append(
                            draw.Line(crossing_point1[0], crossing_point1[1], child_stub_end[0], child_stub_end[1],
                                      stroke='black', stroke_width=2))
                drawing.save_svg('out.svg')  # Save your vector
                # Child number label as before (optional, unchanged)
                if child.stroomrichting == "horizontal" and self.stroomrichting == "vertical" and getattr(child,"show_number_label",True):
                    in_cx, in_cy = child.connectionpoint_input
                    child_abs_x = child.grid_x + x_spacing + in_cx
                    child_abs_y = child.grid_y + y_spacing + in_cy
                    bus_x = parent_stub_end[0]  # old
                    # If you want the label near the secondary output, use `bus_x, bus_y0` instead in label_x
                    preferred_x = child_abs_x - (self.pixels_tussen_kringen_H + 15)
                    label_x = max(preferred_x, bus_x)
                    label_y = child_abs_y + 15
                    label_x = self.taknummer_x +10
                    label_y = self.taknummer_y + 10
                    drawing.append(draw.Text(str(idx + 1), 17, label_x, label_y, fill='blue', center=True))
                    drawing.save_svg('out.svg')  # Save your vector
                    pass

        # Recurse for children
        for child in self.children:
            child.draw_svg(drawing, x_spacing, y_spacing, swapy=False)


    # ---- Usage example:
    # find_and_move_subtree(domo, te_tekenen_startpunt, tempymover=-2, tempxmover_start=1)

    def move_element_met_kinderen(self, dx, dy):
        self.x += dx
        self.y += dy
        for child in self.children:
            child.move_element_met_kinderen(dx, dy)

    def get_bus_start_coords(self, child, parent_stub_end):
        """
        Helper for draw_svg: Determine where the bus should start for a child.
        Applies special logic for CircuitBreaker with 'late' horizontal child.
        """
        if (
            isinstance(self, CircuitBreaker)
            and child.stroomrichting == "horizontal"
            and (child.x - self.x > 1)
            and getattr(self, "secundary_aftakpunt", None) is not None
        ):
            return self.secundary_aftakpunt
        return parent_stub_end

    def walk_tree(self):
        yield self
        for c in self.children:
            yield from c.walk_tree()

    def get_canvas_size(self):
            max_x = 0
            max_y = 0
            def visit(node):
                nonlocal max_x, max_y
                right = node.grid_x + node.boundarybox_hoogte
                bottom = node.grid_y + node.boundarybox_hoogte
                if right > max_x:
                    max_x = right
                if bottom > max_y:
                    max_y = bottom
                for c in node.children:
                    visit(c)
            visit(self)
            return max_x, max_y

    def swapy(self):
        all_nodes = []
        def collect(node):
            all_nodes.append(node)
            for child in node.children:
                collect(child)
        collect(self)
        max_y = max(node.grid_y for node in all_nodes)
        # 2. Recursively set nulpunt and flip y for all nodes
        def flip_nulpunt_and_y(node):
            node.nulpunt = "bottom_left"
            node.grid_y = max_y - node.grid_y
            for child in node.children:
                flip_nulpunt_and_y(child)
        flip_nulpunt_and_y(self)

    def print_ascii_tree_with_regel(self, prefix=" "):
        regel = getattr(self, "_regel_used", "?")
        print(f"{prefix}{self.label} SVG({self.grid_x},{self.grid_y})  core({self.x},{self.y})\t\t{regel}")
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

    def explode_coordinates_to_canvas(self, x=None, y=None):
        if y is None:
            y = self.pixels_tussen_takken_V
        if x is None:
            x = self.pixels_tussen_kringen_H
        # Default: full width
        width_factor = 1.0
        # Only for direct children
        if isinstance(self.parent, CircuitBreaker):
            width_factor = 1
            # Instead of placing based on self.x, always place to the right of parent:
            self.grid_x = self.parent.grid_x + (x + int(width_factor * self.boundarybox_breedte))
        else:
            self.grid_x = self.x * (x + int(width_factor * self.boundarybox_breedte))

        self.grid_y = self.y * (y + self.boundarybox_hoogte)
        for child in self.children:
            child.explode_coordinates_to_canvas(x, y)



    @property
    def connectionpoint_input(self):
        if self.stroomrichting == "horizontal":
            # Input always at left center (0,50)
            return (0, self.boundarybox_hoogte // 2)  # INPUT  0,50 horizonataal altijd 0,50 Linkerkant
        else:
            if self.nulpunt == "top_left":
                # Bottom center (default)
                return (self.boundarybox_breedte // 2, 0) # IN vertikaal 50,0 , Bovenaan
            elif self.nulpunt == "bottom_left":
                # Top center for bottom-up logic
                return (self.boundarybox_breedte // 2, self.boundarybox_hoogte) #50,100 = input langs onderkant
            else:
                return (self.boundarybox_breedte // 2, 0)

    @property
    def connectionpoint_output(self):
        if self.stroomrichting == "horizontal":
            # Always right center
            return (self.boundarybox_breedte, self.boundarybox_hoogte // 2) # Horizontaal OUTPUT altijd 100,50 rechterkant
        else:
            if self.nulpunt == "top_left":
                # Output is at bottom center (default)
                return (self.boundarybox_breedte // 2, self.boundarybox_hoogte) #vertikaal OUT = 50,100 onderkant
            elif self.nulpunt == "bottom_left":
                # Output is at top center (for bottom-up layouts)
                return (self.boundarybox_breedte // 2, 0)  # 50,0 bovenkant
            else:
                # Default to top_left logic if something else
                return (self.boundarybox_breedte // 2, self.boundarybox_hoogte)

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
    def __init__(self, label, lokatie, amperage=16, polen=2, vertrekkende_kabel="XVB_3G1.5", vertrekkendelengte=None ,  klemmen=None, millies=None, **kwargs):
        super().__init__(label, lokatie, **kwargs)
        self.stroomrichting = "vertical"
        self.amperage = amperage
        self.polen = polen
        self.millies = millies
        self.vertrekkende_kabel = vertrekkende_kabel
        self.vertrekkendelengte = vertrekkendelengte
        self.klemmen = klemmen
        self.lokatie = lokatie
        self.secundary_aftakpunt = None #als je zeer veel elementen op u zekering hebt aangesloten

class CircuitBreaker(Component):
    show_boundarybox = True
    def __init__(self, label, lokatie, amperage=None, polen=None, vertrekkende_kabel=None, vertrekkendelengte=None ,  klemmen=None, image_path=None, **kwargs):
        super().__init__(label, lokatie, **kwargs)
        self.stroomrichting = "vertical"
        self.amperage = amperage
        self.polen = polen
        self.vertrekkende_kabel = vertrekkende_kabel
        self.vertrekkendelengte = vertrekkendelengte
        self.klemmen = klemmen
        self.lokatie = lokatie
        self.secundary_aftakpunt = None #als je zeer veel elementen op u zekering hebt aangesloten

class Appliance(Component):
    def __init__(self, label, lokatie, **kwargs):
        super().__init__(label, lokatie, **kwargs)
        self.stroomrichting = "horizontal"
        self.lijsttoestellen = ["vaatwas", "droogkast", "oven", "reserve"]

    def draw_svg(self, drawing, x_spacing=0, y_spacing=0, swapy=False):
        # First, call the base method to draw the boundary
        super().draw_svg(drawing, x_spacing, y_spacing, swapy)
        # Now, add the text just right of the boundary box
        pixel_x = self.grid_x + x_spacing
        pixel_y = self.grid_y + y_spacing
        label_x = pixel_x + self.boundarybox_breedte + 10  # 10px gap to the right
        label_y = pixel_y + self.boundarybox_hoogte // 2   # Vertically centered
        drawing.append(draw.Text(
            self.label,    # Or any text you'd like
            17,            # Font size
            label_x, label_y,
            fill='blue',
            center=False,    # Or True if you want centering logic
            valign='middle'
        ))

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
    def __init__(self, label, lokatie, bediening=None, hydro=False, verlichteknop=False, soort="gloei", aantal=1, **kwargs):
        super().__init__(label, lokatie, **kwargs)
        self.stroomrichting = "horizontal"
        self.bediening = bediening
        self.hydro = hydro
        self.verlichteknop = verlichteknop
        self.soort = soort
        self.aantal = aantal
        self.ALLOWED_BEDIENINGEN = {None , "dim", "domo", "tele", "wissel", "bewegingmelder", "dubbel", "domodim"}
        self.ALLOWED_SOORTEN = {"led", "gloei", "halogeen", "tl", "ledstrip"}

class Voeding(Component):
    def __init__(self, label, lokatie, **kwargs):
        super().__init__(label, lokatie, **kwargs)
        self.stroomrichting = "vertical"

class Teller(Component):
    def __init__(self, label, lokatie, **kwargs):
        super().__init__(label, lokatie, **kwargs)
        self.stroomrichting = "horizontal"

class Prieze(Component):
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
kopkwhmeter = Appliance("kopkwhmeter_H", "appliance")
teller = Appliance("Teller_H", "teller")
bord1 = Bord("Bord1_V", "bord")
bord1 = Bord("bord1_V", "bord")
dif300 = Differential("Diff300_V", "differential" , amperage=630,polen=3, millies=300)
dif30 = Differential("Diff30_V", "differential")
dif100 = Differential("Diff100_V", "differential")
dif3 = Differential("Diff3_V", "differential",polen=7, millies=206)
prieze = Prieze("prieze", "prieze" , aantal=1)
priezedub = Prieze("priezedub", "prieze" , aantal=2)
zek3001 = CircuitBreaker("zek3001_V", "circuit_breaker")
zek3002 = CircuitBreaker("zek3002_V", "circuit_breaker")
zek1001 = CircuitBreaker("zek1001_V" , "vb"  , 20 , 2 , "vob_3x2.5" , 36, None   ) #(self, label, lokatie, amperage=16, polen=2, vertrekkende_kabel=1.5, klemmen=None, image_path=None, **kwargs):
zek3003 = CircuitBreaker("zek3003_V", "circuit_breaker")
zek3004verl = CircuitBreaker("zek3004verl_V", "circuit_breaker")
vaatwas301 = Appliance("vaatwas301_H", "keuken")
droogkast3002 = Appliance("droogkast3002_H", "appliance")
oven3002 = Appliance("oven3002_H", "keuken")
lamp3004 = Appliance("lamp3004_H", "appliance")
microoven3002 = Appliance("microoven3002_H", "appliance")
contaxop3004 = Contax("contaxop3004_H", "appliance")
contaxopcontax = Contax("contaxopcontax_H", "appliance")
domo = Domomodule("Domomodule_H", "domomodule")
verlH6 = Verlichting("centraal", "slpk2", bediening="dim" , hydro=False ,verlichteknop = False, soort="led" , aantal=15)

verlH = Verlichting("eettafel", "living" , bediening="wissel" , hydro=False ,verlichteknop = False, soort="led" , aantal=3)
verlH2 = Verlichting("phaar", "tuin", bediening="domo" , hydro=False,verlichteknop = False , soort="ledstrip" , aantal=3)
verlH3 = Verlichting("dressoir", "living", bediening="tele" , hydro=False,verlichteknop = False , soort="led" , aantal=3)
verlH4 = Verlichting("centraal", "garage", bediening="dubbel" , hydro=True ,verlichteknop = True, soort="gloei" , aantal=3)
verlH5 = Verlichting("kot", "kot", bediening="bewegingmelder" , hydro=False ,verlichteknop = False, soort="spot" , aantal=1)
zonnepaneelopdif3 = Appliance("zonnepaneelopdif3_H", "appliance")
faaropcontax = Verlichting("faaropcontax_H", "verlichting", bediening="domodim" , hydro=False ,verlichteknop = False, soort="led" , aantal=3)
verlicht1 = Verlichting("inkom", "inkom" , aantal=2 , bediening="domo")
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
zek3004verl.add_child( verlicht2, verlicht3, lamp3004)
zek3004verl.add_child(contaxop3004)
dif300.add_child(zek3004verl)
zek1001.add_child(vaatwas301 , prieze , priezedub , verlH6 , verlicht1)
dif30.add_child(reserve)
dif300.add_child(dif100)
contaxop3004.add_child(contaxopcontax)
contaxopcontax.add_child(faaropcontax)
dif3.add_child(zonnepaneelopdif3)
dif100.add_child(zek1001)
kopkwhmeter.add_child(teller)
# ---- Drawing on Canvas ----

def collect_all_cuts_x(node, result=None):
    if result is None:
        result = []
    # Add this node's allowed_cuts_x (if any)
    result.extend(getattr(node, 'allowed_cuts_x', []))
    for child in getattr(node, 'children', []):
        collect_all_cuts_x(child, result)
    return result

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

def verste_afstammeling_x(node):
    if not node.children:
        return node.x
    return max([node.x] + [verste_afstammeling_x(child) for child in node.children])




if __name__ == "__main__":
    te_tekenen_startpunt = kopkwhmeter
    te_tekenen_startpunt.sort_children()


    te_tekenen_startpunt.assign_coordinates_by_rules()



    # ruimte vorzin om kabeltype te plaatsen in de grid
    increment_y_for_circuitbreaker_descendants(te_tekenen_startpunt)

    #te_tekenen_startpunt.multiply_coordinates(1)
    te_tekenen_startpunt.print_ascii_tree_with_regel()
    #exit()


    #te_tekenen_startpunt.insert_kolom_at(7)
    priezedub.x = priezedub.x +   1
    priezedub.y = priezedub.y + 1
    te_tekenen_startpunt.explode_coordinates_to_canvas() #tak en kring tussenruimte
    te_tekenen_startpunt.print_ascii_tree_with_regel()
    #exit()


    # Optionally, explode coordinates to canvas pixels

    # Set canvas size as needed
    canvas_width, canvas_height = te_tekenen_startpunt.get_canvas_size()
    drawing = draw.Drawing(canvas_width + 100, canvas_height + 100)

    te_tekenen_startpunt.draw_svg(drawing, 50, 50, swapy=True)

    drawing.save_svg('out.svg')  # Save your vector

    exit()



