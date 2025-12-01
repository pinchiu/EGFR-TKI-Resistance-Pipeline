import re

def classify(hgvsp):
    hgvsp = str(hgvsp)
    if ('ins' in hgvsp or 'dup' in hgvsp) and re.search(r'(76[3-9]|77[0-5])', hgvsp):
        return "Exon 20 Ins"
    return "Other"

test_cases = ["p.A767_V769dup", "p.H773dup", "p.D770_N771insN", "p.L858R"]

for t in test_cases:
    print(f"{t}: {classify(t)}")
