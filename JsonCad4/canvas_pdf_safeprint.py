from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors


from components  import *
from example_tree import te_tekenen_startpunt

zonewaarjenietkanprintenopuwblad = 10
LEFT_MARGIN = zonewaarjenietkanprintenopuwblad
RIGHT_MARGIN = zonewaarjenietkanprintenopuwblad
TOP_MARGIN = zonewaarjenietkanprintenopuwblad
BOTTOM_MARGIN = zonewaarjenietkanprintenopuwblad
PRINTABLE_WIDTH = 297 - LEFT_MARGIN - RIGHT_MARGIN
PRINTABLE_HEIGHT = 210 - TOP_MARGIN - BOTTOM_MARGIN



def calculate_bounding_box(objects):
    min_x = float('inf')
    min_y = float('inf')
    max_x = float('-inf')
    max_y = float('-inf')

    for obj in objects:
        x0, y0, x1, y1 = obj.get_bounding_box()
        min_x = min(min_x, x0)
        min_y = min(min_y, y0)
        max_x = max(max_x, x1)
        max_y = max(max_y, y1)
    return min_x, min_y, max_x, max_y

class CanvasObject:
    def __init__(self, x_mm, y_mm):
        self.x_mm = x_mm
        self.y_mm = y_mm

    def to_points(self, mm_val):
        return mm_val * mm

    def get_bounding_box(self):
        # Default: treat as a point
        return (self.x_mm, self.y_mm, self.x_mm, self.y_mm)

    def draw(self, c, offset_x_mm=0, offset_y_mm=0):
        pass

    def draw_on_page(self, c, page_x0, page_y0, page_x1, page_y1, offset_x_mm=0, offset_y_mm=0):
        # Default: draw if any part is on the page
        obj_min_x, obj_min_y, obj_max_x, obj_max_y = self.get_bounding_box()
        if obj_max_x > page_x0 and obj_min_x < page_x1 and obj_max_y > page_y0 and obj_min_y < page_y1:
            self.draw(c, offset_x_mm, offset_y_mm)

class Square(CanvasObject):
    def __init__(self, x_mm, y_mm, size_mm, color):
        super().__init__(x_mm, y_mm)
        self.size_mm = size_mm
        self.color = color

    def get_bounding_box(self):
        return (self.x_mm, self.y_mm, self.x_mm + self.size_mm, self.y_mm + self.size_mm)

    def draw(self, c, offset_x_mm=0, offset_y_mm=0):
        x = self.to_points(self.x_mm + offset_x_mm)
        y = self.to_points(self.y_mm + offset_y_mm)
        size = self.to_points(self.size_mm)
        c.setFillColor(self.color)
        c.rect(x, y, size, size, fill=1)

    def draw_on_page(self, c, page_x0, page_y0, page_x1, page_y1, offset_x_mm=0, offset_y_mm=0):
        # Clip square to page if needed
        left = max(self.x_mm, page_x0)
        top = max(self.y_mm, page_y0)
        right = min(self.x_mm + self.size_mm, page_x1)
        bottom = min(self.y_mm + self.size_mm, page_y1)
        if right > left and bottom > top:
            x = self.to_points(left + offset_x_mm)
            y = self.to_points(top + offset_y_mm)
            width = self.to_points(right - left)
            height = self.to_points(bottom - top)
            c.setFillColor(self.color)
            c.rect(x, y, width, height, fill=1)

class HorizontalLine(CanvasObject):
    def __init__(self, x_mm, y_mm, length_mm, color, width_mm=0.5):
        super().__init__(x_mm, y_mm)
        self.length_mm = length_mm
        self.color = color
        self.width_mm = width_mm

    def get_bounding_box(self):
        return (self.x_mm, self.y_mm, self.x_mm + self.length_mm, self.y_mm)

    def draw(self, c, offset_x_mm=0, offset_y_mm=0):
        x = self.to_points(self.x_mm + offset_x_mm)
        y = self.to_points(self.y_mm + offset_y_mm)
        length = self.to_points(self.length_mm)
        width = self.to_points(self.width_mm)
        c.setStrokeColor(self.color)
        c.setLineWidth(width)
        c.line(x, y, x + length, y)

    def draw_on_page(self, c, page_x0, page_y0, page_x1, page_y1, offset_x_mm=0, offset_y_mm=0):
        # Only draw the visible segment
        line_start = max(self.x_mm, page_x0)
        line_end = min(self.x_mm + self.length_mm, page_x1)
        if line_end > line_start and self.y_mm >= page_y0 and self.y_mm < page_y1:
            visible_length = line_end - line_start
            x = self.to_points(line_start + offset_x_mm)
            y = self.to_points(self.y_mm + offset_y_mm)
            length = self.to_points(visible_length)
            width = self.to_points(self.width_mm)
            c.setStrokeColor(self.color)
            c.setLineWidth(width)
            c.line(x, y, x + length, y)




