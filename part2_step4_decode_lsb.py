import re
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("[ERROR] Pillow is not installed.")
    print("Install it with: py -m pip install pillow")
    sys.exit(1)


# ตำแหน่งไฟล์ PNG จาก Part 1
png_path = Path(
    r"D:\test\Blue-Team-Scenario"
    r"\part1-output\final_payload.png"
)

if not png_path.exists():
    raise FileNotFoundError(
        f"PNG file not found: {png_path}"
    )


# เปิดภาพและแปลงเป็น RGB
with Image.open(png_path) as source_image:
    image = source_image.convert("RGB")
    pixels = list(image.getdata())


# ดึงบิตสุดท้ายตามลำดับ Red -> Green -> Blue
bits = []

for red, green, blue in pixels:
    bits.append(red & 1)
    bits.append(green & 1)
    bits.append(blue & 1)


# รวมทุก 8 บิตแบบ MSB-first แล้วแปลงเป็น byte
decoded = bytearray()

for position in range(0, len(bits) - 7, 8):
    value = 0

    for bit in bits[position:position + 8]:
        value = (value << 1) | bit

    decoded.append(value)


# แสดงข้อมูลช่วงต้นก่อนถึง binary noise
preview = decoded[:200].decode(
    "ascii",
    errors="replace",
)


# ค้นหา Flag ที่อยู่ในข้อมูลที่ถอดได้
flag_match = re.search(
    rb"WORLDSKILLS-TH\{[^}]+\}",
    decoded,
)

if flag_match:
    flag = flag_match.group().decode(
        "ascii",
        errors="replace",
    )
else:
    flag = None


# หยุดแสดงข้อความเมื่อพบเครื่องหมาย } ตัวแรก
closing_brace = decoded.find(b"}")

if closing_brace != -1:
    clean_message = decoded[
        :closing_brace + 1
    ].decode(
        "ascii",
        errors="replace",
    )
else:
    clean_message = preview


print("=" * 90)
print("PART 2 - STEP 4: RGB LSB DECODING")
print("=" * 90)
print("File:", png_path)
print("Image size:", image.size)
print("Pixel count:", f"{len(pixels):,}")
print("LSB order: Red -> Green -> Blue")
print("Byte order: MSB-first")

print()
print("DECODED MESSAGE")
print("-" * 90)
print(clean_message)

print()
print("FLAG EXTRACTION")
print("-" * 90)

if flag:
    print("[FOUND] Part 2 Flag:")
    print(flag)
else:
    print("[NOT FOUND] No valid flag pattern was detected.")

print()
print("NOTE")
print("-" * 90)
print(
    "Decoding stops at the closing brace because "
    "the remaining bytes are binary noise."
)
print("=" * 90)
