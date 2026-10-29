"""Serialize the review plan and exact resource arithmetic; never run neurons."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil

HERE = Path(__file__).resolve().parent
P3 = HERE.parent / "phase3_ablation_screen_20261010"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def dump(p, x):
    with Path(p).open("x", encoding="utf-8", newline="\n") as f:
        json.dump(x, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    audit = load(HERE / "SOURCE_AUDIT.json")
    old = load(P3 / "spec_snapshot/spec_config.json")
    timing = load(P3 / "artifacts/final_delivery/timing.json")
    counts = dict(candidates=2, conditions=24, steps_per_condition=485,
                  replacement_modes=2, replacement_process_repeats=2,
                  shared_Full_reference_repeats=2, n_nodes=45669)
    replacement_runs = 2 * 24 * 2 * 2
    full_runs = 24 * 2
    payload = 24 * 485 * 45669 * 4
    raw_h_io = sum((c["n_incoming_source_R"] + 4*c["n_H"]) * 24 * 485 * 4 * 4
                   for c in audit["candidates"].values())
    old_times = [p["wall_s"] for p in timing["process_results"]]
    extrapolated_s = sum(old_times) * (replacement_runs / 48)
    free = shutil.disk_usage(HERE).free
    budget = dict(schema="flyvis-phase4-resource-budget/review-v1", status="ESTIMATE_FOR_APPROVAL_NOT_BENCHMARK",
        counts=counts, replacement_condition_runs=replacement_runs,
        replacement_atomic_commits=replacement_runs*485,
        Full_condition_runs=full_runs, Full_state_updates=full_runs*485,
        all_mode_condition_runs=replacement_runs+full_runs,
        all_mode_state_updates=(replacement_runs+full_runs)*485,
        storage=dict(single_24_condition_all_node_float32_payload_bytes=payload,
            Full_2_repeats_payload_bytes=2*payload, replacement_8_trajectories_payload_bytes=8*payload,
            all_mode_payload_bytes=10*payload,
            SOURCE_RAW_old_H_boundary_xH_chemical_new_H_payload_bytes=raw_h_io,
            additional_logs_metrics_per_edge_audits_budget_bytes=4*1024**3,
            reserve_bytes=28*1024**3, reserve_GiB=28,
            pre_run_minimum_free_bytes=36*1024**3, post_run_minimum_free_headroom_GiB=8,
            observed_free_bytes=free, observed_free_GiB=free/1024**3,
            observation_utc=datetime.now(timezone.utc).isoformat(),
            location=str(HERE / "artifacts"), new_artifacts_created=False,
            signed_all_node_delta_policy="derive float64 difference by memory-mapped chunks from preserved raw modes; no duplicate full-size delta file",
            loss_policy="no lossy compression, no condition/node truncation, no deletion of existing runs",
            refusal="stop before starting if free space is below 36 GiB; ask architecture to resolve storage without deleting data"),
        runtime=dict(source=str(P3 / "artifacts/final_delivery/timing.json"), source_sha256=sha(P3 / "artifacts/final_delivery/timing.json"),
            measured_previous_two_process_batch_wall_s=old_times,
            measured_previous_total_replacement_conditions=48,
            linear_extrapolation_replacement_s=extrapolated_s,
            extrapolation_scope="same per-step R/H, validation, comparison and much export; not pure kernel",
            proposed_exclusive_GPU_slot_minutes=[60,90], preparation_and_audit_wall_hours=[1,2],
            new_Full_export_hash_faults_and_analysis_included_in_reserve=True,
            reserved_actual_GPU_slot=None, fresh_GPU_benchmark=False),
        memory=dict(batch_size=1, simultaneous_neural_GPU_processes=1,
            target_GPU_peak_GiB_at_most=4, actual_new_GPU_peak_bytes=None,
            target_analysis_host_working_set_GiB_at_most=2,
            VRAM_policy="measure on first approved condition; fail rather than reduce graph/change input when allocation fails",
            host_policy="memory-map states; chunk official per-neuron metrics; serialize two repeats and candidates"),
        execution_authorization=False, FPGA_execution=False)
    dump(HERE / "RESOURCE_BUDGET.json", budget)
    windows = old["windows_zero_based_inclusive"]
    reg = dict(schema="flyvis-phase4-direction-extension/review-v1", version=1,
        status="PROPOSED_BEFORE_NEW_24_CONDITION_INFERENCE_PENDING_ARCH_AND_USER_APPROVAL",
        created_utc=datetime.now(timezone.utc).isoformat(), date_local="2026-10-10", timezone="Asia/Shanghai",
        new_phase4_neural_updates=0, source_audit_sha256=sha(HERE / "SOURCE_AUDIT.json"),
        resource_budget_sha256=sha(HERE / "RESOURCE_BUDGET.json"),
        source_phase3_operator=old["spec_document"], model=audit["model"],
        candidate_ids=list(audit["candidates"]), candidate_identities=audit["candidates"],
        fixture=audit["fixture"], conditions=load(HERE / "prepared_inputs/conditions.json"),
        dataset_config_identity=dict(path=str(HERE / "prepared_inputs/official_dataset_config.json"),
            sha256=sha(HERE / "prepared_inputs/official_dataset_config.json")),
        independent_reference_processes=2, independent_replacement_processes=2,
        candidate_modes=["Full", "Sham", "Ablation"],
        Full_policy=dict(shared_across_candidates=True,
            planned="new official GPU all-node Full24 plus independent Full24 repeat; verified all-node identical-identity Full may substitute first reference",
            historical_center_only_Full_eligible=False,
            required_shape=[24,485,45669], dtype="float32",
            identity_keys=["checkpoint", "source_commit", "expanded_parameters", "initial_state_full", "stimulus", "time", "conditions", "nodes_full", "dt", "state_after_time"],
            comparison_use="post-commit only; never production R or H boundary",
            old_G2_four_condition_use="regression overlap only; no implicit replacement of 20 missing directions"),
        dynamics=dict(profile="SOURCE_RAW", native_H_updates_in_replacement=0,
            input_state="H and R both read own committed a[k]; commit a[k+1] after both results validate",
            state_after="saved mode[:,k,:]=a[k+1]", stimulus="prepared float32 sample[k]", dt_s=.005,
            additional_warmup=False, reset_exact_full_a0_every_condition=True),
        operator=dict(name="BLOCK_HR_RELEASE", start_step=200, gate_location="original edge current BEFORE R scatter",
            Sham="gain=1 on every original edge and time",
            Ablation="gain=0 iff original edge in candidate HR AND k>=200; otherwise gain=1",
            H_HH_RH_RR_update_unchanged=True, negative_and_zero_weight_edges_retained=True,
            neural_output_zeroing=False),
        readouts=audit["readouts"], windows_zero_based_inclusive=windows,
        readout_priority=dict(primary="primary_visual_readout (shared V, 1057 nodes)",
            confirmation="common_direct_downstream_R (shared D, 3312 nodes)",
            localization="candidate direct targets intersect shared V: 67 -> 634 nodes; 298 -> 1057 nodes",
            secondary=["all own H", "all own R", "common_R", "common_R_T4_T5", "all_T4_T5", "all_65_centers", "all_8_T4_T5_centers"],
            primary_candidate_ranking_not_local_ROI=True, per_neuron_results_include_candidate_H_R_membership=True),
        signed_metrics=dict(activity_units="model activity; no conversion to firing rate",
            z="a_mode[condition,k,r] minus its own mean a_mode[condition,160:200,r]",
            direction_centered="v_mode[polarity,angle,k,r]=z_mode minus mean of z_mode across ALL 12 angles at same polarity,k,r",
            eta="eta[r]=1e-5 + 1e-5*max_abs_Full_over_all_24_conditions_and_485_steps[r]",
            resolved_floor="RMS(reference)>10*RMS(4*eta[r]) broadcast over the readout/time/direction entries",
            projection_S="dot(v_mode,v_Full)/dot(v_Full,v_Full)",
            relative_change_E="norm(v_Ablation-v_Sham)/norm(v_Full)",
            orthogonal_E="norm(delta - delta_S*v_Full)/norm(v_Full); delta_S=dot(delta,v_Full)/dot(v_Full,v_Full)",
            decomposition="E^2 = delta_S^2 + orthogonal_E^2; retain signed delta_S and S_Sham/S_Ablation separately",
            cosine="dot(v_mode,v_Full)/(norm(v_mode)*norm(v_Full)); null if unresolved",
            angle_independent_component="report mean_angle(z_mode), signed AUC and RMS separately; do not call it direction loss",
            axes="flatten predefined angle/time/neuron entries, no neuron/angle selection or type averaging before primary metrics",
            polarities=["OFF","ON","JOINT"],
            per_condition="same S/E/decomposition on q_mode=z_mode[one angle] and q_Full; distinct from all-angle direction metric",
            opposite_pairs_deg=[[0,180],[30,210],[60,240],[90,270],[120,300],[150,330]],
            opposite_pair_trace="d_mode=z_mode[theta]-z_mode[theta+180]; report S/E for ALL 6 pairs per polarity",
            scalar_readouts=["signed mean", "signed AUC (.005*sum(z))", "RMS(z)", "signed peak at argmax(abs(z)) with earliest tie", "peak step/time"],
            time_windows=["primary_response","motion","post_motion"],
            unresolved="retain raw quantities, flag unresolved, normalized S/E/phase/lag become null; never set zero"),
        official_direction_metrics=dict(**audit["official_metrics"],
            neurons="union(all_T4_T5,all_65_centers); preserve individual nodes and cell types; no average-population DSI substitution",
            parameters=dict(average=True,norm=None,from_degree=None,to_degree=None),
            dataset_dimensions=["network_id","sample","frame","neuron"],
            coordinates="original angle,width,intensity,speed,time and fixed global node ID/cell_type",
            definitions="peak rectifies raw activity in official offsets time mask; DSI divisor is angle sum maximized over intensity; PD radians converted modulo360",
            display_PD_quality="for both compared modes: DSI>=0.05 AND abs(vector_sum)>10*sum_angle(eta_r) AND peak-sum normalization>10*sum_angle(eta_r)",
            raw_PD_retained=True, unqualified_PD_delta=None,
            PD_delta="wrap((PD_Ablation-PD_Sham)+180,360)-180 in degrees",
            DSI_delta="DSI_Ablation-DSI_Sham", official_metric_mask_export_required=True),
        temporal_structure=dict(role="secondary descriptive test; cannot replace raw primary E or be used to pick a new ROI",
            signal="q=z for fixed center and common V/D per condition; opposite-pair d additionally",
            lag_grid_steps=list(range(-10,11)), lag_grid_s=[k*.005 for k in range(-10,11)],
            correlation="flatten time/neuron after temporal centering per neuron; compare Sham[t] and Ablation[t+lag]",
            core_rule="for window [a,b], fix common t=[a+10,b-10] for ALL 21 lags",
            positive_lag="Ablation is delayed relative to Sham",
            tie_rule="minimum absolute lag then signed ascending; export all 21 correlations",
            unresolved="apply 10x floor to both centered traces; correlation/lag null when unresolved"),
        proposed_thresholds=dict(status="PENDING_III_APPROVAL_ENGINEERING_SCREEN_NOT_BIOLOGICAL_SIGNIFICANCE",
            contribution_E_at_least=.20, contribution_noise_multiplier=10,
            contribution_required="resolved, norm(A-S)>10*max(norm(S-F),norm(4*eta)), repeat-stable, original gate/all-state tests pass",
            Full_axis_attenuation_S_at_most=.80, Full_axis_enhancement_S_at_least=1.20,
            negative_Full_axis_S="label signed direction-pattern inversion, not activity death",
            direction_change_PD_abs_deg_at_least=15, official_DSI_abs_change_at_least=.10,
            direction_claim_scope="individual fixed neuron with PD quality passed; summarize fixed population counts, not biological behavioral prediction",
            temporal_shift_abs_s_at_least=.010, temporal_shift_correlation_gain_at_least=.05,
            trace_difference_with_preserved_axis="if E>=.20 but S in (.8,1.2), report perpendicular/PD/time/offset evidence; no label of response loss",
            deterministic_metrics_not_p_values=True),
        software_acceptance=dict(atol=1e-5,rtol=1e-5,all_full_H_R_every_step=True,
            Sham_Full_tolerance_violations=0, nonfinite=0,
            pre_onset_Ablation_Sham_bitwise=True, H_new_step_200_Ablation_Sham_bitwise=True,
            original_H_guard_calls=0, all_original_edges_time_axis_checked=True,
            independent_H_recompute_from_own_live_R_required=True,
            process_repeat_all_node_tolerance_required=True,
            repeat_S_E_absolute_at_most=.01,
            repeat_PDs_abs_deg_at_most=1.0, repeat_DSI_abs_at_most=1e-4,
            repeat_lag_steps_at_most=1,
            fault_tests=["wrong step_id", "NaN", "duplicate conflicting submit/commit", "H failure", "state node ordering mismatch", "run/comparison identity mismatch"],
            fail_policy="no R-alone commit, zero fill, automatic Full/software fallback or hidden condition exclusion; preserve failures"),
        stimulus_recommendation_rule=dict(status="FUTURE_RULE_NO_NEW_OUTCOME_AVAILABLE",
            primary_gate="both process repeats meet per-condition shared-V contribution threshold; D confirms resolved and >10x numerical floor",
            secondary_gate="if primary gate absent but structurally fixed local-V gate met in both repeats, label localized model-activity effect and keep shared-V negative result",
            ranking="separate candidate and polarity; descending per-condition E on shared V (or explicitly localized secondary tier); ties -> smaller original sample ID",
            selected_count="at most two qualifying angles per polarity plus each matched opposite; keep 0/180 reference pair",
            full_ranked_24_table_required=True,
            no_qualifier="report negative/unresolved; recommend numerical replacement fidelity only, no functional recovery claim",
            cross_24_comparison="enumerated deterministic screen, no population p-values or claim from selected maximum without full ranking",
            existing_67_hardware="recommendations for later fresh-a0 Full/Sham/real_FPGA matched recovery only after hardware identity/numeric gates pass",
            candidate_298="software contribution research only; requires future 298 hardware, never substitute 67 device result",
            historical_104_deg="coverage motivation only; OFF90/120 and270/300 included along with all others, not selected from new Ablation"),
        preservation=dict(raw_full_states_all_modes_all_repeats=True, raw_SOURCE_RAW_H_io_all_replacement_steps=True,
            original_edge_ids_and_gain_logs=True, H_R_all_node_step_differences=True,
            signed_full_deltas="losslessly reproducible from raw modes; float64 chunkwise derived, not duplicate 8GB file",
            identity_and_manifest="SHA256 file/array/code/source + request/prepare/commit hash chains",
            negative_results=True, actual_simulation_or_replay_label_required=True),
        approval=dict(technical_spec_III=None, acceptance_registry_III_2=None,
            user_candidate_list_and_GPU_slot=None, run_authorized=False,
            precise_decisions=["approve 67 and 298 full24 with two independent replacement repeats",
            "approve listed ROIs/windows/metrics/engineering thresholds",
            "approve shared Full24 reference/replay identity policy and 28GiB storage budget",
            "confirm exclusive 60-90 minute GPU slot; preserve 8GiB free headroom"],
            approval_changes="issue version2 before any new formal run; preserve version1 proposal and rejection/changes",
            no_hardware_numeric_or_protocol_freeze=True),
        no_modification_to_lane_6=True, FPGA_execution=False)
    dump(HERE / "PRE_REGISTRATION_PROPOSED_v1.json", reg)
    print(json.dumps(dict(status=reg["status"], budget_bytes=budget["storage"]["all_mode_payload_bytes"],
        SOURCE_RAW_H_io_bytes=raw_h_io, replacement_steps=replacement_runs*485, full_steps=full_runs*485,
        extrapolation_minutes=extrapolated_s/60, reserve_GiB=28,
        registration_sha256=sha(HERE / "PRE_REGISTRATION_PROPOSED_v1.json"))))


if __name__ == "__main__":
    main()
