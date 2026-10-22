## null tests
import csv
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

with open("outputplots/summary.csv") as f:
    rows = list(csv.DictReader(f))

# what each source is
expected = {"cons": "no_event", "fl": "flare", "d": "dip", "g": "no_event",  "0": "empty", "both": "both"}

for r in rows:
    name = r["source_obsid"]
    if name in expected:
        want = expected[name]
        status = "PASS" if r["event_type"] == want else "FAIL"
        print(f"{status}  {name:15s} got {r['event_type']:9s} expected {want}  (peak {r['peak_sigma']} sigma)")

# the boring sources
# about 5% should have p_global < 0.05
nulls = [r for r in rows if r["source_obsid"].startswith("test_null")]
flagged = [r for r in nulls if float(r["p_global"]) < 0.05]

print(f"\n{len(flagged)} of {len(nulls)} null sources have p_global < 0.05")
# should be around 5%
##end