# Godot Game Skills contributor guidance

This is a portable agent-skills package for Godot 4, primarily procedural 3D games.
Keep each skill independently installable: runtime helpers and references belong
inside that skill's folder. Repository maintenance tools may live in `scripts/`.
Do not introduce dependencies on the game this package was extracted from,
personal paths, paid services, or a particular agent/model.

Preserve user scope, renderer, art direction and existing test framework. Explain
the smallest relevant check before implementation. Use original small examples;
do not bundle third-party game assets. Keep factual compatibility claims tied to
actual checks. Headless assertions do not establish visual quality or GPU speed.

Use Python's standard library for portable helpers and unittest for their tests.
Use explicit `preload` references in the small Godot example so a fresh checkout
does not depend on an existing editor class cache. Check subprocess exit codes,
Godot error output, timeout behavior, and expected success markers separately.

Run `python3 scripts/validate_package.py` and the relevant unittest module after
changes. Example checks use the packaged runner and example manifest described
in README.md. Do not change a golden expectation merely to silence a failure.
