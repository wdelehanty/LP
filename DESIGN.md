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
