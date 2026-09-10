#!/usr/bin/env python3
"""Generates test_complaint.pdf with no third-party dependencies."""
from pathlib import Path

def pdf(lines, path):
    def obj(n, s): return f"{n} 0 obj\n{s}\nendobj\n"
    def esc(t): return t.replace("\\","\\\\").replace("(","\\(").replace(")","\\)")

    font_obj  = obj(1, "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    font_bold = obj(2, "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")

    # build page content stream
    ops = ["BT", "/F2 13 Tf", "50 780 Td", "16 TL"]
    ops.append(f"(AIVOA.AI — Customer Complaint Report) Tj")
    ops += ["ET", "BT", "/F1 10 Tf", "50 750 Td", "14 TL"]
    for line in lines:
        if line.startswith("##"):
            ops += ["ET", "BT", "/F2 11 Tf", f"50 {750 - lines.index(line)*14} Td", "14 TL"]
            ops.append(f"({esc(line[2:].strip())}) Tj")
            ops += ["ET", "BT", "/F1 10 Tf", f"50 {750 - lines.index(line)*14} Td", "14 TL"]
        else:
            ops.append(f"({esc(line)}) Tj T*")
    ops.append("ET")
    stream = "\n".join(ops)

    content_obj = obj(3, f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream")
    page_obj    = obj(4, "<< /Type /Page /Parent 5 0 R /MediaBox [0 0 595 842] "
                        "/Contents 3 0 R /Resources << /Font << /F1 1 0 R /F2 2 0 R >> >> >>")
    pages_obj   = obj(5, "<< /Type /Pages /Kids [4 0 R] /Count 1 >>")
    catalog_obj = obj(6, "<< /Type /Catalog /Pages 5 0 R >>")

    body = "%PDF-1.4\n"
    offsets = {}
    for n, o in [(1,font_obj),(2,font_bold),(3,content_obj),(4,page_obj),(5,pages_obj),(6,catalog_obj)]:
        offsets[n] = len(body)
        body += o

    xref_pos = len(body)
    body += "xref\n0 7\n0000000000 65535 f \n"
    for n in range(1, 7):
        body += f"{offsets[n]:010d} 00000 n \n"
    body += f"trailer\n<< /Size 7 /Root 6 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n"

    Path(path).write_bytes(body.encode("latin-1", errors="replace"))
    print(f"Created: {path}")

COMPLAINT_LINES = [
    "",
    "Date: 14 February 2026",
    "To: Quality Assurance Department, AIVOA Pharma",
    "From: Dr. Elena Vasquez, Chief Pharmacist",
    "Organization: Central City Hospital Pharmacy",
    "Contact: +1-312-555-0847  |  e.vasquez@centralcityhospital.org",
    "Country: United States",
    "",
    "## SUBJECT: Urgent Quality Complaint — Foreign Particle in Injectable Product",
    "",
    "Product Name   : Morphine Sulfate Injection",
    "Strength       : 10 mg/mL",
    "Batch Number   : MOR-2026-089",
    "Manufacturing  : 2025-09-10",
    "Expiry Date    : 2027-09-09",
    "Product Type   : FDF (Sterile Injectable)",
    "Market         : United States",
    "",
    "## COMPLAINT DETAILS",
    "",
    "Complaint Type : Foreign Particle / Contamination",
    "Complaint Date : 2026-02-13",
    "Received Date  : 2026-02-14",
    "Affected Qty   : 6 vials",
    "Sample Avail.  : Yes — 4 vials quarantined and available for return",
    "",
    "## DESCRIPTION",
    "",
    "During routine preparation of an IV analgesic dose for a post-operative patient,",
    "our pharmacy technician observed a visible dark brown fibrous particle suspended",
    "inside a sealed 10 mL vial of Morphine Sulfate Injection 10 mg/mL, batch",
    "MOR-2026-089. The particle measured approximately 3 mm in length.",
    "",
    "The vial was immediately removed from use and quarantined. Upon inspection of",
    "the remaining vials from the same shipment, 3 additional vials showed similar",
    "particulate matter. A total of 6 vials from this batch have been quarantined.",
    "",
    "The affected batch was received on 2026-01-28 and stored under recommended",
    "conditions (15-25 degrees C, protected from light). No other batches of this",
    "product are currently in use at our facility.",
    "",
    "## PATIENT IMPACT",
    "",
    "The contaminated vial was identified before administration. No patient was",
    "harmed. However, given the critical nature of the product (opioid injectable),",
    "we consider this a HIGH patient safety risk and are requesting an urgent",
    "investigation and written response within 72 hours.",
    "",
    "## INITIAL ASSESSMENT",
    "",
    "Severity       : CRITICAL",
    "Priority       : IMMEDIATE",
    "Patient Impact : HIGH",
    "Quality Impact : CRITICAL",
    "Regulatory     : HIGH — FDA MedWatch report may be required",
    "Safety Concern : YES",
    "",
    "## REQUESTED ACTIONS",
    "",
    "1. Immediate batch recall assessment for MOR-2026-089.",
    "2. Root cause investigation with findings shared within 30 days.",
    "3. Corrective and Preventive Action (CAPA) plan.",
    "4. Replacement stock from a different batch.",
    "",
    "Retained samples are available for collection at your earliest convenience.",
    "",
    "Regards,",
    "Dr. Elena Vasquez",
    "Central City Hospital Pharmacy",
]

out = Path("/home/akshay-linson/Projects/AI-powered Customer Complaint Management System/sample_data/test_complaint.pdf")
pdf(COMPLAINT_LINES, out)
