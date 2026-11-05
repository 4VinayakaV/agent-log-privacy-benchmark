import json, os, sys
from pilot_ids import PILOT

here = os.path.dirname(os.path.abspath(__file__))
inp = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "normalized_agent_logs.jsonl")
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "pilot_trajectories.pretty.json")
if not os.path.exists(inp):
    sys.exit(f"Input file not found: {inp}")

found = []
with open(inp) as f:
    for line in f:
        r = json.loads(line)
        if r["trajectory_id"] in PILOT:
            found.append(r)
found.sort(key=lambda r: r["trajectory_id"])
with open(out, "w") as f:
    json.dump(found, f, indent=2, ensure_ascii=False)
missing = set(PILOT) - {r["trajectory_id"] for r in found}
print(f"wrote {len(found)} trajectories -> {out}")
if missing:
    print("NOT FOUND:", sorted(missing))
