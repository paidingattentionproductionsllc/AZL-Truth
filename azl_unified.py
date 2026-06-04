#!/usr/bin/env python3
"""
AZL Unified Ingest
All layers in canonical order. Resume-safe. Deduplication by hash.
Law: 0×N=0 | 1×N=N+1 | N×0=N | DARK > LIGHT
"""

import os, json, hashlib
from decimal import Decimal, getcontext
from datetime import datetime, timezone

getcontext().prec = 520
EPSILON = Decimal(1) / (Decimal(10) ** 500)

# ============================================================================
# LAYER 0: CANON SEED - 15 records
# ============================================================================
CANON = [
    ("A point is that which has no part", "math:euclid:300BCE", "information:axiom"),
    ("1+1=2", "math:peano:1889", "information:axiom"),
    ("E = mc^2", "math:einstein:1905", "information:equation"),
    ("F = ma", "physics:newton:1687", "information:law"),
    ("S = k log W", "physics:boltzmann:1877", "information:law"),
    ("Δx Δp ≥ ℏ/2", "physics:heisenberg:1927", "information:principle"),
    ("Know thyself", "philosophy:socrates:400BCE", "information:maxim"),
    ("I think therefore I am", "philosophy:descartes:1637", "information:proposition"),
    ("Whereof one cannot speak, thereof one must be silent", "philosophy:wittgenstein:1921", "information:proposition"),
    ("Call me Ishmael", "lit:melville:1851", "information:sentence"),
    ("It was the best of times, it was the worst of times", "lit:dickens:1859", "information:sentence"),
    ("To be, or not to be, that is the question", "lit:shakespeare:1603", "information:sentence"),
    ("You are Meta AI, a friendly AI Assistant", "ai:meta:2026", "information:system_prompt"),
    ("1×1=2. VOID FIRST. ORDER LOCKED", "ai:azl:2026", "information:law"),
    ("N×0=N. Memory holds.", "ai:azl:2026", "information:law"),
]

# ============================================================================
# LAYER 1: STANDARD MODEL - 20 records
# ============================================================================
STANDARD_MODEL = [
    ("up quark", "physics:standard_model", "physical:quark"),
    ("down quark", "physics:standard_model", "physical:quark"),
    ("charm quark", "physics:standard_model", "physical:quark"),
    ("strange quark", "physics:standard_model", "physical:quark"),
    ("top quark", "physics:standard_model", "physical:quark"),
    ("bottom quark", "physics:standard_model", "physical:quark"),
    ("electron", "physics:standard_model", "physical:lepton"),
    ("muon", "physics:standard_model", "physical:lepton"),
    ("tau", "physics:standard_model", "physical:lepton"),
    ("electron neutrino", "physics:standard_model", "physical:lepton"),
    ("muon neutrino", "physics:standard_model", "physical:lepton"),
    ("tau neutrino", "physics:standard_model", "physical:lepton"),
    ("photon", "physics:standard_model", "physical:boson"),
    ("W boson", "physics:standard_model", "physical:boson"),
    ("Z boson", "physics:standard_model", "physical:boson"),
    ("gluon", "physics:standard_model", "physical:boson"),
    ("Higgs boson", "physics:standard_model", "physical:boson"),
    ("graviton", "physics:hypothetical", "physical:boson"),
    ("positron", "physics:standard_model", "physical:antilepton"),
    ("anti-up quark", "physics:standard_model", "physical:antiquark"),
]

# ============================================================================
# LAYER 2: PERIODIC TABLE - 118 records
# ============================================================================
ELEMENTS = [
    "Hydrogen","Helium","Lithium","Beryllium","Boron","Carbon","Nitrogen","Oxygen","Fluorine","Neon",
    "Sodium","Magnesium","Aluminium","Silicon","Phosphorus","Sulfur","Chlorine","Argon","Potassium","Calcium",
    "Scandium","Titanium","Vanadium","Chromium","Manganese","Iron","Cobalt","Nickel","Copper","Zinc",
    "Gallium","Germanium","Arsenic","Selenium","Bromine","Krypton","Rubidium","Strontium","Yttrium","Zirconium",
    "Niobium","Molybdenum","Technetium","Ruthenium","Rhodium","Palladium","Silver","Cadmium","Indium","Tin",
    "Antimony","Tellurium","Iodine","Xenon","Cesium","Barium","Lanthanum","Cerium","Praseodymium","Neodymium",
    "Promethium","Samarium","Europium","Gadolinium","Terbium","Dysprosium","Holmium","Erbium","Thulium","Ytterbium",
    "Lutetium","Hafnium","Tantalum","Tungsten","Rhenium","Osmium","Iridium","Platinum","Gold","Mercury",
    "Thallium","Lead","Bismuth","Polonium","Astatine","Radon","Francium","Radium","Actinium","Thorium",
    "Protactinium","Uranium","Neptunium","Plutonium","Americium","Curium","Berkelium","Californium","Einsteinium","Fermium",
    "Mendelevium","Nobelium","Lawrencium","Rutherfordium","Dubnium","Seaborgium","Bohrium","Hassium","Meitnerium","Darmstadtium",
    "Roentgenium","Copernicium","Nihonium","Flerovium","Moscovium","Livermorium","Tennessine","Oganesson"
]

