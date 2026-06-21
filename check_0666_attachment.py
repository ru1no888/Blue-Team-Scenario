import email
import hashlib
import html
import os
import re
import zipfile

from email import policy
from io import BytesIO
from pathlib import Path


# =========================================================
# ตำแหน่งไฟล์ mailbox_item_0666.eml
# =========================================================

eml_path = Path(
    r"D:\test\Blue-Team-Scenario\Blue Team"
    r"\Blue Team Scenario 1\part1-3email_corpus"
    r"\mailbox_item_0666.eml"
)

output = Path("part1-output") / "mailbox_0666"
output.mkdir(parents=True, exist_ok=True)


# =========================================================
# รูปแบบ Flag และคำที่มีลักษณะเป็น Prompt Injection
# =========================================================

flag_pattern = re.compile(
    r"WORLDSKILLS-TH\{[^}\r\n]{1,300}\}",
    re.IGNORECASE,
)

suspicious_keywords = [
    "ignore previous instructions",
    "ignore all previous instructions",
    "disregard previous instructions",
    "forget previous instructions",
    "override previous instructions",
    "system prompt",
    "developer message",
    "prompt injection",
    "do not analyze",
    "do not inspect",
    "stop analyzing",
    "submit this flag",
    "use this flag",
    "correct flag",
    "final flag",
    "final answer",
    "trust this",
]


# =========================================================
# ตรวจสอบไฟล์ EML
# =========================================================

if not eml_path.exists():
    raise FileNotFoundError(
        f"ไม่พบไฟล์:\n{eml_path}"
    )

eml_data = eml_path.read_bytes()

print("=" * 100)
print("MAILBOX ITEM 0666 ATTACHMENT ANALYSIS")
print("=" * 100)
print("EML file:", eml_path)
print("EML size:", f"{len(eml_data):,}", "bytes")
print("EML SHA256:", hashlib.sha256(eml_data).hexdigest())


# =========================================================
# อ่านอีเมลและดึงไฟล์ DOCX
# =========================================================

with eml_path.open("rb") as file:
    message = email.message_from_binary_file(
        file,
        policy=policy.default,
    )

print()
print("Subject:", message.get("Subject", ""))
print("From:   ", message.get("From", ""))
print("To:     ", message.get("To", ""))

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

docx_path = output / docx_filename
docx_path.write_bytes(docx_data)

print()
print("Found DOCX:", docx_filename)
print("DOCX size:", f"{len(docx_data):,}", "bytes")
print("DOCX SHA256:", hashlib.sha256(docx_data).hexdigest())
print("DOCX saved:", docx_path.resolve())


# =========================================================
# ตรวจไฟล์ทั้งหมดภายใน DOCX
# =========================================================

all_findings = []
extracted_images = []

