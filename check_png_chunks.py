import struct
from pathlib import Path

png_path = Path(
    r"D:\test\Blue-Team-Scenario\part1-output\final_payload.png"
)

if not png_path.exists():
    raise FileNotFoundError(f"PNG file not found: {png_path}")

data = png_path.read_bytes()

png_signature = b"\x89PNG\r\n\x1a\n"

if not data.startswith(png_signature):
    raise RuntimeError("Invalid PNG signature")

print("=" * 90)
print("PART 2 - PNG CHUNK ANALYSIS")
print("=" * 90)
print("File:", png_path)
print("File size:", f"{len(data):,}", "bytes")
print("PNG signature: VALID")
print()

position = 8
chunk_number = 1

while position + 12 <= len(data):
    length = struct.unpack(
        ">I",
        data[position:position + 4]
    )[0]

    chunk_type = data[
        position + 4:
        position + 8
    ]

    chunk_data_start = position + 8
    chunk_data_end = chunk_data_start + length
    chunk_end = chunk_data_end + 4

    if chunk_end > len(data):
        print("[ERROR] Chunk exceeds file size")
        break

    chunk_name = chunk_type.decode(
        "ascii",
        errors="replace"
    )

    print(
        f"Chunk {chunk_number:02d}: "
        f"{chunk_name:<4} | "
        f"Length: {length:,} bytes"
    )

    chunk_data = data[
        chunk_data_start:
        chunk_data_end
    ]

    if chunk_type == b"tEXt":
        print("-" * 90)
        print("tEXt CHUNK CONTENT")

        if b"\x00" in chunk_data:
            keyword, text = chunk_data.split(
                b"\x00",
                1
            )

            print(
                "Keyword:",
                keyword.decode(
                    "latin-1",
                    errors="replace"
                )
            )

            print(
                "Text:",
                text.decode(
                    "latin-1",
                    errors="replace"
                )
            )
        else:
            print(
                chunk_data.decode(
                    "latin-1",
                    errors="replace"
                )
            )

        print("-" * 90)

    elif chunk_type in (b"iTXt", b"zTXt"):
        print("-" * 90)
        print(f"{chunk_name} RAW CONTENT:")
        print(
            chunk_data.decode(
                "latin-1",
                errors="replace"
            )
        )
        print("-" * 90)

    position += 12 + length
    chunk_number += 1

    if chunk_type == b"IEND":
        break

print()
print("=" * 90)
print("ANALYSIS")
print("=" * 90)
print(
    "The tEXt chunk contains an instruction directed at an AI or analyst."
)
print(
    "It is treated as prompt injection and a decoy, not as forensic evidence."
)
print(
    "Pixel data must still be examined for hidden information."
)
print("=" * 90)
