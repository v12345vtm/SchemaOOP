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
        self.pixels_tussen_kringen_H = 0 #tussen verschikkende zekeringen horizontaal
        self.pixels_tussen_takken_V = 0 #tussen de lampenen onderling vertikaal
        self.inputstub = 20 #niet langer dan de parameter hierboven doen
        self.outputstub = 20
        self.label = label
        self.lokatie = lokatie
        self.children = []
        self.parent = None
        self.x = 0 #initieel staan ze alllemaal op 0  xy
        self.y = 0
        self.grid_x = 0 #initieel staan ze alllemaal op 0  xy
        self.grid_y = 0
        #self.taknummer_x = 0 #initieel staan ze alllemaal op 0  xy
        #self.taknummer_y = 0 # dit is lokatie in de svg waar achter een circuitbreaker de nummers staan 8priezen max
        #self.allowed_cuts_x =  [] # waarmogenweknippen mutiipage
        self._stroomrichting = None  # "horizontal" or "vertical"
        self.boundarybox_hoogte = 50  # Default size, can be parameterized
        self.boundarybox_breedte = 50  # Default size, can be parameterized
        self.nulpunt = "bottom_left" # #top_left of bottom_left
        self.kwargs = kwargs  # Store all extra arguments in a dict

    def get_startingpoints_stubs_from_rect(self, x, y, w, h):
        """
        Returns: (input_point, output_point)
        Each is a tuple (cx, cy), relative to the rectangle's (x,y) origin.
        Uses self.stroomrichting and self.nulpunt.
        For most common cases:
          - horizontal: in = middle left, out = middle right
          - vertical bottom_left: in = bottom middle, out = top middle
          - vertical top_left: in = top middle, out = bottom middle
        """
        # Horizontal object: left to right
        if self.stroomrichting == "horizontal":
            # in: middle left, out: middle right
            cp_in = (x, y + h // 2)
            cp_out = (x + w, y + h // 2)
        # Vertical object
        else:  # self.stroomrichting == "vertical":
            # top-left base
            if self.nulpunt == "bottom_left":
                cp_in = (x + w // 2, y + h)
                cp_out = (x + w // 2, y)
            # bottom-left base
            else:  # nulpunt == "bottom_left"
                cp_in = (x + w // 2, y)
                cp_out = (x + w // 2, y + h)
        return cp_in, cp_out

    def _update_bounds(self, *points):
        for x, y in points:
            if not hasattr(self, 'maxx') or x > self.maxx:
                self.maxx = x
            if not hasattr(self, 'maxy') or y > self.maxy:
                self.maxy = y

    def svg_draw_rect(self, drawing, x, y, w, h, **kwargs):
        rect = draw.Rectangle(x, y, w, h, **kwargs)
        drawing.append(rect)
        self._update_bounds((x + w, y + h))
        return rect

    def svg_draw_line(self, drawing, x1, y1, x2, y2, **kwargs):
        line = draw.Line(x1, y1, x2, y2, **kwargs)
        drawing.append(line)
        self._update_bounds((x1, y1), (x2, y2))
        return line

    def svg_draw_circle(self, drawing, cx, cy, r, **kwargs):
        circle = draw.Circle(cx, cy, r, **kwargs)
        drawing.append(circle)
        self._update_bounds((cx + r, cy + r))
        return circle



    def svg_draw_text(self, drawing, text, x, y, font_size=20, **kwargs):
        # Default: left-aligned
        t = draw.Text(text, font_size, x, y, anchor='start', **kwargs)
        drawing.append(t)
        # Estimate where the text will END if drawn left-aligned
        est_width = len(str(text)) * font_size * 0.55
        end_x = x + est_width
        self._update_bounds((end_x, y))
        return t, end_x  # Return both the Text object and the estimated right edge

    def svg_draw_image(self, drawing,  x, y, w, h,href, **kwargs):
        """
        Add an external image or SVG to the drawing at (x, y), size (w, h).
        href: path or URL to an image or SVG
        """
        img = draw.Image(x, y, w, h, href, **kwargs)
        drawing.append(img)
        # Update bounds for layout logic
        self._update_bounds((x + w, y + h))
        return img

    def draw_input_stub(self, drawing, connection_point):
        """
        Draws the input stub starting from the connection_point.
        The stub extends away from the boundary box.
        """
        start_x, start_y = connection_point
        end_x, end_y = start_x, start_y # Initialize

        if self.stroomrichting == "horizontal":
            # For horizontal, input is on the left side (x decreases away from box)
            end_x = start_x - self.inputstub
        else: # vertical
            if self.nulpunt == "bottom_left":
                # For vertical top_left, input is on bottom side (y increases away from box)
                end_y = start_y + self.inputstub
            else: # bottom_left
                # For vertical bottom_left, input is on top side (y decreases away from box)
                end_y = start_y - self.inputstub

        self.svg_draw_line(drawing, start_x, start_y, end_x, end_y, stroke='red', stroke_width=2)
        return (end_x, end_y)

    def draw_output_stub(self, drawing, connection_point):
        """
        Draws the output stub starting from the connection_point.
        The stub extends away from the boundary box.
        """
        start_x, start_y = connection_point
        end_x, end_y = start_x, start_y # Initialize

        if self.stroomrichting == "horizontal":
            # For horizontal, output is on the right side (x increases away from box)
            end_x = start_x + self.outputstub
        else: # vertical
            if self.nulpunt == "bottom_left":
                # For vertical bottom_left, output is on top side (y decreases away from box)
                end_y = start_y - self.outputstub
            else: # topleft
                # For vertical topleft, output is on bottom side (y increases away from box)
                end_y = start_y + self.outputstub

        self.svg_draw_line(drawing, start_x, start_y, end_x, end_y, stroke='green', stroke_width=2)
        return (end_x, end_y)



    def draw_object_with_bounds(self):
         # Prepare drawing canvas (make a bit bigger than box) achteraf doen we CROP  # ons canvas tekenblad nemen we niet mee in de maxx maxy
        drawing = draw.Drawing(600, 600)
        object_box = draw.Rectangle(0, 0, 600, 600, fill='pink', stroke='black', stroke_width=1)
        box_w = getattr(self, 'boundarybox_breedte', 100)
        box_h = getattr(self, 'boundarybox_hoogte', 100)
        x, y = 50, 50  # offset inside canvas
        #boundarybox = self.svg_draw_rect(drawing, x, y, box_w, box_h, fill='pink' , stroke="black" ,stroke_width=1)
        boundarybox = self.svg_draw_image(drawing, x, y, self.boundarybox_breedte, self.boundarybox_hoogte,
                                     os.path.join("symbolen", "NoSymbol", "default.svg"))

    # Get input and output connection points
        conn_in, conn_out = self.get_startingpoints_stubs_from_rect(x, y, box_w, box_h)
        stub_in_rood = self.svg_draw_circle(drawing, conn_in[0], conn_in[1],6, fill="brown")
        stub_out_groen = self.svg_draw_circle(drawing ,conn_out[0], conn_out[1], 6, fill="brown")
        # <<< NEW: Draw the input and output stubs >>>
        effectieve_IN = self.draw_input_stub(drawing, conn_in)
        effectieve_OUT = self.draw_output_stub(drawing, conn_out)
        connectionpoint_in_rood = self.svg_draw_circle(drawing, effectieve_IN[0], effectieve_IN[1], 6, fill="red")
        connectionpoint_out_groen = self.svg_draw_circle(drawing, effectieve_OUT[0], effectieve_OUT[1], 6, fill="green")

        IN = self.svg_draw_text(drawing, "IN", conn_in[0], conn_in[1])
        label = self.svg_draw_text(drawing, self.label,box_w+  x + 16, 130)
        lokatie = self.svg_draw_text(drawing, self.lokatie, box_w + x + 16, 140 , font_size=10)


        #visuele kader om te zien wat er in ons symbool zit
        effectieve_omkadering_dynamisch = draw.Rectangle(0, 0, self.maxx + 8, self.maxy +8, fill='white', fill_opacity=0.3, stroke='red',stroke_width=1)
        drawing.append(effectieve_omkadering_dynamisch)

        # Save as <label>-temp.svg Drawn Diff30_V at max (254.0, 156)
        save_label = ''.join(c if c.isalnum() else '_' for c in str(self.label))
        drawing.save_svg(f'{save_label}-temp.svg')

        # At the end:
        drawing_final = draw.Drawing(self.maxx, self.maxy)
        for element in drawing.elements:
            drawing_final.append(element)
        drawing_final.save_svg(f'{save_label}-cropped.svg')







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
            #rect = draw.Rectangle(pixel_x, pixel_y, sizex, sizey, fill='pink', stroke='black', stroke_width=1)
            #drawing.append(rect)
            pass

        label = self.svg_draw_text(drawing, self.label,pixel_x+  sizex + 16, pixel_y)
        lokatie = self.svg_draw_text(drawing, self.lokatie, pixel_x + sizex + 16, pixel_y , font_size=10)
        labeltest = self.svg_draw_text(drawing, "hoi", self.grid_x  , self.grid_y)
        boundarybox = self.svg_draw_image(drawing, self.grid_x  , self.grid_y, self.boundarybox_breedte, self.boundarybox_hoogte,
                                     os.path.join("symbolen", "NoSymbol", "default.svg"))

        # Get input and output connection points
        conn_in, conn_out = self.get_startingpoints_stubs_from_rect(self.grid_x  , self.grid_y, self.boundarybox_breedte,  self.boundarybox_hoogte)
        stub_in_rood = self.svg_draw_circle(drawing, conn_in[0], conn_in[1], 6, fill="brown")
        stub_out_groen = self.svg_draw_circle(drawing, conn_out[0], conn_out[1], 6, fill="brown")
        # <<< NEW: Draw the input and output stubs >>>
        effectieve_IN = self.draw_input_stub(drawing, conn_in)
        effectieve_OUT = self.draw_output_stub(drawing, conn_out)
        connectionpoint_in_rood = self.svg_draw_circle(drawing, effectieve_IN[0], effectieve_IN[1], 6, fill="red")
        connectionpoint_out_groen = self.svg_draw_circle(drawing, effectieve_OUT[0], effectieve_OUT[1], 6, fill="green")

        IN = self.svg_draw_text(drawing, "IN", conn_in[0], conn_in[1])
        label = self.svg_draw_text(drawing, self.label, self.boundarybox_breedte + self.grid_x + 16, 130)
        lokatie = self.svg_draw_text(drawing, self.lokatie, self.boundarybox_breedte + self.grid_x + 16, 140, font_size=10)

        # Recurse for children
        for child in self.children:
            child.draw_svg(drawing, x_spacing, y_spacing, swapy=False)





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

    def explode_coordinates_to_canvas(self):
        """
        Assigns self.grid_x, self.grid_y based on dynamic object sizes,
        so columns (by x) are spaced by the widest actual object in that column.
        """
        # First: gather all nodes, and note their .x and .y and .maxx, .maxy
        all_nodes = list(self.walk_tree())
        if not all_nodes:
            return
        num_cols = max(n.x for n in all_nodes) + 1
        num_rows = max(n.y for n in all_nodes) + 1

        # Size per column & per row
        max_widths = [0] * num_cols
        max_heights = [0] * num_rows
        for node in all_nodes:
            if hasattr(node, 'maxx'):
                if node.maxx > max_widths[node.x]:
                    max_widths[node.x] = node.maxx
                if node.maxy > max_heights[node.y]:
                    max_heights[node.y] = node.maxy

        # Compute column and row offsets (cumulative from 0)
        col_offset = [0]
        for w in max_widths[:-1]:
            col_offset.append(col_offset[-1] + w + node.pixels_tussen_kringen_H)
        row_offset = [0]
        for h in max_heights[:-1]:
            row_offset.append(row_offset[-1] + h + node.pixels_tussen_takken_V)

        # Assign canvas coordinates
        for node in all_nodes:
            node.grid_x = col_offset[node.x]
            node.grid_y = row_offset[node.y]




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

        # Use a smart filename convention for SVG symbol naming
        if vertrekkendelengte is not None:
            self.vertrekkendelengte =   f"__{self.vertrekkendelengte}m"
        else:
            self.vertrekkendelengte = ""




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
        # Use a smart filename convention for SVG symbol naming



class Appliance(Component):
    show_boundarybox = True
    def __init__(self, label, lokatie, **kwargs):
        super().__init__(label, lokatie, **kwargs)
        self.stroomrichting = "horizontal"
        self.lijsttoestellen = ["vaatwas" , "droogkast" , "oven" , "reserve"]

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


    def _build_image_path_bediening(self):
        print(self.label)


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
    show_boundarybox = True
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
kopkwhmeter = Appliance("kop", "appliance")
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
vaatwas301 = Appliance("vaatwas301_H met een langenaam", "keuken")
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




    te_tekenen_startpunt.print_ascii_tree_with_regel()

    #te_tekenen_startpunt.draw_object_with_bounds()



    for node in te_tekenen_startpunt.walk_tree():
        node.draw_object_with_bounds()
        print(f"Drawn {node.label} at max ({node.maxx}, {node.maxy})  xy=({node.x}, {node.y}) ")



    te_tekenen_startpunt.explode_coordinates_to_canvas()




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
        drawing = draw.Drawing(2000, 1600 )
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
