Vendored from Yuan1z0825/nature-skills, commit 14ca69710cae192325395a380e9cdd4ae5d9d0c8, skills/nature-figure/scripts/.
Source: https://github.com/Yuan1z0825/nature-skills/tree/14ca69710cae192325395a380e9cdd4ae5d9d0c8
License: Apache-2.0; original LICENSE retained alongside scripts.
Only three auditors are included; upstream workflow instructions are not adopted.

Local patch (after-v2, 2026-11-17): audit_figure_collisions.py tracks explicit rectangular clipping scopes and rejects wholly clipped text/stroke candidates. Ordinary drawing indexes and upstream checks are retained. Complex clips and partially clipped intersections are not solved. See LOCAL_PATCH.md.
