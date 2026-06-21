import email
import hashlib
import zipfile

from email import policy
from io import BytesIO
from pathlib import Path


# =========================================================
# กำหนดตำแหน่งไฟล์
# =========================================================

eml_path = Path(
    r"D:\test\Blue-Team-Scenario\Blue Team"
    r"\Blue Team Scenario 1\part1-3email_corpus"
    r"\mailbox_item_0504.eml"
)

output = Path("part1-output")
output.mkdir(parents=True, exist_ok=True)


# =========================================================
# ตรวจสอบไฟล์ EML
# =========================================================

if not eml_path.exists():
    raise FileNotFoundError(
        f"ไม่พบไฟล์ EML:\n{eml_path}"
    )


# =========================================================
# อ่านไฟล์ EML
# =========================================================

eml_data = eml_path.read_bytes()

message = email.message_from_bytes(
    eml_data,
    policy=policy.default,
)


# =========================================================
# ดึงไฟล์ DOCX จาก EML
# =========================================================

docx_data = None

for part in message.walk():
    filename = part.get_filename() or ""

    if filename.lower().endswith(".docx"):
        docx_data = part.get_payload(decode=True)
        print("Found DOCX:", filename)
        break

if docx_data is None:
    raise RuntimeError("DOCX attachment not found")


# =========================================================
# ดึง Embedded Image จาก DOCX
# =========================================================

with zipfile.ZipFile(BytesIO(docx_data), "r") as archive:
    image_data = archive.read("word/media/image1.png")


# =========================================================
# ตัดข้อมูลหลัง PNG IEND marker
# =========================================================

png_end_marker = b"IEND" + bytes.fromhex("ae426082")

png_end = image_data.rfind(png_end_marker)

if png_end == -1:
    raise RuntimeError("PNG IEND marker not found")

png_end += len(png_end_marker)

valid_png = image_data[:png_end]


# =========================================================
# คำนวณ SHA-256
# =========================================================

eml_sha256 = hashlib.sha256(eml_data).hexdigest()
docx_sha256 = hashlib.sha256(docx_data).hexdigest()
embedded_image_sha256 = hashlib.sha256(image_data).hexdigest()
valid_png_sha256 = hashlib.sha256(valid_png).hexdigest()


# =========================================================
# แสดง Artifact Hashes
# =========================================================

print()
print("=" * 100)
print("ARTIFACT HASHES")
print("=" * 100)
print(f"{'Artifact':<30} {'SHA-256'}")
print("-" * 100)
print(f"{'mailbox_item_0504.eml':<30} {eml_sha256}")
print(f"{'Report_504.docx':<30} {docx_sha256}")
print(f"{'Embedded image full':<30} {embedded_image_sha256}")
print(f"{'PNG after payload removal':<30} {valid_png_sha256}")
print("=" * 100)


# =========================================================
# บันทึกผลลงไฟล์ artifact_hashes.txt
# =========================================================

hash_report = (
    "Artifact Hashes\n"
    "===============\n"
    f"mailbox_item_0504.eml\n"
    f"{eml_sha256}\n\n"
    f"Report_504.docx\n"
    f"{docx_sha256}\n\n"
    f"Embedded image full\n"
    f"{embedded_image_sha256}\n\n"
    f"PNG after payload removal\n"
    f"{valid_png_sha256}\n"
)

hash_report_path = output / "artifact_hashes.txt"

hash_report_path.write_text(
    hash_report,
    encoding="utf-8",
)

print()
print("Hash report saved:")
print(hash_report_path.resolve())