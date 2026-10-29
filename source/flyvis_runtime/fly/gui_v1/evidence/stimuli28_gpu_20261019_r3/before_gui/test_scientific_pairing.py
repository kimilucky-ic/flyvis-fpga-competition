"""Bounded metadata checks; no model, service, camera, board or new activity."""
from copy import deepcopy
import hashlib
from pathlib import Path
import unittest

from data_store import read_json, sha256
from unified_flow import UnifiedFlow, SOURCE_KINDS
from workbench import (IDENTITY_KEYS, scientific_handoff_contract,
                       scientific_pairing_policy)


def tag(text):
    return hashlib.sha256(text.encode()).hexdigest()


def header(mode='Full_GPU'):
    # All invented identifiers below are explicitly CPU protocol fixtures.
    return dict(run_id='CPU_FIXTURE_' + mode, condition_id='CPU_FIXTURE_ON60',
                backend='CPU_PROTOCOL_FIXTURE_NOT_COMPUTATION', mode=mode,
                numeric_family='STRICT_FP32', readout_kind='official_DecoderGAVP',
                readout_sha256=tag('CPU_FIXTURE_readout'),
                intervention_sha256=tag('CPU_FIXTURE_no_intervention'),
                identity_fingerprint={key: tag('CPU_FIXTURE_' + key) for key in IDENTITY_KEYS})


class ScientificPairing(unittest.TestCase):
    def test_same_profile_never_creates_acceptance(self):
        result = scientific_pairing_policy(header(), header('Full_FPGA'))
        self.assertTrue(result['state_equivalence_context_compatible'])
        self.assertTrue(result['functional_pairing_compatible'])
        self.assertIsNone(result['numeric_pass'])
        self.assertIsNone(result['functional_pass'])
        self.assertIsNone(result['hardware_execution_verified'])
        self.assertEqual(result['display_kind'], 'offline_replay')

    def test_mismatched_input_initial_model_mapping_or_time(self):
        for key in ('model', 'expanded', 'node_map', 'stimulus', 'initial', 'time', 'activity_time'):
            with self.subTest(key=key):
                other = header('Full_FPGA')
                other['identity_fingerprint'][key] = tag('different_' + key)
                result = scientific_pairing_policy(header(), other)
                self.assertIn(key, result['mismatched_context'])
                self.assertFalse(result['functional_pairing_compatible'])
                self.assertFalse(result['state_equivalence_context_compatible'])

    def test_fp32_and_q24_are_separate_numeric_references(self):
        other = header('FPGA_Replacement')
        other['numeric_family'] = 'HYBRID_Q24'
        other['identity_fingerprint']['numeric'] = tag('CPU_FIXTURE_Q24_profile')
        result = scientific_pairing_policy(header(), other)
        self.assertTrue(result['functional_pairing_compatible'])
        self.assertFalse(result['state_equivalence_context_compatible'])
        self.assertEqual(result['state_comparison_rule'], 'SEPARATE_NUMERIC_REFERENCE_REQUIRED')

    def test_intervention_is_a_functional_treatment_not_equivalence(self):
        other = header('Sham_Ablation')
        other['intervention_sha256'] = tag('CPU_FIXTURE_T5_block')
        result = scientific_pairing_policy(header(), other)
        self.assertTrue(result['functional_pairing_compatible'])
        self.assertFalse(result['state_equivalence_context_compatible'])

    def test_official_and_local_or_changed_metric_are_not_mixed(self):
        for key in ('readout_kind', 'readout_sha256', 'metrics'):
            with self.subTest(key=key):
                other = header('Python_Replacement')
                if key == 'metrics':
                    other['identity_fingerprint'][key] = tag('different_metric_definition')
                else:
                    other[key] = 'frozen_local_readout' if key == 'readout_kind' else tag('other_readout')
                self.assertFalse(scientific_pairing_policy(header(), other)['functional_pairing_compatible'])

    def test_different_conditions_do_not_become_same_input_comparison(self):
        other = header(); other['condition_id'] = 'CPU_FIXTURE_OFF90'
        self.assertIn('condition_id', scientific_pairing_policy(header(), other)['mismatched_context'])

    def test_incomplete_or_unknown_header_is_rejected(self):
        variants = []
        missing = header(); del missing['identity_fingerprint']['initial']; variants.append(missing)
        bad = header(); bad['readout_sha256'] = 'not-a-hash'; variants.append(bad)
        for key in ('mode', 'numeric_family', 'readout_kind'):
            bad = header(); bad[key] = 'invented'; variants.append(bad)
        for other in variants:
            with self.assertRaises(ValueError): scientific_pairing_policy(header(), other)

    def test_existing_flow_has_requirements_without_admitting_or_running(self):
        flow = UnifiedFlow.__new__(UnifiedFlow)
        flow.presenter = flow.workbench = None; flow.presenter_error = 'CPU fixture: no presenter loaded'
        capabilities = flow.capabilities()
        self.assertEqual(tuple(capabilities['source_kinds']), SOURCE_KINDS)
        self.assertEqual(capabilities['execution']['status'], 'NOT_CONNECTED')
        self.assertEqual(capabilities['scientific_stimuli'], scientific_handoff_contract())
        self.assertEqual(capabilities['scientific_stimuli']['admitted_new_result_packages'], 0)
        self.assertEqual(capabilities['scientific_stimuli']['input_preview']['url'], '/api/controlled-stimuli28')
        self.assertEqual(capabilities['scientific_stimuli']['input_preview']['result_status'], 'NOT_RUN')
        self.assertIn('Full_FPGA', capabilities['scientific_stimuli']['run_header']['modes'])

    def test_saved_p0_fingerprint_uses_the_same_existing_fields(self):
        gui = Path(__file__).resolve().parent
        config = read_json(gui/'phase3.json')
        source = Path(config['input_bundle'])/'video_manifest.json'
        self.assertEqual(sha256(source), config['input_pins']['video_manifest.json'])
        fingerprint = read_json(source)['identity_fingerprint']
        self.assertEqual(set(fingerprint), IDENTITY_KEYS)
        # Reuse actual frozen identities, but never relabel their original run.
        left, right = header(), header('Full_FPGA')
        left['identity_fingerprint'] = deepcopy(fingerprint)
        right['identity_fingerprint'] = deepcopy(fingerprint)
        self.assertTrue(scientific_pairing_policy(left, right)['same_input_context'])
        self.assertIsNone(scientific_pairing_policy(left, right)['hardware_execution_verified'])


if __name__ == '__main__':
    unittest.main()
