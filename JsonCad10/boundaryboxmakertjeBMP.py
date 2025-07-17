from PIL import Image, ImageDraw

# Image size and border thickness
size = 100
border = 4
divider_width = 4
center_square_size = 28  # Calculated to fit in the center with 4px border

# Create white background
img = Image.new("RGB", (size, size), "white")
draw = ImageDraw.Draw(img)

# Draw black border
draw.rectangle([0, 0, size-1, size-1], outline="black", width=border)

# Draw horizontal divider (red, 4px)
h_start = (size - divider_width) // 2
draw.rectangle([0, h_start, size-1, h_start + divider_width - 1], fill="red")

# Draw vertical divider (red, 4px)
v_start = (size - divider_width) // 2
draw.rectangle([v_start, 0, v_start + divider_width - 1, size-1], fill="red")

# Draw central square with black border
# Calculate the top-left and bottom-right coordinates for the square
square_outer = [
    (size - center_square_size) // 2,
    (size - center_square_size) // 2,
    (size + center_square_size) // 2 - 1,
    (size + center_square_size) // 2 - 1
]
draw.rectangle(square_outer, outline="black", width=border)

# Save as BMP
img.save("output.bmp")
