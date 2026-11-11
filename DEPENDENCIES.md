# Runtime and dependencies / 运行环境

Use **Python 3.11 or newer** for the combined bundle; Python 3.12 is the locally exercised version. The writing-state manager itself uses only the standard library and supports Python 3.9+, but the pinned slide runtime requires Python >=3.11.

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python install_skills.py --dest ./installed-skills
```

Windows: activate with `.venv\Scripts\activate`. The installer copies all 11 skills and their resources; it does not install Python dependencies and refuses to overwrite existing skills. Omit `--dest` to use `CODEX_HOME/skills`, or `~/.codex/skills` when CODEX_HOME is unset.

| Workflow | Dependencies |
|---|---|
| Writing state, source metadata and structured review | Python standard library; source retrieval needs network access only when invoked |
| Figure rendering and portable tests | `requirements.txt`: Matplotlib 3.9.4, ASE 3.26.0, PyMuPDF 1.26.5, PyYAML 6.0.3, with their package dependencies |
| Actual 3D rendering | `python -m pip install -r requirements-3d.txt` adds OVITO 3.16.0; platform graphics/runtime support is also needed |
| Re-extract condition-map HDF5 sources | `python -m pip install -r requirements-source-data.txt` adds h5py >=3.10; normal example plotting uses included CSVs |
| Native editable-slide export | The bundled ansatz-slide Python CLI and PyYAML; no separate deck exporter is needed |
| Slide PDF/PNG visual previews | A supported Office/LibreOffice renderer and the fonts used by the deck; availability depends on the host |

Matplotlib brings NumPy and Pillow as transitive dependencies. ASE enables structure preparation without requiring an OVITO render. PyMuPDF is included in root requirements for reference PDF intake and tests; users running only standard-library writing commands do not need plotting dependencies. The two bundled public examples render from their included CSV/image assets with the root plotting environment.

No paid API key, model checkpoint or paper download is required for the deterministic helpers. Research interpretation and skill execution are performed by the user's agent host; network search and optional host tools remain separate capabilities. The scripts do not install or configure an agent model.

## Entry points

```bash
# Figure project with explicit synthetic demo inputs
python skills/research-harness/scripts/research.py init work/demo --demo
python skills/research-harness/scripts/research.py check work/demo/research.json
python skills/research-harness/scripts/research.py render work/demo/research.json --out work/demo/build

# Writing state (draft export paths must be inside the project)
python skills/argument-architect/scripts/academic_harness.py --project work/writing init
python skills/argument-architect/scripts/academic_harness.py --project work/writing audit
# After registering source/claim/unit records using the shared schemas:
python skills/argument-architect/scripts/academic_harness.py --project work/writing export work/writing/draft.md

# Editable-slide source format and export
python skills/ansatz-slide/scripts/ansatz_slide.py validate path/to/pptx.yaml
python skills/ansatz-slide/scripts/ansatz_slide.py export path/to/pptx.yaml --offline -o path/to/deck.pptx
python skills/ansatz-slide/scripts/ansatz_slide.py inspect path/to/deck.pptx
```

The slide `pyproject.toml`/`uv.lock` describe its standalone uv environment (`package = false`); they are not a promise that `pip install -e skills/ansatz-slide` registers a global CLI. Use the bundled script path shown above.

Dependencies retain their upstream licensing terms. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Local verification used an existing environment, not a fresh installation on every supported platform; exact observed versions and limits are in [VERIFICATION.md](VERIFICATION.md).
