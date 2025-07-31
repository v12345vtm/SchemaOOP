from bigtree import Node
import svgwrite


# Define ElectricNode subclasses
class Component(Node):
    def __init__(self, name, node_type="generic", **kwargs):
        super().__init__(name, **kwargs)
        self.node_type = node_type

    def describe(self):
        # Safely include 'polen' if attribute exists
        polen_str = getattr(self, 'polen', 'N/A')
        return f"{self.name}: {self.node_type} : : {polen_str}"


class Teller(Component):
    def __init__(self, name, polen, amp, **kwargs):
        super().__init__(name, "Meter (Teller)", **kwargs)
        self.polen = polen  # Save attributes
        self.amp = amp


class Differentieel(Component):
    def __init__(self, name, polen, amp, millies, dif_type="Type A", **kwargs):
        super().__init__(name, "Differential Switch (Differentieel)", **kwargs)
        self.polen = polen   # Save attributes
        self.amp = amp
        self.millies = millies
        self.dif_type = dif_type


class CircuitBreaker(Component):
    def __init__(self, name, **kwargs):
        super().__init__(name, "Circuit Breaker", **kwargs)


class RelayNode(Component):
    def __init__(self, name, **kwargs):
        super().__init__(name, "Relay", **kwargs)

class RelaisSpoel(Component):
    def __init__(self, relay_name, **kwargs):
        # Use relay_name + "_Coil" as this part's name
        name = f"{relay_name}_Coil"
        super().__init__(name, "Relay Coil", **kwargs)


class RelayContact(Component):
    def __init__(self, relay_name, **kwargs):
        # Use relay_name + "_Switch" as this part's name
        name = f"{relay_name}_Switch"
        super().__init__(name, "Relay Switch", **kwargs)

class Prieze(Component):
    def __init__(self, name, **kwargs):
        super().__init__(name, "Power Plug", **kwargs)


class Appliance(Component):
    def __init__(self, name, **kwargs):
        super().__init__(name, "Appliance", **kwargs)


class LightNode(Component):
    def __init__(self, name, **kwargs):
        super().__init__(name, "Light", **kwargs)


# Build the electric tree example
root = Teller("Main Meter", 2, 40)
diff1 = Differentieel("1", 2, 40, 300, parent=root)
diff2 = Differentieel("2", 2, 40, 300, parent=root)

q1 = CircuitBreaker("Q1", parent=diff1)
q2 = CircuitBreaker("Q2", parent=diff1)


# Add coil and switch as children with prefix relay_name
ct1spoel = RelaisSpoel("ct1", parent=q1)
ct1contact = RelayContact("ct1", parent=q2)

plug1 = Prieze("Plug 1", parent=ct1contact)
appliance1 = Appliance("Washing Machine", parent=plug1)

plug2 = Prieze("Plug 2", parent=ct1spoel)
appliance2 = Appliance("Dishwasher", parent=plug2)

light1 = LightNode("Kitchen Light", parent=q1)
light2 = LightNode("Bathroom Light", parent=q2)

# Optional: print descriptions
for node in root.descendants:
    print(node.describe())


# Eendraadschema-style SVG drawing function
def draw_eendraadschema_svg(root_node, filename="eendraadschema.svg",
                            node_radius=30, x_gap=100, y_gap=100):
    dwg = svgwrite.Drawing(filename, profile='tiny')

    # Store node positions: horizontal axis is traversal order, vertical axis = depth
    node_positions = {}
    current_x = 50  # start x coordinate

    def assign_pos(node, depth=0):
        nonlocal current_x
        x = current_x
        y = 50 + depth * y_gap
        node_positions[node] = (x, y)
        current_x += x_gap
        for child in node.children:
            assign_pos(child, depth + 1)

    assign_pos(root_node)

    # Draw edges: lines from each parent node horizontally to child's vertical line, then down/up
    for node, (x, y) in node_positions.items():
        for child in node.children:
            cx, cy = node_positions[child]

            # Path from parent to child as horizontal then vertical (like wires)
            # Horizontal line from parent node edge
            start_h = (x + node_radius, y)
            # Horizontal line endpoint at child's vertical line x offset
            end_h = (cx - node_radius, y)

            # Vertical line down/up from horizontal line end to child node center
            end_v = (cx - node_radius, cy)

            dwg.add(dwg.line(start=start_h, end=end_h, stroke='black', stroke_width=2))
            dwg.add(dwg.line(start=end_h, end=end_v, stroke='black', stroke_width=2))
            # Horizontal line into child's circle
            dwg.add(dwg.line(start=end_v, end=(cx - node_radius / 2, cy), stroke='black', stroke_width=2))

    # Draw nodes: circles with name above and type below
    for node, (x, y) in node_positions.items():
        dwg.add(dwg.circle(center=(x, y), r=node_radius, fill='lightyellow', stroke='black', stroke_width=2))
        dwg.add(dwg.text(node.name,
                         insert=(x, y - 10),
                         text_anchor="middle",
                         font_size=14,
                         font_weight="bold"))
        dwg.add(dwg.text(node.node_type,
                         insert=(x, y + 20),
                         text_anchor="middle",
                         font_size=11,
                         fill='darkgray'))

    dwg.save()
    print(f"Eendraadschema SVG saved as '{filename}'")


# Generate the SVG diagram
draw_eendraadschema_svg(root)

# Optionally display the tree structure textually
root.show()
