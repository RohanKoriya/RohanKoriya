# Setup guide

## What you get
A hand-designed profile (portrait + introduction, contribution activity, statistics, languages,
stack, learning, projects, snake) generated from **live GitHub data** and refreshed daily by GitHub Actions.
Dark and light themes are both generated; GitHub shows the one matching the viewer's theme.

Everything you edit lives in **`profile.toml`**. Statistics are never typed in by hand.

## Prerequisites
- A GitHub profile repository named exactly like your username (`RohanKoriya/RohanKoriya`), public
- Git, and Python 3.11+ (only for previewing locally; GitHub Actions needs nothing installed)

## Preview locally (optional)
```bash
python -m venv .venv
# macOS/Linux:  source .venv/bin/activate        Windows PowerShell:  .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m unittest discover -s tests            # all tests should pass

# Layout preview with SAMPLE numbers (never commit this output):
python -m generator --demo

# Real data (needs a token, see below):
#   macOS/Linux:  export GH_TOKEN=ghp_xxx        Windows PowerShell:  $env:GH_TOKEN="ghp_xxx"
python -m generator
```
Open the files in `generated/` by double-clicking them (do **not** use VS Code Live Server for `.svg`
files; it injects a script that breaks SVG XML).

## See everything together (combined preview)
```bash
python -m generator --demo --open      # sample numbers, opens preview.html in your browser
python -m generator --open             # your real data (needs GH_TOKEN)
```
`preview.html` stacks every section in the same order as the README, with a dark/light switch.
You can also double-click `preview.html`, or right-click it in VS Code → *Open with Live Server*
(this works because the SVGs are loaded as images; opening a raw `.svg` in Live Server is what breaks).
Press refresh after re-running the generator.

## Publish
```bash
git clone https://github.com/RohanKoriya/RohanKoriya.git
cd RohanKoriya
git rm -r -q .                       # removes the OLD design, workflow and scripts
# copy EVERYTHING from this project into this folder, including hidden items (.github)
#   macOS/Linux: cp -R /path/to/profile/. .
#   Windows:     xcopy /E /H /Y C:\path\to\profile\* .
git add -A
git commit -m "Redesign profile"
git push
```

## Enable Actions
1. Repo → **Settings → Actions → General**: *Allow all actions and reusable workflows*.
2. Same page → **Workflow permissions** → **Read and write permissions** → Save.
3. Repo → **Actions → Update profile → Run workflow** (the push also starts it automatically).
4. Wait ~1 minute; it commits `generated/` and updates the block between the `PROFILE:START/END`
   markers in `README.md`. Anything you write outside those markers is preserved.

No secrets are required. The built-in `GITHUB_TOKEN` is enough for public data.
Optional: add a fine-grained, read-only token as secret `PROFILE_TOKEN` to include private-contribution counts.

## Customise
- Text, links, stack, learning, projects: `profile.toml`.
- Pin projects: `pin = ["Smart-Leads-Dashboard", "SEO-Rank-Tracker"]`.
- Project descriptions come from each repository's **About** field on GitHub. Fill those in.
- Portrait: add a photo at `assets/portrait.png` (or `.jpg`/`.webp`) to use it instead of your avatar.
  A square, evenly lit headshot on a plain background works best.
- Colors/typography: `generator/kit.py`. Section layouts: `generator/sections.py`.

## Verify
- Open `https://github.com/RohanKoriya`: toggle GitHub's theme (Settings → Appearance) to check both.
- Actions tab: the latest run is green. A yellow "Profile data fallback" annotation means GitHub's API was
  unreachable and the last good data was reused (the footer shows its real timestamp).

## Troubleshooting
| Symptom | Fix |
|---|---|
| Broken images right after pushing | The first run has not finished; wait for the green run, then refresh. |
| Run fails: "Permission denied … 403" on push | Step 2 above (Read and write permissions). |
| `Config error: Link … must start with https://` | Fix the URL in `profile.toml`; only `https://` and `mailto:` are allowed. |
| "No live data and no usable cache" | Token missing/invalid (local run) or API outage on the very first run; re-run later. |
| Old design still visible | Hard refresh; GitHub caches images for a few minutes. Confirm the old workflow file was removed. |
| Numbers look low | Contributions are the last 12 months of **public** activity unless `PROFILE_TOKEN` is set. |
| Portrait looks odd | Add `assets/portrait.png`, or adjust `columns` in `[portrait]`. |
| Scheduled runs stopped | GitHub pauses idle repos after 60 days; press **Run workflow** once. |
