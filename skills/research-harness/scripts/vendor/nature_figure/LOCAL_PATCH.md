# Local rectangular-clip exclusion

Only `audit_figure_collisions.py` differs from the pinned upstream auditors. Extraction adds the active explicit one-rectangle clip stack to each stroke, using extended drawing sequence numbers while retaining ordinary drawing indexes. A text/stroke candidate is excluded only when the full text box is disjoint from an enclosing explicit rectangle. Nested scopes expire at their recorded hierarchy level. This resolves invisible path portions without moving figure labels.

This is not full clipping support. Complex clip shapes are not interpreted; known enclosing rectangles remain safe exclusion constraints. Partial clipping remains subject to the original segment test. Filled-region clipping, text clipping within paths, dashed lines, and opacity groups are unchanged. No universal font threshold or scientific acceptance rule is added. No-text reports retain NOT AUDITABLE (unknown), not PASS. Requires a PyMuPDF version supporting extended drawing extraction; verified with 1.26.5.

Original copyright and Apache-2.0 LICENSE are retained. The source commit is recorded in UPSTREAM.md.
