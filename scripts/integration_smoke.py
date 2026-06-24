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

    # 4. Frontier repos (8-10) are standalone; verify each coexists and runs a
    # minimal end-to-end check in the same environment.
    _smoke_frontier()
    return 0


def _smoke_frontier() -> None:
    """Best-effort checks that the standalone frontier repos import and run."""
    try:
        from qldpc import build_code, code_capacity_ler

        code = build_code("bb72")
        assert code.num_logicals == 12
        ler = code_capacity_ler(code, p=0.01, shots=50, seed=1, backend="scratch")
        assert 0.0 <= ler.logical_error_rate <= 1.0

        from qecnoise import NoiseProfile, build_toric_code, estimate_logical_error_rate

        toric = build_toric_code(4)
        erasure = estimate_logical_error_rate(
            toric, NoiseProfile(kind="erasure"), p=0.2, shots=50, seed=1
        )
        assert 0.0 <= erasure.logical_error_rate <= 1.0

        from avcompiler import HardwareSpec, analyze_circuit, optimize_factories, ripple_carry_adder

        spec = analyze_circuit(ripple_carry_adder(8))
        result = optimize_factories(spec, HardwareSpec(code_distance=11))
        assert result.best.num_factories >= 1

        print(
            "frontier OK: qldpc-builder, qec-noise-profiles and active-volume-compiler "
            f"all import and run (bb72 k={code.num_logicals}, toric erasure LER="
            f"{erasure.logical_error_rate:.3f}, adder8 optimal factories="
            f"{result.best.num_factories})"
        )
    except ImportError as exc:
        print(f"frontier skipped (standalone repos not installed): {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
