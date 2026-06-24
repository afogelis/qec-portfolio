"""Cross-repository integration smoke test.

Installs of the three core packages (``surface-code-simulator`` ->
``decoder-benchmark`` -> ``decoder-accuracy-reproduction``) are exercised
together to prove the published, separately-versioned repositories still wire
into one pipeline. Run after installing the chain in dependency order:

    python scripts/integration_smoke.py
"""

from __future__ import annotations

import numpy as np


def main() -> int:
    # 1. Foundation: build and sample a tiny surface-code circuit.
    from surfacecode.circuits import build_surface_code_circuit
    from surfacecode.sampling import sample_syndromes
    from surfacecode.types import ExperimentConfig

    config = ExperimentConfig(distance=3, rounds=3, p=0.01, shots=200, seed=7)
    circuit = build_surface_code_circuit(config)
    sample = sample_syndromes(circuit, shots=200, seed=7)
    assert sample.detection_events.shape[0] == 200

    # 2. Decoder benchmark consumes the same circuit and decodes it.
    from decbench.registry import get_decoder

    decoder = get_decoder("mwpm")
    decoder.fit(circuit)
    predictions = decoder.decode_batch(sample.detection_events)
    assert predictions.shape == (sample.num_shots, sample.num_observables)

    # 3. Capstone reproduction computes an exact optimal-vs-MWPM comparison.
    from darepro.accuracy import sweep_accuracy

    results = sweep_accuracy(distances=[3], error_rates=[0.05])
    assert results, "expected at least one enumerable result"
    for r in results:
        assert r.suboptimality_ratio >= 1.0 - 1e-9, "MWPM cannot beat the optimal bound"

    flips = int(np.count_nonzero(np.any(predictions != sample.observable_flips, axis=1)))
    print(
        "integration OK: simulator -> benchmark -> reproduction wired together "
        f"(d=3 mwpm failures={flips}/200, exact suboptimality ratio="
        f"{results[0].suboptimality_ratio:.3f})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
