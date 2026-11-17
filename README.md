# photo-blue-background

A [WorkBuddy](https://www.workbuddy.cn/) skill that replaces a photo's background with a solid blue `RGB(67, 142, 219)` — the standard ID-photo blue.

## What it does

1. Cut out the subject from the original photo (`matting` via WorkBuddy's built-in image processing).
2. Composite the transparent cut-out onto a solid blue background using `scripts/compose_blue_bg.py`.

If the input is already a transparent PNG cut-out, step 1 is skipped.

## Install

Copy this folder into your WorkBuddy skills directory:

```
~/.workbuddy/skills/photo-blue-background/
```

Then just say something like "把这张照片换成蓝底" in WorkBuddy and provide the photo.

## Script usage

```bash
python3 scripts/compose_blue_bg.py -i cutout.png -o result.png -c 67,142,219
```

- `-i` / `--input`: transparent (RGBA) cut-out image.
- `-o` / `--output`: output path (default `<input>_blue.<ext>`).
- `-c` / `--color`: background color `R,G,B` (default `67,142,219`).
- `-f` / `--format`: output format (inferred from output suffix).

The script auto-installs Pillow if missing and errors out if the input has no transparency.

## License

MIT
