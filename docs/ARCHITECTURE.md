# Architecture and engineering trade-offs

This document explains the structural decisions behind the portfolio, and answers the most common
reviewer question: *why ten separate repositories instead of a monorepo?*

## Why multiple repositories

The portfolio is split into independent repositories rather than a single monorepo. This is a
deliberate trade-off, not an accident:

- **Independent installability.** Each repo is a standalone, `pip install`-able package with its own
  pinned dependencies, so a reviewer can clone and run any one of them in isolation without building
  the whole portfolio.
- **Discoverability.** Each project is independently citable and discoverable (its own README,
  topics, and release tags), which suits a portfolio whose goal is to be read by others.
- **Clear dependency boundaries.** The dependencies between projects are explicit `pip` requirements
  (pinned to git tags), which forces clean interfaces between, for example, the simulator and the
  decoders that consume its circuits.

### What a monorepo would buy instead

For a **single, actively-maintained product**, a monorepo would be the better choice. The
counter-argument is:

- A schema or interface change in `surface-code-simulator` currently requires a version bump and a
  re-pin in every downstream repo, rather than a single atomic commit.
- CI runs per-repo rather than once across the whole tree.
- Cross-cutting refactors are harder.

If this codebase were a team-maintained product rather than a portfolio, it would be a monorepo with
a workspace tool (uv / Hatch / Poetry workspaces). The multi-repo layout optimizes for *reviewability
and independent reuse*, which is the actual goal here.

## Dependency and version pinning

Downstream repositories depend on upstream ones via git tags in their `pyproject.toml`, for example:

```toml
dependencies = [
    "surface-code-simulator @ git+https://github.com/afogelis/surface-code-simulator.git@v0.1.0",
]
```

| Repository | Depends on | Notes |
|------------|-----------|-------|
| `surface-code-simulator` | — | Foundation; no portfolio dependencies. |
| `decoder-benchmark` | `surface-code-simulator` | Consumes circuits and metrics. |
| `qec-dashboard` | (artifacts only) | Reads JSON artifacts; no hard code dependency. |
| `ml-qec-decoder` | `surface-code-simulator`, `decoder-benchmark` | Registers ML decoders into the benchmark. |
| `fault-tolerance-economics` | — | Self-contained resource model. |
| `google-surface-code-reproduction` | `surface-code-simulator` | Uses the simulator to extract logical error per cycle. |
| `decoder-accuracy-reproduction` | `surface-code-simulator`, `decoder-benchmark` | Validates the benchmarked MWPM decoder against an exact optimum. |
| `qldpc-builder` | — | Standalone: own GF(2) code construction and BP+OSD decoder. |
| `qec-noise-profiles` | — | Standalone: own toric code, weighted matching and peeling decoder. |
| `active-volume-compiler` | — | Standalone: own circuit model and resource estimator. |

The three frontier repositories (8-10) are deliberately **standalone**: each carries its own code
construction, decoders and resource model so it can be read and run in isolation. They share the
portfolio's engineering conventions but take no dependency on the surface-code foundation.

## Integration testing across repositories

Because the repos are separate, an [integration workflow](../.github/workflows/integration.yml) in
this landing repository installs the core chain (`surface-code-simulator` ->
`decoder-benchmark` -> `decoder-accuracy-reproduction`) in dependency order and runs a smoke test.
The same workflow also installs the three standalone frontier packages and verifies that each
imports and runs a minimal end-to-end check in the shared environment. This proves the published
packages still wire together (and coexist) despite living in separate repositories -- the main risk
the monorepo critique correctly identifies.

## Shared conventions

Every repository follows the same standards so the portfolio reads as one body of work:

- `src/` package layout with a console-script entry point.
- Pydantic v2 typed configuration, receive-an-object / return-an-object interfaces.
- `pytest` suites that exercise the real Stim / PyMatching stack, not mocks.
- `ruff` lint + format, a `pre-commit` config, and GitHub Actions CI across Python 3.10-3.13.
- A committed headline figure in `docs/`, a `CITATION.cff`, and the MIT license.
