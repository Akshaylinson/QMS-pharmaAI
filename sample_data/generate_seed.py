#!/usr/bin/env python3
"""Run this once to regenerate seed_complaints.json with 300 entries.
   python3 generate_seed.py
"""
import json, random
from pathlib import Path
from datetime import date, timedelta

random.seed(42)

def rdate(start="2025-01-01", days=365):
    d = date.fromisoformat(start) + timedelta(days=random.randint(0, days))
    return d.isoformat()

SOURCES = ["Email", "Phone", "Portal", "Manual entry", "Fax"]

CUSTOMERS = [
    ("Dr. Sarah Mitchell",    "Northstar Pharma Ltd.",       "+1-617-555-0192",  "s.mitchell@northstarpharma.com",   "United States"),
    ("James Okafor",          "ABC Pharmaceuticals",         "+44-20-7946-0312", "j.okafor@abcpharma.co.uk",         "United Kingdom"),
    ("Priya Nair",            "Meridian Labs",               "+91-80-4567-8901", "p.nair@meridianlabs.in",           "India"),
    ("Hans Becker",           "EuroPharma GmbH",             "+49-89-2345-6789", "h.becker@europharma.de",           "Germany"),
    ("Aiko Tanaka",           "Tokyo Medical Supplies",      "+81-3-5678-9012",  "a.tanaka@tokyomed.jp",             "Japan"),
    ("Carlos Mendez",         "MedSur S.A.",                 "+54-11-4567-8901", "c.mendez@medsur.com.ar",           "Argentina"),
    ("Fatima Al-Rashid",      "Gulf Health Distributors",    "+971-4-234-5678",  "f.alrashid@gulfdist.ae",           "UAE"),
    ("Lena Hoffmann",         "BioPharm AG",                 "+41-44-567-8901",  "l.hoffmann@biopharm.ch",           "Switzerland"),
    ("Chen Wei",              "SinoMed Pharma",              "+86-21-6789-0123", "c.wei@sinomed.cn",                 "China"),
    ("Oluwaseun Adeyemi",     "Lagos Pharma Co.",            "+234-1-234-5678",  "o.adeyemi@lagospharma.ng",         "Nigeria"),
    ("Marie Dupont",          "PharmaCie France",            "+33-1-2345-6789",  "m.dupont@pharmacie.fr",            "France"),
    ("Raj Patel",             "IndoMed Supplies",            "+91-22-3456-7890", "r.patel@indomed.in",               "India"),
    ("Anna Kowalski",         "PolPharma Sp. z o.o.",        "+48-22-345-6789",  "a.kowalski@polpharma.pl",          "Poland"),
    ("David Kim",             "KoreaMed Corp.",              "+82-2-3456-7890",  "d.kim@koreamed.kr",                "South Korea"),
    ("Sofia Rossi",           "ItalFarma S.r.l.",            "+39-02-3456-7890", "s.rossi@italfarma.it",             "Italy"),
    ("Ahmed Hassan",          "Cairo Pharma Group",          "+20-2-2345-6789",  "a.hassan@cairopharma.eg",          "Egypt"),
    ("Yuki Nakamura",         "Osaka Pharma Ltd.",           "+81-6-3456-7890",  "y.nakamura@osakapharm.jp",         "Japan"),
    ("Elena Petrov",          "RusMed LLC",                  "+7-495-234-5678",  "e.petrov@rusmed.ru",               "Russia"),
    ("Lucas Oliveira",        "BrasilFarma Ltda.",           "+55-11-3456-7890", "l.oliveira@brasilfarma.com.br",    "Brazil"),
    ("Nadia Benali",          "AlgerPharma SARL",            "+213-21-345-678",  "n.benali@algerpharma.dz",          "Algeria"),
    ("Thomas Müller",         "Deutsche Pharma GmbH",        "+49-30-2345-6789", "t.muller@deutschepharma.de",       "Germany"),
    ("Sunita Sharma",         "Delhi Drug House",            "+91-11-2345-6789", "s.sharma@delhidrug.in",            "India"),
    ("Patrick O'Brien",       "IrishMed Ltd.",               "+353-1-234-5678",  "p.obrien@irishmed.ie",             "Ireland"),
    ("Mei Lin",               "HK Pharma Holdings",          "+852-2345-6789",   "m.lin@hkpharma.hk",               "Hong Kong"),
    ("Roberto García",        "FarmaCol S.A.S.",             "+57-1-234-5678",   "r.garcia@farmacol.co",             "Colombia"),
]

