# This script segment is generated automatically by AutoPilot

set name flyvis_t5c_source_raw_mul_29s_16ns_45_1_1
if {${::AESL::PGuard_rtl_comp_handler}} {
	::AP::rtl_comp_handler $name BINDTYPE {op} TYPE {mul} IMPL {auto} LATENCY 0 ALLOW_PRAGMA 1
}


set name flyvis_t5c_source_raw_mul_31s_28ns_59_1_1
if {${::AESL::PGuard_rtl_comp_handler}} {
	::AP::rtl_comp_handler $name BINDTYPE {op} TYPE {mul} IMPL {auto} LATENCY 0 ALLOW_PRAGMA 1
}


if {${::AESL::PGuard_rtl_comp_handler}} {
	::AP::rtl_comp_handler flyvis_t5c_source_raw_flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_124_4_FLYVIS_BIAS_Q22_ROM_AUTO_1R BINDTYPE {storage} TYPE {rom} IMPL {auto} LATENCY 2 ALLOW_PRAGMA 1
}


if {${::AESL::PGuard_rtl_comp_handler}} {
	::AP::rtl_comp_handler flyvis_t5c_source_raw_flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_124_4_FLYVIS_INVTau_Q22_ROM_AUTO_1R BINDTYPE {storage} TYPE {rom} IMPL {auto} LATENCY 2 ALLOW_PRAGMA 1
}


