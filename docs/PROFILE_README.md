# Hi, I'm Andrew Fogelis

I build **quantum error correction (QEC) software**: stabilizer simulators, decoders implemented from
scratch, hardware-realistic noise models, and the resource/economics models that turn physics into
engineering decisions.

My work is organized as a **[ten-part QEC research portfolio](https://github.com/afogelis/qec-portfolio)**.
Start there for the full narrative, the dependency graph, and reproducible results. The repositories
group into three layers:

## The physics core — simulation and noise

| Repo | What it is |
|------|------------|
| [`surface-code-simulator`](https://github.com/afogelis/surface-code-simulator) | Circuit-level surface-code Monte Carlo pipeline on Stim + PyMatching. Clean threshold crossing at p_th ~ 0.6%. |
| [`qec-noise-profiles`](https://github.com/afogelis/qec-noise-profiles) | Biased-Pauli and heralded-erasure noise on the toric code. Reproduces the analytic 0.5 erasure threshold. |
| [`google-surface-code-reproduction`](https://github.com/afogelis/google-surface-code-reproduction) | Simulation reproduction of Google's Nature 2023 scaling result (error suppression Lambda ~ 2.2). |

## The algorithmic layer — decoders, ML, and qLDPC codes

| Repo | What it is |
|------|------------|
| [`decoder-benchmark`](https://github.com/afogelis/decoder-benchmark) | MWPM vs from-scratch union-find and belief propagation, split into accuracy and runtime tiers. |
| [`decoder-accuracy-reproduction`](https://github.com/afogelis/decoder-accuracy-reproduction) | Exact maximum-likelihood vs MWPM by error-pattern enumeration — sampling-free optimality bounds. |
| [`qldpc-builder`](https://github.com/afogelis/qldpc-builder) | Bivariate/generalized-bicycle qLDPC code construction with a from-scratch BP+OSD decoder. |
| [`ml-qec-decoder`](https://github.com/afogelis/ml-qec-decoder) | A controlled negative study: when do ML decoders fail against MWPM? (They fail at d=5.) |

## The strategy and presentation layer — compilation, economics, observability

| Repo | What it is |
|------|------------|
| [`active-volume-compiler`](https://github.com/afogelis/active-volume-compiler) | Compile Clifford+T circuits to a surface-code layout; optimize the magic-state factory ratio. |
| [`fault-tolerance-economics`](https://github.com/afogelis/fault-tolerance-economics) | Resource model: ~20M qubits / ~8 hours to break RSA-2048 (reproduces Gidney-Ekera). |
| [`qec-dashboard`](https://github.com/afogelis/qec-dashboard) | Streamlit artifact viewer over simulation and benchmark outputs. |

## How it fits together

```
                 physics core
   surface-code-simulator ──► decoder-benchmark ──► decoder-accuracy-reproduction
            │                      │       ▲                 (capstone)
            │                      │       ╎ matrix/Stim export
            ▼                      ▼       ╎
   google-reproduction      ml-qec-decoder  qldpc-builder
            │                      │
            └──────────► qec-dashboard (artifact viewer)

   standalone frontier:  qec-noise-profiles   active-volume-compiler
```

Every repository is independently `pip install`-able (cross-repo dependencies pinned to git tags),
tested with pytest, and runs CI across Python 3.10–3.14.

**Common stack:** [Stim](https://github.com/quantumlib/Stim), [PyMatching](https://pymatching.readthedocs.io/),
NumPy/SciPy, Pydantic v2, pytest, GitHub Actions.

Read the full story → **[github.com/afogelis/qec-portfolio](https://github.com/afogelis/qec-portfolio)**
