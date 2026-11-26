#!/usr/bin/env python3
"""Generate every page and data file in this repo from the files in source/.

Usage:  python3 scripts/build.py

Checks the source data before writing anything. Stops with an error if any
judge's 22 trait scores don't add up to the stated total, if the stated
averages or ranks don't match the per-judge totals, or if a quote used in the
README is not found in its story. Story text, scores and commentary are
copied through unchanged.

Generated (replaced on every run): README.md, brief.md, rubric.md,
judge_prompt.md, Stories/, LLM Judgement/, data/.
"""

import csv
import json
import re
import shutil
import sys
from decimal import Decimal
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source"

STORIES_FILE = SRC / "stories_anonymized.txt"
KEY_FILE = SRC / "story_key.txt"
SCORES_FILE = SRC / "judgments_scores_final.txt"
PROMPT_FILE = SRC / "judge_prompt_A-V.txt"

STORY_DIR = "Stories"
JUDGE_DIR = "LLM Judgement"
JUDGE_URL = quote(JUDGE_DIR)  # URL-safe form for links: LLM%20Judgement
AVERAGES_FILE = "average-scores.md"

JUDGES = [
    ("GEMINI HYDROGEN", "Gemini Hydrogen"),
    ("GLM 5.3", "GLM 5.3"),
    ("META MUSE SPARK 1.3", "Meta Muse Spark 1.3"),
    ("FABLE 5.2", "Fable 5.2"),
]
SELF_JUDGE = ("GLM 5.3", "GLM 5.3")  # (judge display name, contestant model name)

N_TRAITS = 22
MAX_TOTAL = 20 * N_TRAITS

# Quotes used in the README, copied from the write-up. build.py checks each one
# appears in its story, so a wrong quote stops the build.
HEATER = [
    ("Sonnet 4.5", "The heater ticked like a cooling engine."),
    ("GLM 5.3", "the heater under the front bench went on ticking the way it had for three days now, steady as a clock with nowhere to be."),
    ("Opus 4.6 Max", "a metallic knock every eight or nine seconds that Dale couldn't fix and couldn't stop hearing."),
    ("Gemini Argon", "the defroster fan under Dale's left knee kept up its dry, rhythmic tick—a bent fin catching the housing every third revolution."),
    ("Meta Wonder", "The heater under Dale's left foot ticked, stopped, ticked again."),
    ("DeepSeek 4.1 Flash", "Under the dash the heater ticked, ticked, ticked, a small hard noise with a wrongness in it he had reported twice."),
    ("Fable 5.1", "the heater under the dash kept ticking the way it did, the metal cooling"),
    ("GPT-6 Astra", "At nine fourteen, the heater began ticking again."),
]
REPOSSESSION = [
    ("GLM 5.3", "In October two men had taken the Corolla out of the visitor spot at his building at ten to five in the morning, and he had watched from the kitchen window in his coat, coffee in his hand, and said nothing to anyone."),
    ("Opus 5.5", "a man with a clipboard and a tow truck took the Ranger out of the lot behind his building at six in the morning while Dale stood on the step in his socks."),
    ("GPT 5.5", "The tow truck had come in October, before sunrise, polite as a funeral director."),
    ("Gemini Neon", "The repo truck had taken the car in October while it was still on all-seasons, leaving the winters stacked on steel rims in the basement locker."),
    ("Kimi K3.1 Pro", "The Volkswagen had been taken away in October."),
    ("DeepSeek 4.1 Flash", "The car had gone back in October and he hadn't told Carla or his daughter."),
    ("6.2 Sol", "He'd been deleting little bits of sentences since October, when the finance company sent a man for the Pontiac."),
    ("Luna 6", "The repossession had happened in October, while he was at the dentist."),
]
OPENINGS = [
    ("GPT 5.5", "On Thursday, the nineteenth of February, Hamilton looked rinsed and left in the freezer."),
    ("DeepSeek 4.1 Flash", "The thaw had broken around suppertime, and by nine the nineteenth had turned back into February."),
    ("Gemini Neon", "By nine o'clock the afternoon thaw had turned back into iron."),
    ("Sonnet 5.5", "By nine o'clock the thaw had quit."),
    ("Luna 6", "By nine o'clock, the thaw had turned the streets of Hamilton into a long, dirty reflection."),
    ("Mistral Small 4", "The thaw had turned the streets to slush, and the windshield wipers were fighting a losing battle."),
    ("6.2 Sol", "At a quarter to nine on Thursday, February 19, Dale Varga took over a bus with a full tank and a wet seat."),
    ("Meta Ember", "Dale Varga was forty-seven and in his eleventh year with the city, and on Thursday, February 19, he had the 20 for the last three hours of his shift, eastbound from downtown to the garage on the east side."),
]
ENDINGS = [
    ("Astra 6.2", "Dale lifted the clipboard so the boy could brush them into his palm."),
    ("6.2 Sol", "Theo slapped his other hand down on it."),
    ("GPT 5.6 Sol", "On the meter, $4.75 appeared, held for a moment, then climbed."),
    ("GPT-6 Astra", "\"Got it,\" she said."),
    ("GLM 5.3", "and at Lottridge the light went green for nobody and he crossed on it anyway."),
    ("GPT 6 Sol", "Behind the office glass, Ana shifted the phone to her other ear and tucked Theo's hat under his chin."),
    ("Mistral Large 4", "He turned the key."),
    ("Mistral Small 4", "The twenty in his pocket burned."),
    ("Sonnet 4.5", "and somewhere in the building, someone laughed, the sound carried on the wind like smoke."),
]