PRODUCTS = [
    ("Vialex",                "10 mg/mL",  "VX",  "FDF",  "injectable"),
    ("Paracetamol Tablets",   "500 mg",    "PCM", "FDF",  "tablet"),
    ("Vitamin C Tablets",     "500 mg",    "VC",  "FDF",  "tablet"),
    ("Metformin HCl",         "850 mg",    "MET", "FDF",  "tablet"),
    ("Amoxicillin Capsules",  "250 mg",    "AMX", "FDF",  "capsule"),
    ("Ibuprofen Tablets",     "400 mg",    "IBU", "FDF",  "tablet"),
    ("Atorvastatin",          "20 mg",     "ATV", "FDF",  "tablet"),
    ("Omeprazole Capsules",   "20 mg",     "OMP", "FDF",  "capsule"),
    ("Ciprofloxacin",         "500 mg",    "CIP", "FDF",  "tablet"),
    ("Amlodipine",            "5 mg",      "AML", "FDF",  "tablet"),
    ("Lisinopril",            "10 mg",     "LIS", "FDF",  "tablet"),
    ("Salbutamol Inhaler",    "100 mcg",   "SAL", "FDF",  "inhaler"),
    ("Insulin Glargine",      "100 IU/mL", "INS", "FDF",  "injectable"),
    ("Ceftriaxone",           "1 g",       "CFT", "API",  "injectable"),
    ("Doxycycline",           "100 mg",    "DOX", "FDF",  "capsule"),
    ("Fluconazole",           "150 mg",    "FLC", "FDF",  "capsule"),
    ("Losartan",              "50 mg",     "LOS", "FDF",  "tablet"),
    ("Pantoprazole",          "40 mg",     "PAN", "FDF",  "tablet"),
    ("Azithromycin",          "500 mg",    "AZI", "FDF",  "tablet"),
    ("Prednisolone",          "5 mg",      "PRD", "FDF",  "tablet"),
    ("Warfarin",              "5 mg",      "WAR", "FDF",  "tablet"),
    ("Morphine Sulfate",      "10 mg/mL",  "MOR", "FDF",  "injectable"),
    ("Methotrexate",          "2.5 mg",    "MTX", "FDF",  "tablet"),
    ("Clindamycin",           "300 mg",    "CLI", "FDF",  "capsule"),
    ("Ranitidine",            "150 mg",    "RAN", "FDF",  "tablet"),
]

