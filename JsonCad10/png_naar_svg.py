import os
from pixels2svg import pixels2svg

def convert_all_png_to_svg(root_folder):
    for dirpath, dirnames, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.lower().endswith('.png'):
                png_path = os.path.join(dirpath, filename)
                svg_path = os.path.splitext(png_path)[0] + '.svg'
                try:
                    print(f"Converting {png_path} ...")
                    pixels2svg(png_path, svg_path)
                    print(f"Saved as {svg_path}")
                except Exception as e:
                    print(f"Failed to convert {png_path}: {e}")

if __name__ == "__main__":
    # Change this if your folder location is different
    convert_all_png_to_svg('symbolen')
