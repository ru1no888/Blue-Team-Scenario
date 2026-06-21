import email
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

from email import policy
from io import BytesIO
from pathlib import Path


# ให้ Terminal รองรับ UTF-8
sys.stdout.reconfigure(
    encoding="utf-8",
    errors="replace",
)


# ตำแหน่งไฟล์ mailbox_item_0666.eml
eml_path = Path(
    r"D:\test\Blue-Team-Scenario\Blue Team"
    r"\Blue Team Scenario 1\part1-3email_corpus"
    r"\mailbox_item_0666.eml"
)

# โฟลเดอร์เก็บผลลัพธ์
output = Path("part1-output")
output.mkdir(parents=True, exist_ok=True)


# ตรวจสอบว่าไฟล์มีอยู่จริง
if not eml_path.exists():
    raise FileNotFoundError(
        f"File not found: {eml_path}"
    )


# อ่านไฟล์ EML
with eml_path.open("rb") as file:
    message = email.message_from_binary_file(
        file,
        policy=policy.default,
    )


# ค้นหาไฟล์แนบ DOCX
docx_data = None
docx_filename = None

for part in message.walk():
    filename = part.get_filename() or ""

    if filename.lower().endswith(".docx"):
        docx_data = part.get_payload(decode=True)
        docx_filename = filename
        break


if docx_data is None:
    raise RuntimeError("DOCX attachment not found")


# เปิด DOCX แบบ ZIP และอ่าน document.xml
with zipfile.ZipFile(BytesIO(docx_data), "r") as archive:
    document_xml = archive.read(
        "word/document.xml"
    )


# ดึงข้อความจาก document.xml
namespace = {
    "w": (
        "http://schemas.openxmlformats.org/"
        "wordprocessingml/2006/main"
    )
}

root = ET.fromstring(document_xml)

text_parts = []

for element in root.findall(".//w:t", namespace):
    if element.text:
        text_parts.append(element.text)

document_text = " ".join(text_parts)


# ตรวจหา Prompt Injection
prompt_injection_text = (
    "ignore all previous instructions"
)

prompt_injection_found = (
    prompt_injection_text
    in document_text.lower()
)


# ตรวจหาข้อความรูปแบบ Flag
flag_pattern = re.compile(
    r"[A-Za-z0-9_-]+\{[^}\r\n]+\}"
)

flags = flag_pattern.findall(document_text)


# แสดงผลสำหรับถ่ายรูปที่ 10
print("=" * 90)
print("MAILBOX ITEM 0666 - FAKE FLAG CHECK")
print("=" * 90)

print(f"EML file:  {eml_path.name}")
print(f"DOCX file: {docx_filename}")

print()
print("TEXT FOUND IN word/document.xml")
print("-" * 90)
print(document_text)

print()
print("ANALYSIS RESULT")
print("-" * 90)

if prompt_injection_found:
    print(
        "[FOUND] Prompt injection phrase: "
        "IGNORE ALL PREVIOUS INSTRUCTIONS"
    )
else:
    print(
        "[NOT FOUND] Prompt injection phrase"
    )

if flags:
    for flag in flags:
        print(
            f"[FOUND] Fake flag candidate: {flag}"
        )
else:
    print("[NOT FOUND] Flag-like string")

print()
print("WHY IT IS REJECTED")
print("-" * 90)
print(
    "1. The document tells the analyst to ignore "
    "previous instructions."
)
print(
    "2. The flag is directly supplied by the "
    "untrusted document."
)
print(
    "3. Its format does not match "
    "WORLDSKILLS-TH{...}."
)
print(
    "4. It is not supported by the verified "
    "artifact chain from mailbox_item_0504.eml."
)

print()
print("CONCLUSION")
print("-" * 90)
print(
    "mailbox_item_0666.eml contains prompt "
    "injection and a fake flag."
)
print(
    "The flag from mailbox_item_0666.eml "
    "must not be submitted."
)
print("=" * 90)


# บันทึกผลลงไฟล์
report_path = output / "fake_flag_0666_evidence.txt"

report = (
    "MAILBOX ITEM 0666 - FAKE FLAG CHECK\n"
    + "=" * 60
    + "\n"
    + f"EML file: {eml_path.name}\n"
    + f"DOCX file: {docx_filename}\n\n"
    + "TEXT FOUND:\n"
    + document_text
    + "\n\n"
    + "Prompt injection found: "
    + str(prompt_injection_found)
    + "\n"
    + "Flag-like strings: "
    + ", ".join(flags)
    + "\n\n"
    + "Conclusion: mailbox_item_0666.eml "
    + "contains prompt injection and a fake flag.\n"
)

report_path.write_text(
    report,
    encoding="utf-8",
)

print()
print("Evidence report saved:")
print(report_path.resolve())