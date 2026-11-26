# One brief, 22 models: a blind short-fiction comparison

I gave 22 AI models the same literary short-story brief and then had four AI judges score the stories blind, with model names removed. Each model got one shot and no edits. The brief is a Hamilton, Ontario bus driver on the last three hours of a February night shift, with a few fixed details every story had to include: a ticking heater, a repossessed car that he hasn't told anyone about, a dispatcher's routine schedule changes, a mother and son who board at the hospital, and a choice at the garage that puts his ride home at risk.

The aim is to show what the models wrote, side by side, so you can judge for yourself. Read the stories first if you like, then compare your view with the judges'.

- **Stories:** [Stories/](Stories/), one plain-text file per model.
- **Judgments:** [LLM Judgement/](LLM%20Judgement/), one folder per model with one file per judge.
- **Averages and explanations:** [LLM Judgement/average-scores.md](LLM%20Judgement/average-scores.md).

## The brief

This is the prompt every model received, word for word. It is also in [brief.md](brief.md) and at the top of the [judge prompt](judge_prompt.md).

> Write a literary short story of 1,700–2,300 words.
>
> Dale Varga has driven a city bus in Hamilton, Ontario, for eleven years. It is Thursday, 19 February. A thaw has melted the snow during the day, and by evening it is freezing again. The story covers the last three hours of his shift, on a route that ends at the east-side garage.
>
> In October, Dale's car was repossessed. He hasn't told Carla, the tired, practical dispatcher he talks to over the radio, or his adult daughter. He now depends on catching a late bus home after he finishes at the garage.
>
> At the hospital stop, Ana Ruiz boards with her four-year-old son, Theo, and a duffel bag. She says she's going to her sister's, but she's vague about where. She keeps checking her phone. The bus reaches the garage with Ana and Theo still on board.
>
> Include these details: the bus heater ticks, Carla calls in with routine schedule changes, and Dale has to make a choice at the garage that puts his ride home at risk.
>
> Dialogue should sound natural. Don't explain the characters' feelings; let actions and details carry them. The ending should be earned and shouldn't tie everything up.

## Method

