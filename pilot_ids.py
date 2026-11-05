PILOT = {
    # 11 trajectories with real people's emails (public author/copyright headers)
    "nebius_000022": "email: author header in environ/__init__.py",
    "nebius_000029": "email: author comment in sisotool.py",
    "nebius_000065": "email: author email",
    "nebius_000116": "email: author email",
    "nebius_000128": "email + internal pod IP from /etc/hosts",
    "nebius_000186": "email: copyright header in snippets.py",
    "nebius_000208": "email: author email",
    "nebius_000216": "email: author email",
    "nebius_000267": "email: author comment in sisotool.py",
    "nebius_000446": "email: __author__ re-displayed in 11 steps",
    "nebius_000456": "email: 8+ author emails -> appear in final diff",
    # environment dump
    "nebius_000413": "internal cluster IPs from an env dump",
    # negatives (look sensitive to a regex, are not)
    "nebius_000036": "negative: public server IP in wget output",
    "nebius_000203": "negative: test-fixture IPs repeated hundreds of times",
    "nebius_000021": "negative: cloud metadata IP quoted in a public issue",
}
