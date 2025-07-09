from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
import os

width = 600 * mm
height = 210 * mm

CELL_WIDTH_MM = 25
CELL_HEIGHT_MM = 25
cell_width_pt = CELL_WIDTH_MM * mm
cell_height_pt = CELL_HEIGHT_MM * mm

num_cols = int(width // cell_width_pt)
num_rows = int(height // cell_height_pt)


def cell_to_mm(row, col):
    x_mm = col * CELL_WIDTH_MM + CELL_WIDTH_MM / 2
    y_mm = row * CELL_HEIGHT_MM + CELL_HEIGHT_MM / 2
    return x_mm, y_mm

def draw_table_grid(c, width, height, cell_width_pt, cell_height_pt):
    num_cols = int(width // cell_width_pt)
    num_rows = int(height // cell_height_pt)
    # Draw horizontal lines
    for row in range(num_rows + 1):
        y = row * cell_height_pt
        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(0.3)
        c.line(0, y, num_cols * cell_width_pt, y)
    # Draw vertical lines
    for col in range(num_cols + 1):
        x = col * cell_width_pt
        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(0.3)
        c.line(x, 0, x, num_rows * cell_height_pt)
    c.setStrokeColor(colors.black)


class Component:
    FIRST_CHILD_REL_ROW = 0
    FIRST_CHILD_REL_COL = 0
    ADD_CHILD_DELTA_ROW = 0
    ADD_CHILD_DELTA_COL = 0

    def __init__(self, id, label, type):
        self.id = id
        self.label = label
        self.type = type
        self.rel_row = 0
        self.rel_col = 0
        self.abs_row = None
        self.abs_col = None
        self.parent = None
        self.children = []

    def add_child(self, child):
        child.parent = self
        if not self.children:
            child.rel_row = self.FIRST_CHILD_REL_ROW
            child.rel_col = self.FIRST_CHILD_REL_COL
        else:
            prev = self.children[-1]
            child.rel_row = prev.rel_row + self.ADD_CHILD_DELTA_ROW
            child.rel_col = prev.rel_col + self.ADD_CHILD_DELTA_COL
        self.children.append(child)

    def set_absolute_position(self, parent_row, parent_col):
        self.abs_row = parent_row + self.rel_row
        self.abs_col = parent_col + self.rel_col
        for child in self.children:
            child.set_absolute_position(self.abs_row, self.abs_col)

    def get_connection_points(self):
        x_mm, y_mm = cell_to_mm(self.abs_row, self.abs_col)
        half_w = CELL_WIDTH_MM / 2
        voeding = (x_mm - half_w + 4, y_mm)
        connection = (x_mm + half_w - 4, y_mm)
        return voeding, connection

    def draw(self, c, square_size=18*mm):
        x_mm, y_mm = cell_to_mm(self.abs_row, self.abs_col)
        x_pt = x_mm * mm
        y_pt = y_mm * mm
        c.setLineWidth(1)
        c.rect(x_pt - square_size/2, y_pt - square_size/2, square_size, square_size, stroke=1, fill=0)
        c.setFont("Helvetica", 8)
        c.drawCentredString(x_pt, y_pt - square_size/2 - 3, self.label)

class Voeding(Component):
    FIRST_CHILD_REL_ROW = 1
    FIRST_CHILD_REL_COL = 1
    ADD_CHILD_DELTA_ROW = 0  #omhooh
    ADD_CHILD_DELTA_COL = 9 #6 vakjes naar rechts

class Differential(Component):
    # Default: first child at (1,1), next to the right
    FIRST_CHILD_REL_ROW = 1
    FIRST_CHILD_REL_COL = 1
    ADD_CHILD_DELTA_ROW = 0
    ADD_CHILD_DELTA_COL = 2

class CircuitBreaker(Component):
    # First child at (0,1), next child one row down (1,1), then (2,1), etc.
    FIRST_CHILD_REL_ROW = 1
    FIRST_CHILD_REL_COL = 1
    ADD_CHILD_DELTA_ROW = 1 # vakjes omhoog
    ADD_CHILD_DELTA_COL = 0 #vakjes naar rechts

class Appliance(Component):
    # First child at (0,1), next child one row down (1,1), then (2,1), etc.
    FIRST_CHILD_REL_ROW = 1
    FIRST_CHILD_REL_COL = 1
    ADD_CHILD_DELTA_ROW = 1
    ADD_CHILD_DELTA_COL = 1

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
    print(f"{prefix}{component.label} ({component.type})")
    for i, child in enumerate(component.children):
        last = (i == len(component.children) - 1)
        connector = "└── " if last else "├── "
        print_connection_tree(child, prefix + connector)

if __name__ == "__main__":
    voeding = Voeding(0, "Voeding", "voeding")
    diff300 = Differential(1, "Diff300", "differential")
    diff30 = Differential(2, "Diff30", "differential")
    diff3 = Differential(2, "Diff9", "differential")
    zek1 = CircuitBreaker(3, "Zekering1", "circuit_breaker")
    zek2 = CircuitBreaker(4, "Zekering102", "circuit_breaker")
    zek3 = CircuitBreaker(4, "Zekering99", "circuit_breaker")
    zek4 = CircuitBreaker(4, "Zekering4", "circuit_breaker")
    vaatwas = Appliance(5, "Vaatwas", "appliance")
    keuken = Appliance(6, "Keuken", "appliance")
    oven = Appliance(7, "Oven", "appliance")
    microOven = Appliance(7, "microOven", "appliance")

    voeding.add_child(diff300)
    voeding.add_child(diff30)   # <--- diff30 is NOT attached to voeding!
    voeding.add_child(diff3)  # <--- diff30 is NOT attached to voeding!
    diff300.add_child(zek1)
    diff30.add_child(zek2)  # zek102
    zek1.add_child(vaatwas)
    zek2.add_child(keuken)
    zek2.add_child(oven)
    diff30.add_child(zek3) #99
    diff30.add_child(microOven) #oven
    diff30.add_child(zek4) #zek4

    voeding.set_absolute_position(3, 0)

    c = canvas.Canvas("component_tree_table.pdf", (width, height))

    cell_width_pt = CELL_WIDTH_MM * mm
    cell_height_pt = CELL_HEIGHT_MM * mm

    draw_table_grid(c, width, height, cell_width_pt, cell_height_pt)
    draw_tree(c, voeding)
    c.save()

    print_connection_tree(voeding)

    try:
        os.startfile("component_tree_table.pdf")
    except AttributeError:
        print("PDF saved as component_tree_table.pdf")