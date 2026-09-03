# Demo call

How the Stedd demo call on /stedd was recorded (Brief 8, item 3), so it can be
redone when the agent changes.

1. `python3 scripts/demo-call/make_lines.py` synthesizes the caller's lines
   from `lines.json` into `lines/` (gitignored).
2. Register a web call on the demo agent through the Retell MCP server
   (`createWebCall`, agent "Stedd Receptionist") and take its access token.
3. With the local server on 127.0.0.1:8765, run
   `NODE_PATH=<puppeteer-core install> node scripts/demo-call/run_call.js <token> log.json`.
   `harness.html` feeds the lines into the call as the microphone and picks
   each reply from what the agent just said; the agent hangs up on "bye".
4. `getCall` returns the recording and a word-timed transcript. Cap the gaps
   between turns at 1.2 s, remap the timestamps, then
   `sh scripts/prep_demo_call.sh <trimmed.wav>` and paste the lines into the
   transcript list on stedd/index.html with `data-t` seconds.