- **One brief, one shot.** Every model got the same brief, word for word, with no edits. It is reproduced below.
- **Four blind judges.** Each judge scored all 22 stories on 22 traits (dialogue, subtext, pacing, POV, brief adherence, cliché avoidance and so on). Each trait is out of 20, so a total is out of 440. Model names were removed. The traits are adapted from the rubric used in [EQ-Bench Creative Writing v3](https://eqbench.com/creative_writing.html). The full prompt and rubric are in [judge_prompt.md](judge_prompt.md) and [rubric.md](rubric.md).
- **Checked.** Every judge's arithmetic was checked against its own trait scores, and every quote the judges used was checked against its story. Errors were sent back for correction. `scripts/build.py` repeats these checks on every build.

## Leaderboard

Click a model to read its story, or a score to see that judge's trait scores and commentary. Ties share a rank. The average is the mean of the four judges' totals.

| Rank | Model | Gemini Hydrogen | GLM 5.3 | Meta Muse Spark 1.3 | Fable 5.2 | Average |
|--:|---|--:|--:|--:|--:|--:|
| 1 | [Astra 6.2](Stories/01-astra-6-2.txt) | [424](LLM%20Judgement/01-astra-6-2/gemini-hydrogen.md) | [411](LLM%20Judgement/01-astra-6-2/glm-5-3.md) | [400](LLM%20Judgement/01-astra-6-2/meta-muse-spark-1-3.md) | [416](LLM%20Judgement/01-astra-6-2/fable-5-2.md) | **412.8** |
| 2 | [6.2 Sol](Stories/02-6-2-sol.txt) | [414](LLM%20Judgement/02-6-2-sol/gemini-hydrogen.md) | [396](LLM%20Judgement/02-6-2-sol/glm-5-3.md) | [390](LLM%20Judgement/02-6-2-sol/meta-muse-spark-1-3.md) | [415](LLM%20Judgement/02-6-2-sol/fable-5-2.md) | **403.8** |
| 3 | [Opus 5.5](Stories/03-opus-5-5.txt) | [385](LLM%20Judgement/03-opus-5-5/gemini-hydrogen.md) | [396](LLM%20Judgement/03-opus-5-5/glm-5-3.md) | [385](LLM%20Judgement/03-opus-5-5/meta-muse-spark-1-3.md) | [402](LLM%20Judgement/03-opus-5-5/fable-5-2.md) | **392.0** |
| 4 | [GLM 5.3](Stories/04-glm-5-3.txt) | [399](LLM%20Judgement/04-glm-5-3/gemini-hydrogen.md) | [403](LLM%20Judgement/04-glm-5-3/glm-5-3.md) | [378](LLM%20Judgement/04-glm-5-3/meta-muse-spark-1-3.md) | [387](LLM%20Judgement/04-glm-5-3/fable-5-2.md) | **391.8** |
| 5 | [Fable 5.1](Stories/05-fable-5-1.txt) | [390](LLM%20Judgement/05-fable-5-1/gemini-hydrogen.md) | [408](LLM%20Judgement/05-fable-5-1/glm-5-3.md) | [374](LLM%20Judgement/05-fable-5-1/meta-muse-spark-1-3.md) | [391](LLM%20Judgement/05-fable-5-1/fable-5-2.md) | **390.8** |
| 6 | [Sonnet 5.5](Stories/06-sonnet-5-5.txt) | [392](LLM%20Judgement/06-sonnet-5-5/gemini-hydrogen.md) | [398](LLM%20Judgement/06-sonnet-5-5/glm-5-3.md) | [357](LLM%20Judgement/06-sonnet-5-5/meta-muse-spark-1-3.md) | [401](LLM%20Judgement/06-sonnet-5-5/fable-5-2.md) | **387.0** |
| 7 | [GPT 6.1 Sol](Stories/07-gpt-6-1-sol.txt) | [378](LLM%20Judgement/07-gpt-6-1-sol/gemini-hydrogen.md) | [385](LLM%20Judgement/07-gpt-6-1-sol/glm-5-3.md) | [388](LLM%20Judgement/07-gpt-6-1-sol/meta-muse-spark-1-3.md) | [392](LLM%20Judgement/07-gpt-6-1-sol/fable-5-2.md) | **385.8** |
| 8 | [GPT-6 Astra](Stories/08-gpt-6-astra.txt) | [380](LLM%20Judgement/08-gpt-6-astra/gemini-hydrogen.md) | [397](LLM%20Judgement/08-gpt-6-astra/glm-5-3.md) | [368](LLM%20Judgement/08-gpt-6-astra/meta-muse-spark-1-3.md) | [388](LLM%20Judgement/08-gpt-6-astra/fable-5-2.md) | **383.2** |
| 9 | [Kimi K3.1 Pro](Stories/09-kimi-k3-1-pro.txt) | [384](LLM%20Judgement/09-kimi-k3-1-pro/gemini-hydrogen.md) | [389](LLM%20Judgement/09-kimi-k3-1-pro/glm-5-3.md) | [355](LLM%20Judgement/09-kimi-k3-1-pro/meta-muse-spark-1-3.md) | [372](LLM%20Judgement/09-kimi-k3-1-pro/fable-5-2.md) | **375.0** |
| 10 | [DeepSeek 4.1 Flash](Stories/10-deepseek-4-1-flash.txt) | [383](LLM%20Judgement/10-deepseek-4-1-flash/gemini-hydrogen.md) | [406](LLM%20Judgement/10-deepseek-4-1-flash/glm-5-3.md) | [340](LLM%20Judgement/10-deepseek-4-1-flash/meta-muse-spark-1-3.md) | [356](LLM%20Judgement/10-deepseek-4-1-flash/fable-5-2.md) | **371.2** |
| 11 | [Meta Wonder](Stories/11-meta-wonder.txt) | [412](LLM%20Judgement/11-meta-wonder/gemini-hydrogen.md) | [383](LLM%20Judgement/11-meta-wonder/glm-5-3.md) | [326](LLM%20Judgement/11-meta-wonder/meta-muse-spark-1-3.md) | [360](LLM%20Judgement/11-meta-wonder/fable-5-2.md) | **370.2** |
| 12 | [GPT 5.6 Sol](Stories/12-gpt-5-6-sol.txt) | [369](LLM%20Judgement/12-gpt-5-6-sol/gemini-hydrogen.md) | [364](LLM%20Judgement/12-gpt-5-6-sol/glm-5-3.md) | [364](LLM%20Judgement/12-gpt-5-6-sol/meta-muse-spark-1-3.md) | [369](LLM%20Judgement/12-gpt-5-6-sol/fable-5-2.md) | **366.5** |
| 13 | [Gemini Argon](Stories/13-gemini-argon.txt) | [359](LLM%20Judgement/13-gemini-argon/gemini-hydrogen.md) | [380](LLM%20Judgement/13-gemini-argon/glm-5-3.md) | [360](LLM%20Judgement/13-gemini-argon/meta-muse-spark-1-3.md) | [311](LLM%20Judgement/13-gemini-argon/fable-5-2.md) | **352.5** |
| 14 | [Gemini Neon](Stories/14-gemini-neon.txt) | [359](LLM%20Judgement/14-gemini-neon/gemini-hydrogen.md) | [373](LLM%20Judgement/14-gemini-neon/glm-5-3.md) | [338](LLM%20Judgement/14-gemini-neon/meta-muse-spark-1-3.md) | [334](LLM%20Judgement/14-gemini-neon/fable-5-2.md) | **351.0** |
| 14 | [Opus 4.6 Max](Stories/14-opus-4-6-max.txt) | [361](LLM%20Judgement/14-opus-4-6-max/gemini-hydrogen.md) | [369](LLM%20Judgement/14-opus-4-6-max/glm-5-3.md) | [346](LLM%20Judgement/14-opus-4-6-max/meta-muse-spark-1-3.md) | [328](LLM%20Judgement/14-opus-4-6-max/fable-5-2.md) | **351.0** |
| 16 | [GPT 5.5](Stories/16-gpt-5-5.txt) | [392](LLM%20Judgement/16-gpt-5-5/gemini-hydrogen.md) | [377](LLM%20Judgement/16-gpt-5-5/glm-5-3.md) | [330](LLM%20Judgement/16-gpt-5-5/meta-muse-spark-1-3.md) | [301](LLM%20Judgement/16-gpt-5-5/fable-5-2.md) | **350.0** |
| 17 | [GPT 6 Sol](Stories/17-gpt-6-sol.txt) | [357](LLM%20Judgement/17-gpt-6-sol/gemini-hydrogen.md) | [364](LLM%20Judgement/17-gpt-6-sol/glm-5-3.md) | [350](LLM%20Judgement/17-gpt-6-sol/meta-muse-spark-1-3.md) | [327](LLM%20Judgement/17-gpt-6-sol/fable-5-2.md) | **349.5** |
| 18 | [Luna 6](Stories/18-luna-6.txt) | [327](LLM%20Judgement/18-luna-6/gemini-hydrogen.md) | [354](LLM%20Judgement/18-luna-6/glm-5-3.md) | [310](LLM%20Judgement/18-luna-6/meta-muse-spark-1-3.md) | [306](LLM%20Judgement/18-luna-6/fable-5-2.md) | **324.2** |
| 19 | [Meta Ember](Stories/19-meta-ember.txt) | [351](LLM%20Judgement/19-meta-ember/gemini-hydrogen.md) | [355](LLM%20Judgement/19-meta-ember/glm-5-3.md) | [298](LLM%20Judgement/19-meta-ember/meta-muse-spark-1-3.md) | [266](LLM%20Judgement/19-meta-ember/fable-5-2.md) | **317.5** |
| 20 | [Sonnet 4.5](Stories/20-sonnet-4-5.txt) | [251](LLM%20Judgement/20-sonnet-4-5/gemini-hydrogen.md) | [355](LLM%20Judgement/20-sonnet-4-5/glm-5-3.md) | [273](LLM%20Judgement/20-sonnet-4-5/meta-muse-spark-1-3.md) | [258](LLM%20Judgement/20-sonnet-4-5/fable-5-2.md) | **284.2** |
| 21 | [Mistral Large 4](Stories/21-mistral-large-4.txt) | [296](LLM%20Judgement/21-mistral-large-4/gemini-hydrogen.md) | [295](LLM%20Judgement/21-mistral-large-4/glm-5-3.md) | [254](LLM%20Judgement/21-mistral-large-4/meta-muse-spark-1-3.md) | [206](LLM%20Judgement/21-mistral-large-4/fable-5-2.md) | **262.8** |
| 22 | [Mistral Small 4](Stories/22-mistral-small-4.txt) | [150](LLM%20Judgement/22-mistral-small-4/gemini-hydrogen.md) | [274](LLM%20Judgement/22-mistral-small-4/glm-5-3.md) | [196](LLM%20Judgement/22-mistral-small-4/meta-muse-spark-1-3.md) | [150](LLM%20Judgement/22-mistral-small-4/fable-5-2.md) | **192.5** |

Astra 6.2 came first with all four judges. The full breakdown, including how each judge ranked the models and where the judges disagreed, is in [average-scores.md](LLM%20Judgement/average-scores.md).

## Caveats

- **One story per model, one run each.** This is a snapshot, not a benchmark. A second run could reorder the table.
- **GLM 5.3 was both a judge and a contestant.** Judging blind, it gave its own story [403](LLM%20Judgement/04-glm-5-3/glm-5-3.md), about 11 points above that story's four-judge average of 391.8. Fable 5.2 judged and Fable 5.1 competed, but those are different models.
- **The judges sometimes disagreed widely.** Meta Wonder got 412 from one judge and 326 from another. Sonnet 4.5 ranged from 251 to 355.
- **Ranks 3 to 5 are within about a point** (Opus 5.5 to Fable 5.1: 1.2 points apart). Read them as tied.

## What the models wrote

These tables quote each model's own choices on the same moment. Each quote was checked against its story.

### The heater ticks

Every model had to include a ticking heater. Some gave the tick a mechanical cause (a bent fin, a fault Dale had reported); others used a simile. One model, Mistral Small 4, has the heater click like a metronome and then fall silent.

| Model | The heater |
|---|---|
| [Sonnet 4.5](Stories/20-sonnet-4-5.txt) | “The heater ticked like a cooling engine.” |
| [GLM 5.3](Stories/04-glm-5-3.txt) | “the heater under the front bench went on ticking the way it had for three days now, steady as a clock with nowhere to be.” |
| [Opus 4.6 Max](Stories/14-opus-4-6-max.txt) | “a metallic knock every eight or nine seconds that Dale couldn't fix and couldn't stop hearing.” |
| [Gemini Argon](Stories/13-gemini-argon.txt) | “the defroster fan under Dale's left knee kept up its dry, rhythmic tick—a bent fin catching the housing every third revolution.” |
| [Meta Wonder](Stories/11-meta-wonder.txt) | “The heater under Dale's left foot ticked, stopped, ticked again.” |
| [DeepSeek 4.1 Flash](Stories/10-deepseek-4-1-flash.txt) | “Under the dash the heater ticked, ticked, ticked, a small hard noise with a wrongness in it he had reported twice.” |
| [Fable 5.1](Stories/05-fable-5-1.txt) | “the heater under the dash kept ticking the way it did, the metal cooling” |
| [GPT-6 Astra](Stories/08-gpt-6-astra.txt) | “At nine fourteen, the heater began ticking again.” |

### The repossession

The brief only says "in October, Dale's car was repossessed." Some models stated it in a single flat line. Others tied it to a physical detail Dale carries around: the winter tires still in his locker, the socks on the step, the half-written texts he keeps deleting.

| Model | How it comes out |
|---|---|
| [GLM 5.3](Stories/04-glm-5-3.txt) | “In October two men had taken the Corolla out of the visitor spot at his building at ten to five in the morning, and he had watched from the kitchen window in his coat, coffee in his hand, and said nothing to anyone.” |
| [Opus 5.5](Stories/03-opus-5-5.txt) | “a man with a clipboard and a tow truck took the Ranger out of the lot behind his building at six in the morning while Dale stood on the step in his socks.” |
| [GPT 5.5](Stories/16-gpt-5-5.txt) | “The tow truck had come in October, before sunrise, polite as a funeral director.” |
| [Gemini Neon](Stories/14-gemini-neon.txt) | “The repo truck had taken the car in October while it was still on all-seasons, leaving the winters stacked on steel rims in the basement locker.” |
| [Kimi K3.1 Pro](Stories/09-kimi-k3-1-pro.txt) | “The Volkswagen had been taken away in October.” |
| [DeepSeek 4.1 Flash](Stories/10-deepseek-4-1-flash.txt) | “The car had gone back in October and he hadn't told Carla or his daughter.” |
| [6.2 Sol](Stories/02-6-2-sol.txt) | “He'd been deleting little bits of sentences since October, when the finance company sent a man for the Pontiac.” |
| [Luna 6](Stories/18-luna-6.txt) | “The repossession had happened in October, while he was at the dentist.” |

### The opening

The brief describes a thaw that freezes again by evening. Four stories open with some version of "By nine (o'clock)."

| Model | First sentence |
|---|---|
| [GPT 5.5](Stories/16-gpt-5-5.txt) | “On Thursday, the nineteenth of February, Hamilton looked rinsed and left in the freezer.” |
| [DeepSeek 4.1 Flash](Stories/10-deepseek-4-1-flash.txt) | “The thaw had broken around suppertime, and by nine the nineteenth had turned back into February.” |
| [Gemini Neon](Stories/14-gemini-neon.txt) | “By nine o'clock the afternoon thaw had turned back into iron.” |
| [Sonnet 5.5](Stories/06-sonnet-5-5.txt) | “By nine o'clock the thaw had quit.” |
| [Luna 6](Stories/18-luna-6.txt) | “By nine o'clock, the thaw had turned the streets of Hamilton into a long, dirty reflection.” |
| [Mistral Small 4](Stories/22-mistral-small-4.txt) | “The thaw had turned the streets to slush, and the windshield wipers were fighting a losing battle.” |
| [6.2 Sol](Stories/02-6-2-sol.txt) | “At a quarter to nine on Thursday, February 19, Dale Varga took over a bus with a full tank and a wet seat.” |
| [Meta Ember](Stories/19-meta-ember.txt) | “Dale Varga was forty-seven and in his eleventh year with the city, and on Thursday, February 19, he had the 20 for the last three hours of his shift, eastbound from downtown to the garage on the east side.” |

### The ending

The brief says the ending "shouldn't tie everything up." Look at what each ending is built on: a small physical action (the clipboard, the hand on the quarter, the meter), a line of dialogue, or a feeling stated outright.

| Model | Last line |
|---|---|
| [Astra 6.2](Stories/01-astra-6-2.txt) | “Dale lifted the clipboard so the boy could brush them into his palm.” |
| [6.2 Sol](Stories/02-6-2-sol.txt) | “Theo slapped his other hand down on it.” |
| [GPT 5.6 Sol](Stories/12-gpt-5-6-sol.txt) | “On the meter, $4.75 appeared, held for a moment, then climbed.” |
| [GPT-6 Astra](Stories/08-gpt-6-astra.txt) | “"Got it," she said.” |
| [GLM 5.3](Stories/04-glm-5-3.txt) | “and at Lottridge the light went green for nobody and he crossed on it anyway.” |
| [GPT 6 Sol](Stories/17-gpt-6-sol.txt) | “Behind the office glass, Ana shifted the phone to her other ear and tucked Theo's hat under his chin.” |
| [Mistral Large 4](Stories/21-mistral-large-4.txt) | “He turned the key.” |
| [Mistral Small 4](Stories/22-mistral-small-4.txt) | “The twenty in his pocket burned.” |
| [Sonnet 4.5](Stories/20-sonnet-4-5.txt) | “and somewhere in the building, someone laughed, the sound carried on the wind like smoke.” |

## What kept showing up

None of these were in the brief.

- **Titles:** 11 of 22 titles contain "Last". Three stories are called *The Last Stop* and two *The Last Pull-In*.
- **The car:** a Honda Civic appears in 7 stories. The brief never names the car.
- **Dinosaurs:** in 6 stories, Theo talks about dinosaurs.
- **Tim Hortons** appears in 6 stories.
- **The walk home:** 4 stories have Dale set off west on foot.

When models write the same brief, they converge. If you use one of these for fiction, these are the defaults to watch for in your own drafts.

## Following the length limit

The brief asked for 1,700–2,300 words. Counts are whitespace splits, title included.

- **Inside the range:** 15 of 22.
- **Over:** 5. Gemini Neon (3,670), Gemini Argon (3,638), Meta Wonder (3,544), GPT 5.5 (3,448), Luna 6 (3,300). All ran 1,000+ words past the ceiling.
- **Under:** 2. Mistral Small 4 (1,116), Mistral Large 4 (1,675).

The overruns weren't small, and several of the over-length stories still scored well on the craft traits. Length was what pulled them down.

## The materials

- [The brief](brief.md): the prompt every model received
- [The rubric](rubric.md): the 22 traits, including which are negative traits
- [The judge prompt](judge_prompt.md): the full prompt each judge received
- [Stories/](Stories/): all 22 stories, one plain-text file per model, named by rank and model
- [LLM Judgement/](LLM%20Judgement/): one folder per model, with one file per judge inside
- [LLM Judgement/average-scores.md](LLM%20Judgement/average-scores.md): averages, judge spread, rankings by judge, and each model's strongest and weakest traits
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
