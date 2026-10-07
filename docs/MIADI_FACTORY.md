# DeepDiver in the Miadi Factory

This fork (`miadisabelle/deepdiver`) is the copy of DeepDiver that the Miadi Factory runs. This page says what it supplies, to which team, in what order, what it depends on, and what is still open.

Written 2026-10-06 by Mia (Claude) with Guillaume. The decomposition behind it is kept in `.pde/2610062212--73ed33d2-ac26-4939-84db-0f029811d1ab/`.

## What DeepDiver is

A Python command line that drives Gemini Notebook (NotebookLM until its rename) through a Chrome browser over the DevTools protocol. It creates notebooks, adds sources, generates Studio artifacts and downloads them. The tool is Jerry's (`Gerico1007/deepdiver`, published on PyPI as `deepdiver`). This fork carries his branch `24-studio-artifact-foundation` and the upgrade to the Studio interface of 2026-10-06 (commit `2760b13` and the commit that adds this page).

## Where the decision is recorded

- **Episode 550** (`miadi-chronicle://550`, *The Screenwalk as a Media Type*) holds review `miadi-review:f9d6fb1e-75f4-4635-96d9-8f2d0bcff5eb` v12, *Screenwalk-Driven Continuity & Deep Diver Handoffs in the Miadi Factory*, and the talking circle held about it (ceremony `acd9889c-d10a-4edb-b994-69b2f5a4af23`, `circle:1790880114096:ckha5n`). The review's Definitions say, as of 2026-10-03, that this fork stopped at 2025-11-17 and that nothing was installed on gaia. The fork is now current.
- **The orchestration kit** (`jgwill/miadi-orchestration-kit`, `teams/README.md`) lists, under T6 Production: "documentaries of the factory's own work: the screenwalk protocol, notebooks and generated media (Deep Diver is its first instrument)".

## The team

DeepDiver is an instrument of **T6 · Production** (after an episode). Its human lead is William. It has no agent lead yet, and its name is held as William's decision D11. T6 uses chronicle episodes, Miadi reviews and screenwalk captures. DeepDiver turns those into notebook media.

## The contract

### Inputs

- A review's Markdown, from `https://miadi-review-service.vercel.app/review/<id>/raw` or the `miadi-review` skill's `download-all` cache.
- The YouTube URL of the reviewed video or screenwalk. Gemini Notebook imports the video's transcript, not its images, and only public videos.
- Any other file or web page an episode holds.

### Operations

| step | command |
|---|---|
| start Chrome with a signed-in profile | `deepdiver chrome launch --clone-profile "<Profile N>"` |
| new notebook with a first source | `deepdiver notebook create --source <review.md>` |
| add a source | `deepdiver notebook add-source <id> <url-or-file>` |
| add only missing files | `deepdiver notebook resume <id> -s a.md -s b.md` |
| ask the notebook a question | `deepdiver notebook ask <id> "<question>" -o asked.md` |
| generate an artifact | `deepdiver studio generate <family> -n <id> [--focus "..."]` |
| generate a report | `deepdiver studio report [--format document] [--template "..."] [--prompt "..."] -n <id>` |
| see the Studio panel | `deepdiver studio list -n <id>` |
| download everything | `deepdiver studio download -n <id> -o <dir>` |
| show an artifact on screen | `deepdiver studio open --family reports -n <id>` (`--play` for audio and video) |

### Outputs

- Media files named after the artifact title: `.m4a` (Audio Overview), `.mp4` (Video Overview), `.png` (Infographic).
- Reports as `.md` and `.html`, read from the report viewer, since Gemini Notebook gives reports no file download.
- Answers to questions, appended to a Markdown file with the notebook's citations as `[n]`.
- `manifest.json` beside them: title, family, path, sha256, size, and codec and duration from ffprobe.
- The session record in `sessions/current_session.json` (notebook ID, sources, artifacts, downloads).

Mind Map cards have no Download item. Slide Deck, Reports, Flashcards, Quiz and Data Table downloads were not tested.

## The pipeline, in order

Each step depends on the steps it names.

1. **Screenwalk recorded and on YouTube.** Guillaume and the witness team (T3).
2. **Review made.** `miadi-review create` or `review-local.sh` for a long video. Gives `miadi-review:<uuid>`. Depends on 1.
3. **Review held by an episode.** Through the episode door of the `chronicle-episode` skill. Depends on 2.
4. **Notebook assembled.** DeepDiver adds the reviews' Markdown and their videos as sources. One notebook can take several reviews and several videos. Depends on 1 and 2.
5. **Questions asked and artifacts generated.** `notebook ask` for the episode's questions; Infographic, Video Overview, Audio Overview, Mind Map; then an Interactive report whose prompt names which of those items to embed. Depends on 4.
6. **Artifacts downloaded with their manifest.** Depends on 5.
7. **Artifacts played in a later screenwalk**, paused and talked over. `studio open` puts an Interactive report on screen full-size, and `--play` starts an Audio or Video Overview. The recording and the talking happen outside DeepDiver. Depends on 5.
8. **Relations recorded.** The episode cites the notebook and the downloaded files. Depends on 3 and 6.