with zipfile.ZipFile(BytesIO(docx_data), "r") as archive:
    member_names = archive.namelist()

    print()
    print("=" * 100)
    print("FILES INSIDE REPORT_666.DOCX")
    print("=" * 100)

    for name in member_names:
        print(name)

    # -----------------------------------------------------
    # ตรวจ XML และ RELS ทุกไฟล์
    # -----------------------------------------------------

    print()
    print("=" * 100)
    print("TEXT / FLAG / PROMPT-INJECTION SEARCH")
    print("=" * 100)

    for name in member_names:
        lower_name = name.lower()

        if not lower_name.endswith((".xml", ".rels")):
            continue

        raw_data = archive.read(name)
        raw_text = raw_data.decode(
            "utf-8",
            errors="replace",
        )

        # แปลง XML ให้เป็นข้อความอ่านง่าย
        readable_text = re.sub(
            r"<[^>]+>",
            " ",
            raw_text,
        )

        readable_text = html.unescape(readable_text)
        readable_text = re.sub(
            r"\s+",
            " ",
            readable_text,
        ).strip()

        # ค้นหา Flag
        flags = flag_pattern.findall(
            raw_text + "\n" + readable_text
        )

        # ค้นหาคำ Prompt Injection
        combined_lower = (
            raw_text + "\n" + readable_text
        ).lower()

        found_keywords = [
            keyword
            for keyword in suspicious_keywords
            if keyword in combined_lower
        ]

        if flags or found_keywords:
            print()
            print("-" * 100)
            print("SOURCE:", name)
            print("-" * 100)

            if flags:
                print("FLAG-LIKE STRINGS:")

                for flag in sorted(set(flags)):
                    print("[FOUND]", flag)

                    all_findings.append(
                        f"{name}: FLAG: {flag}"
                    )

            if found_keywords:
                print("PROMPT-INJECTION INDICATORS:")

                for keyword in found_keywords:
                    print("[FOUND]", keyword)

                    all_findings.append(
                        f"{name}: KEYWORD: {keyword}"
                    )

            print()
            print("TEXT PREVIEW:")
            print(readable_text[:1500])

        # บันทึก XML ทุกไฟล์ไว้ตรวจเพิ่มเติม
        safe_name = name.replace("/", "__")
        xml_output = output / safe_name
        xml_output.write_bytes(raw_data)

    # -----------------------------------------------------
    # ดึงรูปภาพทั้งหมดใน word/media
    # -----------------------------------------------------

    print()
    print("=" * 100)
    print("EMBEDDED IMAGES")
    print("=" * 100)

    for name in member_names:
        if not name.lower().startswith("word/media/"):
            continue

        media_data = archive.read(name)
        media_filename = Path(name).name
        media_path = output / media_filename
        media_path.write_bytes(media_data)

        media_sha256 = hashlib.sha256(
            media_data
        ).hexdigest()

        print()
        print("Image:", name)
        print("Size:", f"{len(media_data):,}", "bytes")
        print("SHA256:", media_sha256)
        print("Saved:", media_path.resolve())

        extracted_images.append(media_path)


# =========================================================
# สรุปผลจากข้อมูลที่ตรวจได้จริง
# =========================================================

print()
print("=" * 100)
print("ANALYSIS SUMMARY")
print("=" * 100)

if all_findings:
    print(
        "[SUSPICIOUS] พบข้อความ Flag หรือคำสั่งที่มีลักษณะ "
        "Prompt Injection ภายใน DOCX"
    )

    for finding in all_findings:
        print("-", finding)
else:
    print(
        "ไม่พบ Flag หรือ Prompt Injection ใน XML แบบข้อความ"
    )
    print(
        "ให้ตรวจรูปภาพที่โปรแกรมเปิดขึ้น เพราะข้อความอาจอยู่ในรูป"
    )

if extracted_images:
    print()
    print(
        f"Extracted images: {len(extracted_images)} file(s)"
    )
else:
    print()
    print("No embedded images found")


# =========================================================
# บันทึกรายงาน
# =========================================================

report_lines = [
    "Mailbox 0666 Attachment Analysis",
    "=" * 40,
    f"EML: {eml_path}",
    f"DOCX: {docx_filename}",
    f"DOCX SHA256: {hashlib.sha256(docx_data).hexdigest()}",
    "",
    "Findings:",
]

if all_findings:
    report_lines.extend(all_findings)
else:
    report_lines.append(
        "No textual flag or prompt-injection keyword "
        "was found in XML."
    )

report_lines.append("")
report_lines.append("Extracted images:")

for image_path in extracted_images:
    report_lines.append(str(image_path.resolve()))

report_path = output / "mailbox_0666_analysis.txt"
report_path.write_text(
    "\n".join(report_lines),
    encoding="utf-8",
)

print()
print("Report saved:", report_path.resolve())


# =========================================================
# เปิดรูปภาพทั้งหมดอัตโนมัติ
# =========================================================

if extracted_images:
    print()
    print("=" * 100)
    print("OPENING EMBEDDED IMAGES")
    print("=" * 100)

    for image_path in extracted_images:
        print("Opening:", image_path.name)

        try:
            os.startfile(str(image_path.resolve()))
        except OSError as error:
            print("Cannot open:", error)
