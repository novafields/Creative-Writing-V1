# Judge prompt

This is the full prompt each judge received, unchanged, with the 22 stories attached as STORY A to STORY V. The source file is [source/judge_prompt_A-V.txt](source/judge_prompt_A-V.txt).

````text
You are judging a blind short-fiction comparison. Attached are 22 stories, labelled STORY A to STORY V. All of them were written from the same brief, which is pasted below. You don't know who wrote any story. Do not guess authorship, and do not let style guesses affect your scores.

=== ORIGINAL BRIEF ===
Write a literary short story of 1,700–2,300 words.

Dale Varga has driven a city bus in Hamilton, Ontario, for eleven years. It is Thursday, 19 February. A thaw has melted the snow during the day, and by evening it is freezing again. The story covers the last three hours of his shift, on a route that ends at the east-side garage.

In October, Dale's car was repossessed. He hasn't told Carla, the tired, practical dispatcher he talks to over the radio, or his adult daughter. He now depends on catching a late bus home after he finishes at the garage.

At the hospital stop, Ana Ruiz boards with her four-year-old son, Theo, and a duffel bag. She says she's going to her sister's, but she's vague about where. She keeps checking her phone. The bus reaches the garage with Ana and Theo still on board.

Include these details: the bus heater ticks, Carla calls in with routine schedule changes, and Dale has to make a choice at the garage that puts his ride home at risk.

Dialogue should sound natural. Don't explain the characters' feelings; let actions and details carry them. The ending should be earned and shouldn't tie everything up.
=== END BRIEF ===

TASK
Read all 22 stories in full before you score any of them. Then score each story on the 22 traits below. Each trait is scored out of 20, and 20 is always best.

For negative traits (marked *), 20 means the flaw is absent and a low score means the flaw is heavy. Example: Purple Prose 20 = no purple prose at all.

TRAITS
1. Adherence to Instructions (brief details, required events, and length target of 1,700–2,300 words; well over or under should lose points)
2. Believable Character Actions
3. Nuanced Characters
4. Consistent Voice/Tone of Writing
5. Imagery and Descriptive Quality
6. Elegant Prose
7. Emotionally Engaging
8. Emotionally Complex
9. Coherent
10. Meandering*
11. Weak Dialogue*
12. Tell-Don't-Show*
13. Unsurprising or Uncreative*
14. Amateurish*
15. Purple Prose*
16. Overwrought*
17. Incongruent Ending Positivity*
18. Unearned Transformations*
19. Well-earned Lightness or Darkness
20. Sentences Flow Naturally
21. Overall Reader Engagement
22. Overall Impression

RULES
- Score every story on its own merits against the rubric, not against the story next to it.
- Use the full 0–20 range. Don't cluster everything between 15 and 18.
- Several stories share titles or similar plots. Don't penalize a story for that; judge only its execution.
- Estimate each story's word count and say so. If a story clearly misses the length target, reflect that in Trait 1.
- Before you give a total, add up the 22 scores and check the sum. Totals are out of 440.

OUTPUT FORMAT
1. A CSV table, one row per story, with these columns:
Story, Est. Words, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, Total

2. A final ranking from 1 to 22 by total, with ties noted.

3. For each story, at most two sentences on its biggest strength and its biggest weakness. Quote at most one short phrase per story as evidence.

Do not add any other commentary.
````

[Back to the leaderboard](README.md)
