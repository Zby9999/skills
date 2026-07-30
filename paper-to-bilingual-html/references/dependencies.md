# Runtime Dependencies

Read this reference on the first run on a machine, or whenever the dependency preflight fails. Run commands from the skill root.

## Required

- Python 3.10 or newer.
- PyMuPDF, installed as the `pymupdf` package and imported as `fitz`.
- An image-viewing capability for the mandatory visual inspection of every extracted figure and table.

The extraction script does not require Poppler, `pdftotext`, Pillow, OpenCV, Chrome, or Playwright. `pdftotext` is an optional source-recovery route; use PyMuPDF when it is unavailable. The bundled Geist and IBM Plex Serif font files require no system installation.

## Preflight

Choose the first available Python launcher:

- macOS/Linux: `python3`, then `python`
- Windows: `py -3`, then `python`

Use that same interpreter for installation and every later script command. It is ready only when both checks pass:

```bash
python3 -c 'import sys, fitz; assert sys.version_info >= (3, 10), sys.version; print(sys.version.split()[0], fitz.version[0])'
python3 scripts/extract_figures.py --help
```

Replace `python3` with the selected launcher when necessary.

## Acquire Missing Dependencies

If a suitable Python environment already exists, install PyMuPDF into that environment:

```bash
python3 -m pip install pymupdf
```

Otherwise, prefer a task-local virtual environment so the installation does not alter the machine-wide Python environment.

macOS/Linux:

```bash
python3 -m venv .paper-html-venv
.paper-html-venv/bin/python -m pip install pymupdf
.paper-html-venv/bin/python -c 'import sys, fitz; assert sys.version_info >= (3, 10); print(sys.version.split()[0], fitz.version[0])'
.paper-html-venv/bin/python scripts/extract_figures.py --help
```

Windows:

```powershell
py -3 -m venv .paper-html-venv
.paper-html-venv\Scripts\python.exe -m pip install pymupdf
.paper-html-venv\Scripts\python.exe -c "import sys, fitz; assert sys.version_info >= (3, 10); print(sys.version.split()[0], fitz.version[0])"
.paper-html-venv\Scripts\python.exe scripts\extract_figures.py --help
```

Follow the host environment's approval policy before installing software or accessing the network. If Python itself is missing, use the platform-approved Python installer or package manager, then repeat the preflight. If package download is blocked, request network access or a compatible PyMuPDF wheel from the user; do not report the dependency as ready until both checks pass.

## Capability Gate

Before extracting figures, confirm that the agent can open the generated PNG files at readable resolution. If no image-viewing capability is available, extraction may proceed, but the final HTML is blocked because the required crop inspection cannot be completed.
