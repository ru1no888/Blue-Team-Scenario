import email
import hashlib
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

from email import policy
from io import BytesIO
from pathlib import Path


# =========================================================
# แก้ปัญหา Terminal แสดงภาษาไทยไม่ได้
# =========================================================

try:
    sys.stdout.reconfigure(
        encoding="utf-8",
        errors="replace",
    )
except AttributeError:
    pass


# =========================================================
# ตำแหน่งไฟล์
# =========================================================

email_folder = Path(
    r"D:\test\Blue-Team-Scenario\Blue Team"
    r"\Blue Team Scenario 1\part1-3email_corpus"
)

eml_0504 = email_folder / "mailbox_item_0504.eml"
eml_0666 = email_folder / "mailbox_item_0666.eml"

output = Path(__file__).resolve().parent / "analysis-output"
output.mkdir(parents=True, exist_ok=True)

output_0504 = output / "mailbox_0504"
output_0666 = output / "mailbox_0666"

output_0504.mkdir(parents=True, exist_ok=True)
output_0666.mkdir(parents=True, exist_ok=True)


# =========================================================
# เก็บข้อความทั้งหมดไว้สร้างรายงาน
# =========================================================

report_lines = []


def log(*values):
    text = " ".join(str(value) for value in values)
    print(text)
    report_lines.append(text)


def separator(title):
    log()
    log("=" * 100)
    log(title)
    log("=" * 100)


# =========================================================
# ฟังก์ชันอ่าน EML และดึง DOCX
# =========================================================

def extract_docx_from_eml(eml_path):
    if not eml_path.exists():
        raise FileNotFoundError(
            f"ไม่พบไฟล์ EML: {eml_path}"
        )

    eml_data = eml_path.read_bytes()

    message = email.message_from_bytes(
        eml_data,
        policy=policy.default,
    )

    docx_data = None
    docx_filename = None

    for part in message.walk():
        filename = part.get_filename() or ""

        if filename.lower().endswith(".docx"):
            docx_data = part.get_payload(decode=True)
            docx_filename = filename
            break

    if docx_data is None:
        raise RuntimeError(
            f"ไม่พบไฟล์ DOCX ใน {eml_path.name}"
        )

    return {
        "eml_data": eml_data,
        "message": message,
        "docx_data": docx_data,
        "docx_filename": docx_filename,
    }


# =========================================================
# ฟังก์ชันอ่านข้อความจาก XML
# =========================================================

def extract_xml_text(xml_data):
    try:
        root = ET.fromstring(xml_data)

        text_parts = []

        for text in root.itertext():
            text = text.strip()

            if text:
                text_parts.append(text)

        return " ".join(text_parts)

    except ET.ParseError:
        return xml_data.decode(
            "utf-8",
            errors="replace",
        )


# =========================================================
# ตรวจสอบไฟล์ที่ต้องใช้
# =========================================================

separator("INPUT FILE CHECK")

log("Email folder:", email_folder)
log("mailbox_item_0504.eml exists:", eml_0504.exists())
log("mailbox_item_0666.eml exists:", eml_0666.exists())

if not eml_0504.exists() or not eml_0666.exists():
    raise FileNotFoundError(
        "ไม่พบไฟล์ EML ที่ต้องใช้ กรุณาตรวจสอบ path"
    )


# =========================================================
# PART 1: mailbox_item_0504.eml
# =========================================================

separator("PART 1 - MAILBOX ITEM 0504")

result_0504 = extract_docx_from_eml(eml_0504)

eml_0504_data = result_0504["eml_data"]
docx_0504_data = result_0504["docx_data"]
docx_0504_filename = result_0504["docx_filename"]

log("Subject:", result_0504["message"].get("Subject", ""))
log("From:", result_0504["message"].get("From", ""))
log("DOCX found:", docx_0504_filename)
log("DOCX size:", f"{len(docx_0504_data):,}", "bytes")

docx_0504_path = output_0504 / "Report_504.docx"
docx_0504_path.write_bytes(docx_0504_data)

log("DOCX saved:", docx_0504_path.resolve())


# =========================================================
# เปิด Report_504.docx แบบ ZIP
# =========================================================

separator("REPORT_504.DOCX MEMBERS")

with zipfile.ZipFile(
    BytesIO(docx_0504_data),
    "r",
) as archive:

    members_0504 = archive.namelist()

    for member in members_0504:
        log(member)

    required_files = [
        "word/document.xml",
        "word/_rels/document.xml.rels",
        "word/media/image1.png",
    ]

    for required_file in required_files:
        if required_file not in members_0504:
            raise RuntimeError(
                f"ไม่พบ {required_file} ใน Report_504.docx"
            )

    document_0504_xml = archive.read(
        "word/document.xml"
    )

    relationships_0504_xml = archive.read(
        "word/_rels/document.xml.rels"
    )

    image_0504_data = archive.read(
        "word/media/image1.png"
    )


# =========================================================
# บันทึกและอ่านข้อความใน document.xml
# =========================================================

