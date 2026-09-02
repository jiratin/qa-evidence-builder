# Application icon assets

The master artwork is `qa-evidence-builder-master.png`, supplied and approved
for this project by Guide Jir on 2026-09-02.

Packaged outputs:

- `qa-evidence-builder.ico` — Windows executable icon
- `qa-evidence-builder.icns` — macOS application icon
- `png/` — runtime and standard-size PNG icons

To rebuild ICO and ICNS containers after regenerating the PNG sizes, run:

```bash
python scripts/package_icons.py
```
