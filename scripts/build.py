#!/usr/bin/env python3
"""Generate every page and data file in this repo from the files in source/.

Usage:  python3 scripts/build.py

The script checks the source data before it writes anything. It stops with
an error if any judge's 22 trait scores don't add up to the stated total, or
if the stated averages or ranks don't match the per-judge totals. Story text,
scores and commentary are copied through unchanged.

Generated (and replaced on every run): README.md, brief.md, rubric.md,
judge_prompt.md, stories/, judgments/, data/.
"""

import csv
import json
import re
import shutil
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source"

STORIES_FILE = SRC / "stories_anonymized.txt"
KEY_FILE = SRC / "story_key.txt"
SCORES_FILE = SRC / "judgments_scores_final.txt"
PROMPT_FILE = SRC / "judge_prompt_A-V.txt"

# Judge headers as they appear in judgments_scores_final.txt, in column order,
# mapped to display names.
JUDGES = [
    ("GEMINI HYDROGEN", "Gemini Hydrogen"),
    ("GLM 5.3", "GLM 5.3"),
    ("META MUSE SPARK 1.3", "Meta Muse Spark 1.3"),
    ("FABLE 5.2", "Fable 5.2"),
]
# The contestant that also judged (for the README caveat).
SELF_JUDGE = ("GLM 5.3", "GLM 5.3")  # (judge display name, contestant model name)

N_TRAITS = 22
MAX_TOTAL = 20 * N_TRAITS

class DataError(Exception):
    pass

