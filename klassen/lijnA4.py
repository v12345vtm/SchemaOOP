from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
import math
import json

PAGE_WIDTH, PAGE_HEIGHT = landscape(A4)
BORDER_WIDTH = 7 * mm  # border width from edge in millimeters
OFFSET_X = 17 * mm  # horizontal start offset on all pages

# Parameters to manipulate page number position, color, and size
PAGE_NUM_X = BORDER_WIDTH + 255 * mm
PAGE_NUM_Y = BORDER_WIDTH + 5 * mm
PAGE_NUM_COLOR = colors.darkblue
PAGE_NUM_SIZE = 12

# Voedingslijn parameters
VOEDINGSLIJN_Y = 60 * mm  # Y position of voedingslijn (line)
VOEDINGSLIJN_LENGTH = 240 * mm  # Total length of the voedingslijn

# Calculate the drawable width of each page (accounting for left & right offsets)
DRAWABLE_WIDTH = PAGE_WIDTH - 2 * BORDER_WIDTH - 2 * OFFSET_X

# Load data from root_json_str.json
with open("root_json_str.json", "r") as f:
    json_data = json.load(f)

print("Loaded JSON:", json_data)


class Border:
    def __init__(self, canvas, page_width, page_height, border_width, color=colors.darkblue):
        self.canvas = canvas
        self.page_width = page_width
        self.page_height = page_height
        self.border_width = border_width
        self.color = color

    def draw(self):
        self.canvas.setStrokeColor(self.color)
        self.canvas.rect(
            self.border_width,
            self.border_width,
            self.page_width - 2 * self.border_width,
            self.page_height - 2 * self.border_width
        )


class OnderKader:
    def __init__(self, canvas, page_width, border_width, height_mm, color=colors.darkblue):
        self.canvas = canvas
        self.page_width = page_width
        self.border_width = border_width
        self.height = height_mm * mm
        self.color = color

        # Page number defaults:
        self.page_num_x = PAGE_NUM_X
        self.page_num_y = PAGE_NUM_Y
        self.page_num_color = PAGE_NUM_COLOR
        self.page_num_size = PAGE_NUM_SIZE

    def draw(self):
        self.canvas.setStrokeColor(self.color)
        self.canvas.rect(
            self.border_width,
            self.border_width,
            self.page_width - 2 * self.border_width,
            self.height
        )

    def set_page_number_params(self, x=None, y=None, color=None, size=None):
        if x is not None:
            self.page_num_x = x
        if y is not None:
            self.page_num_y = y
        if color is not None:
            self.page_num_color = color
        if size is not None:
            self.page_num_size = size

    def draw_page_number(self, page_number_str):
        self.canvas.setFont("Helvetica", self.page_num_size)
        self.canvas.setFillColor(self.page_num_color)
        self.canvas.drawString(self.page_num_x, self.page_num_y, page_number_str)
        self.canvas.setFillColor(colors.black)  # reset fill color


class VoedingsLijn:
    def __init__(self, canvas, y_pos, total_length, border_width, offset_x):
        self.canvas = canvas
        self.y_pos = y_pos
        self.total_length = total_length
        self.border_width = border_width
        self.offset_x = offset_x
        self.line_width = 2

        # Drawable width per page (accounting for borders and offsets)
        self.drawable_width = PAGE_WIDTH - 2 * self.border_width - 2 * self.offset_x

    def draw(self, page_index):
        start_x = self.border_width + self.offset_x
        # Calculate the length to draw on this page (may be partial)
        remaining_length = self.total_length - page_index * self.drawable_width
        draw_length = min(self.drawable_width, remaining_length)
        end_x = start_x + draw_length

        self.canvas.setLineWidth(self.line_width)
        self.canvas.setStrokeColor(colors.black)
        self.canvas.line(start_x, self.y_pos, end_x, self.y_pos)


class ZekeringHandler:
    def __init__(self, canvas, zekeringen, start_x, y_base, line_height, spacing):
        """
        zekeringen: list of dicts from JSON for each zekering
        start_x: starting x position for first zekering (in points)
        y_base: y position baseline for vertical lines (in points)
        line_height: height of each vertical line (in points)
        spacing: horizontal spacing between zekeringen (in points)
        """
        self.canvas = canvas
        self.zekeringen = zekeringen
        self.start_x = start_x
        self.y_base = y_base
        self.line_height = line_height
        self.spacing = spacing

    def draw(self):
        self.canvas.setStrokeColor(colors.red)
        self.canvas.setLineWidth(1.5)

        for i, zekering in enumerate(self.zekeringen):
            x = self.start_x + i * self.spacing
            y1 = self.y_base
            y2 = y1 + self.line_height

            # Draw vertical line
            self.canvas.line(x, y1, x, y2)

            # Draw zekering name and amp next to the line
            self.canvas.setFont("Helvetica", 8)
            self.canvas.setFillColor(colors.black)
            text = f"{zekering['naam']} ({zekering['amp']}A)"
            self.canvas.drawString(x + 2 * mm, y2 - 4 * mm, text)


# Number of pages needed
num_pages = math.ceil(VOEDINGSLIJN_LENGTH / DRAWABLE_WIDTH)

# Create a PDF canvas and rename to eendraadschema
eendraadschema = canvas.Canvas("horizontal_line_output.pdf", pagesize=landscape(A4))

# Create instances for borders and voedingslijn
page_border = Border(eendraadschema, PAGE_WIDTH, PAGE_HEIGHT, BORDER_WIDTH)
onderkader = OnderKader(eendraadschema, PAGE_WIDTH, BORDER_WIDTH, 50)
voedings_lijn = VoedingsLijn(eendraadschema, VOEDINGSLIJN_Y, VOEDINGSLIJN_LENGTH, BORDER_WIDTH, OFFSET_X)

# Prepare ZekeringHandler with parameters
zekeringen_list = json_data.get("Zekering", [])
zekering_start_x = BORDER_WIDTH + OFFSET_X + 10 * mm  # inside voedingslijn start + margin
zekering_y_base = VOEDINGSLIJN_Y
zekering_line_height = 30 * mm
zekering_spacing = 40 * mm

zekering_handler = ZekeringHandler(eendraadschema, zekeringen_list, zekering_start_x, zekering_y_base, zekering_line_height, zekering_spacing)

# Optionally adjust page number params if you want:
# onderkader.set_page_number_params(x=..., y=..., color=..., size=...)

# Draw pages loop
for i in range(num_pages):
    page_border.draw()
    onderkader.draw()
    voedings_lijn.draw(i)

    # Draw vertical zekering lines
    zekering_handler.draw()

    # Draw page number
    onderkader.draw_page_number(f"Page {i + 1} of {num_pages}")

    # Add 'X' character on page 2 (index 1)
    if i == 1:
        eendraadschema.setFont("Helvetica-Bold", 20)
        eendraadschema.drawString(PAGE_WIDTH / 2, VOEDINGSLIJN_Y + 30 * mm, "X")

    eendraadschema.showPage()

eendraadschema.save()

print(f"PDF with voedingslijn, onderkader, zekeringen, and page numbers created. Total pages: {num_pages}")
