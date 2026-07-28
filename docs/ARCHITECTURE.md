# Architecture

## Data flow

```
GitHub REST + GraphQL API
        │
        ▼
data_fetcher.collect_all(username)
        │   returns one plain dict:
        │   { profile, repos, top_repos, languages, calendar, visitors, total_stars }
        ▼
svg_builder.build_profile_svg(data, theme)
        │   composes:
        │     theme.build_defs()          -> <defs> gradients/filters
        │     components.sidebar.build()
        │     components.terminal.build()
        │     components.stats.build()
        │     components.contribution_graph.build()
        │     components.languages.build()
        │     components.project_cards.build()
        │     components.visitor_counter.build()
        ▼
output/profile.svg   (embedded by README.md)

components.snake.render(data)  -> output/snake.svg, output/snake-dark.svg
```

## Design principles

1. **No network calls outside `data_fetcher.py`.** Every component
   receives already-fetched, plain-Python data. This makes components
   trivially unit-testable and means the whole SVG can be re-rendered
   offline from a cached JSON blob if needed.

2. **No third-party runtime dependencies.** The generator only uses the
   standard library. This keeps the GitHub Action fast (~2s install) and
   removes an entire class of supply-chain risk from a repo that runs on
   a schedule with `contents: write` permissions.

3. **Components are pure functions.** Every `build()` function takes a
   position/size and returns a string — no shared mutable state, no
   classes to instantiate. This is what makes the layout in
   `svg_builder.py` a flat, readable list of function calls.

4. **Colors and fonts flow from one dict.** `config.THEME` is threaded
   through every component; nothing hard-codes a hex value inline
   (aside from a couple of language-brand colors in `languages.py`,
   which intentionally do NOT follow the theme, mirroring GitHub's own
   language-color convention).

5. **Animations are SMIL, not JavaScript.** `<animate>`, `<animateMotion>`
   and `<animateTransform>` all run natively when GitHub (or any static
   `<img>` tag) renders the SVG — no `<script>` tag survives GitHub's
   sanitizer, so JS-based animation would silently do nothing in a
   README. SMIL does not have this limitation.

## Why a fallback for missing `GITHUB_TOKEN`

`data_fetcher.py` returns deterministic sample data when no token is
present (seeded off the username, so it's stable across runs). This lets
contributors preview layout changes locally with
`python -m generator.main` without needing to mint a token first.
