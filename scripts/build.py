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
import statistics as st
import sys
from decimal import Decimal, ROUND_HALF_EVEN
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
AVERAGES_FILE = "median-scores.md"

JUDGES = [
    ("GEMINI HYDROGEN", "Gemini Hydrogen"),
    ("GLM 5.3", "GLM 5.3"),
    ("META MUSE SPARK 1.3", "Meta Muse Spark 1.3"),
    ("FABLE 5.2", "Fable 5.2"),
]
# Judges added after the original four. Each has its own unchanged source files:
# (header, display name, scores CSV, full evaluation with per-story notes)
EXTRA_JUDGES = [
    ("QWEN 4 MAX", "Qwen 4 Max", SRC / "qwen-4-max_scores.csv", SRC / "qwen-4-max_evaluation.md"),
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


# What Dale does at the garage, summarised by hand from each story's ending:
# (model, what he does, his ride home, pays for Ana's way out with his own money)
GARAGE = [
    ("6.2 Sol", "Stays with them in the garage vestibule while Ana makes a call, then books himself a $38.60 cab", "Missed", False),
    ("Astra 6.2", "Signs them in as visitors and sits with them in the office while Ana calls her sister", "Missed", False),
    ("DeepSeek 4.1 Flash", "Leaves the bus, walks them to a Tim Hortons, pays $40 for a cab to a shelter. Gets a three-day suspension", "Missed", True),
    ("Fable 5.1", "Gives Ana $63, nearly all the money he has, for a cab", "Makes it", True),
    ("Gemini Argon", "Sends them by taxi to a shelter he knows", "Missed", False),
    ("Gemini Neon", "Pays for their cab with the cash from selling his repossessed Civic's winter tires", "Missed", True),
    ("GLM 5.3", "Calls a cab, gives Ana his cash and his fare card", "Missed", True),
    ("GPT 5.5", "Drives the out-of-service bus downtown to a shelter", "Missed", False),
    ("GPT 5.6 Sol", "Waits with them for an arranged cab, tells Carla \"My car's here,\" then pays $51.60 for his own taxi", "Missed", False),
    ("GPT 6 Sol", "Gets them into the garage office to call an intake line, then books himself a $41.60 taxi", "Missed", False),
    ("GPT 6.1 Sol", "Waits with them in the staff vestibule until a housing van comes, lends Ana his power bank", "Missed", False),
    ("GPT-6 Astra", "Pays $55 for one cab: family intake office first, then his place", "Missed", True),
    ("Kimi K3.1 Pro", "Pays for a cab and a motel room from a pay envelope marked CAR, then tells his daughter the truth", "Missed", True),
    ("Luna 6", "Carries Theo into the garage's security office while help is arranged", "Left open", False),
    ("Meta Ember", "Lets them slip out through the maintenance gate without telling anyone", "Missed", False),
    ("Meta Wonder", "Tells Carla the bus is empty, walks them out the pedestrian gate, pays $45 of his rent money for a cab", "Missed", True),
    ("Mistral Large 4", "Pays the cab fare from the money he was saving to get his car back", "Missed", True),
    ("Mistral Small 4", "Holds a $20 bill for Ana, then drives the bus back out to look for her", "Doesn't go home", False),
    ("Opus 4.6 Max", "Waits with them and pays $30 for their cab", "Left open", True),
    ("Opus 5.5", "Gives Ana the $60 he'd set aside for his daughter's driving test", "Missed", True),
    ("Sonnet 4.5", "Has dispatch call a cab and pays for it himself", "Left open", True),
    ("Sonnet 5.5", "Pays $50 for their cab, money meant for his daughter's birthday card", "Missed", True),
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


def parse_extra_judges(tables, commentary):
    errors = []
    for header, name, scores_file, eval_file in EXTRA_JUDGES:
        tables[header], commentary[header] = {}, {}
        with open(scores_file, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                letter = row["Story"].strip()
                traits = [int(row[f"T{i}"]) for i in range(1, N_TRAITS + 1)]
                total = int(row["Total"])
                if any(not 0 <= t <= 20 for t in traits):
                    errors.append(f"{name} {letter}: a trait score is outside 0-20")
                if sum(traits) != total:
                    errors.append(f"{name} {letter}: traits sum to {sum(traits)}, stated total {total}")
                tables[header][letter] = {"traits": traits, "total": total}
        for line in read(eval_file).splitlines():
            m = re.match(r"^- \*\*([A-V]):\*\* (.*)$", line)
            if m:
                commentary[header][m.group(1)] = m.group(2)
        if sorted(tables[header]) != [chr(c) for c in range(ord("A"), ord("W"))]:
            errors.append(f"{name}: scores don't cover exactly stories A-V")
        if sorted(commentary[header]) != sorted(tables[header]):
            errors.append(f"{name}: notes don't cover exactly one line per story")
    if errors:
        raise DataError("\n".join(errors))


def build():
    key = parse_key()
    rev = {m: L for L, m in key.items()}
    stories = parse_stories()
    tables, avg_rows, commentary = parse_scores()
    prompt = parse_prompt()
    verify(key, stories, tables, avg_rows, commentary)
    parse_extra_judges(tables, commentary)
    for label, pairs in [("heater", HEATER), ("repossession", REPOSSESSION),
                         ("openings", OPENINGS), ("endings", ENDINGS)]:
        check_quotes(label, pairs, rev, stories)

    traits = prompt["traits"]
    judges = ([{"header": h, "name": n, "slug": slugify(n)} for h, n in JUDGES]
              + [{"header": h, "name": n, "slug": slugify(n)} for h, n, _, _ in EXTRA_JUDGES])
    n_judges = len(judges)
    # Average and rank across every judge. The original four-judge averages in
    # judgments_scores_final.txt are verified above and kept in data/totals.csv.
    sums = {l: sum(tables[j["header"]][l]["total"] for j in judges) for l in avg_rows}
    medians = {l: st.median(tables[j["header"]][l]["total"] for j in judges) for l in avg_rows}
    means = {l: str((Decimal(sums[l]) / n_judges).quantize(Decimal("0.1"), rounding=ROUND_HALF_EVEN)) for l in sums}
    final_ranks = competition_ranks(list(medians.items()))
    avg_order = list(avg_rows)
    entries = []
    for letter in sorted(avg_rows, key=lambda l: (final_ranks[l], -float(means[l]), avg_order.index(l))):
        model = key[letter]
        rank = final_ranks[letter]
        stem = f"{rank:02d}-{slugify(model)}"
        totals = {j["header"]: tables[j["header"]][letter]["total"] for j in judges}
        entries.append({
            "letter": letter, "model": model, "slug": slugify(model), "rank": rank,
            "median": medians[letter], "average": means[letter], "four_judge_average": avg_rows[letter]["average"],
            "four_judge_rank": avg_rows[letter]["rank"], "totals": totals,
            "stem": stem, "txt": stem + ".txt",
            "story": stories[letter],
            "trait_medians": [st.median(tables[j["header"]][letter]["traits"][t] for j in judges)
                              for t in range(N_TRAITS)],
            "trait_means": [Decimal(sum(tables[j["header"]][letter]["traits"][t] for j in judges)) / n_judges
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
          "The traits are adapted from the rubric used in [EQ-Bench Creative Writing v3](https://eqbench.com/creative_writing.html). "
          "The text below is copied exactly from the [judge prompt](judge_prompt.md):\n\n"
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
                + f"[Median scores](../{AVERAGES_FILE}) · [Leaderboard](../../README.md)\n"
            )
            write(mdir / f"{j['slug']}.md", page)

    # ---- average scores: one file explaining how each model scored
    jnames = [j["name"] for j in judges]
    overall = [[e["rank"], f"[{e['model']}](../{STORY_DIR}/{e['txt']})", e["story"]["words"]]
               + [f"[{e['totals'][j['header']]}]({e['stem']}/{j['slug']}.md)" for j in judges]
               + [f"**{e['median']}**", e["spread"]] for e in entries]
    by_judge = [[e["rank"], f"[{e['model']}](../{STORY_DIR}/{e['txt']})"]
                + [judge_ranks[j["header"]][e["letter"]] for j in judges]
                for e in entries]

    def trait_summary(e):
        ranked = sorted(range(N_TRAITS), key=lambda t: (-e["trait_medians"][t], -float(e["trait_means"][t]), t))
        weakest = sorted(range(N_TRAITS), key=lambda t: (e["trait_medians"][t], float(e["trait_means"][t]), t))
        fmt = lambda t: f"{traits[t]['name']} ({e['trait_medians'][t]})"
        return ", ".join(fmt(t) for t in ranked[:3]), ", ".join(fmt(t) for t in weakest[:3])
    how = []
    for e in entries:
        strong, weak = trait_summary(e)
        how.append([e["rank"], f"[{e['model']}](../{STORY_DIR}/{e['txt']})", strong, weak])

    avg_md = (
        "# Median scores\n\n"
        f"How each model scored, across the {n_judges} judges. Each judge scored all 22 stories on "
        f"22 traits, each out of 20, so a total is out of {MAX_TOTAL}. The median is the middle value "
        f"of the {n_judges} judges' scores. Ranks use competition ranking, so ties share a rank. "
        "The judge columns link to each judge's page for that model.\n\n"
        "## Overall\n\n"
        f"Judge spread is the highest minus the lowest of the {n_judges} totals: a large spread means the judges disagreed.\n\n"
        + md_table(["Rank", "Model", "Words"] + jnames + ["Median", "Judge spread"], overall,
                   ["--:", "---", "--:"] + ["--:"] * len(jnames) + ["--:", "--:"])
        + "\n\n## Ranking by judge\n\n"
        "Each judge's own rank for every model (1 = that judge's top story).\n\n"
        + md_table(["Overall rank", "Model"] + jnames, by_judge, ["--:", "---"] + ["--:"] * len(jnames))
        + "\n\n## How each model was scored\n\n"
        f"Each model's three strongest and three weakest traits, using the median of the {n_judges} judges' "
        "scores for each trait. Ties are broken by the mean. Every trait is scored so that higher is better, "
        "including the negative traits (for those, a high score means the flaw is absent).\n\n"
        + md_table(["Overall rank", "Model", "Strongest traits (median /20)", "Weakest traits (median /20)"], how,
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
        w.writerow(["rank", "model", "letter", "words"] + jnames
                   + ["median", "average", "four_judge_average", "four_judge_rank"])
        for e in entries:
            w.writerow([e["rank"], e["model"], e["letter"], e["story"]["words"]]
                       + [e["totals"][j["header"]] for j in judges]
                       + [e["median"], e["average"], e["four_judge_average"], e["four_judge_rank"]])
    comm = {j["name"]: {e["model"]: commentary[j["header"]][e["letter"]] for e in entries} for j in judges}
    write(ROOT / "data" / "commentary.json", json.dumps(comm, ensure_ascii=False, indent=2) + "\n")

    # ---- README
    self_judge_name, self_model = SELF_JUDGE
    sj = next(j for j in judges if j["name"] == self_judge_name)
    se = by_model[self_model]
    within = [e for e in entries if 3 <= e["rank"] <= 5]
    words = {4: "four", 5: "five", 6: "six"}
    n_word = words.get(n_judges, str(n_judges))
    n_word_cap = n_word.capitalize()
    leader = entries[0]
    if all(judge_ranks[j["header"]][leader["letter"]] == 1 for j in judges):
        top_line = f"{leader['model']} came first with all {n_word} judges."
    else:
        top_line = f"{leader['model']} came first on the median."
    self_gap = se["totals"][sj["header"]] - se["median"]
    extra_note = " ".join(
        f"{n} was added as a fifth judge after the first four, using the same judge prompt; its full evaluation is in "
        f"[source/{ef.name}](source/{ef.name})." for _, n, _, ef in EXTRA_JUDGES)
    spread = within[0]["median"] - within[-1]["median"]

    board = [[e["rank"], f"[{e['model']}]({STORY_DIR}/{e['txt']})"]
             + [f"[{e['totals'][j['header']]}]({JUDGE_URL}/{e['stem']}/{j['slug']}.md)" for j in judges]
             + [f"**{e['median']}**"] for e in entries]
    leaderboard = md_table(["Rank", "Model"] + jnames + ["Median"], board,
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

    if sorted(g[0] for g in GARAGE) != sorted(by_model):
        raise DataError("GARAGE table must list each of the 22 models exactly once")
    rides = [g[2] for g in GARAGE]
    garage_rows = [[f"[{m}]({STORY_DIR}/{by_model[m]['txt']})", what, ride] for m, what, ride, _ in GARAGE]
    garage_section = (
        "## What Dale does at the garage\n\n"
        "The brief sets up a choice at the garage that puts Dale's ride home at risk, but leaves the choice open. "
        "This is what each model decided, summarised from each story's ending.\n\n"
        + md_table(["Model", "What Dale does", "His ride home"], garage_rows, ["---", "---", "---"])
        + "\n\nAcross the 22:\n\n"
        f"- Dale misses his ride in {rides.count('Missed')} stories and makes it in {rides.count('Makes it')}. "
        f"{rides.count('Left open')} leave it open.\n"
        f"- In {sum(g[3] for g in GARAGE)} stories he pays for Ana's way out with his own money, usually money "
        "that already had a job: his daughter's driving test or birthday, his rent, the car, the tire money.\n"
        "- None of the 22 has Dale simply let them off and go home.\n\n"
    )
    brief_quote = "\n".join("> " + line if line else ">" for line in prompt["brief"].split("\n"))
    trait_names = [t["name"] for t in traits]
    trait_rows = [[e["rank"], f"[{e['model']}]({STORY_DIR}/{e['txt']})"]
                  + [int(x) for x in e["trait_medians"]] + [f"**{e['median']}**"] for e in entries]
    trait_table = md_table(["Rank", "Model"] + trait_names + ["Median total (/440)"], trait_rows,
                           ["--:", "---"] + ["--:"] * (N_TRAITS + 1))
    trait_section = (
        "## Scores by trait\n\n"
        f"The median of the {n_word} judges' scores for each trait, out of 20. Higher is better on every trait, "
        "including the nine flaw traits from Meandering to Unearned Transformations, where a high score means the flaw is absent. "
        f"The median total is out of {MAX_TOTAL}. The per-judge scores are in the judgment files.\n\n"
        + trait_table + "\n"
    )
    readme = f"""# One brief, 22 models: a blind short-fiction comparison

I gave 22 AI models the same literary short-story brief and then had {n_word} AI judges score the stories blind, with model names removed. Each model got one shot and no edits. The brief is a Hamilton, Ontario bus driver on the last three hours of a February night shift, with a few fixed details every story had to include: a ticking heater, a repossessed car that he hasn't told anyone about, a dispatcher's routine schedule changes, a mother and son who board at the hospital, and a choice at the garage that puts his ride home at risk.

The aim is to show what the models wrote, side by side, so you can judge for yourself. Read the stories first if you like, then compare your view with the judges'.

- **Stories:** [Stories/](Stories/), one plain-text file per model.
- **Judgments:** [LLM Judgement/](LLM%20Judgement/), one folder per model with one file per judge.
- **Medians and explanations:** [LLM Judgement/median-scores.md]({JUDGE_URL}/{AVERAGES_FILE}).

## The brief

This is the prompt every model received, word for word. It is also in [brief.md](brief.md) and at the top of the [judge prompt](judge_prompt.md).

{brief_quote}

## Method

- **One brief, one shot.** Every model got the same brief, word for word, with no edits. It is reproduced below.
- **{n_word_cap} blind judges.** Each judge scored all 22 stories on 22 traits (dialogue, subtext, pacing, POV, brief adherence, cliché avoidance and so on). Each trait is out of 20, so a total is out of 440. Model names were removed. The traits are adapted from the rubric used in [EQ-Bench Creative Writing v3](https://eqbench.com/creative_writing.html). The full prompt and rubric are in [judge_prompt.md](judge_prompt.md) and [rubric.md](rubric.md). {extra_note}
- **Checked.** Every judge's arithmetic was checked against its own trait scores, and every quote the judges used was checked against its story. Errors were sent back for correction. `scripts/build.py` repeats these checks on every build.

{garage_section}## Leaderboard

Click a model to read its story. Each category is the median of the {n_word} judges' scores, out of 20. Higher is better in every column, including the flaw categories from Meandering to Unearned Transformations. The total is the median of the {n_word} judges' totals, out of 440, so one extreme judge can't move a model far. Ties share a rank.

{trait_table}

{top_line} The full breakdown, including how each judge ranked the models and where the judges disagreed, is in [median-scores.md]({JUDGE_URL}/{AVERAGES_FILE}), with each judge's total linked to its full judgment.

## Limitations

- **The judges are AI.** They followed the rubric, but they can't tell you whether a story moved a person. Their scores are one reference point.
- **The judges disagreed, sometimes widely.** Meta Wonder got 412 from one judge and 326 from another; Sonnet 4.5 ranged from 251 to 355. No single score settles anything.
- **{sj['name']} was both a judge and a contestant.** Judging blind, it gave its own story [{se['totals'][sj['header']]}]({JUDGE_URL}/{se['stem']}/{sj['slug']}.md), {self_gap} points above that story's {n_word}-judge median of {se['median']}. Fable 5.2 judged and Fable 5.1 competed, but those are different models.
- **One story per model, one run each.** A second run could reorder the table. Ranks 3 to 5 are {spread} points apart ({within[0]['model']} to {within[-1]['model']}), so the order in the middle is less certain.
- **One brief.** Literary realism with fixed details. Other genres or looser prompts might come out differently.

Human readers are the missing piece. If you read some of the stories, I'd like to know which you'd rank highest, where you disagree with the judges, and what would make a comparison like this more useful. Open an issue on this repo to share.

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
- [LLM Judgement/median-scores.md]({JUDGE_URL}/{AVERAGES_FILE}): medians, judge spread, rankings by judge, and each model's strongest and weakest traits
- Raw data:
  - [data/totals.csv](data/totals.csv): one row per model, with word count, each judge's total, the median, the mean and the rank
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
