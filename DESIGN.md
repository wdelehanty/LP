# williamdelehanty.com v2: Steel and Signal

Design plan for the 2026 rebuild. Source brief: CC Brief 5 in the career repo.
This file is the reference for every page that ships. If a page and this file
disagree, fix one of them before pushing.

## 1. Direction

The site is dark and technical because its strongest material is workflow
diagrams and dashboards, and they read best on a dark ground. The base is a
slightly warm gunmetal, never pure black. One accent: safety yellow from the
workwear world. The signature element is a status rail showing real running
systems. One section per page may break the technical frame with real
photography carrying visible grain.

## 2. Tokens

```
--bg          #15181B   gunmetal, base
--bg-panel    #1E2226   raised panels, cards
--line        #3A4046   dividers, diagram strokes
--line-soft   #2A2F34   hairlines inside panels
--text        #E6E4DF   warm off-white body
--text-muted  #9AA0A6   captions, metadata
--signal      #F2C230   safety yellow, the ONLY accent
--signal-ink  #15181B   text on signal fills
--photo-warm  #B08968   photo captions in personal sections only
```

Rules: one accent. Signal yellow is for the status rail, active states, one
underline per page, and diagram highlights. Never fill a section with it. No
gradients. No glassmorphism, no blur, no glow.

## 3. Type

- Display and body: Barlow. Display 600, tracking -0.02em, sizes on a 1.25
  modular scale from 17px. Body 400, 17px, line-height 1.55.
- Labels, eyebrows, stats, table data: Barlow Condensed 600, uppercase,
  letter-spacing 0.08em, 12 to 13px.
- Code, IDs, dimensions, diagram captions: IBM Plex Mono 400, 13px.
- Self-hosted woff2 in /assets/fonts/ (latin subset, 60K total), preloaded.
- Never: Inter, Geist, Fraunces, Playfair, Space Grotesk, Roboto.
- Headings left-aligned. Nothing centered except the 404 page.

## 4. Layout

- 12-column grid, max width 1180px, gutters 24px, generous left margin.
  Content sits left; the right third carries margin notes, metadata, and
  diagrams so pages feel asymmetric.
- Section separators: 1px --line rule, Barlow Condensed eyebrow on the left,
  Plex Mono section ID on the right (WORK / 03). IDs are real anchors.
- Radius 2px on panels, 0 on images. No pills. No icon-in-circle cards.
- Photos full-bleed or two-thirds width, never a uniform 3-up grid. All
  photography gets a film grain overlay (CSS noise, opacity 0.06).

## 5. Signature element: the status rail

A slim strip at the top of every page (below the nav on mobile):

```
* 52 WORKFLOWS   * 36 ACTIVE   * LAST RUN 07:50 ET   * SITE v2.0.0
```

