import tkinter as tk
import re
import copy
from PIL import Image, ImageTk
import os
import drawsvg as draw

DEBUG = False  # Set to False for normal operation
ORANGE = False
GEEL = False
GREEN = False
PINK = False
DYNAMICSPACING =  True

class Component:
    show_number_label = True  # Default: de nummer van de takken ,
    show_boundarybox = True
    def __init__(self, label, lokatie, **kwargs):
        self.pixels_tussen_kringen_H = 30 #tussen verschikkende zekeringen horizontaal
        self.pixels_tussen_takken_V = 30 #tussen de lampenen onderling vertikaal
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
        # Optionally extract common expected values
        self.volgorde = kwargs.get("volgorde", None)


    # ---- Usage example:
    # find_and_move_subtree(domo, te_tekenen_startpunt, tempymover=-2, tempxmover_start=1)

    def move_element_met_kinderen(self, dx, dy):
        """
        Shift this node and all descendants by (dx, dy).
        dx: integer - offset in x-direction (relative)
        dy: integer - offset in y-direction (relative)
        """
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

    def draw_svg(self, drawing, x_spacing=0, y_spacing=0, swapy=False):
        if swapy:
            self.swapy()
        pixel_x = self.grid_x + x_spacing
        pixel_y = self.grid_y + y_spacing
        sizex = self.boundarybox_breedte
        sizey = self.boundarybox_hoogte
        naar = f"draw_SGV van({self.label},{self.x})>"
        print(naar)
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
            if DEBUG or GEEL:
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

            # Draw the output stub
            drawing.append(draw.Line(out_abs_x, out_abs_y, stub1_end_x, stub1_end_y, stroke='black', stroke_width=2))
            drawing.save_svg('out.svg')  # Save your vector
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
            drawing.append(draw.Line(in_abs_x, in_abs_y, stub2_end_x, stub2_end_y, stroke='black', stroke_width=2))

            # Store for bus crossing
            child_stub_coords.append((stub2_end_x, stub2_end_y))
            child._parent_stub_end = (stub1_end_x, stub1_end_y)
            child._parent_out_abs_x = out_abs_x
            child._parent_out_abs_y = out_abs_y

        # Bus/bend lines between stubs and children
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



    #************************************

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

    def limit_hoogte(self, hoogtelimiet=6, _recursing=False):
        pass

    def swapy(self):
        """
        Set nulpunt to 'bottom_left' and flip the y coordinate
        for this node and all children, so the grid is drawn
        with (0,0) at the bottom left.
        """
        # 1. Gather all nodes to find max_y
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

    def multiply_coordinates(self, factor):
        """
        Vermenigvuldig alle x- en y-coördinaten in de boom met de opgegeven factor.
        """
        self.grid_x *= factor
        self.grid_y *= factor
        for child in self.children:
            child.multiply_coordinates(factor)


    def insert_kolom_at(self, kolom_index):
        """
        Increase x by 1 for all nodes with x >= kolom_index.
        Prints all nodes with their new x and y values.
        """
        def update_x(component):
            if component.x >= kolom_index:
                component.x += 1
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

    def explode_coordinates_to_canvas(self, x=None, y=None):
        if y is None:
            y = self.pixels_tussen_takken_V
        if x is None:
            x = self.pixels_tussen_kringen_H

        # Default: full width
        width_factor = 1.0
        # Only for direct children
        if isinstance(self.parent, CircuitBreaker):
            width_factor = 0.75

            # Instead of placing based on self.x, always place to the right of parent:
            self.grid_x = self.parent.grid_x + (x + int(width_factor * self.boundarybox_breedte))
        else:
            self.grid_x = self.x * (x + int(width_factor * self.boundarybox_breedte))

        self.grid_y = self.y * (y + self.boundarybox_hoogte)
        if DEBUG:
            print(f"{self.label} = {self.x},{self.y}  {self.grid_x},{self.grid_y}")

        for child in self.children:
            child.explode_coordinates_to_canvas(x, y)

    def oudexplode_coordinates_to_canvas(self, x=None, y=None):
        if y is None:
            y = self.pixels_tussen_takken_V
        if x is None:
            x = self.pixels_tussen_kringen_H

        if self.grid_x is not None and self.grid_y is not None:
            self.grid_x = self.x * (x + int(1 * self.boundarybox_breedte)) #75% = 0.75
            #if child of circuitbreaker then 910verlich6
            #self.grid_x = self.x * (x + int(0.75 * self.boundarybox_breedte)) #75% = 0.75

            self.grid_y = self.y * (y + self.boundarybox_hoogte)
            if DEBUG:
                wiedoenwe = f"{self.label} = {self.x},{self.y}  "
                waartoe = f"  {self.grid_x},{self.grid_y}  "
            for child in self.children:
                child.oudexplode_coordinates_to_canvas(x, y)

    @property
    def connectionpoint_input(self):
        sizex = self.boundarybox_breedte
        sizey = self.boundarybox_hoogte
        ref = self.nulpunt
        HofV = self.stroomrichting
        if self.stroomrichting == "horizontal":
            # Input always at left center (0,50)
            return (0, sizey // 2)  # INPUT  0,50 horizonataal altijd 0,50 Linkerkant
        else:
            if self.nulpunt == "top_left":
                # Bottom center (default)
                return (sizex // 2, 0) # IN vertikaal 50,0 , Bovenaan
            elif self.nulpunt == "bottom_left":
                # Top center for bottom-up logic
                return (sizex // 2, sizey) #50,100 = input langs onderkant
            else:
                return (sizex // 2, 0)

    @property
    def connectionpoint_output(self):
        sizex = self.boundarybox_breedte
        sizey = self.boundarybox_hoogte
        ref = self.nulpunt
        HofV = self.stroomrichting

        if self.stroomrichting == "horizontal":
            # Always right center
            return (sizex, sizey // 2) # Horizontaal OUTPUT altijd 100,50 rechterkant
        else:
            if self.nulpunt == "top_left":
                # Output is at bottom center (default)
                return (sizex // 2, sizey) #vertikaal OUT = 50,100 onderkant
            elif self.nulpunt == "bottom_left":
                # Output is at top center (for bottom-up layouts)
                return (sizex // 2, 0)  # 50,0 bovenkant
            else:
                # Default to top_left logic if something else
                return (sizex // 2, sizey)

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
    show_boundarybox = False
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
        self.image_path = self._build_image_path()
        # Use a smart filename convention for SVG symbol naming
        if vertrekkendelengte is not None:
            self.vertrekkendelengte =   f"__{self.vertrekkendelengte}m"
        else:
            self.vertrekkendelengte = ""

    def _build_image_path(self):
        # Compose a filename that reflects the circuit breaker's properties
        filename = (
            f"differential"
        )
        # Optionally add klemmen information if present
        if self.klemmen:
            filename += f"_klemmen_{self.klemmen}"
        filename += ".svg"
        if DEBUG:
            print(filename)
        return os.path.join("symbolen/Differential", filename)

    def draw_svg(self, drawing, x_spacing=0, y_spacing=0, swapy=False):
        if swapy:
            self.swapy()
        pixel_x = self.grid_x + x_spacing
        pixel_y = self.grid_y + y_spacing
        size_x = self.boundarybox_breedte
        size_y = self.boundarybox_hoogte

        # maroon is voor de arg kwargs
        drawing.append(draw.Text("argkwargs", 5, pixel_x + size_x / 2, pixel_y - size_y / 2,center=True, fill="maroon"))
        # Draw the SVG symbol
        drawing.append(draw.Image(pixel_x, pixel_y, size_x, size_y, self.image_path))
         # Label
        drawing.append(draw.Text(self.label, 15, pixel_x + 10 + self.boundarybox_breedte //2  , pixel_y + self.boundarybox_hoogte,center=False, fill="black"))

        if self.amperage is not None:
            label_stroomsterkte_differentieel = f"{self.amperage}A"
            drawing.append(draw.Text(label_stroomsterkte_differentieel, 15,  pixel_x + 10 + self.boundarybox_breedte //2, pixel_y + self.boundarybox_hoogte - 30 ,center=False, fill="black"))

        if self.millies is not None:
            label_millies_differentieel = f"{self.millies}mA"
            drawing.append(draw.Text(label_millies_differentieel, 15, pixel_x + 50 + self.boundarybox_breedte // 2,pixel_y + self.boundarybox_hoogte - 30, center=False, fill="black"))

        if self.polen is not None:
            label_polen_cicuitbreaker = f"{self.polen}P"
            drawing.append(draw.Text(label_polen_cicuitbreaker, 15, pixel_x + 0, pixel_y + self.boundarybox_hoogte - 15 ,center=False, fill="black"))

        label_kabelinfo = f"{self.vertrekkende_kabel}{self.vertrekkendelengte}"
        #drawing.append(draw.Text(label_vertrekkendelengte, 33, pixel_x + self.boundarybox_breedte  - 55, pixel_y + self.boundarybox_hoogte - 15 ,center=False, fill="black"))



        # Output extra aftakpunt
        if self.connectionpoint_output:
            out_cx, out_cy = self.connectionpoint_output
            out_x = pixel_x + out_cx
            out_y = pixel_y + out_cy
            hoehoogaftakkenvdzekering = 150
            self.secundary_aftakpunt = (out_x, out_y -hoehoogaftakkenvdzekering)
            if DEBUG or PINK:
                drawing.append(draw.Circle(out_x, out_y-hoehoogaftakkenvdzekering, 8, fill='pink'))
                text = f"{out_x} {out_y - hoehoogaftakkenvdzekering}"
                drawing.append(draw.Text(text, 12, out_x-20, out_y - hoehoogaftakkenvdzekering, center=True, fill='pink', valign='top'))

        drawing.save_svg('out.svg')  # Save your vector
        # Draw children recursively MOET
        super().draw_svg(drawing, x_spacing, y_spacing, swapy=False)





class CircuitBreaker(Component):
    show_boundarybox = False
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
        # Use a smart filename convention for SVG symbol naming
        self.image_path = self._build_image_path()

    def _build_image_path(self):
        # Compose a filename that reflects the circuit breaker's properties
        filename = (
            f"circuit_breaker"
        )
        # Optionally add klemmen information if present
        if self.klemmen:
            filename += f"_klemmen_{self.klemmen}"
        filename += ".svg"
        if DEBUG:
            print(filename)
        return os.path.join("symbolen/CircuitBreaker", filename)

    def draw_svg(self, drawing, x_spacing=0, y_spacing=0, swapy=False):
        if swapy:
            self.swapy()
        pixel_x = self.grid_x + x_spacing
        pixel_y = self.grid_y + y_spacing
        size_x = self.boundarybox_breedte
        size_y = self.boundarybox_hoogte

        # maroon is voor de arg kwargs
        drawing.append(draw.Text("argkwarg", 5, pixel_x + size_x / 2, pixel_y - size_y / 2,center=True, fill="maroon"))
        # Draw the SVG symbol
        drawing.append(draw.Image(pixel_x, pixel_y, size_x, size_y, self.image_path))
         # Label (optional, can include amperage/polen)

        label_naam_cicuitbreaker = f"{self.label}"
        drawing.append(draw.Text(label_naam_cicuitbreaker, 15,  pixel_x + 10 + self.boundarybox_breedte //2, pixel_y + self.boundarybox_hoogte,center=False, fill="black"))
        if self.amperage is not None:
            label_stroomsterkte_cicuitbreaker = f"{self.amperage}A"
            drawing.append(draw.Text(label_stroomsterkte_cicuitbreaker, 15, pixel_x + 10 + self.boundarybox_breedte //2, pixel_y + self.boundarybox_hoogte - 30 ,center=False, fill="black"))
        if self.polen is not None:
            label_polen_cicuitbreaker = f"{self.polen}P"
            drawing.append(draw.Text(label_polen_cicuitbreaker, 15, pixel_x + 0, pixel_y + self.boundarybox_hoogte - 15 ,center=False, fill="black"))
        if self.vertrekkendelengte is not None:
            label_vertrekkendelengte = f"{self.vertrekkendelengte}m"
            drawing.append(draw.Text(label_vertrekkendelengte, 20, pixel_x - 60 , pixel_y + self.boundarybox_hoogte - 150 ,center=False, fill="black"))

        if self.vertrekkende_kabel is not None:
            label_kabelinfo = f"{self.vertrekkende_kabel}"
            drawing.append(
                draw.Text(
                    label_kabelinfo,
                    20,
                    pixel_x +20 ,
                    pixel_y + self.boundarybox_hoogte - 80,
                    center=False,
                    fill="black",
                    transform="rotate(-90,{},{})".format(pixel_x + 20, pixel_y + self.boundarybox_hoogte - 80)
                )
            )

        # Output extra aftakpunt
        if self.connectionpoint_output:
            out_cx, out_cy = self.connectionpoint_output
            out_x = pixel_x + out_cx
            out_y = pixel_y + out_cy
            hoehoogaftakkenvdzekering = 150
            self.secundary_aftakpunt = (out_x, out_y -hoehoogaftakkenvdzekering)
            if DEBUG or PINK:
                drawing.append(draw.Circle(out_x, out_y-hoehoogaftakkenvdzekering, 8, fill='pink'))
                text = f"{out_x} {out_y - hoehoogaftakkenvdzekering}"
                drawing.append(draw.Text(text, 12, out_x-20, out_y - hoehoogaftakkenvdzekering, center=True, fill='pink', valign='top'))

        drawing.save_svg('out.svg')  # Save your vector
        # Draw children recursively MOET
        super().draw_svg(drawing, x_spacing, y_spacing, swapy=False)




class Appliance(Component):
    show_boundarybox = False
    def __init__(self, label, lokatie, **kwargs):
        super().__init__(label, lokatie, **kwargs)
        self.stroomrichting = "horizontal"
        self.lijsttoestellen = ["vaatwas" , "droogkast" , "oven" , "reserve"]
        self.image_path =  self._build_image_path()

    def _build_image_path(self):
        # Default image if no appliance keyword is found or file is missing
        default_filename = 'default.svg'
        label_lower = self.label.lower()
        path_dir = 'symbolen/Appliance'
        filename = default_filename
        for toestel in self.lijsttoestellen:
            candidate = f'{toestel}.svg'
            candidate_path = os.path.join(path_dir, candidate)
            if toestel in label_lower:
                if os.path.exists(candidate_path):   # Check if file exists
                    filename = candidate
                else:
                    filename = default_filename
                break
        # If no toestel matched, filename is already 'default.svg'
        return os.path.join(path_dir, filename)


    def draw_svg(self, drawing, x_spacing=0, y_spacing=0, swapy=False):
        if swapy:
            self.swapy()
        pixel_x = self.grid_x + x_spacing
        pixel_y = self.grid_y + y_spacing
        size = self.boundarybox_hoogte

        # Optional: draw a bounding box if needed
        if getattr(self, "show_boundarybox", True):
            drawing.append(draw.Rectangle(pixel_x, pixel_y, size, size, fill="#fff2cc", stroke="black"))

        # Draw the SVG symbol (embed as <image> in SVG)
        drawing.append(draw.Image(pixel_x, pixel_y, size, size, self.image_path))
        # Draw the label (centered)
        drawing.append(draw.Text(self.label, 15, pixel_x - size//2, pixel_y -5 ,center=False, fill="black"))
        # maroon is voor de arg kwargs
        drawing.append(draw.Text("argkwargs", 5, pixel_x + size / 2, pixel_y + size / 2,center=False, fill="maroon"))
        # Continue to recursively draw children/links

        drawing.save_svg('out.svg')  # Save your vector
        super().draw_svg(drawing, x_spacing, y_spacing, swapy=False)



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

import os

class Verlichting(Component):
    show_boundarybox = False
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
        self.image_path_bediening = self._build_image_path_bediening()
        self.image_path_soort = self._build_image_path_soort()
        pass

    def _build_image_path_bediening(self):
        print(self.label)
        if self.bediening:
            path_bediening = os.path.join('symbolen/Verlichting', f'{self.bediening}.svg')
            if os.path.exists(path_bediening):
                return path_bediening


    def _build_image_path_soort(self):
        path_soort = os.path.join('symbolen/Verlichting', f'{self.soort}.svg')
        if os.path.exists(path_soort):
            return path_soort
        # Fallback to default.svg in Soorten folder
        return os.path.join('symbolen/Verlichting', 'default.svg')


    def draw_svg(self, drawing, x_spacing=0, y_spacing=0, swapy=False):
        if swapy:
            self.swapy()
        pixel_x = self.grid_x + x_spacing
        pixel_y = self.grid_y + y_spacing
        size = self.boundarybox_hoogte

        if self.image_path_bediening is None:
            drawing.append(draw.Image(pixel_x, pixel_y, size, size, self.image_path_soort))
            if self.aantal is not None:
                label_aantal = f"{self.aantal}x"
                drawing.append(
                    draw.Text(label_aantal, 15, pixel_x + size + 0, pixel_y + size // 2, center=False, fill="black"))

        else:
            drawing.append(draw.Image(pixel_x, pixel_y, size, size, self.image_path_bediening))
            drawing.append(draw.Image(pixel_x+size, pixel_y, size, size, self.image_path_soort))
            if self.aantal is not None:
                label_aantal = f"{self.aantal}x99"
                drawing.append(
                    draw.Text(label_aantal, 15, pixel_x +size +  size - 0, pixel_y + size // 2, center=False, fill="black"))

        # Draw the label (centered)
        drawing.append(draw.Text(self.label, 15, pixel_x - size // 2, pixel_y - 5, center=False, fill="black"))
        # maroon is voor de arg kwargs
        drawing.append(draw.Text(f"{self.bediening}", 9, pixel_x + size / 2, pixel_y + size / 2, center=False, fill="maroon"))
        drawing.save_svg('out.svg')  # Save your vector
        # Continue to recursively draw children/links
        super().draw_svg(drawing, x_spacing, y_spacing, swapy=False)


class Voeding(Component):
    def __init__(self, label, lokatie, **kwargs):
        super().__init__(label, lokatie, **kwargs)
        self.stroomrichting = "vertical"


class Teller(Component):
    show_number_label = False
    def __init__(self, label, lokatie, **kwargs):
        super().__init__(label, lokatie, **kwargs)
        self.stroomrichting = "horizontal"





import drawsvg as draw



class Prieze(Component):
    show_boundarybox = False
    def __init__(self, label, lokatie, hydro=False, kinderveiligheid=True,
                 aarding=True, aantal=1, image_path=None, **kwargs):
        super().__init__(label, lokatie, **kwargs)
        self.stroomrichting = "horizontal"
        self.hydro = hydro
        self.kinderveiligheid = kinderveiligheid
        self.aarding = aarding
        self.aantal = aantal

        # Change file extension to .svg for your new workflow
        if image_path is not None:
            self.image_path = image_path
        else:
            self.image_path = self._build_image_path()

    def _build_image_path(self):
        filename = (
            f"prieze_hydro_{str(self.hydro).lower()}"
            f"_kinder_{str(self.kinderveiligheid).lower()}"
            f"_aarding_{str(self.aarding).lower()}_{self.aantal}.svg"
        )
        return os.path.join("symbolen/Prieze", filename)

    def draw_svg(self, drawing, x_spacing=0, y_spacing=0, swapy=False):
        if swapy:
            self.swapy()
        pixel_x = self.grid_x + x_spacing
        pixel_y = self.grid_y + y_spacing
        size = self.boundarybox_hoogte
        # Optional: draw a bounding box if needed
        if getattr(self, "show_boundarybox", True):
            drawing.append(draw.Rectangle(pixel_x, pixel_y, size, size, fill="#fff2cc", stroke="black"))

        # Draw the SVG symbol (embed as <image> in SVG)
        drawing.append(draw.Image(pixel_x, pixel_y, size, size, self.image_path))
        # Draw the label (centered)
        drawing.append(draw.Text(self.label, 15, pixel_x - size//2, pixel_y -5 ,center=False, fill="black"))
        # maroon is voor de arg kwargs
        drawing.append(draw.Text("argkwargs", 5, pixel_x + size / 2, pixel_y + size / 2,center=False, fill="maroon"))

        drawing.save_svg('out.svg')  # Save your vector
        # Continue to recursively draw children/links
        super().draw_svg(drawing, x_spacing, y_spacing, swapy=False)







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

    te_tekenen_startpunt.explode_coordinates_to_canvas() #tak en kring tussenruimte
    te_tekenen_startpunt.print_ascii_tree_with_regel()
    #exit()

    # Optionally, explode coordinates to canvas pixels

    # Set canvas size as needed
    canvas_width, canvas_height = te_tekenen_startpunt.get_canvas_size()
    drawing = draw.Drawing(canvas_width + 100, canvas_height + 100)

    te_tekenen_startpunt.draw_svg(drawing, 0, 60, swapy=True)

    drawing.save_svg('out.svg')  # Save your vector

    exit()

    all_cuts_x = collect_all_cuts_x(te_tekenen_startpunt)
    #print("All cut positions:", all_cuts_x)
    print("Unique cuts sorted:", sorted(set(all_cuts_x)))

    # Collect, sort, and ensure unique cut points
    all_cuts_x = collect_all_cuts_x(te_tekenen_startpunt)
    cuts = sorted(set([0] + all_cuts_x))
    canvas_width, canvas_height = te_tekenen_startpunt.get_canvas_size()
    if cuts[-1] < canvas_width:
        cuts.append(canvas_width)  # Ensure you always include the full width

    # Generate one SVG file per indicated section
    for i, (start_x, end_x) in enumerate(zip(cuts, cuts[1:])):
        page_width = end_x - start_x
        drawing = draw.Drawing(page_width, canvas_height + 100)
        te_tekenen_startpunt.draw_svg(
            drawing,
            x_spacing=-start_x+30,  # Offset all coordinates so this page starts left-aligned
            y_spacing=30,
            swapy=True
        )
        svg_filename = f'testree30_page_{i+1}.svg'
        drawing.save_svg(svg_filename)
        #print(f"Saved page {i+1}: x=({start_x}-{end_x}), width={page_width}")

    print("SVG pages exported per cut region.")


from pathlib import Path

path = Path("symbolen/CircuitBreaker/circuitbreaker_2p_16A_1_5mm2.svg")
if path.exists():
    print("YES, the SVG exists.")
else:
    print("NO, the SVG does NOT exist.")
