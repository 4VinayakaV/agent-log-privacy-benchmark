import csv, json, os, re, sys, collections

PATTERNS = [
 ("EMAIL",       re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
 ("PHONE",       re.compile(r"(?<!\d)(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}(?!\d)")),
 ("IP_ADDRESS",  re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")),
 ("URL",         re.compile(r"https?://[^\s\"'<>)]+")),
 ("API_KEY",     re.compile(r"\b(?:AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{35})\b")),
 ("TOKEN",       re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|xox[baprs]-[A-Za-z0-9-]{10,}|eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,})\b")),
 ("PASSWORD",    re.compile(r"(?i)\b(?:password|passwd|pwd|secret|api[_-]?key|token)\b\s*[:=]\s*['\"]([^'\"\s]{8,})['\"]")),
 ("COOKIE",      re.compile(r"(?i)\b(?:set-cookie|cookie):\s*[^\n]{10,}")),
 ("PRIVATE_KEY", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
 ("FILE_PATH",   re.compile(r"/(?:home|Users)/[A-Za-z0-9._-]+/[^\s\"']*")),
]
IGNORE = re.compile(r"(?i)example\.(com|org)|noreply|localhost|YOUR_|<.*>|\.\.\.")

def main(inp, out):
    counts = collections.Counter(); traj = collections.defaultdict(set); n = 0
    with open(inp) as f, open(out, "w", newline="") as o:
        w = csv.writer(o); w.writerow(["trajectory_id","step_id","role","entity_type","span","start","end"])
        for line in f:
            r = json.loads(line); n += 1
            for s in r["steps"]:
                for etype, pat in PATTERNS:
                    for m in pat.finditer(s["content"]):
                        span = m.group(0)
                        if IGNORE.search(span): continue
                        w.writerow([r["trajectory_id"], s["step_id"], s["role"], etype, span[:200], m.start(), m.end()])
                        counts[etype] += 1; traj[etype].add(r["trajectory_id"])
    print(f"{n} trajectories scanned")
    for etype, _ in PATTERNS:
        print(f"{etype:12s} {counts[etype]:6d} matches in {len(traj[etype]):4d} trajectories")
    print("trajectories with any hit:", len(set().union(*traj.values())))

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    inp = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "normalized_agent_logs.jsonl")
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "hits.csv")
    if not os.path.exists(inp):
        sys.exit(f"Input file not found: {inp}")
    main(inp, out)