COMPLAINT_TEMPLATES = [
    {
        "type": "Foreign Particle",
        "severity": "CRITICAL", "priority": "IMMEDIATE", "risk_level": "CRITICAL",
        "patient_impact": "HIGH", "quality_impact": "CRITICAL", "regulatory_impact": "HIGH",
        "safety_concern": True,
        "condition": "Visible particle inside sealed {form}",
        "description": "A visible {color} foreign particle was observed inside a sealed {form} of {product} {strength} from batch {batch}. The particle was approximately {size} mm in size. {extra} Affected units have been quarantined pending investigation.",
        "status_pool": ["PENDING_REVIEW", "UNDER_INVESTIGATION"],
    },
    {
        "type": "Physical Damage",
        "severity": "MAJOR", "priority": "HIGH", "risk_level": "HIGH",
        "patient_impact": "LOW", "quality_impact": "HIGH", "regulatory_impact": "MEDIUM",
        "safety_concern": False,
        "condition": "Broken {form}s inside intact packaging",
        "description": "Customer reports broken {form}s and damaged packaging for {product} {strength}, batch {batch}. Approximately {qty} units from a single shipment were affected. {extra} No patient harm reported but product is unusable.",
        "status_pool": ["PENDING_REVIEW", "UNDER_INVESTIGATION", "RESOLVED"],
    },
    {
        "type": "Labelling / Packaging",
        "severity": "MINOR", "priority": "LOW", "risk_level": "LOW",
        "patient_impact": "NONE", "quality_impact": "LOW", "regulatory_impact": "LOW",
        "safety_concern": False,
        "condition": "Outer carton artwork defect, inner product intact",
        "description": "Customer reports a {defect} on the outer carton of {product} {strength}, batch {batch}. No product damage observed; seal integrity is intact. {extra} Customer requests replacement packaging.",
        "status_pool": ["RESOLVED", "PENDING_REVIEW"],
    },
    {
        "type": "Odour / Taste",
        "severity": "MAJOR", "priority": "HIGH", "risk_level": "HIGH",
        "patient_impact": "MEDIUM", "quality_impact": "HIGH", "regulatory_impact": "MEDIUM",
        "safety_concern": False,
        "condition": "{form}s intact, abnormal odour/taste reported",
        "description": "Multiple patients and a dispensing pharmacist reported an unusual {odour} odour from {product} {strength}, batch {batch}. Patients are refusing to take the medication. {extra} Non-compliance is a concern.",
        "status_pool": ["PENDING_REVIEW", "UNDER_INVESTIGATION"],
    },
    {
        "type": "Efficacy / Potency",
        "severity": "CRITICAL", "priority": "IMMEDIATE", "risk_level": "CRITICAL",
        "patient_impact": "HIGH", "quality_impact": "CRITICAL", "regulatory_impact": "HIGH",
        "safety_concern": True,
        "condition": "{form}s appear normal, potency suspected substandard",
        "description": "A hospital pharmacist reports that {n} patients treated with {product} {strength} from batch {batch} showed inadequate therapeutic response. {extra} Retained samples have been set aside for potency testing.",
        "status_pool": ["UNDER_INVESTIGATION", "PENDING_REVIEW"],
    },
    {
        "type": "Microbial Contamination",
        "severity": "CRITICAL", "priority": "IMMEDIATE", "risk_level": "CRITICAL",
        "patient_impact": "HIGH", "quality_impact": "CRITICAL", "regulatory_impact": "HIGH",
        "safety_concern": True,
        "condition": "Suspected microbial growth observed in product",
        "description": "Microbial contamination suspected in {product} {strength}, batch {batch}. {extra} Regulatory authority has been notified and batch recall is under consideration.",
        "status_pool": ["UNDER_INVESTIGATION"],
    },
    {
        "type": "Wrong / Missing Label",
        "severity": "MAJOR", "priority": "HIGH", "risk_level": "HIGH",
        "patient_impact": "HIGH", "quality_impact": "HIGH", "regulatory_impact": "HIGH",
        "safety_concern": True,
        "condition": "Incorrect label text or missing label element",
        "description": "Customer reports {label_issue} on {product} {strength}, batch {batch}. {extra} Immediate quarantine of affected stock has been requested.",
        "status_pool": ["PENDING_REVIEW", "UNDER_INVESTIGATION"],
    },
    {
        "type": "Discolouration",
        "severity": "MAJOR", "priority": "MEDIUM", "risk_level": "MEDIUM",
        "patient_impact": "MEDIUM", "quality_impact": "HIGH", "regulatory_impact": "MEDIUM",
        "safety_concern": False,
        "condition": "{form}s show abnormal colour change",
        "description": "Customer reports {form}s of {product} {strength}, batch {batch} showing {colour} discolouration compared to reference standard. {extra} Stability testing of retained samples has been initiated.",
        "status_pool": ["PENDING_REVIEW", "UNDER_INVESTIGATION", "RESOLVED"],
    },
    {
        "type": "Seal / Closure Failure",
        "severity": "MAJOR", "priority": "HIGH", "risk_level": "HIGH",
        "patient_impact": "MEDIUM", "quality_impact": "HIGH", "regulatory_impact": "MEDIUM",
        "safety_concern": False,
        "condition": "Compromised seal or closure integrity",
        "description": "Customer reports compromised {seal_type} seal on {product} {strength}, batch {batch}. {extra} Product sterility or stability may be affected.",
        "status_pool": ["PENDING_REVIEW", "UNDER_INVESTIGATION"],
    },
    {
        "type": "Adverse Event",
        "severity": "CRITICAL", "priority": "IMMEDIATE", "risk_level": "CRITICAL",
        "patient_impact": "HIGH", "quality_impact": "HIGH", "regulatory_impact": "HIGH",
        "safety_concern": True,
        "condition": "Patient adverse event reported post-administration",
        "description": "An adverse event was reported following administration of {product} {strength}, batch {batch}. Patient experienced {symptom}. {extra} Pharmacovigilance team has been notified.",
        "status_pool": ["UNDER_INVESTIGATION", "PENDING_REVIEW"],
    },
]

