---
name: photo-blue-background
description: Replace a photo's background with a solid blue RGB(67, 142, 219), the standard ID-photo blue. Use this skill whenever a user asks to change a photo to a blue background, make an ID/passport photo blue-backed, replace the backdrop with blue, or composite a cut-out subject onto blue. Handles both raw photos (with an existing background) and already-cut-out transparent PNGs.
agent_created: true
---

# Photo Blue Background

## Overview

Produce an image whose subject sits on a flat blue background `RGB(67, 142, 219)` (the standard Chinese ID-photo blue). This is a two-stage workflow: first isolate the subject from its original background, then composite it onto the solid blue. The two stages are deliberately separate because background removal alone yields only transparency, never a colored backdrop.

## Workflow Decision Tree

- **Input is a raw photo with a visible background** → run Stage 1 (matting) then Stage 2 (composite).
- **Input is already a transparent PNG cut-out** → skip Stage 1, go straight to Stage 2.
- **User requests a different background color** → still follow this workflow, but pass `--color R,G,B` to Stage 2. The default is always `67,142,219`.

Confirm the input image path before starting. Local image files must be non-empty and under 4 MB for the matting service.

## Stage 1 — Cut out the subject (only for photos with a background)

Load the `buddy-image-processing` skill via the Skill tool and follow its instructions exactly to run the `matting` operation on the user's photo:

1. Call `connect_cloud_service` once to obtain `clientTempToken`; use only that token and stop if it is missing.
2. Run its `image-edit` with `--operation matting --image-file "<absolute path>" --token "<clientTempToken>"`.
3. Read `result_files[].path` from the output — this is the transparent-background PNG to feed into Stage 2.

Never claim that matting alone completed a blue background. Never retry a timed-out `image-edit` submission; if submission times out before a task id, report `SUBMISSION_STATUS_UNKNOWN`. Never display, cache, or reuse credentials.

If the user has already supplied a transparent cut-out, note its path and proceed to Stage 2.

## Stage 2 — Composite onto the blue background

Use the bundled script. It is self-contained and installs Pillow automatically if missing.

```bash
python3 <SKILL_DIR>/scripts/compose_blue_bg.py \
  --input "<path to transparent cut-out PNG>" \
  --output "<desired output path>" \
  --color 67,142,219
```

- `--input` / `-i` (required): the transparent cut-out image.
- `--output` / `-o` (optional): output path. Defaults to `<input>_blue.<ext>`.
- `--color` / `-c` (optional): background color `R,G,B`. Default `67,142,219`.
- `--format` / `-f` (optional): output format; inferred from the output suffix otherwise.

Use `python` instead of `python3` if `python3` is unavailable. The script converts the input to RGBA, creates a solid background of the requested color, alpha-composites the foreground over it, and saves an RGB image. It exits with an error if the input is fully opaque (no alpha), which means Stage 1 was skipped for a photo that still has its background.

Finally, call `present_files` with the output path and report the full path to the user.

## Resources

### scripts/
- `compose_blue_bg.py` — composites a transparent cut-out onto a solid color background; default `RGB(67, 142, 219)`.