class StopcontactAREI(CanvasObject):
    def __init__(self, x_mm, y_mm, size_mm=20, body_color=colors.white, pin_color=colors.black, ground_color=colors.green):
        super().__init__(x_mm, y_mm)
        self.size_mm = size_mm
        self.body_color = body_color
        self.pin_color = pin_color
        self.ground_color = ground_color

    def get_bounding_box(self):
        r = self.size_mm / 2
        return (self.x_mm - r, self.y_mm - r, self.x_mm + r, self.y_mm + r)

    def draw(self, c, offset_x_mm=0, offset_y_mm=0):
        x = self.to_points(self.x_mm + offset_x_mm)
        y = self.to_points(self.y_mm + offset_y_mm)
        r = self.to_points(self.size_mm / 2)

        # Outer circle (socket body)
        c.setFillColor(self.body_color)
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.circle(x, y, r, fill=1, stroke=1)

        # Two pin holes (phase and neutral)
        hole_r = self.to_points(self.size_mm * 0.1)
        dx = self.to_points(self.size_mm * 0.22)
        dy = self.to_points(self.size_mm * 0.12)
        c.setFillColor(self.pin_color)
        c.circle(x - dx, y + dy, hole_r, fill=1, stroke=0)
        c.circle(x + dx, y + dy, hole_r, fill=1, stroke=0)

        # Grounding pin (bottom center)
        ground_r = self.to_points(self.size_mm * 0.08)
        c.setFillColor(self.ground_color)
        c.circle(x, y - self.to_points(self.size_mm * 0.18), ground_r, fill=1, stroke=0)

        # Child safety symbol (simple shield)
        shield_width = self.to_points(self.size_mm * 0.18)
        shield_height = self.to_points(self.size_mm * 0.14)
        c.setFillColor(colors.lightgrey)
        c.roundRect(x - shield_width/2, y + self.to_points(self.size_mm * 0.22), shield_width, shield_height, shield_height/2, fill=1, stroke=0)
        c.setStrokeColor(colors.darkgrey)
        c.roundRect(x - shield_width/2, y + self.to_points(self.size_mm * 0.22), shield_width, shield_height, shield_height/2, fill=0, stroke=1)


class ImageIcon(CanvasObject):
    def __init__(self, x_mm, y_mm, image_path, width_mm, height_mm):
        super().__init__(x_mm, y_mm)
        self.image_path = image_path
        self.width_mm = width_mm
        self.height_mm = height_mm

    def get_bounding_box(self):
        return (self.x_mm, self.y_mm, self.x_mm + self.width_mm, self.y_mm + self.height_mm)

    def draw(self, c, offset_x_mm=0, offset_y_mm=0):
        x = self.to_points(self.x_mm + offset_x_mm)
        y = self.to_points(self.y_mm + offset_y_mm)
        w = self.to_points(self.width_mm)
        h = self.to_points(self.height_mm)
        c.drawImage(self.image_path, x, y, width=w, height=h, mask='auto')




class CarIcon(CanvasObject):
    def __init__(self, x_mm, y_mm, width_mm=40, height_mm=20, body_color=colors.blue, wheel_color=colors.black):
        super().__init__(x_mm, y_mm)
        self.width_mm = width_mm
        self.height_mm = height_mm
        self.body_color = body_color
        self.wheel_color = wheel_color

    def get_bounding_box(self):
        # The bounding box covers the whole car including wheels
        return (self.x_mm, self.y_mm, self.x_mm + self.width_mm, self.y_mm + self.height_mm)

    def draw(self, c, offset_x_mm=0, offset_y_mm=0):
        # Convert mm to points
        x = self.to_points(self.x_mm + offset_x_mm)
        y = self.to_points(self.y_mm + offset_y_mm)
        width = self.to_points(self.width_mm)
        height = self.to_points(self.height_mm)

        wheel_radius = height / 4

        # Draw car body (a rounded rectangle or simple rectangle)
        c.setFillColor(self.body_color)
        c.roundRect(x, y + wheel_radius, width, height - wheel_radius, radius=wheel_radius / 2, fill=1)

        # Draw wheels as circles
        c.setFillColor(self.wheel_color)
        # Left wheel
        c.circle(x + wheel_radius * 2, y + wheel_radius, wheel_radius, fill=1)
        # Right wheel
        c.circle(x + width - wheel_radius * 2, y + wheel_radius, wheel_radius, fill=1)