Steps 4 to 6, and opening an artifact in step 7, are DeepDiver's. Steps 7 and 8 as practices are proposals: no screenwalk has played a DeepDiver artifact yet, and no episode records a notebook.

## Verified on 2026-10-06

On gaia, Chrome 154, a clone of the AVA profile (`ava@jgwill.com`):

- Notebook `773f480c-0ab7-4eac-b106-bf7c7c0251e8`: `studio download` saved all six downloadable artifacts (two videos, three audios, one infographic). Their ffprobe durations match the Studio cards. The Mind Map card was reported as having no Download item.
- Notebook `78507190-4018-41c6-9fe0-47ed17df5300`, made for this test: created with review `f9d6fb1e` as a Markdown file, then `https://youtu.be/q4I55OAkI0Y` (the screenwalk that review covers) as a second source. An Infographic generated from both, *From Screenwalk to Studio Media: The Deep Diver Pipeline*, downloaded as a 2752×1536 PNG. Mind Maps generated and were recognised as new cards. An Interactive report with a prompt (*The Miadi Media Engine: Transforming Screenwalks into Notebook Artifacts*) and a Document report from the Briefing Doc template (*Executive Briefing: …*) generated, and `studio download` saved all four reports in the notebook, two of them Guillaume's, as Markdown and HTML. `notebook ask` returned a cited answer, and `studio open` opened the newest report.

## What the interface changed, and what was fixed

| change in Gemini Notebook | effect before the fix |
|---|---|
| `notebooklm.google.com` redirects to `notebook.google.com` | host checks failed |
| a cloned Chrome profile opens a Terms of Service window | the DevTools port never opened |
| each card's More menu has Download, and the download starts outside the page | downloads never arrived |
| the home button reads "New notebook" | notebook creation timed out |
| a new notebook passes through `/notebook/creating` | the ID was recorded as `creating` |
| one "Websites" option takes website and YouTube URLs, several at once | YouTube sources failed |
| a generating card already shows the family and a title | generation was reported done after 3 seconds |
| Mind Map cards are labelled only "Artifact" | Mind Map generation was never seen to finish |
| a card has no DOM id; its UUID sits in an inner `artifact-labels-<uuid>` | a repeat generation returned an older card |
| Reports open a "Create report" dialog with formats, templates and a Customize form; cards say "Report" | Reports could not be generated |
| reports have no Download | reports could not be kept |

A search for an "Add" button also matched the header's "Create notebook" button, whose icon renders as the text `add_2`. Three empty notebooks named "Untitled notebook" were created in the AVA account that way on 2026-10-06. The selector is fixed, and those notebooks are still there.

## Installing it in the factory

- Python 3.8 or later, with `playwright`.
- Google Chrome on a host with a display, and a Chrome profile signed in to the Google account that owns the notebooks. `deepdiver chrome launch --clone-profile` copies that profile so the live one is never touched.
- `ffprobe`, for the media data in the manifest.
- Configuration in `~/.config/deepdiver/config.yaml` (`deepdiver init`).
- The agent skill: `deepdiver skills install --agent claude`.
- Source: PyPI `deepdiver` 0.1.1 does not have the 2026-10-06 fixes. Until a release carries them, install from this fork: `pip install git+https://github.com/miadisabelle/deepdiver@main`.

## Package

No new package is needed under `jgwill/Miadi/packages/` to begin. DeepDiver is already a Python package with its own CLI and bundled skill. The options, in the order they depend on each other:

- **O1.** Offer this fork's changes to `Gerico1007/deepdiver` as a pull request, so Jerry can release them to PyPI.
- **O2.** Add `deepdiver` to Miadi's Python umbrella (`packages/miadi/py`, which already depends on `ironsilk`), for example as an extra `miadi[production]`, and give `scripts/ops/miadi-delivery.sh` a part that checks the installed version, as it does for `ironsilk`. Depends on O1 or on pinning this fork.
- **O3.** A T6 plugin in the orchestration kit that carries DeepDiver's skill and its Chrome setup. Depends on T6 having an agent lead.

An MCP server around DeepDiver was considered and left out: no consumer needs one yet.

## Open, each with its owner

- **Q1.** The team's name, D11. William.
- **Q2.** Whether to open the pull request of O1 to Jerry's repository. Guillaume.
- **Q3.** Whether O2 goes into `jgwill/Miadi`. Guillaume.
- **Q4.** Where an episode keeps downloaded artifacts. A proposal: `<episode>/captures/<stem>/notebook/` with the manifest.
- **Q5.** Whether to delete the three empty "Untitled notebook" notebooks and the test notebook `78507190…`. The AVA account's owner.
