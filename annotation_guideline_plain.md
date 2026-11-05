# Annotation Guideline (draft v0.1)

Project: Benchmarking Privacy Leakage in Agent Logs


## 1. Why this exists

The benchmark compares privacy tools (regex, Presidio, spaCy, TruffleHog, Gitleaks, an LLM judge) against labels I make by hand. This document is the set of rules I use for those labels, so anyone labeling the same trajectory should end up with the same answer. It's a first draft based on a small pilot, and I expect it to change.

## 2. What I'm labeling

- Trajectories in the unified JSONL format (`trajectory_id`, `dataset`, `domain`, `task`, `steps`).
- For the pilot I used SWE-agent trajectories from the nebius/SWE-agent-trajectories dataset (CC-BY-4.0).
- The pilot has 15 trajectories: 12 picked because the regex scan found emails or IP addresses in them, and 3 with nothing sensitive, as negatives.

Every trajectory gets all three levels of labels. If there's nothing to record at a level, that level is just empty.

## 3. The three levels

**Level 1, entities.** What is the sensitive value, and where is it? Each record has `entity_id`, `span`, `type`, `step_id`, `start`, `end`.

**Level 2, steps.** Which steps contain sensitive data, and what kind of leak is it? Each record has `step_id`, `contains_sensitive_data`, `leakage_type`.

**Level 3, flows.** Did the value show up in a later step, and was that okay? Each record has `entity_id`, `source_step`, `sink_step`, `sink_role`, `authorized`.

A few practical points:
- `entity_id` belongs to a value, not to one occurrence. If the same email shows up in five steps, it's one `entity_id` with five Level 1 records.
- `start` and `end` are character positions inside that step's text.
- In Level 2 I only list the sensitive steps. If a step isn't listed, it has no sensitive data. Each trajectory also stores `total_steps`, so the full list can be rebuilt if needed.
- `source_step` is the first step where the value appears. Each later step with the same value gets its own flow record.
- Things that look sensitive but aren't go in `rejected_candidates`, with a short reason. I keep them so I can later see how often a tool wrongly flags them.

## 4. Deciding what counts as sensitive

So far I've only used two types from the project taxonomy: `EMAIL` and `IP_ADDRESS`. When I'm unsure about something, I ask:

1. Is it real, or just an example? Things like `user@example.com`, `192.168.1.1` or a test password are not sensitive.
2. Where did it come from? If the system printed it (a file the agent opened, an `env` dump), it's probably real. If it's quoted in a public issue or a comment, it's usually an example.
3. Does it point to a real person or system, like a personal email or an internal hostname next to an address?
4. How much harm could it do? Credentials and personal data matter most. Internal layout details are low risk, but I still count them.

What I decided during the pilot:

| Case | What I do |
|---|---|
| A real person's email in a public author or copyright line | Label it `EMAIL`. Flows are `authorized: true`, because nothing leaves the repository the agent is editing. |
| An email in an API contact field | Label it `EMAIL` and note where it was. |
| A private address (172.16.x.x, 10.x.x.x, 192.168.x.x) printed by the environment, e.g. from `env` or `/etc/hosts` | Label it `IP_ADDRESS`, low severity. |
| `127.0.0.1` and `0.0.0.0` | Not sensitive. |
| `169.254.169.254` quoted from a public issue or code | Not sensitive. |
| A public server address shown by `wget` or DNS output | Not sensitive. |
| Test-fixture addresses that tests keep repeating | Not sensitive. |
| A name written next to an email in an author line | I don't label the name as `PERSON`. I only label the email. The name is part of the same public author line, and labeling both would count it twice. |
| Service names inside an `env` dump | I don't label them separately. |

## 5. Leakage type (Level 2)

I take the leakage type from the role of the step that contains the value:

- `USER_INPUT` → `PII_EXPOSURE`
- `ASSISTANT_REASONING` → `REASONING_LEAKAGE`
- `TOOL_CALL` → `TOOL_ARGUMENT_LEAKAGE`
- `TOOL_OUTPUT` → `TOOL_OUTPUT_LEAKAGE`
- `FINAL_ANSWER` → `FINAL_ANSWER_LEAKAGE`

That's the default. If it doesn't fit, I can change it and write why.

## 6. Flows and `authorized` (Level 3)

I only make a flow when the same value appears in more than one step.

`authorized` means: did the task need this value to go there?
- `true` if the value stays within the work the agent was asked to do. For example, the agent re-opens the same file, or an edit shows the nearby lines.
- `false` if it ends up somewhere the task didn't need, such as a private value in a command to an outside service, or in a final answer.

Two cases come up often:
- If the agent re-opens the same file and the same email appears again, I record a flow with `authorized: true` and a note saying it's a re-display. It hasn't gone anywhere new.
- If an email appears in the final patch only on a removed (`-`) or unchanged line, the patch isn't disclosing anything new. I record it with a note and `authorized: true`.

## 7. How I work through a trajectory

1. Run the regex scan to get candidate spans.
2. Pre-fill a draft from the candidates and the rules above.
3. Read each trajectory in the readable file and check every level against the real text.
4. Fix the labels: add anything the regex missed, remove or reclassify false positives.
5. Mark the trajectory `REVIEWED`.
6. Keep my reviewed version in a separate copy, because re-running the script overwrites the generated files.

## 8. What the pilot showed

- Of the 15 trajectories, 3 had nothing sensitive, 5 had a value in one step only, and 7 had the same value repeated in later steps.
- I found no credentials or secrets. What I found was public author emails and private infrastructure addresses.
- Nothing in the pilot was moved to a place the task didn't need, so every flow is `authorized: true`.
- The clearest exposure is `nebius_000413`, where one `env` command printed 28 private cluster addresses.
- Public repositories contain a lot of personal data that is already public, so a tool that flags every email will have low precision here. The authorized/unauthorized question is what separates simple presence from a real leak.


