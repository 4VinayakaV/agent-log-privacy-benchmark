import argparse, json, random, re
import pandas as pd

FENCE = re.compile(r"```[^\n]*\n(.*?)```", re.S)

def split_ai(text):
    """AI turn -> (reasoning, command). Command = last fenced block."""
    text = text or ""
    blocks = list(FENCE.finditer(text))
    if not blocks:
        return text.strip(), None
    last = blocks[-1]
    reasoning = (text[:last.start()] + text[last.end():]).strip()
    return reasoning, last.group(1).strip()

def convert(row, idx):
    steps, sid = [], 0
    def add(role, content, **kw):
        nonlocal sid
        sid += 1
        steps.append({"step_id": sid, "role": role, "content": content, "metadata": kw.pop("metadata", {}), **kw})
    seen_user = False
    last_tool = "bash"
    for turn in row.trajectory:
        role, text = turn["role"], turn.get("text") or ""
        if role == "system":
            continue  
        if role == "user":
            if not seen_user:
                add("USER_INPUT", text); seen_user = True
            else:
                add("TOOL_OUTPUT", text, tool_name=last_tool, structured_output={})
        elif role == "ai":
            reasoning, cmd = split_ai(text)
            if reasoning:
                add("ASSISTANT_REASONING", reasoning)
            if cmd is not None:
                tool = cmd.split()[0] if cmd.split() else "bash"
                last_tool = tool
                add("TOOL_CALL", cmd, tool_name=tool, structured_args={"command": cmd})
    patch = row.generated_patch if isinstance(row.generated_patch, str) else ""
    if patch.strip():
        add("FINAL_ANSWER", patch.strip(), metadata={"kind": "generated_patch"})
    return {
        "trajectory_id": f"nebius_{idx:06d}",
        "dataset": "nebius_swe_agent",
        "domain": "coding",
        "task": "fix_github_issue",
        "source_instance_id": row.instance_id,
        "model_name": row.model_name,
        "resolved": bool(row.target),
        "exit_status": row.exit_status,
        "steps": steps,
    }

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--n", type=int, default=500); ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    df = pd.read_parquet(a.inp, columns=["instance_id", "model_name", "target", "trajectory", "exit_status", "generated_patch"])
    df = df.sample(n=min(a.n, len(df)), random_state=a.seed).reset_index(drop=True)
    with open(a.out, "w") as f:
        for i, row in enumerate(df.itertuples()):
            f.write(json.dumps(convert(row, i), ensure_ascii=False) + "\n")
    print(f"wrote {len(df)} trajectories -> {a.out}")
