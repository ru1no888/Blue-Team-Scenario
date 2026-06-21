import hashlib
import os
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("[ERROR] Pillow is not installed.")
    print("Install it with: py -m pip install pillow")
    sys.exit(1)


png_path = Path(
    r"D:\test\Blue-Team-Scenario"
    r"\part1-output\final_payload.png"
)

if not png_path.exists():
    raise FileNotFoundError(
        f"PNG file not found: {png_path}"
    )


png_data = png_path.read_bytes()
png_sha256 = hashlib.sha256(png_data).hexdigest()

with Image.open(png_path) as source_image:
    image = source_image.convert("RGB")

    width, height = image.size
    pixel_count = width * height

    first_pixel = image.getpixel((0, 0))
    center_pixel = image.getpixel(
        (width // 2, height // 2)
    )

    first_red, first_green, first_blue = first_pixel

    first_red_lsb = first_red & 1
    first_green_lsb = first_green & 1
    first_blue_lsb = first_blue & 1


print("=" * 90)
print("PART 2 - STEP 3: PIXEL DATA INSPECTION")
print("=" * 90)

print("File:", png_path)
print("SHA256:", png_sha256)
print("Image format: PNG")
print("Color mode used for analysis: RGB")
print(f"Image dimensions: {width} x {height} pixels")
print(f"Total pixels: {pixel_count:,}")

print()
print("PIXEL DATA SAMPLE")
print("-" * 90)
print(f"First pixel RGB:  {first_pixel}")
print(f"Center pixel RGB: {center_pixel}")

print()
print("LEAST SIGNIFICANT BIT EXAMPLE")
print("-" * 90)
print(f"Red   value: {first_red:3d} | binary: {first_red:08b} | LSB: {first_red_lsb}")
print(f"Green value: {first_green:3d} | binary: {first_green:08b} | LSB: {first_green_lsb}")
print(f"Blue  value: {first_blue:3d} | binary: {first_blue:08b} | LSB: {first_blue_lsb}")

print()
print("ANALYSIS METHOD")
print("-" * 90)
print("1. Read pixels from left to right and top to bottom.")
print("2. Extract the least significant bit from Red.")
print("3. Extract the least significant bit from Green.")
print("4. Extract the least significant bit from Blue.")
print("5. Append the bits in RGB order.")
print("6. Group every 8 bits using MSB-first order.")
print("7. Convert each group into a byte and inspect it as ASCII.")

print()
print("OBSERVATION")
print("-" * 90)
print("The image appears normal when viewed.")
print("Possible LSB changes cannot be reliably identified by eyesight alone.")
print("A separate decoding script is required to recover hidden data.")
print("=" * 90)

try:
    os.startfile(str(png_path.resolve()))
except OSError as error:
    print("Could not open image automatically:", error)