# clear list
if {${::AESL::PGuard_autoexp_gen}} {
    cg_default_interface_gen_dc_begin
    cg_default_interface_gen_bundle_begin
    AESL_LIB_XILADAPTER::native_axis_begin
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 494 \
    name candidate_66_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_66_reload \
    op interface \
    ports { candidate_66_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 495 \
    name candidate_65_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_65_reload \
    op interface \
    ports { candidate_65_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 496 \
    name candidate_64_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_64_reload \
    op interface \
    ports { candidate_64_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 497 \
    name candidate_63_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_63_reload \
    op interface \
    ports { candidate_63_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 498 \
    name candidate_62_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_62_reload \
    op interface \
    ports { candidate_62_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 499 \
    name candidate_61_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_61_reload \
    op interface \
    ports { candidate_61_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 500 \
    name candidate_60_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_60_reload \
    op interface \
    ports { candidate_60_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 501 \
    name candidate_59_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_59_reload \
    op interface \
    ports { candidate_59_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 502 \
    name candidate_58_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_58_reload \
    op interface \
    ports { candidate_58_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 503 \
    name candidate_57_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_57_reload \
    op interface \
    ports { candidate_57_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 504 \
    name candidate_56_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_56_reload \
    op interface \
    ports { candidate_56_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 505 \
    name candidate_55_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_55_reload \
    op interface \
    ports { candidate_55_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 506 \
    name candidate_54_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_54_reload \
    op interface \
    ports { candidate_54_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 507 \
    name candidate_53_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_53_reload \
    op interface \
    ports { candidate_53_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 508 \
    name candidate_52_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_52_reload \
    op interface \
    ports { candidate_52_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 509 \
    name candidate_51_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_51_reload \
    op interface \
    ports { candidate_51_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 510 \
    name candidate_50_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_50_reload \
    op interface \
    ports { candidate_50_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 511 \
    name candidate_49_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_49_reload \
    op interface \
    ports { candidate_49_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 512 \
    name candidate_48_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_48_reload \
    op interface \
    ports { candidate_48_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 513 \
    name candidate_47_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_47_reload \
    op interface \
    ports { candidate_47_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 514 \
    name candidate_46_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_46_reload \
    op interface \
    ports { candidate_46_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 515 \
    name candidate_45_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_45_reload \
    op interface \
    ports { candidate_45_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 516 \
    name candidate_44_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_44_reload \
    op interface \
    ports { candidate_44_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 517 \
    name candidate_43_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_43_reload \
    op interface \
    ports { candidate_43_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 518 \
    name candidate_42_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_42_reload \
    op interface \
    ports { candidate_42_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 519 \
    name candidate_41_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_41_reload \
    op interface \
    ports { candidate_41_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 520 \
    name candidate_40_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_40_reload \
    op interface \
    ports { candidate_40_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 521 \
    name candidate_39_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_39_reload \
    op interface \
    ports { candidate_39_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 522 \
    name candidate_38_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_38_reload \
    op interface \
    ports { candidate_38_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 523 \
    name candidate_37_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_37_reload \
    op interface \
    ports { candidate_37_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 524 \
    name candidate_36_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_36_reload \
    op interface \
    ports { candidate_36_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 525 \
    name candidate_35_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_35_reload \
    op interface \
    ports { candidate_35_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 526 \
    name candidate_34_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_34_reload \
    op interface \
    ports { candidate_34_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 527 \
    name candidate_33_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_33_reload \
    op interface \
    ports { candidate_33_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 528 \
    name candidate_32_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_32_reload \
    op interface \
    ports { candidate_32_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 529 \
    name candidate_31_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_31_reload \
    op interface \
    ports { candidate_31_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 530 \
    name candidate_30_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_30_reload \
    op interface \
    ports { candidate_30_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 531 \
    name candidate_29_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_29_reload \
    op interface \
    ports { candidate_29_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 532 \
    name candidate_28_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_28_reload \
    op interface \
    ports { candidate_28_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 533 \
    name candidate_27_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_27_reload \
    op interface \
    ports { candidate_27_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 534 \
    name candidate_26_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_26_reload \
    op interface \
    ports { candidate_26_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 535 \
    name candidate_25_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_25_reload \
    op interface \
    ports { candidate_25_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 536 \
    name candidate_24_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_24_reload \
    op interface \
    ports { candidate_24_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 537 \
    name candidate_23_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_23_reload \
    op interface \
    ports { candidate_23_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 538 \
    name candidate_22_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_22_reload \
    op interface \
    ports { candidate_22_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 539 \
    name candidate_21_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_21_reload \
    op interface \
    ports { candidate_21_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 540 \
    name candidate_20_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_20_reload \
    op interface \
    ports { candidate_20_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 541 \
    name candidate_19_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_19_reload \
    op interface \
    ports { candidate_19_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 542 \
    name candidate_18_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_18_reload \
    op interface \
    ports { candidate_18_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 543 \
    name candidate_17_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_17_reload \
    op interface \
    ports { candidate_17_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 544 \
    name candidate_16_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_16_reload \
    op interface \
    ports { candidate_16_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 545 \
    name candidate_15_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_15_reload \
    op interface \
    ports { candidate_15_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 546 \
    name candidate_14_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_14_reload \
    op interface \
    ports { candidate_14_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 547 \
    name candidate_13_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_13_reload \
    op interface \
    ports { candidate_13_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 548 \
    name candidate_12_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_12_reload \
    op interface \
    ports { candidate_12_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 549 \
    name candidate_11_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_11_reload \
    op interface \
    ports { candidate_11_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 550 \
    name candidate_10_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_10_reload \
    op interface \
    ports { candidate_10_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 551 \
    name candidate_9_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_9_reload \
    op interface \
    ports { candidate_9_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 552 \
    name candidate_8_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_8_reload \
    op interface \
    ports { candidate_8_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 553 \
    name candidate_7_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_7_reload \
    op interface \
    ports { candidate_7_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 554 \
    name candidate_6_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_6_reload \
    op interface \
    ports { candidate_6_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 555 \
    name candidate_5_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_5_reload \
    op interface \
    ports { candidate_5_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 556 \
    name candidate_4_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_4_reload \
    op interface \
    ports { candidate_4_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 557 \
    name candidate_3_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_3_reload \
    op interface \
    ports { candidate_3_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 558 \
    name candidate_2_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_2_reload \
    op interface \
    ports { candidate_2_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 559 \
    name candidate_1_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_1_reload \
    op interface \
    ports { candidate_1_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 560 \
    name candidate_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_reload \
    op interface \
    ports { candidate_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 561 \
    name chemical_134_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_134_reload \
    op interface \
    ports { chemical_134_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 562 \
    name chemical_135_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_135_reload \
    op interface \
    ports { chemical_135_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 563 \
    name chemical_136_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_136_reload \
    op interface \
    ports { chemical_136_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 564 \
    name chemical_137_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_137_reload \
    op interface \
    ports { chemical_137_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 565 \
    name chemical_138_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_138_reload \
    op interface \
    ports { chemical_138_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 566 \
    name chemical_139_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_139_reload \
    op interface \
    ports { chemical_139_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 567 \
    name chemical_140_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_140_reload \
    op interface \
    ports { chemical_140_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 568 \
    name chemical_141_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_141_reload \
    op interface \
    ports { chemical_141_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 569 \
    name chemical_142_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_142_reload \
    op interface \
    ports { chemical_142_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 570 \
    name chemical_143_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_143_reload \
    op interface \
    ports { chemical_143_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 571 \
    name chemical_144_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_144_reload \
    op interface \
    ports { chemical_144_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 572 \
    name chemical_145_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_145_reload \
    op interface \
    ports { chemical_145_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 573 \
    name chemical_146_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_146_reload \
    op interface \
    ports { chemical_146_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 574 \
    name chemical_147_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_147_reload \
    op interface \
    ports { chemical_147_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 575 \
    name chemical_148_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_148_reload \
    op interface \
    ports { chemical_148_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 576 \
    name chemical_149_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_149_reload \
    op interface \
    ports { chemical_149_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 577 \
    name chemical_150_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_150_reload \
    op interface \
    ports { chemical_150_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 578 \
    name chemical_151_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_151_reload \
    op interface \
    ports { chemical_151_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 579 \
    name chemical_152_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_152_reload \
    op interface \
    ports { chemical_152_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 580 \
    name chemical_153_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_153_reload \
    op interface \
    ports { chemical_153_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 581 \
    name chemical_154_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_154_reload \
    op interface \
    ports { chemical_154_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 582 \
    name chemical_155_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_155_reload \
    op interface \
    ports { chemical_155_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 583 \
    name chemical_156_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_156_reload \
    op interface \
    ports { chemical_156_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 584 \
    name chemical_157_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_157_reload \
    op interface \
    ports { chemical_157_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 585 \
    name chemical_158_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_158_reload \
    op interface \
    ports { chemical_158_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 586 \
    name chemical_159_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_159_reload \
    op interface \
    ports { chemical_159_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 587 \
    name chemical_160_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_160_reload \
    op interface \
    ports { chemical_160_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 588 \
    name chemical_161_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_161_reload \
    op interface \
    ports { chemical_161_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 589 \
    name chemical_162_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_162_reload \
    op interface \
    ports { chemical_162_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 590 \
    name chemical_163_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_163_reload \
    op interface \
    ports { chemical_163_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 591 \
    name chemical_164_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_164_reload \
    op interface \
    ports { chemical_164_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 592 \
    name chemical_165_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_165_reload \
    op interface \
    ports { chemical_165_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 593 \
    name chemical_166_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_166_reload \
    op interface \
    ports { chemical_166_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 594 \
    name chemical_167_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_167_reload \
    op interface \
    ports { chemical_167_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 595 \
    name chemical_168_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_168_reload \
    op interface \
    ports { chemical_168_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 596 \
    name chemical_169_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_169_reload \
    op interface \
    ports { chemical_169_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 597 \
    name chemical_170_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_170_reload \
    op interface \
    ports { chemical_170_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 598 \
    name chemical_171_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_171_reload \
    op interface \
    ports { chemical_171_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 599 \
    name chemical_172_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_172_reload \
    op interface \
    ports { chemical_172_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 600 \
    name chemical_173_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_173_reload \
    op interface \
    ports { chemical_173_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 601 \
    name chemical_174_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_174_reload \
    op interface \
    ports { chemical_174_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 602 \
    name chemical_175_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_175_reload \
    op interface \
    ports { chemical_175_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 603 \
    name chemical_176_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_176_reload \
    op interface \
    ports { chemical_176_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 604 \
    name chemical_177_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_177_reload \
    op interface \
    ports { chemical_177_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 605 \
    name chemical_178_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_178_reload \
    op interface \
    ports { chemical_178_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 606 \
    name chemical_179_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_179_reload \
    op interface \
    ports { chemical_179_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 607 \
    name chemical_180_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_180_reload \
    op interface \
    ports { chemical_180_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 608 \
    name chemical_181_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_181_reload \
    op interface \
    ports { chemical_181_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 609 \
    name chemical_182_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_182_reload \
    op interface \
    ports { chemical_182_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 610 \
    name chemical_183_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_183_reload \
    op interface \
    ports { chemical_183_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 611 \
    name chemical_184_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_184_reload \
    op interface \
    ports { chemical_184_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 612 \
    name chemical_185_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_185_reload \
    op interface \
    ports { chemical_185_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 613 \
    name chemical_186_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_186_reload \
    op interface \
    ports { chemical_186_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 614 \
    name chemical_187_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_187_reload \
    op interface \
    ports { chemical_187_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 615 \
    name chemical_188_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_188_reload \
    op interface \
    ports { chemical_188_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 616 \
    name chemical_189_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_189_reload \
    op interface \
    ports { chemical_189_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 617 \
    name chemical_190_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_190_reload \
    op interface \
    ports { chemical_190_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 618 \
    name chemical_191_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_191_reload \
    op interface \
    ports { chemical_191_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 619 \
    name chemical_192_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_192_reload \
    op interface \
    ports { chemical_192_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 620 \
    name chemical_193_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_193_reload \
    op interface \
    ports { chemical_193_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 621 \
    name chemical_194_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_194_reload \
    op interface \
    ports { chemical_194_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 622 \
    name chemical_195_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_195_reload \
    op interface \
    ports { chemical_195_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 623 \
    name chemical_196_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_196_reload \
    op interface \
    ports { chemical_196_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 624 \
    name chemical_197_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_197_reload \
    op interface \
    ports { chemical_197_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 625 \
    name chemical_198_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_198_reload \
    op interface \
    ports { chemical_198_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 626 \
    name chemical_199_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_199_reload \
    op interface \
    ports { chemical_199_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 627 \
    name chemical_200_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_200_reload \
    op interface \
    ports { chemical_200_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 628 \
    name old_h_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_reload \
    op interface \
    ports { old_h_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 629 \
    name old_h_1_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_1_reload \
    op interface \
    ports { old_h_1_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 630 \
    name old_h_2_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_2_reload \
    op interface \
    ports { old_h_2_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 631 \
    name old_h_3_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_3_reload \
    op interface \
    ports { old_h_3_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 632 \
    name old_h_4_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_4_reload \
    op interface \
    ports { old_h_4_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 633 \
    name old_h_5_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_5_reload \
    op interface \
    ports { old_h_5_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 634 \
    name old_h_6_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_6_reload \
    op interface \
    ports { old_h_6_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 635 \
    name old_h_7_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_7_reload \
    op interface \
    ports { old_h_7_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 636 \
    name old_h_8_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_8_reload \
    op interface \
    ports { old_h_8_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 637 \
    name old_h_9_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_9_reload \
    op interface \
    ports { old_h_9_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 638 \
    name old_h_10_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_10_reload \
    op interface \
    ports { old_h_10_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 639 \
    name old_h_11_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_11_reload \
    op interface \
    ports { old_h_11_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 640 \
    name old_h_12_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_12_reload \
    op interface \
    ports { old_h_12_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 641 \
    name old_h_13_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_13_reload \
    op interface \
    ports { old_h_13_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 642 \
    name old_h_14_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_14_reload \
    op interface \
    ports { old_h_14_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 643 \
    name old_h_15_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_15_reload \
    op interface \
    ports { old_h_15_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 644 \
    name old_h_16_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_16_reload \
    op interface \
    ports { old_h_16_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 645 \
    name old_h_17_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_17_reload \
    op interface \
    ports { old_h_17_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 646 \
    name old_h_18_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_18_reload \
    op interface \
    ports { old_h_18_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 647 \
    name old_h_19_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_19_reload \
    op interface \
    ports { old_h_19_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 648 \
    name old_h_20_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_20_reload \
    op interface \
    ports { old_h_20_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 649 \
    name old_h_21_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_21_reload \
    op interface \
    ports { old_h_21_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 650 \
    name old_h_22_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_22_reload \
    op interface \
    ports { old_h_22_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 651 \
    name old_h_23_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_23_reload \
    op interface \
    ports { old_h_23_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 652 \
    name old_h_24_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_24_reload \
    op interface \
    ports { old_h_24_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 653 \
    name old_h_25_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_25_reload \
    op interface \
    ports { old_h_25_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 654 \
    name old_h_26_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_26_reload \
    op interface \
    ports { old_h_26_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 655 \
    name old_h_27_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_27_reload \
    op interface \
    ports { old_h_27_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 656 \
    name old_h_28_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_28_reload \
    op interface \
    ports { old_h_28_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 657 \
    name old_h_29_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_29_reload \
    op interface \
    ports { old_h_29_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 658 \
    name old_h_30_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_30_reload \
    op interface \
    ports { old_h_30_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 659 \
    name old_h_31_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_31_reload \
    op interface \
    ports { old_h_31_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 660 \
    name old_h_32_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_32_reload \
    op interface \
    ports { old_h_32_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 661 \
    name old_h_33_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_33_reload \
    op interface \
    ports { old_h_33_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 662 \
    name old_h_34_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_34_reload \
    op interface \
    ports { old_h_34_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 663 \
    name old_h_35_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_35_reload \
    op interface \
    ports { old_h_35_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 664 \
    name old_h_36_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_36_reload \
    op interface \
    ports { old_h_36_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 665 \
    name old_h_37_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_37_reload \
    op interface \
    ports { old_h_37_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 666 \
    name old_h_38_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_38_reload \
    op interface \
    ports { old_h_38_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 667 \
    name old_h_39_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_39_reload \
    op interface \
    ports { old_h_39_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 668 \
    name old_h_40_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_40_reload \
    op interface \
    ports { old_h_40_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 669 \
    name old_h_41_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_41_reload \
    op interface \
    ports { old_h_41_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 670 \
    name old_h_42_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_42_reload \
    op interface \
    ports { old_h_42_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 671 \
    name old_h_43_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_43_reload \
    op interface \
    ports { old_h_43_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 672 \
    name old_h_44_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_44_reload \
    op interface \
    ports { old_h_44_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 673 \
    name old_h_45_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_45_reload \
    op interface \
    ports { old_h_45_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 674 \
    name old_h_46_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_46_reload \
    op interface \
    ports { old_h_46_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 675 \
    name old_h_47_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_47_reload \
    op interface \
    ports { old_h_47_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 676 \
    name old_h_48_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_48_reload \
    op interface \
    ports { old_h_48_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 677 \
    name old_h_49_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_49_reload \
    op interface \
    ports { old_h_49_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 678 \
    name old_h_50_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_50_reload \
    op interface \
    ports { old_h_50_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 679 \
    name old_h_51_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_51_reload \
    op interface \
    ports { old_h_51_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 680 \
    name old_h_52_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_52_reload \
    op interface \
    ports { old_h_52_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 681 \
    name old_h_53_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_53_reload \
    op interface \
    ports { old_h_53_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 682 \
    name old_h_54_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_54_reload \
    op interface \
    ports { old_h_54_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 683 \
    name old_h_55_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_55_reload \
    op interface \
    ports { old_h_55_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 684 \
    name old_h_56_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_56_reload \
    op interface \
    ports { old_h_56_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 685 \
    name old_h_57_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_57_reload \
    op interface \
    ports { old_h_57_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 686 \
    name old_h_58_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_58_reload \
    op interface \
    ports { old_h_58_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 687 \
    name old_h_59_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_59_reload \
    op interface \
    ports { old_h_59_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 688 \
    name old_h_60_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_60_reload \
    op interface \
    ports { old_h_60_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 689 \
    name old_h_61_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_61_reload \
    op interface \
    ports { old_h_61_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 690 \
    name old_h_62_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_62_reload \
    op interface \
    ports { old_h_62_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 691 \
    name old_h_63_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_63_reload \
    op interface \
    ports { old_h_63_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 692 \
    name old_h_64_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_64_reload \
    op interface \
    ports { old_h_64_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 693 \
    name old_h_65_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_65_reload \
    op interface \
    ports { old_h_65_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 694 \
    name old_h_66_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_old_h_66_reload \
    op interface \
    ports { old_h_66_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 695 \
    name x_h_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_reload \
    op interface \
    ports { x_h_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 696 \
    name x_h_1_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_1_reload \
    op interface \
    ports { x_h_1_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 697 \
    name x_h_2_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_2_reload \
    op interface \
    ports { x_h_2_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 698 \
    name x_h_3_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_3_reload \
    op interface \
    ports { x_h_3_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 699 \
    name x_h_4_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_4_reload \
    op interface \
    ports { x_h_4_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 700 \
    name x_h_5_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_5_reload \
    op interface \
    ports { x_h_5_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 701 \
    name x_h_6_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_6_reload \
    op interface \
    ports { x_h_6_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 702 \
    name x_h_7_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_7_reload \
    op interface \
    ports { x_h_7_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 703 \
    name x_h_8_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_8_reload \
    op interface \
    ports { x_h_8_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 704 \
    name x_h_9_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_9_reload \
    op interface \
    ports { x_h_9_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 705 \
    name x_h_10_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_10_reload \
    op interface \
    ports { x_h_10_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 706 \
    name x_h_11_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_11_reload \
    op interface \
    ports { x_h_11_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 707 \
    name x_h_12_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_12_reload \
    op interface \
    ports { x_h_12_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 708 \
    name x_h_13_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_13_reload \
    op interface \
    ports { x_h_13_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 709 \
    name x_h_14_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_14_reload \
    op interface \
    ports { x_h_14_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 710 \
    name x_h_15_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_15_reload \
    op interface \
    ports { x_h_15_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 711 \
    name x_h_16_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_16_reload \
    op interface \
    ports { x_h_16_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 712 \
    name x_h_17_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_17_reload \
    op interface \
    ports { x_h_17_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 713 \
    name x_h_18_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_18_reload \
    op interface \
    ports { x_h_18_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 714 \
    name x_h_19_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_19_reload \
    op interface \
    ports { x_h_19_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 715 \
    name x_h_20_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_20_reload \
    op interface \
    ports { x_h_20_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 716 \
    name x_h_21_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_21_reload \
    op interface \
    ports { x_h_21_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 717 \
    name x_h_22_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_22_reload \
    op interface \
    ports { x_h_22_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 718 \
    name x_h_23_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_23_reload \
    op interface \
    ports { x_h_23_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 719 \
    name x_h_24_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_24_reload \
    op interface \
    ports { x_h_24_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 720 \
    name x_h_25_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_25_reload \
    op interface \
    ports { x_h_25_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 721 \
    name x_h_26_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_26_reload \
    op interface \
    ports { x_h_26_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 722 \
    name x_h_27_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_27_reload \
    op interface \
    ports { x_h_27_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 723 \
    name x_h_28_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_28_reload \
    op interface \
    ports { x_h_28_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 724 \
    name x_h_29_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_29_reload \
    op interface \
    ports { x_h_29_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 725 \
    name x_h_30_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_30_reload \
    op interface \
    ports { x_h_30_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 726 \
    name x_h_31_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_31_reload \
    op interface \
    ports { x_h_31_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 727 \
    name x_h_32_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_32_reload \
    op interface \
    ports { x_h_32_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 728 \
    name x_h_33_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_33_reload \
    op interface \
    ports { x_h_33_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 729 \
    name x_h_34_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_34_reload \
    op interface \
    ports { x_h_34_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 730 \
    name x_h_35_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_35_reload \
    op interface \
    ports { x_h_35_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 731 \
    name x_h_36_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_36_reload \
    op interface \
    ports { x_h_36_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 732 \
    name x_h_37_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_37_reload \
    op interface \
    ports { x_h_37_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 733 \
    name x_h_38_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_38_reload \
    op interface \
    ports { x_h_38_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 734 \
    name x_h_39_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_39_reload \
    op interface \
    ports { x_h_39_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 735 \
    name x_h_40_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_40_reload \
    op interface \
    ports { x_h_40_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 736 \
    name x_h_41_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_41_reload \
    op interface \
    ports { x_h_41_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 737 \
    name x_h_42_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_42_reload \
    op interface \
    ports { x_h_42_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 738 \
    name x_h_43_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_43_reload \
    op interface \
    ports { x_h_43_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 739 \
    name x_h_44_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_44_reload \
    op interface \
    ports { x_h_44_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 740 \
    name x_h_45_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_45_reload \
    op interface \
    ports { x_h_45_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 741 \
    name x_h_46_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_46_reload \
    op interface \
    ports { x_h_46_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 742 \
    name x_h_47_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_47_reload \
    op interface \
    ports { x_h_47_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 743 \
    name x_h_48_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_48_reload \
    op interface \
    ports { x_h_48_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 744 \
    name x_h_49_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_49_reload \
    op interface \
    ports { x_h_49_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 745 \
    name x_h_50_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_50_reload \
    op interface \
    ports { x_h_50_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 746 \
    name x_h_51_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_51_reload \
    op interface \
    ports { x_h_51_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 747 \
    name x_h_52_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_52_reload \
    op interface \
    ports { x_h_52_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 748 \
    name x_h_53_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_53_reload \
    op interface \
    ports { x_h_53_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 749 \
    name x_h_54_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_54_reload \
    op interface \
    ports { x_h_54_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 750 \
    name x_h_55_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_55_reload \
    op interface \
    ports { x_h_55_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 751 \
    name x_h_56_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_56_reload \
    op interface \
    ports { x_h_56_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 752 \
    name x_h_57_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_57_reload \
    op interface \
    ports { x_h_57_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 753 \
    name x_h_58_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_58_reload \
    op interface \
    ports { x_h_58_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 754 \
    name x_h_59_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_59_reload \
    op interface \
    ports { x_h_59_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 755 \
    name x_h_60_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_60_reload \
    op interface \
    ports { x_h_60_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 756 \
    name x_h_61_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_61_reload \
    op interface \
    ports { x_h_61_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 757 \
    name x_h_62_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_62_reload \
    op interface \
    ports { x_h_62_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 758 \
    name x_h_63_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_63_reload \
    op interface \
    ports { x_h_63_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 759 \
    name x_h_64_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_64_reload \
    op interface \
    ports { x_h_64_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 760 \
    name x_h_65_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_65_reload \
    op interface \
    ports { x_h_65_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 761 \
    name x_h_66_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_x_h_66_reload \
    op interface \
    ports { x_h_66_reload { I 29 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 762 \
    name candidate_200_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_200_out \
    op interface \
    ports { candidate_200_out { O 29 vector } candidate_200_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 763 \
    name candidate_199_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_199_out \
    op interface \
    ports { candidate_199_out { O 29 vector } candidate_199_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 764 \
    name candidate_198_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_198_out \
    op interface \
    ports { candidate_198_out { O 29 vector } candidate_198_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 765 \
    name candidate_197_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_197_out \
    op interface \
    ports { candidate_197_out { O 29 vector } candidate_197_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 766 \
    name candidate_196_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_196_out \
    op interface \
    ports { candidate_196_out { O 29 vector } candidate_196_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 767 \
    name candidate_195_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_195_out \
    op interface \
    ports { candidate_195_out { O 29 vector } candidate_195_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 768 \
    name candidate_194_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_194_out \
    op interface \
    ports { candidate_194_out { O 29 vector } candidate_194_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 769 \
    name candidate_193_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_193_out \
    op interface \
    ports { candidate_193_out { O 29 vector } candidate_193_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 770 \
    name candidate_192_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_192_out \
    op interface \
    ports { candidate_192_out { O 29 vector } candidate_192_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 771 \
    name candidate_191_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_191_out \
    op interface \
    ports { candidate_191_out { O 29 vector } candidate_191_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 772 \
    name candidate_190_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_190_out \
    op interface \
    ports { candidate_190_out { O 29 vector } candidate_190_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 773 \
    name candidate_189_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_189_out \
    op interface \
    ports { candidate_189_out { O 29 vector } candidate_189_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 774 \
    name candidate_188_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_188_out \
    op interface \
    ports { candidate_188_out { O 29 vector } candidate_188_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 775 \
    name candidate_187_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_187_out \
    op interface \
    ports { candidate_187_out { O 29 vector } candidate_187_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 776 \
    name candidate_186_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_186_out \
    op interface \
    ports { candidate_186_out { O 29 vector } candidate_186_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 777 \
    name candidate_185_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_185_out \
    op interface \
    ports { candidate_185_out { O 29 vector } candidate_185_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 778 \
    name candidate_184_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_184_out \
    op interface \
    ports { candidate_184_out { O 29 vector } candidate_184_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 779 \
    name candidate_183_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_183_out \
    op interface \
    ports { candidate_183_out { O 29 vector } candidate_183_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 780 \
    name candidate_182_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_182_out \
    op interface \
    ports { candidate_182_out { O 29 vector } candidate_182_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 781 \
    name candidate_181_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_181_out \
    op interface \
    ports { candidate_181_out { O 29 vector } candidate_181_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 782 \
    name candidate_180_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_180_out \
    op interface \
    ports { candidate_180_out { O 29 vector } candidate_180_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 783 \
    name candidate_179_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_179_out \
    op interface \
    ports { candidate_179_out { O 29 vector } candidate_179_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 784 \
    name candidate_178_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_178_out \
    op interface \
    ports { candidate_178_out { O 29 vector } candidate_178_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 785 \
    name candidate_177_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_177_out \
    op interface \
    ports { candidate_177_out { O 29 vector } candidate_177_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 786 \
    name candidate_176_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_176_out \
    op interface \
    ports { candidate_176_out { O 29 vector } candidate_176_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 787 \
    name candidate_175_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_175_out \
    op interface \
    ports { candidate_175_out { O 29 vector } candidate_175_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 788 \
    name candidate_174_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_174_out \
    op interface \
    ports { candidate_174_out { O 29 vector } candidate_174_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 789 \
    name candidate_173_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_173_out \
    op interface \
    ports { candidate_173_out { O 29 vector } candidate_173_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 790 \
    name candidate_172_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_172_out \
    op interface \
    ports { candidate_172_out { O 29 vector } candidate_172_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 791 \
    name candidate_171_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_171_out \
    op interface \
    ports { candidate_171_out { O 29 vector } candidate_171_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 792 \
    name candidate_170_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_170_out \
    op interface \
    ports { candidate_170_out { O 29 vector } candidate_170_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 793 \
    name candidate_169_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_169_out \
    op interface \
    ports { candidate_169_out { O 29 vector } candidate_169_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 794 \
    name candidate_168_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_168_out \
    op interface \
    ports { candidate_168_out { O 29 vector } candidate_168_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 795 \
    name candidate_167_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_167_out \
    op interface \
    ports { candidate_167_out { O 29 vector } candidate_167_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 796 \
    name candidate_166_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_166_out \
    op interface \
    ports { candidate_166_out { O 29 vector } candidate_166_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 797 \
    name candidate_165_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_165_out \
    op interface \
    ports { candidate_165_out { O 29 vector } candidate_165_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 798 \
    name candidate_164_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_164_out \
    op interface \
    ports { candidate_164_out { O 29 vector } candidate_164_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 799 \
    name candidate_163_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_163_out \
    op interface \
    ports { candidate_163_out { O 29 vector } candidate_163_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 800 \
    name candidate_162_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_162_out \
    op interface \
    ports { candidate_162_out { O 29 vector } candidate_162_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 801 \
    name candidate_161_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_161_out \
    op interface \
    ports { candidate_161_out { O 29 vector } candidate_161_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 802 \
    name candidate_160_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_160_out \
    op interface \
    ports { candidate_160_out { O 29 vector } candidate_160_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 803 \
    name candidate_159_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_159_out \
    op interface \
    ports { candidate_159_out { O 29 vector } candidate_159_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 804 \
    name candidate_158_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_158_out \
    op interface \
    ports { candidate_158_out { O 29 vector } candidate_158_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 805 \
    name candidate_157_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_157_out \
    op interface \
    ports { candidate_157_out { O 29 vector } candidate_157_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 806 \
    name candidate_156_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_156_out \
    op interface \
    ports { candidate_156_out { O 29 vector } candidate_156_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 807 \
    name candidate_155_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_155_out \
    op interface \
    ports { candidate_155_out { O 29 vector } candidate_155_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 808 \
    name candidate_154_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_154_out \
    op interface \
    ports { candidate_154_out { O 29 vector } candidate_154_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 809 \
    name candidate_153_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_153_out \
    op interface \
    ports { candidate_153_out { O 29 vector } candidate_153_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 810 \
    name candidate_152_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_152_out \
    op interface \
    ports { candidate_152_out { O 29 vector } candidate_152_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 811 \
    name candidate_151_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_151_out \
    op interface \
    ports { candidate_151_out { O 29 vector } candidate_151_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 812 \
    name candidate_150_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_150_out \
    op interface \
    ports { candidate_150_out { O 29 vector } candidate_150_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 813 \
    name candidate_149_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_149_out \
    op interface \
    ports { candidate_149_out { O 29 vector } candidate_149_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 814 \
    name candidate_148_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_148_out \
    op interface \
    ports { candidate_148_out { O 29 vector } candidate_148_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 815 \
    name candidate_147_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_147_out \
    op interface \
    ports { candidate_147_out { O 29 vector } candidate_147_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 816 \
    name candidate_146_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_146_out \
    op interface \
    ports { candidate_146_out { O 29 vector } candidate_146_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 817 \
    name candidate_145_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_145_out \
    op interface \
    ports { candidate_145_out { O 29 vector } candidate_145_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 818 \
    name candidate_144_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_144_out \
    op interface \
    ports { candidate_144_out { O 29 vector } candidate_144_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 819 \
    name candidate_143_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_143_out \
    op interface \
    ports { candidate_143_out { O 29 vector } candidate_143_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 820 \
    name candidate_142_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_142_out \
    op interface \
    ports { candidate_142_out { O 29 vector } candidate_142_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 821 \
    name candidate_141_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_141_out \
    op interface \
    ports { candidate_141_out { O 29 vector } candidate_141_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 822 \
    name candidate_140_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_140_out \
    op interface \
    ports { candidate_140_out { O 29 vector } candidate_140_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 823 \
    name candidate_139_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_139_out \
    op interface \
    ports { candidate_139_out { O 29 vector } candidate_139_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 824 \
    name candidate_138_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_138_out \
    op interface \
    ports { candidate_138_out { O 29 vector } candidate_138_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 825 \
    name candidate_137_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_137_out \
    op interface \
    ports { candidate_137_out { O 29 vector } candidate_137_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 826 \
    name candidate_136_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_136_out \
    op interface \
    ports { candidate_136_out { O 29 vector } candidate_136_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 827 \
    name candidate_135_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_135_out \
    op interface \
    ports { candidate_135_out { O 29 vector } candidate_135_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 828 \
    name candidate_134_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_candidate_134_out \
    op interface \
    ports { candidate_134_out { O 29 vector } candidate_134_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 829 \
    name status_4_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_status_4_out \
    op interface \
    ports { status_4_out { O 32 vector } status_4_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id -1 \
    name ap_ctrl \
    type ap_ctrl \
    reset_level 1 \
    sync_rst true \
    corename ap_ctrl \
    op interface \
    ports { ap_start { I 1 bit } ap_ready { O 1 bit } ap_done { O 1 bit } ap_idle { O 1 bit } } \
} "
}


# Adapter definition:
set PortName ap_clk
set DataWd 1 
if {${::AESL::PGuard_autoexp_gen}} {
if {[info proc cg_default_interface_gen_clock] == "cg_default_interface_gen_clock"} {
eval "cg_default_interface_gen_clock { \
    id -2 \
    name ${PortName} \
    reset_level 1 \
    sync_rst true \
    corename apif_ap_clk \
    data_wd ${DataWd} \
    op interface \
}"
} else {
puts "@W \[IMPL-113\] Cannot find bus interface model in the library. Ignored generation of bus interface for '${PortName}'"
}
}


# Adapter definition:
set PortName ap_rst
set DataWd 1 
if {${::AESL::PGuard_autoexp_gen}} {
if {[info proc cg_default_interface_gen_reset] == "cg_default_interface_gen_reset"} {
eval "cg_default_interface_gen_reset { \
    id -3 \
    name ${PortName} \
    reset_level 1 \
    sync_rst true \
    corename apif_ap_rst \
    data_wd ${DataWd} \
    op interface \
}"
} else {
puts "@W \[IMPL-114\] Cannot find bus interface model in the library. Ignored generation of bus interface for '${PortName}'"
}
}



# merge
if {${::AESL::PGuard_autoexp_gen}} {
    cg_default_interface_gen_dc_end
    cg_default_interface_gen_bundle_end
    AESL_LIB_XILADAPTER::native_axis_end
}


# flow_control definition:
set InstName flyvis_t5c_source_raw_flow_control_loop_pipe_sequential_init_U
set CompName flyvis_t5c_source_raw_flow_control_loop_pipe_sequential_init
set name flow_control_loop_pipe_sequential_init
if {${::AESL::PGuard_autocg_gen} && ${::AESL::PGuard_autocg_ipmgen}} {
if {[info proc ::AESL_LIB_VIRTEX::xil_gen_UPC_flow_control] == "::AESL_LIB_VIRTEX::xil_gen_UPC_flow_control"} {
eval "::AESL_LIB_VIRTEX::xil_gen_UPC_flow_control { \
    name ${name} \
    prefix flyvis_t5c_source_raw_ \
}"
} else {
puts "@W \[IMPL-107\] Cannot find ::AESL_LIB_VIRTEX::xil_gen_UPC_flow_control, check your platform lib"
}
}


if {${::AESL::PGuard_rtl_comp_handler}} {
	::AP::rtl_comp_handler $CompName BINDTYPE interface TYPE internal_upc_flow_control INSTNAME $InstName
}


