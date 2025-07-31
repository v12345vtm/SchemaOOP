class Appliance(Component):

    def __init__(self, label, lokatie, **kwargs):
        super().__init__(label, lokatie, **kwargs)
        self.stroomrichting = "horizontal"
        self.lijsttoestellen = ["vaatwas", "droogkast", "oven", "reserve"]

    def draw_svg(self, drawing, x_spacing=0, y_spacing=0, swapy=False):
        # First, call the base method to draw the boundary
        super().draw_svg(drawing, x_spacing, y_spacing, swapy)

        # Now, add the text just right of the boundary box
        pixel_x = self.grid_x + x_spacing
        pixel_y = self.grid_y + y_spacing

        label_x = pixel_x + self.boundarybox_breedte + 10  # 10px gap to the right
        label_y = pixel_y + self.boundarybox_hoogte // 2   # Vertically centered

        drawing.append(draw.Text(
            self.label,    # Or any text you'd like
            17,            # Font size
            label_x, label_y,
            fill='blue',
            center=False,    # Or True if you want centering logic
            valign='middle'
        ))
