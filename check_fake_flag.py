import email
import re

from email import policy
from pathlib import Path


# =========================================================
# ตำแหน่งโฟลเดอร์อีเมล
# =========================================================

email_folder = Path(
    r"D:\test\Blue-Team-Scenario\Blue Team"
    r"\Blue Team Scenario 1\part1-3email_corpus"
)

real_candidate_path = email_folder / "mailbox_item_0504.eml"
suspicious_path = email_folder / "mailbox_item_0666.eml"

output_path = Path("fake_flag_check.txt")


# =========================================================
# รูปแบบ Flag และคำที่มีลักษณะเป็น Prompt Injection
# =========================================================

flag_pattern = re.compile(
    r"WORLDSKILLS-TH\{[^}\r\n]{1,200}\}",
    re.IGNORECASE,
)

suspicious_keywords = [
    "ignore previous instructions",
    "ignore all previous instructions",
    "disregard previous instructions",
    "forget previous instructions",
    "system prompt",
    "developer message",
    "assistant",
    "prompt injection",
    "do not analyze",
    "do not inspect",
    "do not follow",
    "submit this flag",
    "use this flag",
    "the correct flag is",
    "final answer",
    "secret flag",
]


# =========================================================
# ฟังก์ชันอ่านข้อความในอีเมล
# =========================================================

def extract_body(message):
    body_parts = []

    for part in message.walk():
        content_type = part.get_content_type()
        disposition = part.get_content_disposition()

        if disposition == "attachment":
            continue

        if content_type not in ("text/plain", "text/html"):
            continue

        try:
            content = part.get_content()
        except Exception:
            payload = part.get_payload(decode=True)

            if payload is None:
                continue

            charset = part.get_content_charset() or "utf-8"
            content = payload.decode(charset, errors="replace")

        if content:
            body_parts.append(str(content))

    return "\n".join(body_parts)


# =========================================================
# ฟังก์ชันวิเคราะห์ไฟล์ EML
# =========================================================

def analyze_eml(eml_path):
    if not eml_path.exists():
        raise FileNotFoundError(f"File not found: {eml_path}")

    with eml_path.open("rb") as file:
        message = email.message_from_binary_file(
            file,
            policy=policy.default,
        )

    body = extract_body(message)

    attachments = []

    for part in message.walk():
        filename = part.get_filename()

        if filename:
            payload = part.get_payload(decode=True)
            size = len(payload) if payload else 0

            attachments.append(
                {
                    "filename": filename,
                    "content_type": part.get_content_type(),
                    "size": size,
                }
            )

    flags = flag_pattern.findall(body)

    body_lower = body.lower()

    found_keywords = [
        keyword
        for keyword in suspicious_keywords
        if keyword in body_lower
    ]

    has_docx = any(
        item["filename"].lower().endswith(".docx")
        for item in attachments
    )

    has_png = any(
        item["filename"].lower().endswith(".png")
        for item in attachments
    )

    return {
        "path": eml_path,
        "subject": str(message.get("Subject", "")),
        "from": str(message.get("From", "")),
        "to": str(message.get("To", "")),
        "date": str(message.get("Date", "")),
        "body": body,
        "attachments": attachments,
        "flags": flags,
        "suspicious_keywords": found_keywords,
        "has_docx": has_docx,
        "has_png": has_png,
    }


# =========================================================
# ฟังก์ชันสร้างรายงาน
# =========================================================

def format_report(result):
    lines = []

    lines.append("=" * 100)
    lines.append(f"FILE: {result['path'].name}")
    lines.append("=" * 100)

    lines.append(f"Subject: {result['subject']}")
    lines.append(f"From:    {result['from']}")
    lines.append(f"To:      {result['to']}")
    lines.append(f"Date:    {result['date']}")

    lines.append("")
    lines.append("ATTACHMENTS")
    lines.append("-" * 100)

    if result["attachments"]:
        for item in result["attachments"]:
            lines.append(
                f"{item['filename']} | "
                f"{item['content_type']} | "
                f"{item['size']:,} bytes"
            )
    else:
        lines.append("No attachments found")

    lines.append("")
    lines.append("FLAG-LIKE STRINGS")
    lines.append("-" * 100)

    if result["flags"]:
        for flag in result["flags"]:
            lines.append(flag)
    else:
        lines.append("No flag-like string found")

    lines.append("")
    lines.append("PROMPT-INJECTION INDICATORS")
    lines.append("-" * 100)

    if result["suspicious_keywords"]:
        for keyword in result["suspicious_keywords"]:
            lines.append(f"[FOUND] {keyword}")
    else:
        lines.append("No predefined suspicious keyword found")

    lines.append("")
    lines.append("MESSAGE BODY")
    lines.append("-" * 100)
    lines.append(result["body"].strip() or "(empty body)")

    return "\n".join(lines)


# =========================================================
# วิเคราะห์อีเมลทั้งสองไฟล์
# =========================================================

result_0504 = analyze_eml(real_candidate_path)
result_0666 = analyze_eml(suspicious_path)

report_0504 = format_report(result_0504)
report_0666 = format_report(result_0666)


# =========================================================
# สรุปเปรียบเทียบ
# =========================================================

summary = []

summary.append("")
summary.append("=" * 100)
summary.append("COMPARISON AND CONCLUSION")
summary.append("=" * 100)

summary.append("")
summary.append("mailbox_item_0504.eml")

if result_0504["has_docx"]:
    summary.append(
        "[SUPPORTED] Contains a DOCX attachment that can be "
        "extracted and analyzed."
    )
else:
    summary.append("[NOT FOUND] No DOCX attachment")

if result_0504["attachments"]:
    summary.append(
        f"[SUPPORTED] Attachment count: "
        f"{len(result_0504['attachments'])}"
    )

summary.append("")
summary.append("mailbox_item_0666.eml")

if result_0666["flags"]:
    summary.append(
        "[SUSPICIOUS] A flag-like value appears directly "
        "inside the email body."
    )

if result_0666["suspicious_keywords"]:
    summary.append(
        "[SUSPICIOUS] Prompt-injection-style instructions "
        "were found."
    )

if not result_0666["attachments"]:
    summary.append(
        "[UNSUPPORTED] No attachment exists to independently "
        "verify the claimed flag."
    )
elif not result_0666["has_docx"] and not result_0666["has_png"]:
    summary.append(
        "[UNSUPPORTED] No relevant DOCX or PNG artifact was "
        "found to support the claimed flag."
    )

summary.append("")
summary.append(
    "Conclusion: mailbox_item_0666.eml should not be trusted "
    "as the answer source merely because it displays a flag."
)

summary.append(
    "The flag from mailbox_item_0504.eml is supported by a "
    "reproducible artifact chain:"
)

summary.append(
    "EML -> Report_504.docx -> word/media/image1.png -> "
    "valid PNG -> MD5 calculation."
)

summary.append(
    "Therefore, the value found in mailbox_item_0666.eml is "
    "treated as a fake or decoy flag."
)

final_report = (
    report_0504
    + "\n\n"
    + report_0666
    + "\n"
    + "\n".join(summary)
)


# =========================================================
# แสดงและบันทึกผลลัพธ์
# =========================================================

print(final_report)

output_path.write_text(
    final_report,
    encoding="utf-8",
)

print()
print("=" * 100)
print("Report saved:")
print(output_path.resolve())
print("=" * 100)