def slugify(name):
    """Lowercase, hyphens, no dots: 'GPT-6 Astra' -> 'gpt-6-astra'."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

def competition_ranks(values):
    """values: list of (key, sortable). Higher is better. Ties share a rank (1, 2, 2, 4)."""
    ordered = sorted(values, key=lambda kv: -kv[1])
    ranks, prev, prev_rank = {}, None, 0
    for i, (k, v) in enumerate(ordered, start=1):
        if v != prev:
            prev_rank, prev = i, v
        ranks[k] = prev_rank
    return ranks

# --------------------------------------------------------------------------- parsing

def read(path):
    return path.read_text(encoding="utf-8")

def parse_key():
    key = {}
    for line in read(KEY_FILE).splitlines():
        m = re.match(r"^([A-V])\s+(.+?)\s*$", line)
        if m:
            key[m.group(1)] = m.group(2)
    if len(key) != 22:
        raise DataError(f"story_key.txt: expected 22 entries, found {len(key)}")
    return key

def parse_stories():
    text = read(STORIES_FILE)
    parts = re.split(r"^=+\nSTORY ([A-Z])\n=+\n", text, flags=re.M)
    if parts[0].strip():
        raise DataError("stories file: unexpected text before the first STORY header")
    stories = {}
    for i in range(1, len(parts), 2):
        letter, body = parts[i], parts[i + 1].strip("\n")
        lines = body.split("\n")
        title = lines[0].strip()
        rest = "\n".join(lines[1:]).strip("\n")
        stories[letter] = {"full": body, "title": title, "body": rest,
                           "words": len(body.split())}
    if len(stories) != 22:
        raise DataError(f"stories file: expected 22 stories, found {len(stories)}")
    return stories

def parse_scores():
    lines = read(SCORES_FILE).splitlines()
    headers = [h for h, _ in JUDGES]
    tables, avg_rows, commentary = {}, {}, {}
    i, section = 0, "scores"
    current = None
    while i < len(lines):
        line = lines[i].strip()
        if line == "AVERAGE OF THE FOUR JUDGES":
            section, current = "avg", None
        elif line == "JUDGES' COMMENTARY":
            section, current = "comm", None
        elif line in headers:
            current = line
            if section == "scores":
                tables[current] = {}
            elif section == "comm":
                commentary[current] = {}
        elif section == "scores" and current and re.match(r"^[A-V],", line):
            cells = line.split(",")
            letter, nums = cells[0], [int(c) for c in cells[1:]]
            if len(nums) != N_TRAITS + 1:
                raise DataError(f"{current} {letter}: expected {N_TRAITS} traits + total, got {len(nums)} numbers")
            tables[current][letter] = {"traits": nums[:N_TRAITS], "total": nums[N_TRAITS]}
        elif section == "avg" and re.match(r"^\d+,[A-V],", line):
            cells = line.split(",")
            avg_rows[cells[1]] = {"rank": int(cells[0]),
                                  "totals": [int(c) for c in cells[2:6]],
                                  "average": cells[6]}
        elif section == "comm" and current:
            m = re.match(r"^([A-V]): (.*)$", lines[i])
            if m:
                if m.group(1) in commentary[current]:
                    raise DataError(f"{current}: duplicate commentary for {m.group(1)}")
                commentary[current][m.group(1)] = m.group(2)
        i += 1
    return tables, avg_rows, commentary

def parse_prompt():
    text = read(PROMPT_FILE)
    brief = re.search(r"=== ORIGINAL BRIEF ===\n(.*?)\n=== END BRIEF ===", text, re.S)
    if not brief:
        raise DataError("judge prompt: brief markers not found")
    traits_block = re.search(r"\nTRAITS\n(.*?)\n\nRULES\n", text, re.S)
    if not traits_block:
        raise DataError("judge prompt: TRAITS section not found")
    traits = []
    for line in traits_block.group(1).splitlines():
        m = re.match(r"^(\d+)\. (.+)$", line)
        if m:
            raw = m.group(2)
            negative = raw.endswith("*")
            name = re.sub(r"\s*\(.*\)$", "", raw.rstrip("*")).strip()
            traits.append({"n": int(m.group(1)), "raw": raw, "name": name,
                           "negative": negative})
    if [t["n"] for t in traits] != list(range(1, N_TRAITS + 1)):
        raise DataError("judge prompt: traits are not numbered 1-22")
    scale = re.search(r"Each trait is scored out of 20[^\n]*", text).group(0)
    neg_note = re.search(r"^For negative traits \(marked \*\).*$", text, re.M).group(0)
    return {"text": text, "brief": brief.group(1).strip("\n"), "traits": traits,
            "traits_block": traits_block.group(1), "scale": scale, "neg_note": neg_note}

# --------------------------------------------------------------------------- checks

def verify(key, stories, tables, avg_rows, commentary):
    errors = []
    letters = sorted(key)
    if sorted(stories) != letters:
        errors.append("story letters in stories file don't match story_key.txt")
    for header, _ in JUDGES:
        if header not in tables:
            errors.append(f"no score table for {header}")
            continue
        if sorted(tables[header]) != letters:
            errors.append(f"{header}: score table doesn't have exactly stories A-V")
        for letter, row in tables[header].items():
            for t, s in enumerate(row["traits"], start=1):
                if not 0 <= s <= 20:
                    errors.append(f"{header} {letter} T{t}: score {s} outside 0-20")
            if sum(row["traits"]) != row["total"]:
                errors.append(f"{header} {letter}: traits sum to {sum(row['traits'])}, stated total {row['total']}")
        if sorted(commentary.get(header, {})) != letters:
            errors.append(f"{header}: commentary doesn't have exactly one line per story A-V")
    if sorted(avg_rows) != letters:
        errors.append("average table doesn't have exactly stories A-V")
    if errors:
        raise DataError("\n".join(errors))

    sums = {}
    for letter in letters:
        row = avg_rows[letter]
        judge_totals = [tables[h][letter]["total"] for h, _ in JUDGES]
        if row["totals"] != judge_totals:
            errors.append(f"average table {letter}: totals {row['totals']} != judge tables {judge_totals}")
        sums[letter] = sum(judge_totals)
        # The source rounds exact .x5 averages half-to-even (284.25 -> 284.2,
        # 412.75 -> 412.8). Accept any stated value within rounding distance of
        # the exact mean; the stated value is what gets published.
        exact = Decimal(sums[letter]) / 4
        if abs(Decimal(row["average"]) - exact) > Decimal("0.05"):
            errors.append(f"average table {letter}: stated {row['average']}, exact mean {exact}")
    ranks = competition_ranks([(l, sums[l]) for l in letters])
    for letter in letters:
        if ranks[letter] != avg_rows[letter]["rank"]:
            errors.append(f"average table {letter}: stated rank {avg_rows[letter]['rank']}, computed {ranks[letter]}")
    if errors:
        raise DataError("\n".join(errors))

# --------------------------------------------------------------------------- writing

def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def md_table(header, rows, align=None):
    align = align or ["---"] * len(header)
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(align) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)

def build():
    key = parse_key()
    stories = parse_stories()
    tables, avg_rows, commentary = parse_scores()
    prompt = parse_prompt()
    verify(key, stories, tables, avg_rows, commentary)

    traits = prompt["traits"]
    judges = [{"header": h, "name": n, "slug": slugify(n)} for h, n in JUDGES]

    # Entries in leaderboard order: rank, then source order of the average table.
    avg_order = list(avg_rows)  # dicts keep file order
    entries = []
    for letter in sorted(avg_rows, key=lambda l: (avg_rows[l]["rank"], avg_order.index(l))):
        model = key[letter]
        rank = avg_rows[letter]["rank"]
        slug = slugify(model)
        entries.append({
            "letter": letter, "model": model, "slug": slug, "rank": rank,
            "average": avg_rows[letter]["average"],
            "totals": {j["header"]: tables[j["header"]][letter]["total"] for j in judges},
            "file": f"{rank:02d}-{slug}.md",
            "story": stories[letter],
        })
    slugs = [e["slug"] for e in entries]
    if len(set(slugs)) != len(slugs):
        raise DataError("two models produce the same slug")
    by_letter = {e["letter"]: e for e in entries}

    for d in ("stories", "judgments", "data"):
        shutil.rmtree(ROOT / d, ignore_errors=True)

    neg_label = "Negative (20 = flaw absent)"

    # ---- brief / rubric / judge prompt
    write(ROOT / "brief.md",
          "# The brief\n\n"
          "Every model got this brief, word for word, in a single prompt. It is copied exactly "
          "from the [judge prompt](judge_prompt.md).\n\n"
          + prompt["brief"] + "\n\n[Back to the leaderboard](README.md)\n")

    trait_rows = [[t["n"], t["name"], neg_label if t["negative"] else "Positive"] for t in traits]
    write(ROOT / "rubric.md",
          "# The rubric\n\n"
          "Copied exactly from the [judge prompt](judge_prompt.md):\n\n"
          + prompt["scale"] + "\n\n" + prompt["neg_note"].replace("*", "\\*", 1) + "\n\n"
          + "\n".join(f"{t['n']}. {t['raw'].replace('*', chr(92) + '*')}" for t in traits)
          + "\n\n## At a glance\n\n"
          "Traits 10 to 18 are negative traits: a high score means the flaw is absent.\n\n"
          + md_table(["#", "Trait", "Type"], trait_rows, ["--:", "---", "---"])
          + "\n\n[Back to the leaderboard](README.md)\n")

    write(ROOT / "judge_prompt.md",
          "# Judge prompt\n\n"
          "This is the full prompt each judge received, unchanged, with the 22 stories attached "
          "as STORY A to STORY V. The source file is "
          "[source/judge_prompt_A-V.txt](source/judge_prompt_A-V.txt).\n\n"
          "````text\n" + prompt["text"].rstrip("\n") + "\n````\n\n"
          "[Back to the leaderboard](README.md)\n")

    # ---- story pages
    for idx, e in enumerate(entries):
        s = e["story"]
        prev_e = entries[idx - 1] if idx > 0 else None
        next_e = entries[idx + 1] if idx + 1 < len(entries) else None
        score_rows = [[f"[{j['name']}](../judgments/{j['slug']}/{e['file']})",
                       e["totals"][j["header"]]] for j in judges]
        score_rows.append(["**Average**", f"**{e['average']}**"])
        nav = []
        if prev_e:
            nav.append(f"← Previous: [#{prev_e['rank']} {prev_e['model']}]({prev_e['file']})")
        nav.append("[Leaderboard](../README.md)")
        if next_e:
            nav.append(f"Next: [#{next_e['rank']} {next_e['model']}]({next_e['file']}) →")
        page = (
            f"# {e['model']}\n\n"
            + md_table(["", ""], [
                ["Blind letter", e["letter"]],
                ["Final rank", f"{e['rank']} of 22"],
                ["Average score", f"{e['average']} / {MAX_TOTAL}"],
                ["Word count", f"{s['words']:,} (whitespace split, title included)"],
              ])
            + "\n\n## Scores\n\n"
            + md_table(["Judge", f"Total / {MAX_TOTAL}"], score_rows, ["---", "--:"])
            + "\n\n" + " · ".join(nav) + "\n\n---\n\n"
            + f"## {s['title']}\n\n" + s["body"] + "\n\n---\n\n"
            + "## Judgments\n\n"
            + "\n".join(f"- [{j['name']}](../judgments/{j['slug']}/{e['file']}): "
                        f"{e['totals'][j['header']]} / {MAX_TOTAL}" for j in judges)
            + f"\n\nPlain text: [data/stories/{e['slug']}.txt](../data/stories/{e['slug']}.txt)\n\n"
            + " · ".join(nav) + "\n"
        )
        write(ROOT / "stories" / e["file"], page)
        write(ROOT / "data" / "stories" / f"{e['slug']}.txt", s["full"] + "\n")

    # ---- judgment pages and per-judge rankings
    for j in judges:
        jt = tables[j["header"]]
        jranks = competition_ranks([(l, jt[l]["total"]) for l in jt])
        for e in entries:
            row = jt[e["letter"]]
            trows = [[t["n"], t["name"], "Negative" if t["negative"] else "", row["traits"][t["n"] - 1]]
                     for t in traits]
            trows.append(["", f"**Total**", "", f"**{row['total']} / {MAX_TOTAL}**"])
            page = (
                f"# {j['name']} on {e['model']}\n\n"
                + md_table(["", ""], [
                    ["Judge", f"[{j['name']}](README.md)"],
                    ["Model", f"[{e['model']}](../../stories/{e['file']})"],
                    ["Blind letter", e["letter"]],
                    ["Total", f"{row['total']} / {MAX_TOTAL}"],
                    ["Rank with this judge", f"{jranks[e['letter']]} of 22"],
                  ])
                + "\n\n## Trait scores\n\n"
                "Each trait is out of 20. For negative traits, 20 means the flaw is absent. "
                "See the [rubric](../../rubric.md).\n\n"
                + md_table(["#", "Trait", "Type", "Score"], trows, ["--:", "---", "---", "--:"])
                + "\n\n## Commentary\n\n"
                + "> " + commentary[j["header"]][e["letter"]] + "\n\n"
                + f"[Back to the story](../../stories/{e['file']}) · "
                + f"[All {j['name']} rankings](README.md) · [Leaderboard](../../README.md)\n"
            )
            write(ROOT / "judgments" / j["slug"] / e["file"], page)

        order = sorted(entries, key=lambda e: (jranks[e["letter"]], -jt[e["letter"]]["total"], entries.index(e)))
        rows = [[jranks[e["letter"]], f"[{e['model']}](../../stories/{e['file']})", e["letter"],
                 f"[{jt[e['letter']]['total']}]({e['file']})", e["rank"]] for e in order]
        write(ROOT / "judgments" / j["slug"] / "README.md",
              f"# {j['name']}: full ranking\n\n"
              f"All 22 stories ranked by {j['name']}'s total (out of {MAX_TOTAL}). "
              "Ties share a rank. Click a total to see the trait scores and commentary.\n\n"
              + md_table(["Rank", "Model", "Letter", "Total", "Overall rank"], rows,
                         ["--:", "---", ":-:", "--:", "--:"])
              + "\n\n[Back to the leaderboard](../../README.md)\n")

    # ---- data files
    with open(ROOT / "data" / "scores.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["judge", "model", "letter", "trait_number", "trait_name", "score"])
        for j in judges:
            for e in entries:
                for t in traits:
                    w.writerow([j["name"], e["model"], e["letter"], t["n"], t["name"],
                                tables[j["header"]][e["letter"]]["traits"][t["n"] - 1]])
    with open(ROOT / "data" / "totals.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rank", "model", "letter"] + [j["name"] for j in judges] + ["average"])
        for e in entries:
            w.writerow([e["rank"], e["model"], e["letter"]]
                       + [e["totals"][j["header"]] for j in judges] + [e["average"]])
    comm = {j["name"]: {e["model"]: commentary[j["header"]][e["letter"]] for e in entries} for j in judges}
    write(ROOT / "data" / "commentary.json", json.dumps(comm, ensure_ascii=False, indent=2) + "\n")

    # ---- README
    self_judge_name, self_model = SELF_JUDGE
    sj = next(j for j in judges if j["name"] == self_judge_name)
    se = next(e for e in entries if e["model"] == self_model)
    within = [e for e in entries if 3 <= e["rank"] <= 5]
    spread = Decimal(within[0]["average"]) - Decimal(within[-1]["average"])

    board = [[e["rank"], f"[{e['model']}](stories/{e['file']})"]
             + [f"[{e['totals'][j['header']]}](judgments/{j['slug']}/{e['file']})" for j in judges]
             + [f"**{e['average']}**"] for e in entries]
    readme = README_TEMPLATE.format(
        leaderboard=md_table(["Rank", "Model"] + [j["name"] for j in judges] + ["Average"], board,
                             ["--:", "---"] + ["--:"] * (len(judges) + 1)),
        judge_links=" · ".join(f"[{j['name']}](judgments/{j['slug']}/README.md)" for j in judges),
        self_judge=self_judge_name, self_total=se["totals"][sj["header"]], self_avg=se["average"],
        self_file=se["file"], self_slug=sj["slug"],
        r3=within[0]["model"], r5=within[-1]["model"], spread=spread,
        in_range=sum(1 for e in entries if 1700 <= e["story"]["words"] <= 2300),
        over=sum(1 for e in entries if e["story"]["words"] > 2300),
        under=sum(1 for e in entries if e["story"]["words"] < 1700),
    )
    write(ROOT / "README.md", readme)
    print(f"Built {len(entries)} story pages and {len(entries) * len(judges)} judgment pages. All checks passed.")

README_TEMPLATE = """# One brief, 22 models: a blind short-fiction comparison

