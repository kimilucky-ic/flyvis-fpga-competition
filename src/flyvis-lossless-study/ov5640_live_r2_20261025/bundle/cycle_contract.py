"""Pinned DDR phase counter contract, not wall-clock FPS or legacy MMIO count."""
EXPECTED_CYCLES=2199975
LEGACY_MMIO_CYCLES=2201418

def check_cycles(actual):
    if type(actual) is not int or not 0<actual<2**32:raise ValueError('Invalid DDR cycle count')
    return dict(counter='DDR_PHASE_NONZERO_UNTIL_NEURAL_DONE',actual_cycles=actual,
        expected_cycles=EXPECTED_CYCLES,matches=actual==EXPECTED_CYCLES,
        nominal_clock_hz=100000000,nominal_core_phase_ms=actual/100000,
        physical_frequency_measured=False,full_step_wall_time=False,
        evidence_source='ddr_soc_20261018/AUDIT.json and operator record b0a5cd8079b045bdb1b97c07523c6c55',
        excludes=['phase0 input feed','final DDR publication','PS processing','camera acquisition','PC display'])