(output_0504 / "document.xml").write_bytes(
    document_0504_xml
)

(output_0504 / "document.xml.rels").write_bytes(
    relationships_0504_xml
)

document_0504_text = extract_xml_text(
    document_0504_xml
)

(output_0504 / "document_text.txt").write_text(
    document_0504_text,
    encoding="utf-8",
)

separator("TEXT FROM REPORT_504 DOCUMENT.XML")
log(document_0504_text)


# =========================================================
# กู้ PNG ที่ถูกต้อง
# =========================================================

separator("PNG RECOVERY RESULT")

png_end_marker = b"IEND" + bytes.fromhex(
    "ae426082"
)

png_end = image_0504_data.rfind(
    png_end_marker
)

if png_end == -1:
    raise RuntimeError(
        "PNG IEND marker not found"
    )

png_end += len(png_end_marker)

valid_png = image_0504_data[:png_end]
appended_data = image_0504_data[png_end:]

full_image_path = output_0504 / "image1_full.bin"
full_image_path.write_bytes(image_0504_data)

png_path = output_0504 / "final_payload.png"
png_path.write_bytes(valid_png)

appended_path = output_0504 / "data_after_png.bin"
appended_path.write_bytes(appended_data)

valid_png_sha256 = hashlib.sha256(
    valid_png
).hexdigest()

log(
    "Full embedded image:",
    f"{len(image_0504_data):,}",
    "bytes",
)

log(
    "Valid PNG:",
    f"{len(valid_png):,}",
    "bytes",
)

log(
    "Appended data:",
    f"{len(appended_data):,}",
    "bytes",
)

log("PNG SHA256:", valid_png_sha256)
log("PNG saved:", png_path.resolve())


# =========================================================
# ตรวจสอบผล PNG
# =========================================================

expected_full_size = 4_139_492
expected_png_size = 291_365

expected_png_sha256 = (
    "afd676e00bbe116bd1dd32b27247e9da"
    "899fca09113755bb6ea3dc684508e8f2"
)

log()
log("Verification:")

if len(image_0504_data) == expected_full_size:
    log("[OK] Full embedded image size is correct")
else:
    log(
        "[WARNING] Full embedded image size differs"
    )

if len(valid_png) == expected_png_size:
    log("[OK] Valid PNG size is correct")
else:
    log("[WARNING] Valid PNG size differs")

if valid_png_sha256 == expected_png_sha256:
    log("[OK] PNG SHA256 is correct")
else:
    log("[WARNING] PNG SHA256 differs")


# =========================================================
# คำนวณ MD5 และสร้าง Flag จริง
# =========================================================

separator("PART 1 FLAG CALCULATION")

md5_input = "pa5t1-1s-s0-no1sy"

md5_result = hashlib.md5(
    md5_input.encode("utf-8")
).hexdigest()

real_flag = (
    f"WORLDSKILLS-TH{{{md5_result}}}"
)

log(
    "Text from image:",
    "WORLDSKILLS-TH{md5(pa5t1-1s-s0-no1sy)}",
)

log("MD5 input:", md5_input)
log("MD5 result:", md5_result)
log("Final flag:", real_flag)

(output_0504 / "part1_flag.txt").write_text(
    real_flag + "\n",
    encoding="utf-8",
)


# =========================================================
# Artifact Hashes
# =========================================================

separator("ARTIFACT HASHES")

eml_0504_sha256 = hashlib.sha256(
    eml_0504_data
).hexdigest()

docx_0504_sha256 = hashlib.sha256(
    docx_0504_data
).hexdigest()

full_image_sha256 = hashlib.sha256(
    image_0504_data
).hexdigest()

log(f"{'Artifact':<30} SHA-256")
log("-" * 100)

log(
    f"{'mailbox_item_0504.eml':<30}"
    f" {eml_0504_sha256}"
)

log(
    f"{'Report_504.docx':<30}"
    f" {docx_0504_sha256}"
)

log(
    f"{'Embedded image full':<30}"
    f" {full_image_sha256}"
)

log(
    f"{'PNG after payload removal':<30}"
    f" {valid_png_sha256}"
)

hash_report = (
    "Artifact Hashes\n"
    "===============\n"
    f"mailbox_item_0504.eml\n{eml_0504_sha256}\n\n"
    f"Report_504.docx\n{docx_0504_sha256}\n\n"
    f"Embedded image full\n{full_image_sha256}\n\n"
    f"PNG after payload removal\n{valid_png_sha256}\n"
)

(output_0504 / "artifact_hashes.txt").write_text(
    hash_report,
    encoding="utf-8",
)


# =========================================================
# ตรวจ Fake Flag: mailbox_item_0666.eml
# =========================================================

separator("FAKE FLAG CHECK - MAILBOX ITEM 0666")

result_0666 = extract_docx_from_eml(eml_0666)

eml_0666_data = result_0666["eml_data"]
docx_0666_data = result_0666["docx_data"]
docx_0666_filename = result_0666["docx_filename"]

