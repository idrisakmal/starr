# radarr-custom

Radarr custom formats and quality profiles that **Recyclarr cannot manage**.

Recyclarr only syncs custom formats that exist in the TRaSH Guides (referenced
by `trash_id`). The formats/profile here are hand-made, so they're version
controlled in this repo and applied directly through the Radarr API instead.

Recyclarr leaves these alone: `delete_old_custom_formats: true` only deletes
formats Recyclarr itself created (tracked in `recyclarr/state/`), and it only
touches quality profiles listed in `recyclarr.yml`. Neither applies here.

## Contents

| File | What it is |
|------|-----------|
| `custom-formats/YIFY.json` | Matches YIFY/YTS by release group **or** title. |
| `custom-formats/Non-YIFY-2160p.json` | Matches 2160p releases that are **not** YIFY/YTS. Used to keep non-YIFY 4K out of the YIFY profile. |
| `quality-profiles/YIFY.json` | "Prefer YIFY, else something better" profile. Prefers YIFY at 2160p→1080p→720p; blocks non-YIFY 4K; falls back to the best non-YIFY ≤1080p. |
| `quality-definitions.json` | Quality definitions with **all `minSize` = 0**. Required so small YIFY rips aren't rejected as "too small." Recyclarr's `radarr-quality-definition-movie` template is disabled in `recyclarr.yml` because its ~50 MB/min floor rejected YIFY. |

Custom format scores in the profile are stored **by name** (`customFormatScores`)
and resolved to live format IDs at apply time.

## Apply

```bash
# Uses ../.env for RADARR_API_KEY, default URL http://localhost:7878
python3 radarr-custom/apply.py

# or explicitly
RADARR_URL=http://localhost:7878 RADARR_API_KEY=xxxx python3 radarr-custom/apply.py
```

Idempotent: creates what's missing, updates what exists (matched by name).

## How to use the YIFY profile

Set a movie's **Quality Profile → YIFY** (per movie or via bulk edit) when you
want the small YIFY rip. Everything else stays on your normal profile
(`Remux + WEB 2160p`).
