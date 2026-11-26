# One brief, 22 models: a blind short-fiction comparison

I gave 22 AI models the same literary short-story brief and then had five AI judges score the stories blind, with model names removed. Each model got one shot and no edits. The brief is a Hamilton, Ontario bus driver on the last three hours of a February night shift, with a few fixed details every story had to include: a ticking heater, a repossessed car that he hasn't told anyone about, a dispatcher's routine schedule changes, a mother and son who board at the hospital, and a choice at the garage that puts his ride home at risk.

The aim is to show what the models wrote, side by side, so you can judge for yourself. Read the stories first if you like, then compare your view with the judges'.

- **Stories:** [Stories/](Stories/), one plain-text file per model.
- **Judgments:** [LLM Judgement/](LLM%20Judgement/), one folder per model with one file per judge.
- **Medians and explanations:** [LLM Judgement/median-scores.md](LLM%20Judgement/median-scores.md).

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
- **Five blind judges.** Each judge scored all 22 stories on 22 traits (dialogue, subtext, pacing, POV, brief adherence, cliché avoidance and so on). Each trait is out of 20, so a total is out of 440. Model names were removed. The traits are adapted from the rubric used in [EQ-Bench Creative Writing v3](https://eqbench.com/creative_writing.html). The full prompt and rubric are in [judge_prompt.md](judge_prompt.md) and [rubric.md](rubric.md). Qwen 4 Max was added as a fifth judge after the first four, using the same judge prompt; its full evaluation is in [source/qwen-4-max_evaluation.md](source/qwen-4-max_evaluation.md).
- **Checked.** Every judge's arithmetic was checked against its own trait scores, and every quote the judges used was checked against its story. Errors were sent back for correction. `scripts/build.py` repeats these checks on every build.

## What Dale does at the garage

The brief sets up a choice at the garage that puts Dale's ride home at risk, but leaves the choice open. This is what each model decided, summarised from each story's ending.

| Model | What Dale does | His ride home |
|---|---|---|
| [6.2 Sol](Stories/02-6-2-sol.txt) | Stays with them in the garage vestibule while Ana makes a call, then books himself a $38.60 cab | Missed |
| [Astra 6.2](Stories/01-astra-6-2.txt) | Signs them in as visitors and sits with them in the office while Ana calls her sister | Missed |
| [DeepSeek 4.1 Flash](Stories/10-deepseek-4-1-flash.txt) | Leaves the bus, walks them to a Tim Hortons, pays $40 for a cab to a shelter. Gets a three-day suspension | Missed |
| [Fable 5.1](Stories/05-fable-5-1.txt) | Gives Ana $63, nearly all the money he has, for a cab | Makes it |
| [Gemini Argon](Stories/14-gemini-argon.txt) | Sends them by taxi to a shelter he knows | Missed |
| [Gemini Neon](Stories/16-gemini-neon.txt) | Pays for their cab with the cash from selling his repossessed Civic's winter tires | Missed |
| [GLM 5.3](Stories/08-glm-5-3.txt) | Calls a cab, gives Ana his cash and his fare card | Missed |
| [GPT 5.5](Stories/17-gpt-5-5.txt) | Drives the out-of-service bus downtown to a shelter | Missed |
| [GPT 5.6 Sol](Stories/12-gpt-5-6-sol.txt) | Waits with them for an arranged cab, tells Carla "My car's here," then pays $51.60 for his own taxi | Missed |
| [GPT 6 Sol](Stories/15-gpt-6-sol.txt) | Gets them into the garage office to call an intake line, then books himself a $41.60 taxi | Missed |
| [GPT 6.1 Sol](Stories/06-gpt-6-1-sol.txt) | Waits with them in the staff vestibule until a housing van comes, lends Ana his power bank | Missed |
| [GPT-6 Astra](Stories/06-gpt-6-astra.txt) | Pays $55 for one cab: family intake office first, then his place | Missed |
| [Kimi K3.1 Pro](Stories/09-kimi-k3-1-pro.txt) | Pays for a cab and a motel room from a pay envelope marked CAR, then tells his daughter the truth | Missed |
| [Luna 6](Stories/18-luna-6.txt) | Carries Theo into the garage's security office while help is arranged | Left open |
| [Meta Ember](Stories/19-meta-ember.txt) | Lets them slip out through the maintenance gate without telling anyone | Missed |
| [Meta Wonder](Stories/11-meta-wonder.txt) | Tells Carla the bus is empty, walks them out the pedestrian gate, pays $45 of his rent money for a cab | Missed |
| [Mistral Large 4](Stories/20-mistral-large-4.txt) | Pays the cab fare from the money he was saving to get his car back | Missed |
| [Mistral Small 4](Stories/22-mistral-small-4.txt) | Holds a $20 bill for Ana, then drives the bus back out to look for her | Doesn't go home |
| [Opus 4.6 Max](Stories/13-opus-4-6-max.txt) | Waits with them and pays $30 for their cab | Left open |
| [Opus 5.5](Stories/04-opus-5-5.txt) | Gives Ana the $60 he'd set aside for his daughter's driving test | Missed |
| [Sonnet 4.5](Stories/21-sonnet-4-5.txt) | Has dispatch call a cab and pays for it himself | Left open |
| [Sonnet 5.5](Stories/03-sonnet-5-5.txt) | Pays $50 for their cab, money meant for his daughter's birthday card | Missed |

Across the 22:

- Dale misses his ride in 17 stories and makes it in 1. 3 leave it open.
- In 12 stories he pays for Ana's way out with his own money, usually money that already had a job: his daughter's driving test or birthday, his rent, the car, the tire money.
- None of the 22 has Dale simply let them off and go home.

## Leaderboard

Click a model to read its story. Each category is the median of the five judges' scores, out of 20. Higher is better in every column, including the flaw categories from Meandering to Unearned Transformations. The total is the median of the five judges' totals, out of 440, so one extreme judge can't move a model far. Ties share a rank.

| Rank | Model | Adherence to Instructions | Believable Character Actions | Nuanced Characters | Consistent Voice/Tone of Writing | Imagery and Descriptive Quality | Elegant Prose | Emotionally Engaging | Emotionally Complex | Coherent | Meandering | Weak Dialogue | Tell-Don't-Show | Unsurprising or Uncreative | Amateurish | Purple Prose | Overwrought | Incongruent Ending Positivity | Unearned Transformations | Well-earned Lightness or Darkness | Sentences Flow Naturally | Overall Reader Engagement | Overall Impression | Median total (/440) |
|--:|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| 1 | [Astra 6.2](Stories/01-astra-6-2.txt) | 19 | 19 | 19 | 19 | 19 | 19 | 18 | 19 | 19 | 19 | 19 | 19 | 18 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 18 | 19 | **412** |
| 2 | [6.2 Sol](Stories/02-6-2-sol.txt) | 19 | 19 | 18 | 19 | 18 | 19 | 18 | 18 | 18 | 18 | 19 | 19 | 18 | 19 | 20 | 19 | 18 | 19 | 19 | 19 | 18 | 19 | **411** |
| 3 | [Sonnet 5.5](Stories/03-sonnet-5-5.txt) | 18 | 18 | 18 | 18 | 17 | 18 | 18 | 18 | 18 | 18 | 18 | 18 | 17 | 18 | 18 | 18 | 18 | 18 | 18 | 18 | 18 | 18 | **398** |
| 4 | [Opus 5.5](Stories/04-opus-5-5.txt) | 17 | 18 | 18 | 18 | 18 | 17 | 17 | 17 | 18 | 18 | 18 | 17 | 17 | 18 | 19 | 18 | 18 | 18 | 18 | 18 | 18 | 18 | **393** |
| 5 | [Fable 5.1](Stories/05-fable-5-1.txt) | 17 | 18 | 18 | 18 | 17 | 18 | 18 | 17 | 18 | 18 | 18 | 17 | 17 | 18 | 19 | 18 | 17 | 18 | 17 | 18 | 17 | 17 | **390** |
| 6 | [GPT 6.1 Sol](Stories/06-gpt-6-1-sol.txt) | 19 | 18 | 17 | 18 | 17 | 17 | 16 | 17 | 18 | 18 | 18 | 18 | 16 | 18 | 19 | 19 | 18 | 18 | 17 | 18 | 16 | 17 | **388** |
| 6 | [GPT-6 Astra](Stories/06-gpt-6-astra.txt) | 19 | 18 | 17 | 18 | 18 | 17 | 17 | 16 | 18 | 17 | 18 | 18 | 16 | 18 | 19 | 19 | 18 | 18 | 17 | 17 | 16 | 17 | **388** |
| 8 | [GLM 5.3](Stories/08-glm-5-3.txt) | 18 | 18 | 18 | 18 | 18 | 17 | 18 | 18 | 18 | 17 | 18 | 17 | 17 | 18 | 19 | 18 | 18 | 18 | 18 | 18 | 18 | 17 | **387** |
| 9 | [Kimi K3.1 Pro](Stories/09-kimi-k3-1-pro.txt) | 19 | 18 | 17 | 18 | 17 | 17 | 18 | 17 | 18 | 17 | 17 | 17 | 16 | 18 | 18 | 18 | 17 | 17 | 18 | 18 | 17 | 17 | **384** |
| 10 | [DeepSeek 4.1 Flash](Stories/10-deepseek-4-1-flash.txt) | 17 | 17 | 17 | 18 | 17 | 17 | 17 | 17 | 17 | 18 | 17 | 17 | 17 | 18 | 18 | 18 | 18 | 18 | 18 | 18 | 17 | 17 | **383** |
| 11 | [Meta Wonder](Stories/11-meta-wonder.txt) | 10 | 18 | 18 | 18 | 18 | 17 | 18 | 18 | 16 | 14 | 18 | 17 | 16 | 18 | 18 | 17 | 18 | 18 | 18 | 17 | 17 | 17 | **374** |
| 12 | [GPT 5.6 Sol](Stories/12-gpt-5-6-sol.txt) | 18 | 17 | 16 | 17 | 16 | 16 | 16 | 16 | 17 | 16 | 17 | 16 | 15 | 17 | 18 | 18 | 17 | 17 | 17 | 17 | 16 | 16 | **369** |
| 13 | [Opus 4.6 Max](Stories/13-opus-4-6-max.txt) | 17 | 17 | 16 | 17 | 16 | 16 | 15 | 15 | 17 | 16 | 17 | 17 | 14 | 17 | 19 | 18 | 17 | 18 | 16 | 17 | 15 | 16 | **361** |
| 14 | [Gemini Argon](Stories/14-gemini-argon.txt) | 9 | 17 | 17 | 17 | 18 | 17 | 17 | 17 | 16 | 13 | 17 | 15 | 16 | 17 | 17 | 16 | 18 | 18 | 17 | 17 | 17 | 16 | **360** |
| 15 | [GPT 6 Sol](Stories/15-gpt-6-sol.txt) | 18 | 17 | 16 | 17 | 16 | 16 | 15 | 15 | 17 | 16 | 16 | 16 | 14 | 17 | 19 | 18 | 17 | 18 | 16 | 16 | 15 | 16 | **357** |
| 16 | [Gemini Neon](Stories/16-gemini-neon.txt) | 9 | 17 | 17 | 17 | 17 | 16 | 17 | 16 | 17 | 13 | 17 | 15 | 15 | 16 | 18 | 17 | 18 | 18 | 17 | 17 | 15 | 16 | **351** |
| 17 | [GPT 5.5](Stories/17-gpt-5-5.txt) | 9 | 15 | 16 | 16 | 17 | 16 | 17 | 16 | 16 | 13 | 17 | 15 | 14 | 14 | 17 | 15 | 17 | 18 | 16 | 17 | 16 | 14 | **330** |
| 18 | [Luna 6](Stories/18-luna-6.txt) | 10 | 16 | 15 | 16 | 16 | 15 | 15 | 15 | 16 | 12 | 15 | 15 | 13 | 15 | 18 | 17 | 17 | 17 | 15 | 15 | 14 | 14 | **327** |
| 19 | [Meta Ember](Stories/19-meta-ember.txt) | 15 | 15 | 15 | 15 | 15 | 14 | 14 | 15 | 14 | 15 | 15 | 13 | 14 | 13 | 16 | 17 | 17 | 17 | 15 | 14 | 14 | 14 | **326** |
| 20 | [Mistral Large 4](Stories/20-mistral-large-4.txt) | 13 | 12 | 12 | 13 | 13 | 12 | 13 | 12 | 11 | 14 | 12 | 10 | 11 | 11 | 14 | 13 | 16 | 14 | 13 | 13 | 12 | 12 | **276** |
| 21 | [Sonnet 4.5](Stories/21-sonnet-4-5.txt) | 12 | 13 | 12 | 14 | 13 | 12 | 13 | 12 | 11 | 13 | 13 | 11 | 12 | 12 | 14 | 13 | 15 | 16 | 13 | 14 | 13 | 12 | **273** |
| 22 | [Mistral Small 4](Stories/22-mistral-small-4.txt) | 6 | 8 | 8 | 10 | 10 | 8 | 9 | 8 | 8 | 11 | 10 | 8 | 9 | 7 | 12 | 10 | 13 | 12 | 9 | 10 | 8 | 8 | **196** |

Astra 6.2 came first with all five judges. The full breakdown, including how each judge ranked the models and where the judges disagreed, is in [median-scores.md](LLM%20Judgement/median-scores.md), with each judge's total linked to its full judgment.

## Limitations

- **The judges are AI.** They followed the rubric, but they can't tell you whether a story moved a person. Their scores are one reference point.
- **The judges disagreed, sometimes widely.** Meta Wonder got 412 from one judge and 326 from another; Sonnet 4.5 ranged from 251 to 355. No single score settles anything.
- **GLM 5.3 was both a judge and a contestant.** Judging blind, it gave its own story [403](LLM%20Judgement/08-glm-5-3/glm-5-3.md), 16 points above that story's five-judge median of 387. Fable 5.2 judged and Fable 5.1 competed, but those are different models.
- **One story per model, one run each.** A second run could reorder the table. Ranks 3 to 5 are 8 points apart (Sonnet 5.5 to Fable 5.1), so the order in the middle is less certain.
- **One brief.** Literary realism with fixed details. Other genres or looser prompts might come out differently.

Human readers are the missing piece. If you read some of the stories, I'd like to know which you'd rank highest, where you disagree with the judges, and what would make a comparison like this more useful. Open an issue on this repo to share.

## What the models wrote

These tables quote each model's own choices on the same moment. Each quote was checked against its story.

### The heater ticks

Every model had to include a ticking heater. Some gave the tick a mechanical cause (a bent fin, a fault Dale had reported); others used a simile. One model, Mistral Small 4, has the heater click like a metronome and then fall silent.

| Model | The heater |
|---|---|
| [Sonnet 4.5](Stories/21-sonnet-4-5.txt) | “The heater ticked like a cooling engine.” |
| [GLM 5.3](Stories/08-glm-5-3.txt) | “the heater under the front bench went on ticking the way it had for three days now, steady as a clock with nowhere to be.” |
| [Opus 4.6 Max](Stories/13-opus-4-6-max.txt) | “a metallic knock every eight or nine seconds that Dale couldn't fix and couldn't stop hearing.” |
| [Gemini Argon](Stories/14-gemini-argon.txt) | “the defroster fan under Dale's left knee kept up its dry, rhythmic tick—a bent fin catching the housing every third revolution.” |
| [Meta Wonder](Stories/11-meta-wonder.txt) | “The heater under Dale's left foot ticked, stopped, ticked again.” |
| [DeepSeek 4.1 Flash](Stories/10-deepseek-4-1-flash.txt) | “Under the dash the heater ticked, ticked, ticked, a small hard noise with a wrongness in it he had reported twice.” |
| [Fable 5.1](Stories/05-fable-5-1.txt) | “the heater under the dash kept ticking the way it did, the metal cooling” |
| [GPT-6 Astra](Stories/06-gpt-6-astra.txt) | “At nine fourteen, the heater began ticking again.” |

### The repossession

The brief only says "in October, Dale's car was repossessed." Some models stated it in a single flat line. Others tied it to a physical detail Dale carries around: the winter tires still in his locker, the socks on the step, the half-written texts he keeps deleting.

| Model | How it comes out |
|---|---|
| [GLM 5.3](Stories/08-glm-5-3.txt) | “In October two men had taken the Corolla out of the visitor spot at his building at ten to five in the morning, and he had watched from the kitchen window in his coat, coffee in his hand, and said nothing to anyone.” |
| [Opus 5.5](Stories/04-opus-5-5.txt) | “a man with a clipboard and a tow truck took the Ranger out of the lot behind his building at six in the morning while Dale stood on the step in his socks.” |
| [GPT 5.5](Stories/17-gpt-5-5.txt) | “The tow truck had come in October, before sunrise, polite as a funeral director.” |
| [Gemini Neon](Stories/16-gemini-neon.txt) | “The repo truck had taken the car in October while it was still on all-seasons, leaving the winters stacked on steel rims in the basement locker.” |
| [Kimi K3.1 Pro](Stories/09-kimi-k3-1-pro.txt) | “The Volkswagen had been taken away in October.” |
| [DeepSeek 4.1 Flash](Stories/10-deepseek-4-1-flash.txt) | “The car had gone back in October and he hadn't told Carla or his daughter.” |
| [6.2 Sol](Stories/02-6-2-sol.txt) | “He'd been deleting little bits of sentences since October, when the finance company sent a man for the Pontiac.” |
| [Luna 6](Stories/18-luna-6.txt) | “The repossession had happened in October, while he was at the dentist.” |

### The opening

The brief describes a thaw that freezes again by evening. Four stories open with some version of "By nine (o'clock)."

| Model | First sentence |
|---|---|
| [GPT 5.5](Stories/17-gpt-5-5.txt) | “On Thursday, the nineteenth of February, Hamilton looked rinsed and left in the freezer.” |
| [DeepSeek 4.1 Flash](Stories/10-deepseek-4-1-flash.txt) | “The thaw had broken around suppertime, and by nine the nineteenth had turned back into February.” |
| [Gemini Neon](Stories/16-gemini-neon.txt) | “By nine o'clock the afternoon thaw had turned back into iron.” |
| [Sonnet 5.5](Stories/03-sonnet-5-5.txt) | “By nine o'clock the thaw had quit.” |
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
| [GPT-6 Astra](Stories/06-gpt-6-astra.txt) | “"Got it," she said.” |
| [GLM 5.3](Stories/08-glm-5-3.txt) | “and at Lottridge the light went green for nobody and he crossed on it anyway.” |
| [GPT 6 Sol](Stories/15-gpt-6-sol.txt) | “Behind the office glass, Ana shifted the phone to her other ear and tucked Theo's hat under his chin.” |
| [Mistral Large 4](Stories/20-mistral-large-4.txt) | “He turned the key.” |
| [Mistral Small 4](Stories/22-mistral-small-4.txt) | “The twenty in his pocket burned.” |
| [Sonnet 4.5](Stories/21-sonnet-4-5.txt) | “and somewhere in the building, someone laughed, the sound carried on the wind like smoke.” |

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
- [LLM Judgement/median-scores.md](LLM%20Judgement/median-scores.md): medians, judge spread, rankings by judge, and each model's strongest and weakest traits
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