class Text(CanvasObject):
    def __init__(self, x_mm, y_mm, text, font_size_pt=12, color=colors.black):
        super().__init__(x_mm, y_mm)
        self.text = text
        self.font_size_pt = font_size_pt
        self.color = color

    def get_bounding_box(self, c=None):
        text_height_mm = self.font_size_pt * 0.3528
        if c is not None:
            text_width_pt = c.stringWidth(self.text, "Helvetica", self.font_size_pt)
            text_width_mm = text_width_pt / 2.83465
        else:
            text_width_mm = self.font_size_pt * 0.6 * len(self.text) * 0.3528
        return (self.x_mm, self.y_mm, self.x_mm + text_width_mm, self.y_mm + text_height_mm)

    def draw(self, c, offset_x_mm=0, offset_y_mm=0):
        x = self.to_points(self.x_mm + offset_x_mm)
        y = self.to_points(self.y_mm + offset_y_mm)
        c.setFillColor(self.color)
        c.setFont("Helvetica", self.font_size_pt)
        c.drawString(x, y, self.text)

    def draw_on_page(self, c, page_x0, page_y0, page_x1, page_y1, offset_x_mm=0, offset_y_mm=0):
        min_x, min_y, max_x, max_y = self.get_bounding_box(c)
        if max_x > page_x0 and min_x < page_x1 and max_y > page_y0 and min_y < page_y1:
            self.draw(c, offset_x_mm, offset_y_mm)

# Example: Dot/Point class
class Dot(CanvasObject):
    def __init__(self, x_mm, y_mm, radius_mm=1, color=colors.black):
        super().__init__(x_mm, y_mm)
        self.radius_mm = radius_mm
        self.color = color

    def get_bounding_box(self):
        return (self.x_mm - self.radius_mm, self.y_mm - self.radius_mm,
                self.x_mm + self.radius_mm, self.y_mm + self.radius_mm)

    def draw(self, c, offset_x_mm=0, offset_y_mm=0):
        x = self.to_points(self.x_mm + offset_x_mm)
        y = self.to_points(self.y_mm + offset_y_mm)
        r = self.to_points(self.radius_mm)
        c.setFillColor(self.color)
        c.circle(x, y, r, stroke=0, fill=1)

    def draw_on_page(self, c, page_x0, page_y0, page_x1, page_y1, offset_x_mm=0, offset_y_mm=0):
        min_x, min_y, max_x, max_y = self.get_bounding_box()
        if max_x > page_x0 and min_x < page_x1 and max_y > page_y0 and min_y < page_y1:
            self.draw(c, offset_x_mm, offset_y_mm)

