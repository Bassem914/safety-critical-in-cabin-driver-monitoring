from decision.temporal_rules import (
    TemporalRuleConfig,
    TemporalRuleEngine,
    TemporalState,
)


def print_result(
    label: str,
    result,
) -> None:
    """Print one temporal test result."""

    print(
        f"{label:<30} "
        f"state={result.primary_state.value:<28} "
        f"EAR={result.smoothed_ear} "
        f"MAR={result.smoothed_mar} "
        f"eye={result.eye_closure_duration_seconds:.2f}s "
        f"mouth={result.mouth_open_duration_seconds:.2f}s "
        f"face_loss={result.face_loss_duration_seconds:.2f}s "
        f"blink={result.blink_detected}"
    )


def run_normal_sequence(
    engine: TemporalRuleEngine,
) -> None:
    """Verify the normal visible-face state."""

    engine.reset()

    result = engine.update(
        timestamp_seconds=0.00,
        face_detected=True,
        ear=0.30,
        mar=0.30,
    )

    print_result("Normal face", result)

    assert result.primary_state is TemporalState.NORMAL
    assert result.blink_detected is False


def run_blink_sequence(
    engine: TemporalRuleEngine,
) -> None:
    """Verify detection of a short completed eye closure."""

    engine.reset()

    engine.update(
        timestamp_seconds=0.00,
        face_detected=True,
        ear=0.30,
        mar=0.30,
    )

    engine.update(
        timestamp_seconds=0.10,
        face_detected=True,
        ear=0.10,
        mar=0.30,
    )

    engine.update(
        timestamp_seconds=0.20,
        face_detected=True,
        ear=0.10,
        mar=0.30,
    )

    result = engine.update(
        timestamp_seconds=0.30,
        face_detected=True,
        ear=0.30,
        mar=0.30,
    )

    print_result("Blink candidate", result)

    assert result.primary_state is TemporalState.BLINK_CANDIDATE
    assert result.blink_detected is True


def run_prolonged_eye_closure_sequence(
    engine: TemporalRuleEngine,
) -> None:
    """Verify prolonged eye-closure detection."""

    engine.reset()

    engine.update(
        timestamp_seconds=0.00,
        face_detected=True,
        ear=0.30,
        mar=0.30,
    )

    engine.update(
        timestamp_seconds=0.10,
        face_detected=True,
        ear=0.10,
        mar=0.30,
    )

    result = engine.update(
        timestamp_seconds=1.70,
        face_detected=True,
        ear=0.10,
        mar=0.30,
    )

    print_result("Prolonged eye closure", result)

    assert (
        result.primary_state
        is TemporalState.PROLONGED_EYE_CLOSURE
    )


def run_sustained_mouth_opening_sequence(
    engine: TemporalRuleEngine,
) -> None:
    """Verify sustained mouth-opening detection."""

    engine.reset()

    engine.update(
        timestamp_seconds=0.00,
        face_detected=True,
        ear=0.30,
        mar=0.30,
    )

    engine.update(
        timestamp_seconds=0.10,
        face_detected=True,
        ear=0.30,
        mar=0.80,
    )

    result = engine.update(
        timestamp_seconds=1.20,
        face_detected=True,
        ear=0.30,
        mar=0.80,
    )

    print_result("Sustained mouth opening", result)

    assert (
        result.primary_state
        is TemporalState.SUSTAINED_MOUTH_OPENING
    )


def run_face_loss_sequence(
    engine: TemporalRuleEngine,
) -> None:
    """Verify prolonged face-loss detection."""

    engine.reset()

    engine.update(
        timestamp_seconds=0.00,
        face_detected=True,
        ear=0.30,
        mar=0.30,
    )

    engine.update(
        timestamp_seconds=0.10,
        face_detected=False,
        ear=None,
        mar=None,
    )

    result = engine.update(
        timestamp_seconds=1.20,
        face_detected=False,
        ear=None,
        mar=None,
    )

    print_result("Prolonged face loss", result)

    assert (
        result.primary_state
        is TemporalState.PROLONGED_FACE_LOSS
    )


def run_invalid_timestamp_sequence(
    engine: TemporalRuleEngine,
) -> None:
    """Verify rejection of decreasing source timestamps."""

    engine.reset()

    engine.update(
        timestamp_seconds=1.00,
        face_detected=True,
        ear=0.30,
        mar=0.30,
    )

    try:
        engine.update(
            timestamp_seconds=0.50,
            face_detected=True,
            ear=0.30,
            mar=0.30,
        )

    except ValueError:
        print(
            f"{'Invalid timestamp':<30} "
            "correctly rejected"
        )
        return

    raise AssertionError(
        "A decreasing timestamp should raise ValueError."
    )

def run_blink_display_hold_sequence(
    engine: TemporalRuleEngine,
) -> None:
    """Verify blink-state display hold and expiration."""

    engine.reset()

    engine.update(
        timestamp_seconds=0.00,
        face_detected=True,
        ear=0.30,
        mar=0.30,
    )

    engine.update(
        timestamp_seconds=0.10,
        face_detected=True,
        ear=0.10,
        mar=0.30,
    )

    engine.update(
        timestamp_seconds=0.25,
        face_detected=True,
        ear=0.10,
        mar=0.30,
    )

    blink_result = engine.update(
        timestamp_seconds=0.35,
        face_detected=True,
        ear=0.30,
        mar=0.30,
    )

    assert blink_result.blink_detected is True
    assert (
        blink_result.primary_state
        is TemporalState.BLINK_CANDIDATE
    )

    held_result = engine.update(
        timestamp_seconds=0.60,
        face_detected=True,
        ear=0.30,
        mar=0.30,
    )

    print_result("Blink display held", held_result)

    assert held_result.blink_detected is False
    assert (
        held_result.primary_state
        is TemporalState.BLINK_CANDIDATE
    )

    expired_result = engine.update(
        timestamp_seconds=0.80,
        face_detected=True,
        ear=0.30,
        mar=0.30,
    )

    print_result("Blink display expired", expired_result)

    assert expired_result.blink_detected is False
    assert expired_result.primary_state is TemporalState.NORMAL

def main() -> None:
    """
    Run deterministic temporal-rule smoke tests.
    """

    config = TemporalRuleConfig(
        eye_closed_ear_threshold=0.20,
        mouth_open_mar_threshold=0.60,
        blink_min_duration_seconds=0.08,
        blink_max_duration_seconds=0.50,
        prolonged_eye_closure_seconds=1.50,
        sustained_mouth_opening_seconds=1.00,
        prolonged_face_loss_seconds=1.00,
        smoothing_window_size=1,
    )

    engine = TemporalRuleEngine(config=config)

    run_normal_sequence(engine)
    run_blink_sequence(engine)
    run_blink_display_hold_sequence(engine)
    run_prolonged_eye_closure_sequence(engine)
    run_sustained_mouth_opening_sequence(engine)
    run_face_loss_sequence(engine)
    run_invalid_timestamp_sequence(engine)

    print()
    print("[PASS] All temporal-rule smoke tests passed.")


if __name__ == "__main__":
    main()