22 AI models were each given the same literary short-story brief: a Hamilton, Ontario bus driver on the last three hours of a February night shift, with a few fixed details every story had to include. Each model wrote one story in a single shot, with no edits. The stories were labelled A to V with model names removed. Four AI judges scored every story blind on 22 craft traits, each out of 20, for a total out of 440. The leaderboard ranks models by the average of the four judges' totals.

Every story and every judge's verdict has its own page, so you can read the stories and make your own call before looking at the scores.

## Leaderboard

Click a model to read its story, or a score to see that judge's trait scores and commentary. Ties share a rank.

{leaderboard}

Full rankings by judge: {judge_links}

## Caveats

- **One story per model, one run each.** This is a snapshot, not a benchmark. A second run could reorder the table.
- **{self_judge} was both a judge and a contestant.** Judging blind, it gave its own story [{self_total}](judgments/{self_slug}/{self_file}), against that story's four-judge average of {self_avg}. Fable 5.2 judged and Fable 5.1 competed, but those are different models.
- **The judges sometimes disagreed widely.** Meta Wonder got 412 from one judge and 326 from another; Sonnet 4.5 ranged from 251 to 355.
- **Ranks 3 to 5 are within about a point** ({r3} to {r5}: {spread} points apart). Read them as tied.

## What stood out