class CanvasModel:
    def __init__(self, show_grid=False, grid_spacing_mm=10, page_marker_spacing_mm=297):
        self.objects = []
        self.width_mm = None
        self.height_mm = None
        self.offset_x = 0 # ga naar functie add_offsetvoorbanner voor dat inte stellen
        self.offset_y = 45 # banner of border , gans u tekeing alle objecten 50mm ophoogduwen
        self.show_grid = show_grid
        self.grid_spacing_mm = grid_spacing_mm
        self.page_marker_spacing_mm = page_marker_spacing_mm



    def add_object(self, obj):
        self.objects.append(obj)

    def calculate_size(self):
        if not self.objects:
            self.width_mm = 0
            self.height_mm = 0
            return
        #hier zoeken we van all onze objecten die we tekenden de uiterste posities , om zo een idee te hebben hoe groot ons tekenvlak moet zijn
        min_x, min_y, max_x, max_y = calculate_bounding_box(self.objects)
        border = 10 # mm deze rand doen we nadat we alle objecten geteken hebben dan vergroten we ons blad een beetje
        #self.offset_x = 0 #word op nul gezet om geen offset plus offset + offset te hebben
        #self.offset_y = 0
        self.width_mm = max_x + border
        self.height_mm = max_y + border
        print(f"The bounding box van onze oejecten  coordinates are: min_x = {min_x}, min_y = {min_y}, max_x = {max_x}, max_y = {max_y}.")

        print(f"en met onze extra randen erbij             offset_x: {self.offset_x}, offset_y: {self.offset_y}, width_mm: {self.width_mm}, height_mm: {self.height_mm}")

    def draw_grid(self, c, width_mm, height_mm):
        thin_line_width = 0.1
        thick_line_width = 0.5
        thin_color = colors.lightgrey
        thick_color = colors.grey
        page_marker_color = colors.darkgrey
        page_marker_width = 0.3

        # Regular grid lines
        x = 0
        while x <= width_mm:
            x_pt = x * mm
            if (x % 50) == 0:
                c.setStrokeColor(thick_color)
                c.setLineWidth(thick_line_width)
            else:
                c.setStrokeColor(thin_color)
                c.setLineWidth(thin_line_width)
            c.line(x_pt, 0, x_pt, height_mm * mm)
            x += self.grid_spacing_mm

        # Vertical page marker lines (draw directly)
        x = self.page_marker_spacing_mm
        while x < width_mm:
            x_pt = x * mm
            c.setStrokeColor(page_marker_color)
            c.setLineWidth(page_marker_width)
            c.line(x_pt, 0, x_pt, height_mm * mm)
            x += self.page_marker_spacing_mm

        # Horizontal grid lines
        y = 0
        while y <= height_mm:
            y_pt = y * mm
            if (y % 50) == 0:
                c.setStrokeColor(thick_color)
                c.setLineWidth(thick_line_width)
            else:
                c.setStrokeColor(thin_color)
                c.setLineWidth(thin_line_width)
            c.line(0, y_pt, width_mm * mm, y_pt)
            y += self.grid_spacing_mm

    def draw_single_pagina(self, filename):
        self.calculate_size() #als we 1 lange canvas willen zien , overrzie al ons objecten en kijk hoever ze verspreid staan
        c = canvas.Canvas(filename, pagesize=(self.width_mm * mm, self.height_mm * mm))
        if self.show_grid:
            self.draw_grid(c, self.width_mm, self.height_mm)
        for obj in self.objects:
            #obj.draw(c, self.offset_x, self.offset_y)
            obj.draw(c, 0, 0)
        c.showPage()
        c.save()

    def draw_multi_pages(self, filename):
        page_height_mm = 210  # A4 height in landscape
        page_width_mm = PRINTABLE_WIDTH
        page_height_mm = PRINTABLE_HEIGHT
        self.calculate_size() #als we meerde paginas gaan maken gesplit op de paginaMarkeerlijn die groen is

        # --- Step 1: Extract adjusted split lines (paginaMarkeerlijn=True)
        split_lines = sorted(
            obj.get_bounding_box()[0] for obj in self.objects

            if isinstance(obj, VerticalLine) and getattr(obj, "paginaMarkeerlijn", False)
        )

        # --- Step 2: Calculate page rectangles (x0 to x1)
        page_x_ranges = []
        prev_x = 0
        aantalpaginas = 0
        for x in split_lines:
            page_x_ranges.append((prev_x, x))
            prev_x = x
        page_x_ranges.append((prev_x, self.width_mm))  # Add final segment

        # --- Step 3: Prepare Y pages (static hoogte is normaal 210mm )
        y_pages = int(self.height_mm // page_height_mm) + 1

        # --- Step 4: Begin drawing
        c = canvas.Canvas(filename, pagesize=landscape(A4))

        for y in range(y_pages):
            page_y0 = y * page_height_mm
            page_y1 = page_y0 + page_height_mm

            for x0, x1 in page_x_ranges:
                aantalpaginas = aantalpaginas + 1
                page_number_text = f"Page {aantalpaginas}"
                print(f"aantalpaginas: {aantalpaginas}")
                if self.show_grid:
                    self.draw_grid(c, x1 - x0, page_height_mm)

                for obj in self.objects:
                    print(f"multipage offset x0: {x0}")
                    print(f"multipage offset page_y0: {page_y0}")
                    #testvincent
                    #x0 = x0 + self.offset_x
                    #page_y0 = page_y0 + self.offset_y

                    obj.draw_on_page(
                        c,
                        x0, page_y0, x1, page_y1,
                        offset_x_mm=-x0 + self.offset_x + LEFT_MARGIN,
                        offset_y_mm=-page_y0 + self.offset_y + BOTTOM_MARGIN
                    )

                #banner
                c.rect(10 * mm, 10 * mm, 200 * mm, 30 * mm, fill=1, stroke=0)
                #paginanummering
                c.drawRightString(297-50 , 20 , page_number_text)  # 10mm from right
                # Optionally, draw een rand to visualize the printable area
                c.setStrokeColor(colors.darkblue)
                c.rect(LEFT_MARGIN * mm, BOTTOM_MARGIN * mm, PRINTABLE_WIDTH * mm, PRINTABLE_HEIGHT * mm, fill=0, stroke=1)

                c.setStrokeColor(colors.darkred)
                c.rect(3* mm, 3* mm, (297-3-3) * mm, (210-3-3) * mm, fill=0, stroke=1)

                c.showPage()

        c.save()

    def insert_dynamic_paginasplits(self, page_width_mm=297, overlap_whitelist=(HorizontalLine,)):
        self.calculate_size()  # Ensure width_mm is available
        #hier doen we de truck met de groene en rode lijn , die we verschuiven tot een object moet meegenomen worden naar de volgende pagina

        overlap_blacklist = tuple(obj for obj in set(type(o) for o in self.objects)
                                  if obj not in overlap_whitelist)

        x_pos = page_width_mm  # Start at first split
        while x_pos < self.width_mm:
            theoretical_split = x_pos

            # Step 1: Draw green line (always at theoretical position)
            self.add_object(
                VerticalLine(theoretical_split, 0, self.height_mm/2, colors.green, width_mm=0.3, paginaMarkeerlijn=False)
            )
            print(f"degroenelijn hoogte is mm = {self.height_mm/2}")

            # Step 2: Move left from x_pos until there is no collision with blacklisted objects
            adjusted_split = theoretical_split
            while True:
                overlapping = False
                for obj in self.objects:
                    if isinstance(obj, overlap_blacklist):
                        min_x, min_y, max_x, max_y = obj.get_bounding_box()
                        if min_x < adjusted_split < max_x:
                            overlapping = True
                            adjusted_split -= 1  # move left 1mm
                            break
                if not overlapping:
                    break

            # Step 3: Draw red line at final position
            self.add_object(
                VerticalLine(adjusted_split, 0, self.height_mm/2, colors.red, width_mm=0.5, paginaMarkeerlijn=True)
            )
            print(f"derodelijn is mm = {self.height_mm/2}")

            # Step 4: Continue from the red line split (not the theoretical one)
            x_pos = adjusted_split + page_width_mm


class VerticalLine(CanvasObject):
    def __init__(self, x_mm, y_mm, length_mm, color, width_mm=0.5 ,paginaMarkeerlijn = False ):
        super().__init__(x_mm, y_mm)
        self.length_mm = length_mm
        self.color = color
        self.width_mm = width_mm
        self.paginaMarkeerlijn = paginaMarkeerlijn

    def get_bounding_box(self):
        return (self.x_mm, self.y_mm, self.x_mm, self.y_mm + self.length_mm)

    def draw(self, c, offset_x_mm=0, offset_y_mm=0):
        x = self.to_points(self.x_mm + offset_x_mm)
        y = self.to_points(self.y_mm + offset_y_mm)
        length = self.to_points(self.length_mm)
        width = self.to_points(self.width_mm)
        c.setStrokeColor(self.color)
        c.setLineWidth(width)
        c.line(x, y, x, y + length)


if __name__ == "__main__":

    te_tekenen_startpunt.sort_children()
    Component.assign_coords_safe_stacking(te_tekenen_startpunt)
    te_tekenen_startpunt.print_ascii_tree()

    model = CanvasModel(show_grid=True)
    model.add_object(Square(50, 50, 40, colors.red))
    model.add_object(Square(260, 50, 80, colors.red))
    model.add_object(HorizontalLine(100, 10, 500, colors.blue, 1))
    model.add_object(Text(10, 80, "10/80_Dynamic canvas with grid!", 12, colors.black))
    model.add_object(Text(0, 0, "pos0/0", 12, colors.black))
    model.add_object(Dot(0, 0, radius_mm=2, color=colors.green))
    model.add_object(Dot(297, 60, radius_mm=2, color=colors.green))
    model.add_object(Dot(594, 60, radius_mm=2, color=colors.green))

    #model.add_object(VerticalLine(100, 10, 60, colors.pink, 10))
    model.add_object(CarIcon(100, 100, width_mm=50, height_mm=25, body_color=colors.red, wheel_color=colors.black))
    model.add_object(StopcontactAREI(240, 60, size_mm=25))
    model.add_object(ImageIcon(300 , 70 , "symbolen/prieze.png" , 20, 20))
    # Add pagina marker visualizations
    model.insert_dynamic_paginasplits(
        page_width_mm= PRINTABLE_WIDTH ,
        overlap_whitelist=(HorizontalLine,)  # Only allow horizontal lines to overlap
    )

    model.draw_single_pagina("pdf_singlepage.pdf")
    model.draw_multi_pages("pdf_multipage.pdf")

    for obj in model.objects:
        print(type(obj), obj.__dict__)

import os
# Let Windows open the PDFs ok
#os.startfile("pdf_singlepage.pdf")
#os.startfile("pdf_multipage.pdf")