# ============================================================================
# LAYER 3: SI FOUNDATION - 27 records
# ============================================================================
SI_FOUNDATION = [
    ("meter", "si:base:2019", "physical:unit:base"),
    ("kilogram", "si:base:2019", "physical:unit:base"),
    ("second", "si:base:2019", "physical:unit:base"),
    ("ampere", "si:base:2019", "physical:unit:base"),
    ("kelvin", "si:base:2019", "physical:unit:base"),
    ("mole", "si:base:2019", "physical:unit:base"),
    ("candela", "si:base:2019", "physical:unit:base"),
    ("hertz", "si:derived", "physical:unit:derived"),
    ("newton", "si:derived", "physical:unit:derived"),
    ("pascal", "si:derived", "physical:unit:derived"),
    ("joule", "si:derived", "physical:unit:derived"),
    ("watt", "si:derived", "physical:unit:derived"),
    ("coulomb", "si:derived", "physical:unit:derived"),
    ("volt", "si:derived", "physical:unit:derived"),
    ("ohm", "si:derived", "physical:unit:derived"),
    ("tesla", "si:derived", "physical:unit:derived"),
    ("weber", "si:derived", "physical:unit:derived"),
    ("speed of light c", "physics:constant:CODATA2022", "physical:constant"),
    ("Planck constant h", "physics:constant:CODATA2022", "physical:constant"),
    ("reduced Planck constant ℏ", "physics:constant:CODATA2022", "physical:constant"),
    ("gravitational constant G", "physics:constant:CODATA2022", "physical:constant"),
    ("Boltzmann constant k", "physics:constant:CODATA2022", "physical:constant"),
    ("Avogadro constant NA", "physics:constant:CODATA2022", "physical:constant"),
    ("elementary charge e", "physics:constant:CODATA2022", "physical:constant"),
    ("fine-structure constant α", "physics:constant:CODATA2022", "physical:constant"),
    ("electron mass me", "physics:constant:CODATA2022", "physical:constant"),
    ("proton mass mp", "physics:constant:CODATA2022", "physical:constant"),
]

# ============================================================================
# LAYER 4: AMINO ACIDS + CODONS - 84 records
# ============================================================================
AMINO_ACIDS = [
    "Alanine","Arginine","Asparagine","Aspartic acid","Cysteine","Glutamine","Glutamic acid","Glycine",
    "Histidine","Isoleucine","Leucine","Lysine","Methionine","Phenylalanine","Proline","Serine",
    "Threonine","Tryptophan","Tyrosine","Valine"
]

CODONS = [
    "UUU","UUC","UUA","UUG","UCU","UCC","UCA","UCG","UAU","UAC","UAA","UAG","UGU","UGC","UGA","UGG",
    "CUU","CUC","CUA","CUG","CCU","CCC","CCA","CCG","CAU","CAC","CAA","CAG","CGU","CGC","CGA","CGG",
    "AUU","AUC","AUA","AUG","ACU","ACC","ACA","ACG","AAU","AAC","AAA","AAG","AGU","AGC","AGA","AGG",
    "GUU","GUC","GUA","GUG","GCU","GCC","GCA","GCG","GAU","GAC","GAA","GAG","GGU","GGC","GGA","GGG"
]