- Source: /status.json, written hourly by an n8n workflow ("Portfolio:
  Status Publisher") that counts workflows and active workflows via the n8n
  API and commits the file to this repo through the GitHub API.
- Fallback: if the fetch fails, the rail keeps the static values baked in at
  build time. It never shows an error, a spinner, or an empty slot.
- The fallback values in the markup are real: they are queried from the n8n
  API at build time, not typed. Current bake: 52 workflows, 36 active,
  last run 07:50 ET on 2026-08-31.
- Motion: the dots pulse once on load, then hold. That is the only animation
  on any page. prefers-reduced-motion disables it.
- Weather slot is pending Will's call (open question 4). Omitted until then,
  because a stale baked temperature presented as live would be a small lie.

## 6. Wireframes

### 6.1 Home

```
+--------------------------------------------------------------------------+
| WILLIAM DELEHANTY            WORK  STEDD  LAB  STACK  HOW I WORK  ABOUT  |
+--------------------------------------------------------------------------+
| * 52 WORKFLOWS  * 36 ACTIVE  * LAST RUN 07:50 ET  * SITE v2.0.0          |
+--------------------------------------------------------------------------+
|                                                                          |
|  I build revenue systems.                          |   ACQUISITION       |
|  Acquisition, lifecycle, data, and                 |        |            |
|  the handoff to sales, wired                       |   [ CDP 18M+ ]      |
|  together and measured.                            |        |            |
|                                                    |   [ LIFECYCLE ]     |
|  Eleven years at Forbes ... paragraph              |        |            |
|  (nights and weekends: trades product,             |   [ CRM ROUTING ]   |
|  house that runs itself, job search                |        |            |
|  machine)                                          |      SALES          |
|                                                    |   yellow = mine     |
|--------------------------------------------------------------------------|
|  SELECTED WORK                                              WORK / 01    |
|  ----------------------------------------------------------------------  |
|  Forbes demand engine                                                    |
|  $0 to eight figures, influenced ...            [ mini diagram ]         |
|  salesforce pardot blueconic looker                                      |
|  ----------------------------------------------------------------------  |
|  Forbes Connect on the CDP ...                  [ mini diagram ]         |
|  ----------------------------------------------------------------------  |
|  Stedd ...                                      [ mini diagram ]         |
|  ----------------------------------------------------------------------  |
|  The job search machine ...                     [ mini diagram ]         |
|--------------------------------------------------------------------------|
|  NUMBERS THAT ARE REAL                                      PROOF / 02   |
|  +--------------------+-----------------+---------------+-------------+  |
|  | $0 to 8 figures    | ~2.5x           | 18M+          | 10+         |  |
|  | source line mono   | source line     | source line   | source line |  |
|  +--------------------+-----------------+---------------+-------------+  |
|--------------------------------------------------------------------------|
|  STACK, SHORT                                               STACK / 03   |
|  Salesforce attributes. BlueConic segments. Pardot nurtures. ...         |
|--------------------------------------------------------------------------|
|  OFF HOURS                                                  HOME / 04    |
|  [ photo, two-thirds width, film grain          ]   caption in           |
|  [                                              ]   photo-warm           |
|  two sentences, link to /about                                           |
|--------------------------------------------------------------------------|
|  Built by hand in Warwick, NY. v2.0.0. Last deploy 2026-08-31.           |
+--------------------------------------------------------------------------+
```

### 6.2 Case study

```
+--------------------------------------------------------------------------+
| nav + status rail                                                        |
+--------------------------------------------------------------------------+
|  FORBES / B2B                                    2019 TO PRESENT         |
|  Title of the case study                                                 |
|  Outcome line: the number and the mechanism in one sentence.             |
|--------------------------------------------------------------------------|
|  PROBLEM                                          |  MARGIN NOTES        |
|  2 to 4 sentences.                                |  (Plex Mono asides   |
|                                                   |  in Will's voice)    |
|  WHAT I BUILT                                     |                      |
|  - bullet, in build order                         |  "This took three    |
|  - bullet                                         |  tries. The first    |
|  - bullet                                         |  two routed leads    |
|                                                   |  to the wrong        |
|  STACK                                            |  queue."             |
|  plex mono list                                   |                      |
|                                                   |  WHAT I'D DO         |
|  OUTCOME                                          |  DIFFERENTLY         |
|  The number, how it was measured,                 |  short aside         |
|  what it did not measure.                         |                      |
|--------------------------------------------------------------------------|
|  [ full-width diagram in site tokens                       ]             |
|  Rendered from workflow export, 2026-08-30   (Plex Mono)                 |
|--------------------------------------------------------------------------|
|  footer                                                                  |
+--------------------------------------------------------------------------+
```

### 6.3 About

```
+--------------------------------------------------------------------------+
| nav + status rail                                                        |
+--------------------------------------------------------------------------+
|  ABOUT                                              ABOUT / 01           |
|  [ headshot, two-thirds width, grain ]                                   |
|  Bio, 150 words, first person. Warwick NY, 11 years                      |
|  at Forbes, Ithaca MBA and BBA, founder of Stedd,                        |
|  two boys, a hobby farm.                                                 |
|--------------------------------------------------------------------------|
|  THE FARM AND THE SHOP                              ABOUT / 02           |
|  [ photo, full bleed, grain                                    ]         |
|  caption in photo-warm, larger type, more space                          |
|  [ photo, two-thirds, offset right                    ]                  |
|--------------------------------------------------------------------------|
|  OUTSIDE                                            ABOUT / 03           |
|  One line.                                                               |
|--------------------------------------------------------------------------|
|  Resume download (/resume.pdf)   GitHub   LinkedIn   Email               |
|--------------------------------------------------------------------------|
|  footer                                                                  |
+--------------------------------------------------------------------------+
```

## 7. Build mechanics

- Hand-written HTML and CSS, no framework, no build step beyond
  scripts/stamp.py, which injects the version and deploy date into the
  footer and rail before each push. Placeholders in source are
  data-stamp="version" and data-stamp="date"; the script fails if it
  cannot find them.
- Shared stylesheet /v2/site.css. Diagrams are inline SVG using token hex
  values so they inherit the page fonts.
- The kit-visit beacon ships on every page, byte-identical to the one on
  the current root page: reads ?c= only, sessionStorage dedup per code, no
  localStorage anywhere.
- Page weight budget: 1.5MB home, fonts 60K, no JS libraries.

## 8. Ban list (enforced at QA)

No gradient hero. No purple or electric blue. No icon-in-a-circle grids. No
centered hero. No Inter or Geist. No glassmorphism. No emoji bullets. No
stock illustration or 3D blobs. No "Building the future of" or "Where X
meets Y" copy. No numbered markers unless the content is a sequence. No
scroll-triggered fade-ins; at most one orchestrated moment per page (spent
on the rail pulse). No testimonial carousel. No "trusted by" logo strip.
No em-dashes anywhere, including comments and commit messages.

## 9. Self-critique pass (what changed from the first draft)

Checked the plan against the known AI defaults before building:

1. "Near-black with one bright accent" is the most common AI dark theme.
   What keeps this one a choice: the warm gunmetal base, an accent pulled
   from workwear rather than a neon, a status rail wired to a real API, and
   one photography section with grain that breaks the frame. If any of
   those four get cut later, the theme collapses into the default and
   should be rethought.
2. First draft had a small diagram motif on all four selected-work rows.
   Uniform little diagrams drift toward icon decoration, which is the same
   disease as icon-in-a-circle grids. Revised: each row's visual must be a
   real excerpt of that system's actual diagram, drawn at the same scale
   and style as the full version on its case study page, or the row ships
   with no visual. No filler glyphs.
3. First draft repeated one section rhythm down the whole home page
   (eyebrow, rule, content, four times). Revised: the numbers band is a
   paneled strip, the photo section shifts the grid right and changes
   caption color, so the page has three textures, not one.
4. The IntersectionObserver reveal-on-scroll from the current site is
   dropped entirely, not ported. The one motion budget goes to the rail.
5. The current site's hero reads "William Delehanty." with a serif italic
   flourish, which is a template gesture. v2 opens with the thesis sentence
   instead and the name lives in the nav.
6. Scroll-checked the copy plan for AI cadence: no aphoristic pairs, no
   "X, not Y" framing anywhere on the site, including the how-i-work page,
   whose seed lines get rewritten in prose before shipping.

## 10. Design pass, 2026-08-31 (post Gate 2 feedback: "looks robotic")

Reviewed against 2026 trend guidance Will supplied (kinetic type, micro-
interactions, depth, bento asymmetry, trust cues) and rebuilt the visual
layer without touching copy or tokens:

1. Type drama. Hero at up to 64px, case titles to 66px, proof numerals in
   Barlow Condensed up to 68px set in signal. The proof band is now the
   loudest moment on the page, which is where loud belongs.
2. One load-in moment per page: hero/case headers rise once on load,
   staggered. The rail pulse stays. Nothing is scroll-triggered.
3. Micro-interactions everywhere touchable: nav underline slides, rows get
   full-bleed hover with an arrow that slides in, band cells lighten,
   aside notes flip their border to signal, buttons lift.
4. Drafting-table texture: site-wide grain at 3.5%, blueprint grid behind
   heroes and the footer (SVG tile, not a CSS gradient), a signal
   registration mark, hatched drafting voids for pending photos, DWG title
   lines under diagrams, coordinates in the footer.
5. Signal notches on section rules and h2 rules; square markers in signal.
6. Depth: panel shadows with a 1px light top edge; no glass, no blur.

Rail source order: the live n8n endpoint (Portfolio: Status Endpoint,
webhook /portfolio-status), then /status.json, then baked values.

## 11. Trend layer, 2026-08-31 (Will: "took no design inspiration from the links")

Round two adopted the 2026 trend guidance directly instead of politely.
Will explicitly lifted three of the original bans for this: scroll-
triggered reveals, blur on the sticky rail, and photography beyond his
own. What shipped:

1. Kinetic typography: display headlines split per word by site.js and
   rise staggered on load. Progressive enhancement; no JS or reduced
   motion means static text.
2. Scroll-triggered reveals on rows, bands, notes, figures: fast (500ms,
   16px), once, generous margins. Guarded behind the html.js class so
   nothing is hidden without JS.
3. Glass rail: translucent panel with backdrop blur. The one blur on the
   site.
4. Scroll progress thread: 2px signal bar fixed at the viewport top.
5. Bento proof grid: areas "a b c / a d d", hard offset shadow
   (12px 12px 0), the brutalist accent. Buttons get the same shadow on
   hover.
6. Photography as material: brushed steel (apryan widodo, Unsplash) at
   low opacity behind heroes with a slow scroll drift; a blacksmith
   anvil (Pim de Boer, Unsplash) behind the angled off-hours section,
   captioned honestly as not-my-shop. Both credited in the colophon.
   Will's own photos still replace the hatched voids when they land.
7. The off-hours section top edge is cut at an angle (clip-path), the
   single anti-grid gesture.

Ban list still in force: no gradients, no purple or blue, no centered
hero, no Inter/Geist, no emoji, no carousels, no logo strips, no
em-dashes. The rules that moved, moved because the client said move.

## 12. Visual pass, 2026-09-02 (CC Brief 6, target v2.6.0)

Composition, imagery, density, and motion. Tokens, type, grid, and the
site map are unchanged. Decisions that pages must follow from here:

1. Frames. Every real screen and photo sits in a `.frame`: 1px `--line`
   hairline, 4px radius (the one exception to the 2px panel rule), grain
   at 6%, a slight inner shadow, mono caption outside and beneath.
   Aspect modifiers: `.r43`, `.r11`, default 3:2. Pending assets ship as
   `.frame.slot`, the hatched drafting void with a labeled SLOT tag, at
   the final aspect ratio so layout can be approved before assets land.
2. Photos run at full strength or they do not run. No opacity washes, no
   background photos behind text. The off-hours section is now text left,
   one framed photo right.
3. Hero: "I build revenue systems." on one line, underline kept, the rest
   of the old headline as a 24px body-weight subhead, then two paragraphs.
   Right column is a framed Performance Console crop, 4:3.
4. Status rail is back as a thin mono strip directly under the nav, not
   sticky, no glass. Items: workflows active, last morning round, last
   deploy, separated by 5px signal dots. Source is a Cloudflare Worker
   (see /worker), deployed 2026-09-02 at wd-status.wdelehanty.workers.dev,
   holding no secrets: it reads the n8n webhook served by "Portfolio:
   Status Endpoint v2", which uses the n8n-side credential, and caches 15
   minutes. That workflow needs its credential attached and activating in
   the n8n UI (worker/README.md has the two steps); until then the Worker
   answers 502 and the rail shows the baked values. The zone is on
   Cloudflare but the apex record is DNS-only, so the same-origin
   /api/status route stays commented out until the proxy is turned on.
   Baked values in the markup are real, refreshed by scripts/bake_status.py
   at release time. The rail never shows loading or empty. Bake on
   2026-09-02: 35 active workflows, last Morning Round v2 run Wed 07:00 ET.
   It is on every page, under the nav.
5. Work cards: text 55%, framed image 40%, 5% gutter, image side
   alternates right/left/right/left. Hover lifts the image 4px and runs
   the signal hairline under the title to full width. The arrow slide and
   the row background tint are gone.
6. Photo strip between Work and Proof: five squares, full bleed, 1px
   gaps, grayscale at rest and color on hover, color where hover does not
   exist. One mono line beneath: "Warwick, NY. Weekends."
7. Proof grid: five cells, "a b c / a d e". The tall left cell keeps the
   tenure claim; "$275K direct-booked from $72K paid" fills the bottom
   right. Numerals count up once on scroll into view, 600ms.
8. Motion budget, site-wide and final: scroll reveal (opacity and 12px
   rise, 400ms, once per element) on section heads, cards, figures, and
   proof numerals; hover (image lift, hairline extend, grayscale to color,
   200ms); ambient (rail tick on first paint and slow dot pulse). The
   hero parallax drift and the scroll progress thread are removed.
   `prefers-reduced-motion` disables all of it and leaves the rail's live
   update in place.
9. Nav under 768px hides Stack and How I work; Work, Stedd, Lab, About
   stay. Under 480px the four sit in one row.
10. Version and deploy date come from `scripts/release.sh vX.Y.Z`, never
    by hand. Footer LinkedIn URL is /in/williamdelehanty/.
11. Case studies: "What I built" is two or three subsections, each an H3,
    a short paragraph, at most three bullets, and one figure. `.built.side`
    puts a 3:2 frame in the right column (a screenshot, a slot, or a
    480 by 320 plate from `draw_architecture.py`); `.built.plate` runs a
    full-width drawing beneath the text. The demand engine keeps its full
    system drawing as a closing plate; the funnel is redrawn with what
    actually runs in each stage. Captions never repeat how a drawing was
    made; the colophon says it once. Figures and the aside notes never
    share a column, so the notes stay sticky beside Problem or Outcome.
12. About: the studio headshot is masked onto a gunmetal gradient by
    `scripts/mask_headshot.py` (Pillow and numpy), cropped past the
    watermark, and shown in a 1:1 frame. Coop and shop photos are the
    model for the rest of the site and stay as they are.
13. Photo strip hover is grayscale to color, decided. Card 1 on the home
    page is the horizontal demand-engine plate, decided.
14. Assets filled on 2026-09-02 without the real internal screens: the
    shop photo (Google Photos, square crop of the workbench), the Morning
    Round email in Gmail (no names in frame), and renders of the repo's
    own pitch kit standing in as samples: the lifecycle and pipeline
    console (hero and the demand engine page) and its capture form (the
    demand engine two-up). The Stedd card uses the sample Monday Report.
    Every sample is captioned as a sample; live numbers stay internal.
    The BlueConic slots became a crop of the real Forbes page with its
    Connect with Us button (home card) and a drawn dialogue plate (Connect
    case study). The summit page shows the 2019 Detroit late show, captioned
    by year. No slots remain.

Gate order from the brief: home comp with placeholders, Will approves
layout; Worker live on real n8n data; assets in and home ships as v2.6.0;
case studies and about; QA pass.

## 13. Polish pass, 2026-09-02 (CC Brief 7, target v2.6.1)

1. Diagram grammars. `scripts/draw_architecture.py` now draws eight ways:
   flow (boxes and arrows, the demand engine only, type at +2px), ledger
   (a table with a signal total row), timeline (a rule with ticks, one
   yellow), layers (stacked bands, owned layers in signal), split (before
   muted, after full strength), swimlanes (a human and a system taking
   turns), bars (inventory numbers only, unused so far), and callouts (a
   real screenshot with numbered pins, written as an HTML fragment that
   `inline_diagrams.py` passes through). No page runs two figures of one
   grammar back to back; `scripts/contact_sheet.py` writes qa/diagrams.html
   to prove it. Rendered n8n exports stay for the pure automations; the
   human-in-the-loop ones (morning round, live booking, outcome loop) are
   swimlanes drawn by hand.
2. Headshot: 920 by 1150, hair at 14%, shoulders off the bottom, the mask
   eroded 2px and the rim band darkened, the watermark painted over.
   qa/headshot.html compares old and new at 1x and 2x.
3. Home: the strip runs in full color (grayscale read as a placeholder
   row), the hover is a 4px lift; proof numerals count from 85% over
   500ms so no frame reads as a wrong number; Selected Work and Stack sit
   40px closer to what precedes them; the console crop lost its right
   edge band; the card plate type is 2px larger; off-hours copy aligns
   with the top of the photo. The shop tile shows the coop run until a
   clean shop shot lands.
4. About carousel replaces the single Outside photo: CSS scroll-snap
   track, prev and next buttons on the eyebrow row, dots, arrow keys when
   the track has focus, instant under reduced motion, no autoplay, any
   number of slides. Ships with the frozen lake, the fireworks rig, the
   dog on the shop floor, and the pond.
5. Photo intake: `scripts/intake_photos.py scan` reads the Mac Photos
   library through osxphotos (or a Takeout folder), keeps the last four
   years, skips screenshots, and pre-filters on Apple's own labels so the
   paid tagging pass sees 3,380 photos instead of 9,461. `tag` sends
   batches of ten to Claude with a fixed JSON schema (faces, children,
   plates, clutter, exposure, caption), cached by file hash. `sheet`
   writes qa/intake.html; `apply` processes the ticked picks. The
   intake/ cache is gitignored. Tagging needs an API key and costs about
   twenty five dollars for the filtered set.
6. Intake outcome. No API key was on the machine, so the tagging pass was
   done by eye from contact sheets of the label-filtered subsets, and the
   tags written into intake/tags.json by hand. Four of the six picks were
   iCloud previews locally; osxphotos pulled the originals through
   PhotoKit. Shipped: the wide shop shot in the strip; the boat at sunset,
   skis on the slope, the tractor with the mower, the groomed trail, and
   two dogs in the surf as carousel slides. Photos of the boys stayed out
   entirely. The `tag` step still works as written when a key is present.
