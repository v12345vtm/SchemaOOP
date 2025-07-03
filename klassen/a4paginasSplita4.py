from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors

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

class VerticalLine(CanvasObject):
    def __init__(self, x_mm, y_mm, length_mm, color, width_mm=0.5):
        super().__init__(x_mm, y_mm)
        self.length_mm = length_mm
        self.color = color
        self.width_mm = width_mm

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

    def draw_on_page(self, c, page_x0, page_y0, page_x1, page_y1, offset_x_mm=0, offset_y_mm=0):
        # Only draw the visible segment
        line_start = max(self.y_mm, page_y0)
        line_end = min(self.y_mm + self.length_mm, page_y1)
        if line_end > line_start and self.x_mm >= page_x0 and self.x_mm < page_x1:
            visible_length = line_end - line_start
            x = self.to_points(self.x_mm + offset_x_mm)
            y = self.to_points(line_start + offset_y_mm)
            length = self.to_points(visible_length)
            width = self.to_points(self.width_mm)
            c.setStrokeColor(self.color)
            c.setLineWidth(width)
            c.line(x, y, x, y + length)

class Text(CanvasObject):
    def __init__(self, x_mm, y_mm, text, font_size_pt=12, color=colors.black):
        super().__init__(x_mm, y_mm)
        self.text = text
        self.font_size_pt = font_size_pt
        self.color = color

    def get_bounding_box(self):
        text_height_mm = self.font_size_pt * 0.3528
        text_width_mm = self.font_size_pt * 0.6 * len(self.text) * 0.3528
        return (self.x_mm, self.y_mm, self.x_mm + text_width_mm, self.y_mm + text_height_mm)

    def draw(self, c, offset_x_mm=0, offset_y_mm=0):
        x = self.to_points(self.x_mm + offset_x_mm)
        y = self.to_points(self.y_mm + offset_y_mm)
        c.setFillColor(self.color)
        c.setFont("Helvetica", self.font_size_pt)
        c.drawString(x, y, self.text)

    def draw_on_page(self, c, page_x0, page_y0, page_x1, page_y1, offset_x_mm=0, offset_y_mm=0):
        # Only draw if any part of text is on the page (no clipping)
        min_x, min_y, max_x, max_y = self.get_bounding_box()
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
        self.offset_x = 0
        self.offset_y = 0
        self.show_grid = show_grid
        self.grid_spacing_mm = grid_spacing_mm
        self.page_marker_spacing_mm = page_marker_spacing_mm  # <--- NEW


    def add_object(self, obj):
        self.objects.append(obj)

    def calculate_size(self):
        if not self.objects:
            self.width_mm = 0
            self.height_mm = 0
            return
        min_x, min_y, max_x, max_y = calculate_bounding_box(self.objects)
        border = 10 # mm
        self.offset_x = 0
        self.offset_y = 0
        self.width_mm = max_x + border
        self.height_mm = max_y + border
        print(f"offset_x: {self.offset_x}, offset_y: {self.offset_y}, width_mm: {self.width_mm}, height_mm: {self.height_mm}")

    def draw_grid(self, c, width_mm, height_mm):
        thin_line_width = 0.1
        thick_line_width = 0.5
        thin_color = colors.lightgrey
        thick_color = colors.grey
        page_marker_color = colors.darkgrey
        page_marker_width = 0.3
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

        # Extra vertical page marker lines every 297 mm
        x = self.page_marker_spacing_mm
        while x < width_mm:
            self.add_object(VerticalLine(x, 0, height_mm, page_marker_color, page_marker_width))
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

    def draw_pages(self, filename):
        self.calculate_size()
        c = canvas.Canvas(filename, pagesize=(self.width_mm * mm, self.height_mm * mm))
        if self.show_grid:
            self.draw_grid(c, self.width_mm, self.height_mm)
        for obj in self.objects:
            obj.draw(c, self.offset_x, self.offset_y)
        c.showPage()
        c.save()

    def draw_paginated_pages(self, filename):
        page_width_mm, page_height_mm = landscape(A4)
        page_width_mm /= mm
        page_height_mm /= mm

        self.calculate_size()
        x_pages = int(self.width_mm // page_width_mm) + 1
        y_pages = int(self.height_mm // page_height_mm) + 1

        c = canvas.Canvas(filename, pagesize=landscape(A4))

        for y in range(y_pages):
            for x in range(x_pages):
                page_x0 = x * page_width_mm
                page_y0 = y * page_height_mm
                page_x1 = page_x0 + page_width_mm
                page_y1 = page_y0 + page_height_mm

                if self.show_grid:
                    self.draw_grid(c, page_width_mm, page_height_mm)

                for obj in self.objects:
                    obj.draw_on_page(
                        c,
                        page_x0, page_y0, page_x1, page_y1,
                        offset_x_mm=-page_x0,
                        offset_y_mm=-page_y0
                    )
                c.showPage()
        c.save()


class VerticalLine(CanvasObject):
    def __init__(self, x_mm, y_mm, length_mm, color, width_mm=0.5):
        super().__init__(x_mm, y_mm)
        self.length_mm = length_mm
        self.color = color
        self.width_mm = width_mm

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
    model = CanvasModel(show_grid=True)
    model.add_object(Square(50, 50, 40, colors.red))
    model.add_object(Square(260, 50, 80, colors.red))
    model.add_object(HorizontalLine(100, 10, 250, colors.blue, 1))
    model.add_object(Text(10, 80, "10/80_Dynamic canvas with grid!", 12, colors.black))
    model.add_object(Dot(300, 60, radius_mm=2, color=colors.green))

    model.add_object(VerticalLine(100, 10, 60, colors.pink, 10))

    model.draw_pages("1single_canvas_output.pdf")
    model.draw_paginated_pages("1paginated_canvas_output.pdf")

    for obj in model.objects:
        print(type(obj), obj.__dict__)

