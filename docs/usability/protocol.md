# Usability test protocol

Goal: find out whether each persona can answer their questions from the app without help, and
fix what gets in the way before v2. The target is at least 80% task success on v2 and a
System Usability Scale (SUS) score of 70 or more.

## Participants

Five people, ideally one or two per persona. Retail or reporting experience helps but isn't
required. Each participant uses the test account for their persona, so row-level security shows
them the persona's real view:

| Persona | Test account | App reports |
|---|---|---|
| Store manager | `store.manager@` | Store today (on a phone), Store performance, Fresh and availability |
| Regional manager | `regional.manager@` | Network overview, Store performance, Fresh and availability |
| Category manager | `category.manager@` | Network overview, Fresh and availability, Promotions |
| Head office | `head.office@` | All five |

## Session (about 30 minutes, remote or in person)

1. **Intro (3 min).** "We're testing the report, not you. Please think aloud: say what you're
   looking for and what you expect to happen." Get consent to record the screen and audio.
2. **Tasks (15 min).** Read each task aloud. Don't help. If the participant is stuck for 2
   minutes, note it as a failure and move on.
3. **SUS questionnaire (5 min).** The standard 10 statements, rated 1–5.
4. **Debrief (5 min).** "What was the hardest part? What would you change first?"

## Tasks

Each task maps to a user story in the [requirements](../requirements.md). A task succeeds when
the participant states the correct answer without help.

| # | Persona | Task | Success when… | Story |
|---|---|---|---|---|
| 1 | Store manager (phone) | "How did your store do on the last day in the report, against its target?" | They read Sales Value, Target and the % above/below target on the Store today page | US-01 |
| 2 | Store manager | "Which fresh item is most likely out of stock in your store?" | They name the top item in the 7-day fresh list | US-02 |
| 3 | Regional manager | "Which of your stores is furthest behind on like-for-like sales this year?" | They pick the current year and name the lowest store in the LFL ranking | US-04 |
| 4 | Regional manager | "For that store, is it fewer shoppers or smaller baskets?" | They read the footfall and basket split and say which is negative (or drill through to Store detail) | US-05, US-06 |
| 5 | Category manager | "Which product family gained most from promotions, and did it lose sales afterwards?" | They name the top uplift family and read its post-promotion dip | US-07 |
| 6 | Head office | "Which region is furthest below plan this year?" | They pick the current year and name the region with the lowest Sales vs Target % | US-09 |

Every participant does tasks 1–2 (as a store manager, on a phone) and the tasks for their own
persona. That gives about 5 tasks each.

## What to record

For each task: success (yes / with a hint / no), time on task, and every point where they
hesitated, backtracked or misread something, quoted in their own words. After the session: the
SUS score and the debrief answers.

Results go in `results.md` in this folder: a task-success table, the median time per task, the
SUS scores, and the issues ranked by how many participants hit them. Each issue that drives a v2
change links to its change-log entry.