class DataError(Exception):
    pass


def slugify(name):
    """Lowercase, hyphens, no dots: 'GPT-6 Astra' -> 'gpt-6-astra'."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def competition_ranks(values):
    """values: list of (key, score). Higher is better. Ties share a rank (1, 2, 2, 4)."""
    ordered = sorted(values, key=lambda kv: -kv[1])
    ranks, prev, prev_rank = {}, None, 0
    for i, (k, v) in enumerate(ordered, start=1):
        if v != prev:
            prev_rank, prev = i, v
        ranks[k] = prev_rank
    return ranks


def read(path):
    return path.read_text(encoding="utf-8")


def norm(s):
    s = (s.replace("’", "'").replace("‘", "'").replace("“", '"')
          .replace("”", '"').replace("—", "-").replace("–", "-"))
    return re.sub(r"\s+", " ", s).strip().lower()


# --------------------------------------------------------------------------- parsing

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
        title = body.split("\n", 1)[0].strip()
        stories[letter] = {"full": body, "title": title, "words": len(body.split())}
    if len(stories) != 22:
        raise DataError(f"stories file: expected 22 stories, found {len(stories)}")
    return stories


def parse_scores():
    lines = read(SCORES_FILE).splitlines()
    headers = [h for h, _ in JUDGES]
    tables, avg_rows, commentary = {}, {}, {}
    section, current = "scores", None
    for line in lines:
        stripped = line.strip()
        if stripped == "AVERAGE OF THE FOUR JUDGES":
            section, current = "avg", None
        elif stripped == "JUDGES' COMMENTARY":
            section, current = "comm", None
        elif stripped in headers:
            current = stripped
            if section == "scores":
                tables[current] = {}
            elif section == "comm":
                commentary[current] = {}
        elif section == "scores" and current and re.match(r"^[A-V],", stripped):
            cells = stripped.split(",")
            nums = [int(c) for c in cells[1:]]
            if len(nums) != N_TRAITS + 1:
                raise DataError(f"{current} {cells[0]}: expected {N_TRAITS} traits + total, got {len(nums)} numbers")
            tables[current][cells[0]] = {"traits": nums[:N_TRAITS], "total": nums[N_TRAITS]}
        elif section == "avg" and re.match(r"^\d+,[A-V],", stripped):
            cells = stripped.split(",")
            avg_rows[cells[1]] = {"rank": int(cells[0]),
                                  "totals": [int(c) for c in cells[2:6]],
                                  "average": cells[6]}
        elif section == "comm" and current:
            m = re.match(r"^([A-V]): (.*)$", line)
            if m:
                if m.group(1) in commentary[current]:
                    raise DataError(f"{current}: duplicate commentary for {m.group(1)}")
                commentary[current][m.group(1)] = m.group(2)
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
            traits.append({"n": int(m.group(1)), "raw": raw, "name": name, "negative": negative})
    if [t["n"] for t in traits] != list(range(1, N_TRAITS + 1)):
        raise DataError("judge prompt: traits are not numbered 1-22")
    scale = re.search(r"Each trait is scored out of 20[^\n]*", text).group(0)
    neg_note = re.search(r"For negative traits \(marked \*\)[^\n]*", text).group(0)
    return {"text": text, "brief": brief.group(1).strip("\n"), "traits": traits,
            "scale": scale, "neg_note": neg_note}


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
        # The source rounds exact .x5 averages half-to-even (284.25 -> 284.2).
        exact = Decimal(sums[letter]) / 4
        if abs(Decimal(row["average"]) - exact) > Decimal("0.05"):
            errors.append(f"average table {letter}: stated {row['average']}, exact mean {exact}")
    ranks = competition_ranks([(l, sums[l]) for l in letters])
    for letter in letters:
        if ranks[letter] != avg_rows[letter]["rank"]:
            errors.append(f"average table {letter}: stated rank {avg_rows[letter]['rank']}, computed {ranks[letter]}")
    if errors:
        raise DataError("\n".join(errors))


def check_quotes(label, pairs, rev, stories):
    errors = []
    for model, q in pairs:
        if model not in rev:
            errors.append(f"{label}: unknown model {model!r}")
            continue
        target = norm(q).strip(" .")
        if target not in norm(stories[rev[model]]["full"]):
            errors.append(f"{label}: quote not found in {model}'s story: {q[:70]}")
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
    rev = {m: L for L, m in key.items()}
    stories = parse_stories()
    tables, avg_rows, commentary = parse_scores()
    prompt = parse_prompt()
    verify(key, stories, tables, avg_rows, commentary)
    for label, pairs in [("heater", HEATER), ("repossession", REPOSSESSION),
                         ("openings", OPENINGS), ("endings", ENDINGS)]:
        check_quotes(label, pairs, rev, stories)

    traits = prompt["traits"]
    judges = [{"header": h, "name": n, "slug": slugify(n)} for h, n in JUDGES]
    avg_order = list(avg_rows)
    entries = []
    for letter in sorted(avg_rows, key=lambda l: (avg_rows[l]["rank"], avg_order.index(l))):
        model = key[letter]
        rank = avg_rows[letter]["rank"]
        stem = f"{rank:02d}-{slugify(model)}"
        totals = {j["header"]: tables[j["header"]][letter]["total"] for j in judges}
        entries.append({
            "letter": letter, "model": model, "slug": slugify(model), "rank": rank,
            "average": avg_rows[letter]["average"], "totals": totals,
            "stem": stem, "txt": stem + ".txt",
            "story": stories[letter],
            "trait_avgs": [Decimal(sum(tables[j["header"]][letter]["traits"][t] for j in judges)) / len(judges)
                           for t in range(N_TRAITS)],
            "spread": max(totals.values()) - min(totals.values()),
        })
    if len({e["slug"] for e in entries}) != len(entries):
        raise DataError("two models produce the same slug")
    by_model = {e["model"]: e for e in entries}
    judge_ranks = {j["header"]: competition_ranks([(e["letter"], tables[j["header"]][e["letter"]]["total"])
                                                   for e in entries]) for j in judges}

    for d in (ROOT / STORY_DIR, ROOT / JUDGE_DIR, ROOT / "data" / "stories",
              ROOT / "stories", ROOT / "judgments"):  # last two: old layout
        shutil.rmtree(d, ignore_errors=True)

    # ---- brief / rubric / judge prompt
    write(ROOT / "brief.md",
          "# The brief\n\n"
          "Every model got this brief, word for word, in a single prompt. It is copied exactly "
          "from the [judge prompt](judge_prompt.md).\n\n"
          + prompt["brief"] + "\n\n[Back to the leaderboard](README.md)\n")

    trait_rows = [[t["n"], t["name"], "Negative (20 = flaw absent)" if t["negative"] else "Positive"]
                  for t in traits]
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

    # ---- stories: one plain-text file per model
    for e in entries:
        write(ROOT / STORY_DIR / e["txt"], e["story"]["full"] + "\n")

    # ---- judgments: LLM Judgement/<rank>-<model>/<judge>.md, one file per judge per model
    for e in entries:
        mdir = ROOT / JUDGE_DIR / e["stem"]
        for j in judges:
            row = tables[j["header"]][e["letter"]]
            trows = [[t["n"], t["name"], "Negative" if t["negative"] else "", row["traits"][t["n"] - 1]]
                     for t in traits]
            trows.append(["", "**Total**", "", f"**{row['total']} / {MAX_TOTAL}**"])
            siblings = " · ".join(f"[{o['name']}]({o['slug']}.md)" for o in judges if o is not j)
            page = (
                f"# {j['name']} on {e['model']}\n\n"
                + md_table(["", ""], [
                    ["Judge", j["name"]],
                    ["Model", f"[{e['model']}](../../{STORY_DIR}/{e['txt']})"],
                    ["Blind letter", e["letter"]],
                    ["Total", f"{row['total']} / {MAX_TOTAL}"],
                    ["Rank with this judge", f"{judge_ranks[j['header']][e['letter']]} of 22"],
                  ])
                + "\n\n## Trait scores\n\n"
                "Each trait is out of 20. For negative traits, 20 means the flaw is absent. "
                "See the [rubric](../../rubric.md).\n\n"
                + md_table(["#", "Trait", "Type", "Score"], trows, ["--:", "---", "---", "--:"])
                + "\n\n## Commentary\n\n"
                + "> " + commentary[j["header"]][e["letter"]] + "\n\n"
                + f"Other judges on this story: {siblings}\n\n"
                + f"[Back to the story](../../{STORY_DIR}/{e['txt']}) · "
                + f"[Average scores](../{AVERAGES_FILE}) · [Leaderboard](../../README.md)\n"
            )
            write(mdir / f"{j['slug']}.md", page)

    # ---- average scores: one file explaining how each model scored
    jnames = [j["name"] for j in judges]
    overall = [[e["rank"], f"[{e['model']}](../{STORY_DIR}/{e['txt']})", e["story"]["words"]]
               + [f"[{e['totals'][j['header']]}]({e['stem']}/{j['slug']}.md)" for j in judges]
               + [f"**{e['average']}**", e["spread"]] for e in entries]
    by_judge = [[e["rank"], f"[{e['model']}](../{STORY_DIR}/{e['txt']})"]
                + [judge_ranks[j["header"]][e["letter"]] for j in judges]
                for e in entries]

    def trait_summary(e):
        ranked = sorted(range(N_TRAITS), key=lambda t: (-e["trait_avgs"][t], t))
        weakest = sorted(range(N_TRAITS), key=lambda t: (e["trait_avgs"][t], t))
        fmt = lambda t: f"{traits[t]['name']} ({float(e['trait_avgs'][t]):.2f})"
        return ", ".join(fmt(t) for t in ranked[:3]), ", ".join(fmt(t) for t in weakest[:3])
    how = []
    for e in entries:
        strong, weak = trait_summary(e)
        how.append([e["rank"], f"[{e['model']}](../{STORY_DIR}/{e['txt']})", strong, weak])

    avg_md = (
        "# Average scores\n\n"
        f"How each model scored, across the four judges. Each judge scored all 22 stories on "
        f"22 traits, each out of 20, so a total is out of {MAX_TOTAL}. The average is the mean of "
        "the four judges' totals. Ranks use competition ranking, so ties share a rank. "
        "The judge columns link to each judge's page for that model.\n\n"
        "## Overall\n\n"
        "Judge spread is the highest minus the lowest of the four totals: a large spread means the judges disagreed.\n\n"
        + md_table(["Rank", "Model", "Words"] + jnames + ["Average", "Judge spread"], overall,
                   ["--:", "---", "--:"] + ["--:"] * len(jnames) + ["--:", "--:"])
        + "\n\n## Ranking by judge\n\n"
        "Each judge's own rank for every model (1 = that judge's top story).\n\n"
        + md_table(["Overall rank", "Model"] + jnames, by_judge, ["--:", "---"] + ["--:"] * len(jnames))
        + "\n\n## How each model was scored\n\n"
        "Each model's three strongest and three weakest traits, using the average of the four judges' "
        "scores for each trait. Every trait is scored so that higher is better, including the negative "
        "traits (for those, a high score means the flaw is absent).\n\n"
        + md_table(["Overall rank", "Model", "Strongest traits (avg /20)", "Weakest traits (avg /20)"], how,
                   ["--:", "---", "---", "---"])
        + "\n\n[Back to the leaderboard](../README.md)\n"
    )
    write(ROOT / JUDGE_DIR / AVERAGES_FILE, avg_md)

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
        w.writerow(["rank", "model", "letter", "words"] + jnames + ["average"])
        for e in entries:
            w.writerow([e["rank"], e["model"], e["letter"], e["story"]["words"]]
                       + [e["totals"][j["header"]] for j in judges] + [e["average"]])
    comm = {j["name"]: {e["model"]: commentary[j["header"]][e["letter"]] for e in entries} for j in judges}
    write(ROOT / "data" / "commentary.json", json.dumps(comm, ensure_ascii=False, indent=2) + "\n")

    # ---- README
    self_judge_name, self_model = SELF_JUDGE
    sj = next(j for j in judges if j["name"] == self_judge_name)
    se = by_model[self_model]
    within = [e for e in entries if 3 <= e["rank"] <= 5]
    spread = Decimal(within[0]["average"]) - Decimal(within[-1]["average"])

    board = [[e["rank"], f"[{e['model']}]({STORY_DIR}/{e['txt']})"]
             + [f"[{e['totals'][j['header']]}]({JUDGE_URL}/{e['stem']}/{j['slug']}.md)" for j in judges]
             + [f"**{e['average']}**"] for e in entries]
    leaderboard = md_table(["Rank", "Model"] + jnames + ["Average"], board,
                           ["--:", "---"] + ["--:"] * (len(judges) + 1))

    def qtable(pairs, col):
        return md_table(["Model", col],
                        [[f"[{m}]({STORY_DIR}/{by_model[m]['txt']})", f"“{q}”"] for m, q in pairs],
                        ["---", "---"])

    def count(pattern, flags=0):
        return sum(1 for e in entries if re.search(pattern, e["story"]["full"], flags))
    last_titles = sum("Last" in e["story"]["title"] for e in entries)

    in_range = sum(1 for e in entries if 1700 <= e["story"]["words"] <= 2300)
    over = sorted((e for e in entries if e["story"]["words"] > 2300), key=lambda e: -e["story"]["words"])
    under = sorted((e for e in entries if e["story"]["words"] < 1700), key=lambda e: e["story"]["words"])
    length_list = lambda es: ", ".join(f"{e['model']} ({e['story']['words']:,})" for e in es)

    brief_quote = "\n".join("> " + line if line else ">" for line in prompt["brief"].split("\n"))
    readme = f"""# One brief, 22 models: a blind short-fiction comparison

