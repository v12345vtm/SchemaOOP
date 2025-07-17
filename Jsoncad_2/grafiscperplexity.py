from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
import os

# Use standard A4 landscape dimensions
width, height = landscape(A4)

CELL_WIDTH_MM = 25
CELL_HEIGHT_MM = 25
cell_width_pt = CELL_WIDTH_MM * mm
cell_height_pt = CELL_HEIGHT_MM * mm

def cell_to_mm(row, col):
    x_mm = col * CELL_WIDTH_MM + CELL_WIDTH_MM / 2
    y_mm = row * CELL_HEIGHT_MM + CELL_HEIGHT_MM / 2
    return x_mm, y_mm

def draw_table_grid(c, num_cols, num_rows, cell_width_pt, cell_height_pt):
    for row in range(num_rows + 1):
        y = row * cell_height_pt
        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(0.3)
        c.line(0, y, num_cols * cell_width_pt, y)
    for col in range(num_cols + 1):
        x = col * cell_width_pt
        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(0.3)
        c.line(x, 0, x, num_rows * cell_height_pt)
    c.setStrokeColor(colors.black)

class Component:
    def __init__(self, id, label, type):
        self.id = id
        self.label = label
        self.type = type
        self.abs_row = None
        self.abs_col = None
        self.parent = None
        self.children = []

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def set_absolute_position(self, row=0, col=0, row_tracker=None):
        # Pivot: each parent in a unique row, children in the next row, each in a new column
        if row_tracker is None:
            row_tracker = {}
        if row not in row_tracker:
            row_tracker[row] = 0
        self.abs_row = row
        self.abs_col = row_tracker[row]
        row_tracker[row] += 1
        # Children go to the next row, each in its own column
        for child in self.children:
            child.set_absolute_position(row + 1, row_tracker.get(row + 1, 0), row_tracker)

    def get_connection_points(self):
        x_mm, y_mm = cell_to_mm(self.abs_row, self.abs_col)
        half_h = CELL_HEIGHT_MM / 2
        voeding = (x_mm, y_mm - half_h + 4)
        connection = (x_mm, y_mm + half_h - 4)
        return voeding, connection

    def draw(self, c, square_size=18*mm):
        x_mm, y_mm = cell_to_mm(self.abs_row, self.abs_col)
        x_pt = x_mm * mm
        y_pt = y_mm * mm
        c.setLineWidth(1)
        c.rect(x_pt - square_size/2, y_pt - square_size/2, square_size, square_size, stroke=1, fill=0)
        # Rotate text for vertical orientation
        c.saveState()
        c.translate(x_pt, y_pt)
        c.rotate(90)
        c.setFont("Helvetica", 8)
        c.drawCentredString(0, -square_size/2 - 3, self.label)
        c.restoreState()

class Voeding(Component): pass
class Differential(Component): pass
class CircuitBreaker(Component): pass
class Appliance(Component): pass

def draw_tree(c, component):
    component.draw(c)
    if component.parent:
        my_voeding, _ = component.get_connection_points()
        _, parent_connection = component.parent.get_connection_points()
        c.setLineWidth(1)
        c.line(parent_connection[0]*mm, parent_connection[1]*mm, my_voeding[0]*mm, my_voeding[1]*mm)
    for child in component.children:
        draw_tree(c, child)

def print_connection_tree(component, prefix=""):
    print(f"{prefix}{component.label} ({component.component_type})")
    for i, child in enumerate(component.children):
        last = (i == len(component.children) - 1)
        connector = "└── " if last else "├── "
        print_connection_tree(child, prefix + connector)

if __name__ == "__main__":
    voeding = Voeding(0, "Voeding", "voeding")
    diff300 = Differential(1, "Diff300", "differential")
    diff30 = Differential(2, "Diff30", "differential")
    diff3 = Differential(3, "Diff9", "differential")
    zek1 = CircuitBreaker(4, "Zekering1", "circuit_breaker")
    zek2 = CircuitBreaker(5, "Zekering102", "circuit_breaker")
    zek3 = CircuitBreaker(6, "Zekering99", "circuit_breaker")
    zek4 = CircuitBreaker(7, "Zekering4", "circuit_breaker")
    vaatwas = Appliance(8, "Vaatwas", "appliance")
    keuken = Appliance(9, "Keuken", "appliance")
    oven = Appliance(10, "Oven", "appliance")
    microOven = Appliance(11, "microOven", "appliance")

    voeding.add_child(diff300)
    voeding.add_child(diff30)
    voeding.add_child(diff3)
    diff300.add_child(zek1)
    diff30.add_child(zek2)
    zek1.add_child(vaatwas)
    zek2.add_child(keuken)
    zek2.add_child(oven)
    diff30.add_child(zek3)
    diff30.add_child(microOven)
    diff30.add_child(zek4)

    # Assign absolute positions (pivoted: one parent per row)
    voeding.set_absolute_position(row=0, col=0)

    # Find max row and col used
    def find_max_row_col(comp, max_row_col=[0,0]):
        if comp.abs_row > max_row_col[0]:
            max_row_col[0] = comp.abs_row
        if comp.abs_col > max_row_col[1]:
            max_row_col[1] = comp.abs_col
        for child in comp.children:
            find_max_row_col(child, max_row_col)
        return max_row_col

    max_row, max_col = find_max_row_col(voeding)
    num_cols = max_col + 2
    num_rows = max_row + 2

    c = canvas.Canvas("component_tree_table_pivoted.pdf", (num_cols * cell_width_pt, num_rows * cell_height_pt))

    draw_table_grid(c, num_cols, num_rows, cell_width_pt, cell_height_pt)
    draw_tree(c, voeding)
    c.save()

    print_connection_tree(voeding)

    try:
        os.startfile("component_tree_table_pivoted.pdf")
    except AttributeError:
        print("PDF saved as component_tree_table_pivoted.pdf")
