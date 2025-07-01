from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors

from symboolparameters import *  # mijn eigen klassen met parameters hoe je een symbool tekent
import math
import json
import jsonontleder

with open('root_json_str.json', 'r', encoding='utf-8') as f:
    jsonbestand = json.load(f)

all_differentielen = jsonontleder.find_all_elements(jsonbestand, "differentielen")
print(f"Found {len(all_differentielen)} 'differentielen':")
for diff in all_differentielen:
    print(" -", diff.get("naam"))

all_tellers = jsonontleder.find_all_elements(jsonbestand, "tellers")
print(f"\nFound {len(all_tellers)} 'tellers':")
for teller in all_tellers:
    print(" -", teller.get("naam"))

####################################################

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
VOEDINGSLIJN_LENGTH = 300 * mm  # Total length of the voedingslijn

# Calculate the drawable width of each page (accounting for left & right offsets)
DRAWABLE_WIDTH = PAGE_WIDTH - 2 * BORDER_WIDTH - 2 * OFFSET_X



def draw_grid(canvas, page_width, page_height, spacing_mm=10):
    canvas.setStrokeColor(colors.lightgrey)
    canvas.setLineWidth(0.5)

    spacing = spacing_mm * mm  # convert mm to points

    # Vertical lines
    x = 0
    while x <= page_width:
        canvas.line(x, 0, x, page_height)
        x += spacing

    # Horizontal lines
    y = 0
    while y <= page_height:
        canvas.line(0, y, page_width, y)
        y += spacing

class VirtualBorder:
    def __init__(self, canvas):
        self.canvas = canvas

    def draw(self):
        self.canvas.setStrokeColor(colors.red)  # use global color or constant
        self.canvas.rect(
            17 * mm ,
            17 * mm ,
            PAGE_WIDTH - 2 * 17 * mm ,
            PAGE_HEIGHT - 2 * 17 * mm
        )


class Border:
    def __init__(self, canvas):
        self.canvas = canvas

    def draw(self):
        self.canvas.setStrokeColor(colors.darkblue)  # use global color or constant
        self.canvas.rect(
            BORDER_WIDTH,
            BORDER_WIDTH,
            PAGE_WIDTH - 2 * BORDER_WIDTH,
            PAGE_HEIGHT - 2 * BORDER_WIDTH
        )


class OnderKader:
    def __init__(self, canvas, page_width, border_width, height_mm, color=colors.darkblue):
        self.canvas = canvas #waarop ga je het tekenen ? op u a4blaadjes
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



class TellerHandler:
    def __init__(self, canvas, y_pos, total_length, border_width, offset_x):
        self.canvas = canvas
        self.y_pos = y_pos
        self.total_length = total_length
        self.border_width = border_width
        self.offset_x = offset_x
        # Size of the square to draw
        self.square_size = 20
        # Drawable width per page (accounting for borders and offsets)
        self.drawable_width = PAGE_WIDTH - 2 * self.border_width - 2 * self.offset_x
    def draw(self):
        start_x = self.border_width + self.offset_x
        self.canvas.setLineWidth(1)
        self.canvas.setStrokeColor(colors.darkblue)
        self.canvas.setFillColor(colors.lightblue)
        self.canvas.rect(0, self.y_pos, self.square_size, self.square_size, fill=1, stroke=1)


# Number of pages needed
num_pages = math.ceil(VOEDINGSLIJN_LENGTH / DRAWABLE_WIDTH)

# Create a PDF canvas and rename to eendraadschema
eendraadschema = canvas.Canvas("horizontal_line_output.pdf", pagesize=landscape(A4))

# Create instances for borders and voedingslijn
blauwe_rand = Border(eendraadschema)
virtuelerandzodatnietindeblauwerandtekenen = VirtualBorder(eendraadschema)
onderkader = OnderKader(eendraadschema, PAGE_WIDTH, BORDER_WIDTH, 50)
voedings_lijn = VoedingsLijn(eendraadschema, VOEDINGSLIJN_Y, VOEDINGSLIJN_LENGTH, BORDER_WIDTH, OFFSET_X)
teller_handler = TellerHandler(eendraadschema, y_pos=100, total_length=300, border_width=7*mm, offset_x=17*mm)




# Optionally adjust page number params if you want:
# onderkader.set_page_number_params(x=..., y=..., color=..., size=...)

# Draw pages loop
for i in range(num_pages):
    blauwe_rand.draw()
    onderkader.draw()
    voedings_lijn.draw(i)
    # Draw page number
    onderkader.draw_page_number(f"Page {i + 1} of {num_pages}")
    virtuelerandzodatnietindeblauwerandtekenen.draw()
    # Draw the 1x1 cm grid
    draw_grid(eendraadschema, PAGE_WIDTH, PAGE_HEIGHT)




    eendraadschema.showPage()

    #**************start tekenen op elke pagina






eendraadschema.save()

print(f"PDF with voedingslijn, onderkader, zekeringen, and page numbers created. Total pages: {num_pages}")
