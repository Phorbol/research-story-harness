# Synthetic software fixture

Created for this public package using ASE `fcc100("Cu", size=(4,4,4), a=3.6, vacuum=6.0)`, with in-plane periodicity and all substrate tags set to 0. Three display objects C/O/H (tags 2) were placed at arbitrary positions above the surface. The four named states apply small arbitrary coordinate offsets.

These coordinates are not measured data, optimized structures, transition states, a reaction pathway, or a reconstruction of a measured surface. They test atom identity, periodic display copies, camera registration, style overrides, and read-only preparation.

Copy this directory to a project before rendering. From the repository root, run `python skills/ovito-structure/scripts/surface_render.py <copied-example>/job.json --verify-only`, then use `--preview` when actual graphics are needed.