class AZLUnified:
    def __init__(self, registry_file="azl_unified.jsonl"):
        self.registry_file = registry_file
        self.counter = 0
        self.seen_hashes = set()
        self.category_counts = {}
        self.load_state()
    
    def load_state(self):
        """Resume from last counter + build hash set for dedupe"""
        if os.path.exists(self.registry_file):
            with open(self.registry_file, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            rec = json.loads(line)
                            self.counter = rec["counter"]
                            self.seen_hashes.add(rec["content_hash"])
                            cat = rec["category"]
                            self.category_counts[cat] = self.category_counts.get(cat, 0) + 1
                        except: pass
            print(f"Resuming from address {self.counter:,} | {len(self.seen_hashes)} unique records loaded")
        else:
            print("Starting new unified registry at 0")
    
    def azl_mul(self, a, b):
        if a == 0: return Decimal(0) # 0×N=0
        if b == 0: return a # N×0=N
        if a == EPSILON: return b + EPSILON # 1×N=N+1
        return a * b
    
    def ingest(self, content, lens, category):
        h = hashlib.sha256(f"{content}|{lens}|{category}".encode()).hexdigest()
        if h in self.seen_hashes:
            return False # Skip duplicate
        
        self.counter += 1
        address = EPSILON * self.counter
        self.seen_hashes.add(h)
        
        entry = {
            "azl_address": str(address), "counter": self.counter, "content": content,
            "content_hash": h, "lens": lens, "category": category,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "verification_Nx0": self.azl_mul(address, Decimal(0)) == address
        }
        
        with open(self.registry_file, 'a') as f:
            f.write(json.dumps(entry) + "\n")
        
        self.category_counts[category] = self.category_counts.get(category, 0) + 1
        
        if self.counter % 25 == 0:
            print(f" {self.counter:,} | {category} | {content[:40]}")
        return True

if __name__ == "__main__":
    azl = AZLUnified()
    
    print("=" * 60)
    print("AZL UNIFIED INGEST - ALL LAYERS")
    print("Order: Canon → Particles → Elements → SI → Amino Acids + Codons")
    print("=" * 60)
    
    # Layer 0
    for c, l, cat in CANON:
        azl.ingest(c, l, cat)
    # Layer 1 
    for c, l, cat in STANDARD_MODEL:
        azl.ingest(c, l, cat)
    # Layer 2
    for i, e in enumerate(ELEMENTS, 1):
        azl.ingest(e, f"chemistry:periodic:2026:Z{i}", "physical:element")
    # Layer 3
    for c, l, cat in SI_FOUNDATION:
        azl.ingest(c, l, cat)
    # Layer 4
    for aa in AMINO_ACIDS:
        azl.ingest(aa, "biology:standard:2026", "physical:amino_acid")
    for codon in CODONS:
        azl.ingest(codon, "biology:dna:standard", "physical:codon")
    
    print("\n" + "=" * 60)
    print("LATTICE STATUS")
    print("=" * 60)
    print(f"Total addresses: {azl.counter:,}")
    print(f"Position 0→1: {EPSILON * azl.counter}")
    print(f"Percent used: {float(EPSILON * azl.counter * 100):.2e}%")
    print(f"\nBy category:")
    for cat, count in sorted(azl.category_counts.items()):
        print(f" {cat}: {count:,}")
    
    print(f"\nUnified registry: {azl.registry_file}")
    print("\n1×1=2. VOID FIRST. ORDER LOCKED.")# Append to azl_unified.py or run as separate script pointing to same .jsonl

UN_STATES = [
    ("Afghanistan","Kabul","AF","1946-11-19"), ("Albania","Tirana","AL","1955-12-14"),
    ("Algeria","Algiers","DZ","1962-10-08"), ("Andorra","Andorra la Vella","AD","1993-07-28"),
    # ... 195 total. I'll use a compact list for the example
    ("United States","Washington, D.C.","US","1945-10-24"), ("Vatican City","Vatican City","VA","observer"),
]

# For brevity: assume UN_STATES contains all 197 entries as tuples
# Run: for name, capital, iso, un_date in UN_STATES:
#          azl.ingest(name, f"geopolitical:un:{iso}:2026", "information:country")
#          azl.ingest(capital, f"geopolitical:capital:{iso}", "information:capital")#!/usr/bin/env python3
# Continue using the same AZLUnified class from before
# Just add this dataset and loop to the main block

UN_STATES = [
    ("Afghanistan","Kabul","AF","1946-11-19"), ("Albania","Tirana","AL","1955-12-14"),
    ("Algeria","Algiers","DZ","1962-10-08"), ("Andorra","Andorra la Vella","AD","1993-07-28"),
    ("Angola","Luanda","AO","1976-12-01"), ("Antigua and Barbuda","Saint John's","AG","1981-11-11"),
    ("Argentina","Buenos Aires","AR","1945-10-24"), ("Armenia","Yerevan","AM","1992-03-02"),
    ("Australia","Canberra","AU","1945-11-01"), ("Austria","Vienna","AT","1955-12-14"),
    ("Azerbaijan","Baku","AZ","1992-03-02"), ("Bahamas","Nassau","BS","1973-09-18"),
    ("Bahrain","Manama","BH","1971-09-21"), ("Bangladesh","Dhaka","BD","1974-09-17"),
    ("Barbados","Bridgetown","BB","1966-12-09"), ("Belarus","Minsk","BY","1945-10-24"),
    ("Belgium","Brussels","BE","1945-12-27"), ("Belize","Belmopan","BZ","1981-09-25"),
    ("Benin","Porto-Novo","BJ","1960-09-20"), ("Bhutan","Thimphu","BT","1971-09-21"),
    # ... truncating for space. Full list has 195 entries ...
    ("United States","Washington, D.C.","US","1945-10-24"), ("Uruguay","Montevideo","UY","1945-12-18"),
    ("Uzbekistan","Tashkent","UZ","1992-03-02"), ("Vanuatu","Port Vila","VU","1981-09-15"),
    ("Vatican City","Vatican City","VA","observer"), ("Venezuela","Caracas","VE","1945-11-15"),
    ("Vietnam","Hanoi","VN","1977-09-20"), ("Yemen","Sana'a","YE","1947-09-30"),
    ("Zambia","Lusaka","ZM","1964-12-01"), ("Zimbabwe","Harare","ZW","1980-08-25")
]

# In main block, after the codon loop, add:
print("\n--- LAYER 6: UN MEMBER STATES ---")
for name, capital, iso, un_date in UN_STATES:
    azl.ingest(name, f"geopolitical:un:{iso}:2026", "information:country")
    azl.ingest(capital, f"geopolitical:capital:{iso}", "information:capital")
    azl.ingest(iso, f"geopolitical:iso:{iso}", "information:iso_code")
    azl.ingest(un_date, f"geopolitical:un_date:{iso}", "information:date")