- **Length.** {in_range} of 22 stories landed inside the 1,700–2,300-word target; {over} ran over (all by 1,000+ words) and {under} came in under. The rubric's first trait penalises missing the target, so several well-written stories lost ground here.
- **Convergence.** Without being asked, models reached for the same choices: titles built on "Last" (*The Last Stop* three times), a Honda Civic as the repossessed car, Theo talking about dinosaurs, Tim Hortons, and Dale ending the night on foot.
- **The fixed details.** Because every story had to include a ticking heater, the repossession and a choice at the garage, you can compare how each model handled the same moment. Some give the heater a mechanical cause; one mentions the heater but never has it tick.

## The materials

- [The brief](brief.md): the prompt every model received
- [The rubric](rubric.md): the 22 traits, including which are negative traits
- [The judge prompt](judge_prompt.md): the full prompt each judge received
- Raw data:
  - [data/totals.csv](data/totals.csv): one row per model, with each judge's total, the average and the rank
  - [data/scores.csv](data/scores.csv): every trait score, one row per judge, story and trait
  - [data/commentary.json](data/commentary.json): each judge's commentary on each story
  - [data/stories/](data/stories/): plain-text copies of all 22 stories
  - [source/](source/): the original files these pages were built from, unchanged

## Rebuilding

Every page is generated from `source/` by [scripts/build.py](scripts/build.py) (Python 3, standard library only):

```
python3 scripts/build.py
python3 scripts/check_links.py
```

The build stops with an error if any judge's trait scores don't sum to the stated total, or if the averages or ranks don't match the judges' totals.
"""

if __name__ == "__main__":
    try:
        build()
    except DataError as exc:
        print("Data check failed; nothing was written:\n" + str(exc), file=sys.stderr)
        sys.exit(1)
