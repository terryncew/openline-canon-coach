# openline-canon-coach
# Canon · Coach-Maker · Students (Receipts-Native)

**What this is:** a tiny, working “model that trains other models” around a fixed law.

- **Canon (law):** global rules that never move (bands, monotonic risk→safety, hysteresis, exception doctrine).
- **Coach-Maker (style):** proposes a small, *legal* adapter per lane (forgiveness, smoothing, reflex order, VKD posture).
- **Students:** any model/agent that runs with that adapter.
- **Receipts:** every run emits a one-screen proof file (JSON) you can view on GitHub Pages.

**Why:** many styles, one law. Diversity without drift. Emergence without Goodhart.

**Live page (after enabling Pages, branch `main`, folder `/docs`):**
`https://<you>.github.io/canon-coach-students/`

**How it runs:** a GitHub Action (`coach-run.yml`) executes the coach, simulates a shadow run, judges by Canon, and commits a **Tuning Receipt**. No servers or Codespaces.

**Law vs. Style:**
- Law is published in `canon/law.json` (also mirrored to `docs/receipts/canon.json`).
- Style lives in `adapters/<lane>/style.json` and is adjusted only if the shadow run produces a green **Tuning Receipt**.

**Mantra:** Shadow → Tuning Receipt → Live. Law global; style local.
