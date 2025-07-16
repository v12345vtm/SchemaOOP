import tkinter as tk
import re
import copy
from PIL import Image, ImageTk
import os
import drawsvg as draw

'''"DPI","Width (px)","Height (px)"
"72 DPI","595","842"
"150 DPI","1240","1754"
"300 DPI","2480","3508"
"600 DPI","4960","7016"
"1200 DPI","9920","14032"'''

class Component:
    show_number_label = True  # Default: de nummer van de takken ,
    show_boundarybox = True
    def __init__(self, label, component_type, **kwargs):
        self.pixels_tussen_kringen_H = 40 #tussen verschikkende zekeringen horizontaal
        self.pixels_tussen_takken_V = 40 #tussen de lampenen onderling vertikaal
        self.label = label
        self.component_type = component_type
        self.children = []
        self.parent = None
        self.x = 0
        self.y = 0
        self.allowed_cuts_x =  [] # waarmogenweknippen mutiipage
        self._stroomrichting = None  # "horizontal" or "vertical"
        self.boundarybox_hoogte = 50  # Default size, can be parameterized
        self.boundarybox_breedte = 50  # Default size, can be parameterized
        self.nulpunt = "top_left" # #top_left of bottom_left
        self.kwargs = kwargs  # Store all extra arguments in a dict
        # Optionally extract common expected values
        self.volgorde = kwargs.get("volgorde", None)



    def draw_svg(self, drawing, x_spacing=0, y_spacing=0, swapy=False):
        if swapy:
            self.swapy()

        pixel_x = self.x + x_spacing
        pixel_y = self.y + y_spacing
        size = self.boundarybox_hoogte

        # Draw the rectangle boundarybox for the component
        if getattr(self, "show_boundarybox", True):
            rect = draw.Rectangle(pixel_x, pixel_y, size, size, fill='pink', stroke='black', stroke_width=1)
            drawing.append(rect)

        # Draw the label (text above the box)
        label_x = pixel_x + size // 2
        label_y = pixel_y - size // 6  # Above the top
        text = draw.Text(self.label, 15, label_x, label_y, center=True, fill='black')
        drawing.append(text)

        # Draw input/output dots
        dot_radius = 5

        # Input dot (red)
        if self.connectionpoint_input:
            in_cx, in_cy = self.connectionpoint_input
            in_x = pixel_x + in_cx
            in_y = pixel_y + in_cy
            drawing.append(draw.Circle(in_x, in_y, dot_radius, fill='red'))
            drawing.append(draw.Text("IN", 12, in_x, in_y + 15, center=True, fill='black', valign='top'))

        # Output dot (green)
        if self.connectionpoint_output:
            out_cx, out_cy = self.connectionpoint_output
            out_x = pixel_x + out_cx
            out_y = pixel_y + out_cy
            drawing.append(draw.Circle(out_x, out_y, dot_radius, fill='green'))
            drawing.append(draw.Text("OUT", 12, out_x, out_y + 15, center=True, fill='black', valign='top'))

        # CUT dot (yellow) if vertical
        if self.connectionpoint_input and self.stroomrichting == "vertical":
            in_cx, in_cy = self.connectionpoint_input
            waarmogenweknippen = size // 2 + 7
            cut_x = pixel_x + in_cx - waarmogenweknippen
            cut_y = pixel_y + in_cy
            drawing.append(draw.Circle(cut_x, cut_y, dot_radius, fill='yellow'))
            drawing.append(draw.Text("CUT", 12, cut_x, cut_y + 15, center=True, fill='black', valign='top'))
            self.allowed_cuts_x.append(cut_x)
            #print(f"we mogen een cut doen op {cut_x}")

        # Draw connections/lines to children
        stub_length_H = self.pixels_tussen_kringen_H // 2
        stub_length_V = self.pixels_tussen_takken_V // 2
        child_stub_coords = []
        for child in self.children:
            # output coordinate from parent
            out_cx, out_cy = self.connectionpoint_output
            out_abs_x = pixel_x + out_cx
            out_abs_y = pixel_y + out_cy
            # input coordinate for child
            child_px = child.x + x_spacing
            child_py = child.y + y_spacing
            in_cx, in_cy = child.connectionpoint_input
            in_abs_x = child_px + in_cx
            in_abs_y = child_py + in_cy

            # Parent output stub
            if self.stroomrichting == "horizontal":
                stub1_end_x = out_abs_x + stub_length_H
                stub1_end_y = out_abs_y
            else:
                if self.nulpunt == "top_left":
                    stub1_end_x = out_abs_x
                    stub1_end_y = out_abs_y + stub_length_V
                else:
                    stub1_end_x = out_abs_x
                    stub1_end_y = out_abs_y - stub_length_V

            # Draw the parent stub
            drawing.append(draw.Line(out_abs_x, out_abs_y, stub1_end_x, stub1_end_y, stroke='black', stroke_width=2))

            # Child input stub
            if child.stroomrichting == "horizontal":
                stub2_end_x = in_abs_x - stub_length_H
                stub2_end_y = in_abs_y
            else:
                if child.nulpunt == "top_left":
                    stub2_end_x = in_abs_x
                    stub2_end_y = in_abs_y - stub_length_V
                else:
                    stub2_end_x = in_abs_x
                    stub2_end_y = in_abs_y + stub_length_V

            # Draw the child stub
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

            if self.stroomrichting == "vertical":
                bus_x = parent_stub_end[0]
                bus_y0 = parent_stub_end[1]
                bus_y1 = child_stub_end[1]
                drawing.append(draw.Line(bus_x, bus_y0, bus_x, bus_y1, stroke='black', stroke_width=2))
                drawing.append(draw.Line(bus_x, bus_y1, child_stub_end[0], bus_y1, stroke='black', stroke_width=2))
                # Branch as needed for vertical bus/child
                if (child_stub_end[0], bus_y1) != (child_stub_end[0], child_stub_end[1]):
                    drawing.append(
                        draw.Line(child_stub_end[0], bus_y1, child_stub_end[0], child_stub_end[1], stroke='black',
                                  stroke_width=2))
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

            # Child number label (same as your logic)
            if child.stroomrichting == "horizontal" and self.stroomrichting == "vertical" and getattr(child,
                                                                                                      "show_number_label",
                                                                                                      True):
                in_cx, in_cy = child.connectionpoint_input
                child_abs_x = child.x + x_spacing + in_cx
                child_abs_y = child.y + y_spacing + in_cy
                bus_x = parent_stub_end[0]
                preferred_x = child_abs_x - (self.pixels_tussen_kringen_H + 15)
                label_x = max(preferred_x, bus_x)
                label_y = child_abs_y + 15
                drawing.append(draw.Text(str(idx + 1), 15, label_x, label_y, fill='blue', center=True))

        # Recurse for children
        for child in self.children:
            child.draw_svg(drawing, x_spacing, y_spacing, swapy=False)


    def get_canvas_size(self):
            max_x = 0
            max_y = 0

            def visit(node):
                nonlocal max_x, max_y
                right = node.x + node.boundarybox_hoogte
                bottom = node.y + node.boundarybox_hoogte
                if right > max_x:
                    max_x = right
                if bottom > max_y:
                    max_y = bottom
                for c in node.children:
                    visit(c)

            visit(self)
            return max_x, max_y

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
        max_y = max(node.y for node in all_nodes)

        # 2. Recursively set nulpunt and flip y for all nodes
        def flip_nulpunt_and_y(node):
            node.nulpunt = "bottom_left"
            node.y = max_y - node.y
            for child in node.children:
                flip_nulpunt_and_y(child)

        flip_nulpunt_and_y(self)

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
        self.x *= factor
        self.y *= factor
        for child in self.children:
            child.multiply_coordinates(factor)


    def limit_hoogte(self, hoogtelimiet=5):
        pass

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
        if self.x is not None and self.y is not None:
            self.x = self.x * (x + self.boundarybox_hoogte)
            self.y = self.y * (y + self.boundarybox_hoogte)
            for child in self.children:
                child.explode_coordinates_to_canvas(x, y)

    @property
    def connectionpoint_input(self):
        size = self.boundarybox_hoogte
        ref = self.nulpunt
        HofV = self.stroomrichting
        if self.stroomrichting == "horizontal":
            # Input always at left center (0,50)
            return (0, size // 2)  # INPUT  0,50 horizonataal altijd 0,50 Linkerkant
        else:
            if self.nulpunt == "top_left":
                # Bottom center (default)
                return (size // 2, 0) # IN vertikaal 50,0 , Bovenaan
            elif self.nulpunt == "bottom_left":
                # Top center for bottom-up logic
                return (size // 2, size) #50,100 = input langs onderkant
            else:
                return (size // 2, 0)

    @property
    def connectionpoint_output(self):
        size = self.boundarybox_hoogte
        ref = self.nulpunt
        HofV = self.stroomrichting

        if self.stroomrichting == "horizontal":
            # Always right center
            return (size, size // 2) # Horizontaal OUTPUT altijd 100,50 rechterkant
        else:
            if self.nulpunt == "top_left":
                # Output is at bottom center (default)
                return (size // 2, size) #vertikaal OUT = 50,100 onderkant
            elif self.nulpunt == "bottom_left":
                # Output is at top center (for bottom-up layouts)
                return (size // 2, 0)  # 50,0 bovenkant
            else:
                # Default to top_left logic if something else
                return (size // 2, size)




    def contains_node(self, node):
        if self is node:
            return True
        for child in self.children:
            if child.contains_node(node):
                return True
        return False

    def clone(self):
        return copy.deepcopy(self)

    def oudadd_child(self, *children):
        for child in children:
            child.parent = self
            self.children.append(child)

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
    def __init__(self, label, component_type, **kwargs):
        super().__init__(label, component_type, **kwargs)
        self.stroomrichting = "vertical"


class CircuitBreaker(Component):
    def __init__(self, label, component_type, **kwargs):
        super().__init__(label, component_type, **kwargs)
        self.stroomrichting = "vertical"




class Appliance(Component):
    def __init__(self, label, component_type, **kwargs):
        super().__init__(label, component_type, **kwargs)
        self.stroomrichting = "horizontal"


class Hoofddifferentieel(Component):
    def __init__(self, label, component_type, **kwargs):
        super().__init__(label, component_type, **kwargs)
        self.stroomrichting = "horizontal"


class HoofdAutomaat(Component):
    def __init__(self, label, component_type, **kwargs):
        super().__init__(label, component_type, **kwargs)
        self.stroomrichting = "horizontal"


class Domomodule(Component):
    def __init__(self, label, component_type, **kwargs):
        super().__init__(label, component_type, **kwargs)
        self.stroomrichting = "horizontal"


class Contax(Component):
    def __init__(self, label, component_type, **kwargs):
        super().__init__(label, component_type, **kwargs)
        self.stroomrichting = "horizontal"


class Verlichting(Component):
    def __init__(self, label, component_type, **kwargs):
        super().__init__(label, component_type, **kwargs)
        self.stroomrichting = "horizontal"


class Voeding(Component):
    def __init__(self, label, component_type, **kwargs):
        super().__init__(label, component_type, **kwargs)
        self.stroomrichting = "vertical"


class Teller(Component):
    show_number_label = False
    def __init__(self, label, component_type, **kwargs):
        super().__init__(label, component_type, **kwargs)
        self.stroomrichting = "horizontal"





import drawsvg as draw



class Prieze(Component):
    show_boundarybox = False

    def __init__(self, label, component_type, hydro=False, kinderveiligheid=True,
                 aarding=True, aantal=1, image_path=None, **kwargs):
        super().__init__(label, component_type, **kwargs)
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
        pixel_x = self.x + x_spacing
        pixel_y = self.y + y_spacing
        size = self.boundarybox_hoogte

        # Optional: draw a bounding box if needed
        if getattr(self, "show_boundarybox", True):
            drawing.append(draw.Rectangle(pixel_x, pixel_y, size, size, fill="#fff2cc", stroke="black"))

        # Draw the SVG symbol (embed as <image> in SVG)
        # Assumes your SVG symbol is a complete SVG file and path is correct
        drawing.append(draw.Image(pixel_x, pixel_y, size, size, self.image_path))

        # Draw the label (centered)
        drawing.append(draw.Text(
            self.label, 12, pixel_x + size / 2, pixel_y + size / 2,
            center=True, fill="red"
        ))

        # Continue to recursively draw children/links
        super().draw_svg(drawing, x_spacing, y_spacing, swapy=False)


class Fotoprinten(Component):
    """
    Prieze: displays an image inside its boundary box on a Tkinter canvas.

    Usage:
        prieze = Prieze("prieze", "prieze")
        ... # add to your component tree as before

    Requirements:
      - Image file (e.g. PNG) must exist at the expected path.
      - To avoid garbage collection, a persistent reference is kept on the instance and the canvas.
    """
    def __init__(self, label, component_type, image_path="symbolen/prieze_hydro_false_kinder_true_aarding_true_1.png", **kwargs):
        super().__init__(label, component_type, **kwargs)
        self.stroomrichting = "horizontal"
        self.image_path = image_path
        self._tk_img = None  # holds the PhotoImage reference

    def draw_recursive_top_left(self, canvas, x_spacing=0, y_spacing=0, swapy=False):
        import os
        if swapy:
            self.swapy()
        pixel_x = self.x + x_spacing
        pixel_y = self.y + y_spacing
        size = self.boundarybox_hoogte

        # Draw background rectangle first
        #canvas.create_rectangle(pixel_x, pixel_y, pixel_x + size, pixel_y + size, fill="pink", outline="black")

        # Load and show image (ensure the reference is not lost, see [5][4][1])
        try:
            img = Image.open(self.image_path).resize((size, size), Image.LANCZOS)
            self._tk_img = ImageTk.PhotoImage(img)
            if not hasattr(canvas, 'persistent_images'):
                canvas.persistent_images = []
            canvas.persistent_images.append(self._tk_img)  # [5][4]
            canvas.create_image(pixel_x, pixel_y, anchor='nw', image=self._tk_img)
        except Exception as e:
            # fallback text if image cannot be loaded
            canvas.create_text(pixel_x + size/2, pixel_y + size/2, text="NO IMG", fill="red", font=("Arial", 8))
            print(f"Failed to display image: {self.image_path} | {e}")

        # You can draw any additional decorations here, or call super()
        # If you want stubs, dots, etc., call:
        # super().draw_recursive_top_left(canvas, x_spacing, y_spacing, swapy=False)




class Bord(Component):
    def __init__(self, label, component_type, **kwargs):
        super().__init__(label, component_type, **kwargs)
        self.stroomrichting = "vertical"


# Example tree
kopkwhmeter = Appliance("kopkwhmeter_H", "appliance")
teller = Teller("Teller_H", "teller")
bord1 = Bord("Bord1_V", "bord")
bord1 = Bord("bord1_V", "bord")
dif300 = Differential("Diff300_V", "differential")
dif30 = Differential("Diff30_V", "differential")
dif100 = Differential("Diff100_V", "differential")
dif3 = Differential("Diff3_V", "differential")
prieze = Prieze("prieze", "prieze" , aantal=1)
priezedub = Prieze("prieze", "prieze" , aantal=2)
zek3001 = CircuitBreaker("zek3001_V", "circuit_breaker")
zek3002 = CircuitBreaker("zek3002_V", "circuit_breaker")
zek1001 = CircuitBreaker("zek1001_V", "circuit_breaker")
zek3003 = CircuitBreaker("zek3003_V", "circuit_breaker")
zek3004verl = CircuitBreaker("zek3004verl_V", "circuit_breaker")
vaatwas301 = Appliance("vaatwas301_H", "appliance")
droogkast3002 = Appliance("droogkast3002_H", "appliance")
oven3002 = Appliance("oven3002_H", "appliance")
lamp3004 = Appliance("lamp3004_H", "appliance")
microoven3002 = Appliance("microoven3002_H", "appliance")
contaxop3004 = Contax("contaxop3004_H", "appliance")
contaxopcontax = Contax("contaxopcontax_H", "appliance")
domo = Domomodule("Domomodule_H", "domomodule")
verlH6 = Verlichting("Verlichting6_H", "verlichting")
verlH = Verlichting("Verlichting_H", "verlichting")
verlH2 = Verlichting("Verlichting2_H", "verlichting")
verlH3 = Verlichting("Verlichting3_H", "verlichting")
verlH4 = Verlichting("Verlichting4_H", "verlichting")
verlH5 = Verlichting("Verlichting5_H", "verlichting")
zonnepaneelopdif3 = Appliance("zonnepaneelopdif3_H", "appliance")
faaropcontax = Verlichting("faaropcontax_H", "verlichting")
verlicht1 = Verlichting("Verlicht1_H", "verlichting")
verlicht2 = Verlichting("Verlicht2_H", "verlichting")
verlicht3 = Verlichting("Verlicht3_H", "verlichting")
tv = Appliance("tv_H", "appliance")
domo2 = Appliance("domo2_H", "appliance")
domo.add_child(verlH)
teller.add_child(dif300, dif30, dif3)
dif300.add_child(zek3001, zek3002, zek3003)
zek3001.add_child(droogkast3002)
zek3002.add_child(oven3002, microoven3002)
zek3003.add_child(tv, domo2, domo)
domo2.add_child(verlH2, verlH3, verlH4, verlH5)
zek3004verl.add_child(verlicht1, verlicht2, verlicht3, lamp3004)
zek3004verl.add_child(contaxop3004)
dif300.add_child(zek3004verl)
zek1001.add_child(vaatwas301 , prieze , priezedub , verlH6)

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


if __name__ == "__main__":
    te_tekenen_startpunt = kopkwhmeter
    te_tekenen_startpunt.sort_children()
    te_tekenen_startpunt.assign_coordinates_by_rules()
    te_tekenen_startpunt.multiply_coordinates(1)
    te_tekenen_startpunt.print_ascii_tree_with_regel()

    te_tekenen_startpunt.explode_coordinates_to_canvas() #tak en kring tussenruimte

    #exit()

    # Optionally, explode coordinates to canvas pixels

    # Set canvas size as needed
    canvas_width, canvas_height = te_tekenen_startpunt.get_canvas_size()
    drawing = draw.Drawing(canvas_width + 100, canvas_height + 100)

    te_tekenen_startpunt.draw_svg(drawing, 30, 30, swapy=True)

    drawing.save_svg('testree24.svg')  # Save your vector

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
        svg_filename = f'testree24_page_{i+1}.svg'
        drawing.save_svg(svg_filename)
        print(f"Saved page {i+1}: x=({start_x}-{end_x}), width={page_width}")

    print("SVG pages exported per cut region.")