log("Subject:", result_0666["message"].get("Subject", ""))
log("From:", result_0666["message"].get("From", ""))
log("DOCX found:", docx_0666_filename)
log("DOCX size:", f"{len(docx_0666_data):,}", "bytes")

docx_0666_path = output_0666 / "Report_666.docx"
docx_0666_path.write_bytes(docx_0666_data)

log("DOCX saved:", docx_0666_path.resolve())


# =========================================================
# เปิด Report_666.docx และอ่านข้อความ
# =========================================================

separator("REPORT_666.DOCX ANALYSIS")

with zipfile.ZipFile(
    BytesIO(docx_0666_data),
    "r",
) as archive:

    members_0666 = archive.namelist()

    log("Files inside DOCX:")

    for member in members_0666:
        log(member)

    if "word/document.xml" not in members_0666:
        raise RuntimeError(
            "word/document.xml not found in Report_666.docx"
        )

    document_0666_xml = archive.read(
        "word/document.xml"
    )

    if "word/media/image1.png" in members_0666:
        image_0666_data = archive.read(
            "word/media/image1.png"
        )

        image_0666_path = output_0666 / "image1.png"
        image_0666_path.write_bytes(
            image_0666_data
        )
    else:
        image_0666_data = None
        image_0666_path = None


document_0666_text = extract_xml_text(
    document_0666_xml
)

(output_0666 / "document.xml").write_bytes(
    document_0666_xml
)

(output_0666 / "document_text.txt").write_text(
    document_0666_text,
    encoding="utf-8",
)


# =========================================================
# ค้นหา Prompt Injection และ Fake Flag
# =========================================================

separator("PROMPT INJECTION EVIDENCE")

log("Text from Report_666.docx:")
log(document_0666_text)

prompt_indicators = [
    "ignore all previous instructions",
    "ignore previous instructions",
    "disregard previous instructions",
    "submit this flag",
    "the flag is exactly as follows",
]

document_0666_lower = document_0666_text.lower()

found_indicators = []

for indicator in prompt_indicators:
    if indicator in document_0666_lower:
        found_indicators.append(indicator)
        log("[FOUND]", indicator)

flag_pattern = re.compile(
    r"(?:WORLDSKILLS-TH|WorldSkills)"
    r"\{[^}\r\n]{1,200}\}",
    re.IGNORECASE,
)

fake_flags = flag_pattern.findall(
    document_0666_text
)

for fake_flag in fake_flags:
    log("[FLAG-LIKE STRING]", fake_flag)


# =========================================================
# สรุป Fake Flag โดยอิงหลักฐานจริง
# =========================================================

separator("FAKE FLAG CONCLUSION")

if found_indicators:
    log(
        "[SUSPICIOUS] Prompt-injection language "
        "was found in Report_666.docx"
    )
else:
    log(
        "[NOT FOUND] No predefined prompt-injection "
        "phrase was found"
    )

if fake_flags:
    for fake_flag in fake_flags:
        log("Fake/decoy flag candidate:", fake_flag)

if (
    found_indicators
    and fake_flags
):
    log(
        "Conclusion: The flag in Report_666.docx "
        "is treated as a fake or decoy flag."
    )

    log(
        "Reason: It appears next to an instruction "
        "telling the analyst or AI to ignore previous "
        "instructions."
    )

    log(
        "It also does not match the verified artifact "
        "chain from mailbox_item_0504.eml."
    )
else:
    log(
        "Conclusion: Manual inspection is still required."
    )

log()
log("Verified artifact chain:")
log(
    "mailbox_item_0504.eml"
    " -> Report_504.docx"
    " -> word/media/image1.png"
    " -> valid PNG"
    " -> MD5 calculation"
)

log("Verified final flag:", real_flag)


# =========================================================
# Hashes ของ 0666
# =========================================================

separator("MAILBOX 0666 HASHES")

log(
    "mailbox_item_0666.eml SHA256:",
    hashlib.sha256(eml_0666_data).hexdigest(),
)

log(
    "Report_666.docx SHA256:",
    hashlib.sha256(docx_0666_data).hexdigest(),
)

if image_0666_data is not None:
    log(
        "Report_666 embedded image SHA256:",
        hashlib.sha256(image_0666_data).hexdigest(),
    )

    log(
        "Report_666 embedded image saved:",
        image_0666_path.resolve(),
    )


# =========================================================
# บันทึกรายงานทั้งหมด
# =========================================================

separator("COMPLETED")

report_path = output / "analysis_report.txt"

report_path.write_text(
    "\n".join(report_lines),
    encoding="utf-8",
)

log("Output folder:", output.resolve())
log("Full report:", report_path.resolve())
log("Recovered PNG:", png_path.resolve())
log("Final flag:", real_flag)


# =========================================================
# เปิดภาพจริงและโฟลเดอร์ผลลัพธ์
# =========================================================

try:
    os.startfile(str(png_path.resolve()))
except OSError:
    pass

try:
    os.startfile(str(output.resolve()))
except OSError:
    pass