I gave 22 AI models the same literary short-story brief and then had four AI judges score the stories blind, with model names removed. Each model got one shot and no edits. The brief is a Hamilton, Ontario bus driver on the last three hours of a February night shift, with a few fixed details every story had to include: a ticking heater, a repossessed car that he hasn't told anyone about, a dispatcher's routine schedule changes, a mother and son who board at the hospital, and a choice at the garage that puts his ride home at risk.

The aim is to show what the models wrote, side by side, so you can judge for yourself. Read the stories first if you like, then compare your view with the judges'.

- **Stories:** [Stories/](Stories/), one plain-text file per model.
- **Judgments:** [LLM Judgement/](LLM%20Judgement/), one folder per model with one file per judge.
- **Averages and explanations:** [LLM Judgement/average-scores.md](LLM%20Judgement/average-scores.md).

## The brief

This is the prompt every model received, word for word. It is also in [brief.md](brief.md) and at the top of the [judge prompt](judge_prompt.md).

{brief_quote}

## Method

- **One brief, one shot.** Every model got the same brief, word for word, with no edits. It is reproduced below.
- **Four blind judges.** Each judge scored all 22 stories on 22 traits (dialogue, subtext, pacing, POV, brief adherence, cliché avoidance and so on). Each trait is out of 20, so a total is out of 440. Model names were removed. The traits are adapted from the rubric used in [EQ-Bench Creative Writing v3](https://eqbench.com/creative_writing.html). The full prompt and rubric are in [judge_prompt.md](judge_prompt.md) and [rubric.md](rubric.md).
- **Checked.** Every judge's arithmetic was checked against its own trait scores, and every quote the judges used was checked against its story. Errors were sent back for correction. `scripts/build.py` repeats these checks on every build.

## Leaderboard

Click a model to read its story, or a score to see that judge's trait scores and commentary. Ties share a rank. The average is the mean of the four judges' totals.

{leaderboard}

Astra 6.2 came first with all four judges. The full breakdown, including how each judge ranked the models and where the judges disagreed, is in [average-scores.md]({JUDGE_URL}/{AVERAGES_FILE}).

## Caveats

- **One story per model, one run each.** This is a snapshot, not a benchmark. A second run could reorder the table.
- **{sj['name']} was both a judge and a contestant.** Judging blind, it gave its own story [{se['totals'][sj['header']]}]({JUDGE_URL}/{se['stem']}/{sj['slug']}.md), about 11 points above that story's four-judge average of {se['average']}. Fable 5.2 judged and Fable 5.1 competed, but those are different models.
- **The judges sometimes disagreed widely.** Meta Wonder got 412 from one judge and 326 from another. Sonnet 4.5 ranged from 251 to 355.
- **Ranks 3 to 5 are within about a point** ({within[0]['model']} to {within[-1]['model']}: {spread} points apart). Read them as tied.

## What the models wrote

These tables quote each model's own choices on the same moment. Each quote was checked against its story.

### The heater ticks

Every model had to include a ticking heater. Some gave the tick a mechanical cause (a bent fin, a fault Dale had reported); others used a simile. One model, Mistral Small 4, has the heater click like a metronome and then fall silent.

{qtable(HEATER, "The heater")}

### The repossession

The brief only says "in October, Dale's car was repossessed." Some models stated it in a single flat line. Others tied it to a physical detail Dale carries around: the winter tires still in his locker, the socks on the step, the half-written texts he keeps deleting.

{qtable(REPOSSESSION, "How it comes out")}

### The opening

The brief describes a thaw that freezes again by evening. Four stories open with some version of "By nine (o'clock)."

{qtable(OPENINGS, "First sentence")}

### The ending

The brief says the ending "shouldn't tie everything up." Look at what each ending is built on: a small physical action (the clipboard, the hand on the quarter, the meter), a line of dialogue, or a feeling stated outright.

{qtable(ENDINGS, "Last line")}

## What kept showing up

None of these were in the brief.

- **Titles:** {last_titles} of 22 titles contain "Last". Three stories are called *The Last Stop* and two *The Last Pull-In*.
- **The car:** a Honda Civic appears in {count(r'Civic')} stories. The brief never names the car.
- **Dinosaurs:** in {count(r'dinosaur', re.I)} stories, Theo talks about dinosaurs.
- **Tim Hortons** appears in {count(r'Tim Hortons')} stories.
- **The walk home:** {count(r'started (?:walking )?west', re.I)} stories have Dale set off west on foot.

When models write the same brief, they converge. If you use one of these for fiction, these are the defaults to watch for in your own drafts.

## Following the length limit

The brief asked for 1,700–2,300 words. Counts are whitespace splits, title included.

- **Inside the range:** {in_range} of 22.
- **Over:** {len(over)}. {length_list(over)}. All ran 1,000+ words past the ceiling.
- **Under:** {len(under)}. {length_list(under)}.

The overruns weren't small, and several of the over-length stories still scored well on the craft traits. Length was what pulled them down.

## The materials

- [The brief](brief.md): the prompt every model received
- [The rubric](rubric.md): the 22 traits, including which are negative traits
- [The judge prompt](judge_prompt.md): the full prompt each judge received
- [Stories/](Stories/): all 22 stories, one plain-text file per model, named by rank and model
- [LLM Judgement/](LLM%20Judgement/): one folder per model, with one file per judge inside
- [LLM Judgement/average-scores.md]({JUDGE_URL}/{AVERAGES_FILE}): averages, judge spread, rankings by judge, and each model's strongest and weakest traits
- Raw data:
  - [data/totals.csv](data/totals.csv): one row per model, with word count, each judge's total, the average and the rank
  - [data/scores.csv](data/scores.csv): every trait score, one row per judge, story and trait
  - [data/commentary.json](data/commentary.json): each judge's commentary on each story
  - [source/](source/): the original files these pages were built from, unchanged

## Rebuilding

Every page is generated from `source/` by [scripts/build.py](scripts/build.py) (Python 3, standard library only):

```
python3 scripts/build.py
python3 scripts/check_links.py
```

The build stops with an error if any judge's trait scores don't sum to the stated total, if the averages or ranks don't match the judges' totals, or if a quoted phrase isn't in its story.
"""
    write(ROOT / "README.md", readme)
    print(f"Built {len(entries)} stories, {len(entries) * len(judges)} judgments and {AVERAGES_FILE}. All checks passed.")


if __name__ == "__main__":
    try:
        build()
    except DataError as exc:
        print("Data check failed; nothing was written:\n" + str(exc), file=sys.stderr)
        sys.exit(1)
