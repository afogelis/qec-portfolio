# Quantum Error Correction Portfolio

A ten-part portfolio of quantum-error-correction software, built to demonstrate research-engineering
ability across simulation, decoding algorithms, machine learning, observability, resource modelling,
reproduction of landmark results, and the frontier topics of qLDPC codes, hardware-realistic noise,
and fault-tolerant compilation. Every repository is independently installable, tested, and CI-ready.

Common stack: [Stim](https://github.com/quantumlib/Stim) (stabilizer simulation),
[PyMatching](https://pymatching.readthedocs.io/) (MWPM), Pydantic v2 typed configs, pytest, and
GitHub Actions CI. Each repo follows the same `src/` layout, RORO interfaces, and MIT license.

## What this is, and what it is not

**This is:** reproducible research software. It reproduces two published results from scratch,
implements decoders (union-find, belief propagation, and an exact maximum-likelihood decoder) by
hand to study their behaviour, and turns physics into decision-ready resource estimates. The
engineering is production-grade: typed configs, tests against the real Stim/PyMatching stack, and CI
across four Python versions.

**This is not:** a new QEC theory result, a replacement for Stim or PyMatching, or a production
decoder stack. The foundational simulator (repo 1) is an *experiment pipeline* built on Stim and
PyMatching, not a re-implementation of them. The genuinely algorithmic contribution is the **exact
maximum-likelihood decoder** in repo 7, which measures how far minimum-weight perfect matching sits
from optimal without any Monte Carlo sampling error, and the **from-scratch peeling decoder** in repo
9, which reproduces the analytic 0.5 erasure threshold. Engineering trade-offs (including why this is
ten repos rather than a monorepo) are documented in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## The repositories

Start with the capstones; they show the ability to reproduce published research and to implement a
provably-optimal decoder. The foundation and tooling repos underneath are the infrastructure they
build on.

### Capstones (start here)

| # | Repository | What it does | Highlight |
|---|-----------|--------------|-----------|
| 7 | [`decoder-accuracy-reproduction`](decoder-accuracy-reproduction/) | Exact maximum-likelihood vs MWPM decoder comparison by error-pattern enumeration (arXiv:2311.12503). | Sampling-free: MWPM provably optimal at d=3, quantifiably sub-optimal at d=5. |
| 6 | [`google-surface-code-reproduction`](google-surface-code-reproduction/) | Simulation reproduction of Google's Nature 2023 scaling result. | Reproduces error suppression Lambda ~ 2.2 below threshold. |

### Foundation and tooling

| # | Repository | What it does | Highlight |
|---|-----------|--------------|-----------|
| 1 | [`surface-code-simulator`](surface-code-simulator/) | Infrastructure layer: circuit-level surface-code Monte Carlo pipeline on Stim + PyMatching (build, sample, decode, threshold). | Clean threshold crossing at p_th ~ 0.6%. |
| 2 | [`decoder-benchmark`](decoder-benchmark/) | Benchmark MWPM vs from-scratch union-find and belief propagation, with separate accuracy and runtime tiers and an optional BP-OSD reference. | Plain BP dominated on accuracy; BP-OSD competitive. |
| 5 | [`fault-tolerance-economics`](fault-tolerance-economics/) | Resource/cost model: how many qubits to break RSA-2048 with Shor. | Reproduces ~20M qubits / ~8 hours (Gidney-Ekera). |
| 4 | [`ml-qec-decoder`](ml-qec-decoder/) | A controlled negative study: when do tabular/geometry-aware ML decoders fail against MWPM? | Calibrated finding: ML competitive at d=3, fails at d=5. |
| 3 | [`qec-dashboard`](qec-dashboard/) | Streamlit artifact viewer over simulation/benchmark outputs (demo/observability). | Decoupled JSON data contracts + bundled sample data. |

### Frontier extensions (qLDPC, noise, compilation)

These are independent, advanced topics that round out the portfolio beyond the surface code.

| # | Repository | What it does | Highlight |
|---|-----------|--------------|-----------|
| 8 | [`qldpc-builder`](https://github.com/afogelis/qldpc-builder) | Build bivariate/generalized-bicycle qLDPC codes; decode with a from-scratch BP+OSD; benchmark encoding rate vs the surface code. | High-rate codes match the surface baseline's logical error rate at several times the rate. |
| 9 | [`qec-noise-profiles`](https://github.com/afogelis/qec-noise-profiles) | Biased Pauli noise (weighted matching) and heralded erasure (from-scratch peeling) on the toric code. | Reproduces the analytic 0.5 erasure threshold vs ~0.16 depolarizing. |
| 10 | [`active-volume-compiler`](https://github.com/afogelis/active-volume-compiler) | Compile a Clifford+T circuit to a surface-code layout and optimise the magic-state factory ratio. | Volume-optimal factory count at the factory/logic runtime crossover. |

## Suggested reading order

For a reviewer with limited time: **7 -> 6 -> 9 -> 8 -> 2 -> 1 -> 10 -> 5 -> 4 -> 3**. Repos 7 and
6 reproduce published research and implement an optimal decoder; 9 and 8 implement from-scratch
qLDPC/erasure decoders with analytically-checkable thresholds; 2 and 1 show the core decoding and
simulation engineering; 10 and 5 show fault-tolerant compilation and quantitative modelling; 4 and 3
show an honest ML study and productisation.

## Dependency graph

```mermaid
flowchart TD
  P1[surface-code-simulator] --> P2[decoder-benchmark]
  P1 --> P6[google-surface-code-reproduction]
  P2 --> P4[ml-qec-decoder]
  P1 --> P4
  P2 --> P7[decoder-accuracy-reproduction]
  P1 --> P7
  P1 --> P3[qec-dashboard]
  P2 --> P3
  P4 --> P3
  P8[qldpc-builder]
  P9[qec-noise-profiles]
  P10[active-volume-compiler]
```

Repos 8, 9 and 10 are deliberately standalone: each is self-contained (its own code construction,
decoders and resource model) so it can be read and run without the surface-code foundation.

## Quick start

Each repository is standalone:

```bash
cd surface-code-simulator
pip install -e ".[dev]"
pytest
```

For the repos that depend on siblings (2, 3, 4, 7), install the upstream repos editable into the
same environment first; see each repo's README for the exact commands.

## Test status

All repositories pass their test suites locally (Python 3.10-3.14):

- surface-code-simulator: 15 passed
- decoder-benchmark: 16 passed, 1 skipped (BP-OSD, optional `ldpc` dependency)
- ml-qec-decoder: 7 passed
- qec-dashboard: 4 passed
- fault-tolerance-economics: 7 passed
- google-surface-code-reproduction: 4 passed
- decoder-accuracy-reproduction: 4 passed
- qldpc-builder: 21 passed
- qec-noise-profiles: 18 passed
- active-volume-compiler: 10 passed

## Write-ups

Long-form, paper-structured write-ups of each project (plus this overview) live in
[`writeups/`](writeups/), as both Markdown (for reading on GitHub) and downloadable Word documents,
each with embedded result figures:

| # | Write-up | Markdown | Word |
|---|----------|----------|------|
| - | Portfolio overview | [md](writeups/md/00_portfolio_overview.md) | [docx](writeups/docx/00_portfolio_overview.docx) |
| 1 | Surface-code simulator | [md](writeups/md/01_surface_code_simulator.md) | [docx](writeups/docx/01_surface_code_simulator.docx) |
| 2 | Decoder benchmark | [md](writeups/md/02_decoder_benchmark.md) | [docx](writeups/docx/02_decoder_benchmark.docx) |
| 3 | QEC dashboard | [md](writeups/md/03_qec_dashboard.md) | [docx](writeups/docx/03_qec_dashboard.docx) |
| 4 | ML QEC decoder | [md](writeups/md/04_ml_qec_decoder.md) | [docx](writeups/docx/04_ml_qec_decoder.docx) |
| 5 | Fault-tolerance economics | [md](writeups/md/05_fault_tolerance_economics.md) | [docx](writeups/docx/05_fault_tolerance_economics.docx) |
| 6 | Google reproduction | [md](writeups/md/06_google_reproduction.md) | [docx](writeups/docx/06_google_reproduction.docx) |
| 7 | Decoder accuracy reproduction | [md](writeups/md/07_decoder_accuracy_reproduction.md) | [docx](writeups/docx/07_decoder_accuracy_reproduction.docx) |
| 8 | qLDPC builder | [md](writeups/md/08_qldpc_builder.md) | [docx](writeups/docx/08_qldpc_builder.docx) |
| 9 | QEC noise profiles | [md](writeups/md/09_qec_noise_profiles.md) | [docx](writeups/docx/09_qec_noise_profiles.docx) |
| 10 | Active volume compiler | [md](writeups/md/10_active_volume_compiler.md) | [docx](writeups/docx/10_active_volume_compiler.docx) |

All write-ups are regenerated from [`writeups/generate_writeups.py`](writeups/generate_writeups.py).

## License

All repositories are released under the MIT License.