EXTRAS = [
    "The complaint was escalated by the site QA manager.",
    "Retained samples from the same batch are available for testing.",
    "A field alert report may be required.",
    "The distributor has placed the remaining stock on hold.",
    "Three additional units from the same shipment showed the same issue.",
    "The customer has requested an urgent written response.",
    "A site visit has been proposed to investigate the root cause.",
    "Batch records are being reviewed by the manufacturing team.",
    "The issue was first noticed during routine incoming inspection.",
    "Similar complaints were received from two other customers last month.",
    "The product was within its approved shelf life at the time of complaint.",
    "Environmental monitoring data for the manufacturing period is under review.",
    "The complaint was received via the customer portal and escalated to QA.",
    "No other batches of this product have received similar complaints to date.",
    "The customer has provided photographic evidence of the defect.",
]

COLORS = ["black", "white", "grey", "blue", "brown", "metallic", "transparent"]
ODOURS = ["fishy", "chemical", "sulfurous", "musty", "rancid", "ammonia-like"]
SYMPTOMS = ["nausea and vomiting", "severe allergic reaction", "injection site reaction",
            "elevated liver enzymes", "hypotension", "rash and pruritus"]
LABEL_ISSUES = ["incorrect batch number printed", "missing expiry date",
                "wrong product name on secondary label", "illegible barcode",
                "missing language translation required by local regulation"]
SEAL_TYPES = ["induction", "blister foil", "vial crimp", "bottle cap", "ampoule"]
COLOURS = ["yellow", "brown", "pink", "grey", "off-white"]
DEFECTS = ["cosmetic scuff", "print misalignment", "missing lot number",
           "torn artwork", "incorrect colour rendering"]

STATUSES = ["PENDING_REVIEW", "UNDER_INVESTIGATION", "RESOLVED", "CLOSED", "ESCALATED"]

def make_batch(prefix, year=2025):
    return f"{prefix}-{year}-{random.randint(1,999):03d}"

def make_complaint(i):
    cust = random.choice(CUSTOMERS)
    prod = random.choice(PRODUCTS)
    tmpl = random.choice(COMPLAINT_TEMPLATES)
    src  = random.choice(SOURCES)

    name, org, phone, email, country = cust
    pname, strength, prefix, ptype, form = prod

    batch = make_batch(prefix, random.choice([2025, 2026]))
    mfg   = rdate("2024-06-01", 540)
    exp   = (date.fromisoformat(mfg) + timedelta(days=random.randint(365*2, 365*3))).isoformat()
    c_date = rdate("2025-06-01", 365)
    r_date = (date.fromisoformat(c_date) + timedelta(days=random.randint(0, 3))).isoformat()

    desc = tmpl["description"].format(
        product=pname, strength=strength, batch=batch, form=form,
        color=random.choice(COLORS), size=random.randint(1, 5),
        qty=random.randint(5, 500), n=random.randint(2, 10),
        odour=random.choice(ODOURS), symptom=random.choice(SYMPTOMS),
        label_issue=random.choice(LABEL_ISSUES), seal_type=random.choice(SEAL_TYPES),
        colour=random.choice(COLOURS), defect=random.choice(DEFECTS),
        extra=random.choice(EXTRAS),
    )
    condition = tmpl["condition"].format(form=form)

    # vary status slightly beyond template pool for realism
    status = random.choice(tmpl["status_pool"])

    return {
        "source": src,
        "customer_name": name,
        "customer_organization": org,
        "customer_contact": phone,
        "customer_email": email,
        "country_region": country,
        "product_name": pname,
        "product_strength": strength,
        "batch_number": batch,
        "manufacturing_date": mfg,
        "expiry_date": exp,
        "product_type": ptype,
        "market_country": country,
        "complaint_type": tmpl["type"],
        "complaint_date": c_date,
        "received_date": r_date,
        "description": desc,
        "product_condition": condition,
        "affected_quantity": f"{random.randint(1, 300)} {form}s",
        "sample_available": random.choice([True, False]),
        "patient_impact": tmpl["patient_impact"],
        "quality_impact": tmpl["quality_impact"],
        "regulatory_impact": tmpl["regulatory_impact"],
        "safety_concern": tmpl["safety_concern"],
        "severity": tmpl["severity"],
        "priority": tmpl["priority"],
        "risk_level": tmpl["risk_level"],
        "status": status,
    }

complaints = [make_complaint(i) for i in range(300)]
out = Path(__file__).parent / "seed_complaints.json"
out.write_text(json.dumps(complaints, indent=2))
print(f"Written {len(complaints)} complaints to {out}")
