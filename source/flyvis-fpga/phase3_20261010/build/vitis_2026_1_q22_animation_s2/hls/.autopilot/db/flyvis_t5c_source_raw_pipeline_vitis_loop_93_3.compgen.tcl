# This script segment is generated automatically by AutoPilot

set name flyvis_t5c_source_raw_mul_28ns_22s_50_1_1
if {${::AESL::PGuard_rtl_comp_handler}} {
	::AP::rtl_comp_handler $name BINDTYPE {op} TYPE {mul} IMPL {auto} LATENCY 0 ALLOW_PRAGMA 1
}


if {${::AESL::PGuard_rtl_comp_handler}} {
	::AP::rtl_comp_handler flyvis_t5c_source_raw_sparsemux_135_7_29_1_1 BINDTYPE {op} TYPE {sparsemux} IMPL {compactencoding_dontcare}
}


if {${::AESL::PGuard_rtl_comp_handler}} {
	::AP::rtl_comp_handler flyvis_t5c_source_raw_sparsemux_135_7_48_1_1 BINDTYPE {op} TYPE {sparsemux} IMPL {compactencoding_dontcare}
}


if {${::AESL::PGuard_rtl_comp_handler}} {
	::AP::rtl_comp_handler flyvis_t5c_source_raw_flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_93_3_FLYVIS_EDGE_SRC_ROM_AUTO_1R BINDTYPE {storage} TYPE {rom} IMPL {auto} LATENCY 2 ALLOW_PRAGMA 1
}


if {${::AESL::PGuard_rtl_comp_handler}} {
	::AP::rtl_comp_handler flyvis_t5c_source_raw_flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_93_3_FLYVIS_EDGE_WEIGHT_Q20_ROM_AUTbkb BINDTYPE {storage} TYPE {rom} IMPL {auto} LATENCY 2 ALLOW_PRAGMA 1
}


if {${::AESL::PGuard_rtl_comp_handler}} {
	::AP::rtl_comp_handler flyvis_t5c_source_raw_flyvis_t5c_source_raw_Pipeline_VITIS_LOOP_93_3_FLYVIS_EDGE_DST_ROM_AUTO_1R BINDTYPE {storage} TYPE {rom} IMPL {auto} LATENCY 2 ALLOW_PRAGMA 1
}


# clear list
if {${::AESL::PGuard_autoexp_gen}} {
    cg_default_interface_gen_dc_begin
    cg_default_interface_gen_bundle_begin
    AESL_LIB_XILADAPTER::native_axis_begin
}

# XIL_BRAM:
if {${::AESL::PGuard_autoexp_gen}} {
if {[info proc ::AESL_LIB_XILADAPTER::xil_bram_gen] == "::AESL_LIB_XILADAPTER::xil_bram_gen"} {
eval "::AESL_LIB_XILADAPTER::xil_bram_gen { \
    id 416 \
    name boundary \
    reset_level 1 \
    sync_rst true \
    dir I \
    corename boundary \
    op interface \
    ports { boundary_address0 { O 11 vector } boundary_ce0 { O 1 bit } boundary_q0 { I 29 vector } } \
} "
} else {
puts "@W \[IMPL-110\] Cannot find bus interface model in the library. Ignored generation of bus interface for 'boundary'"
}
}


# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 282 \
    name chemical_66_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_66_reload \
    op interface \
    ports { chemical_66_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 283 \
    name chemical_65_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_65_reload \
    op interface \
    ports { chemical_65_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 284 \
    name chemical_64_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_64_reload \
    op interface \
    ports { chemical_64_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 285 \
    name chemical_63_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_63_reload \
    op interface \
    ports { chemical_63_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 286 \
    name chemical_62_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_62_reload \
    op interface \
    ports { chemical_62_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 287 \
    name chemical_61_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_61_reload \
    op interface \
    ports { chemical_61_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 288 \
    name chemical_60_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_60_reload \
    op interface \
    ports { chemical_60_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 289 \
    name chemical_59_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_59_reload \
    op interface \
    ports { chemical_59_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 290 \
    name chemical_58_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_58_reload \
    op interface \
    ports { chemical_58_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 291 \
    name chemical_57_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_57_reload \
    op interface \
    ports { chemical_57_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 292 \
    name chemical_56_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_56_reload \
    op interface \
    ports { chemical_56_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 293 \
    name chemical_55_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_55_reload \
    op interface \
    ports { chemical_55_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 294 \
    name chemical_54_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_54_reload \
    op interface \
    ports { chemical_54_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 295 \
    name chemical_53_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_53_reload \
    op interface \
    ports { chemical_53_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 296 \
    name chemical_52_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_52_reload \
    op interface \
    ports { chemical_52_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 297 \
    name chemical_51_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_51_reload \
    op interface \
    ports { chemical_51_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 298 \
    name chemical_50_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_50_reload \
    op interface \
    ports { chemical_50_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 299 \
    name chemical_49_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_49_reload \
    op interface \
    ports { chemical_49_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 300 \
    name chemical_48_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_48_reload \
    op interface \
    ports { chemical_48_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 301 \
    name chemical_47_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_47_reload \
    op interface \
    ports { chemical_47_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 302 \
    name chemical_46_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_46_reload \
    op interface \
    ports { chemical_46_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 303 \
    name chemical_45_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_45_reload \
    op interface \
    ports { chemical_45_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 304 \
    name chemical_44_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_44_reload \
    op interface \
    ports { chemical_44_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 305 \
    name chemical_43_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_43_reload \
    op interface \
    ports { chemical_43_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 306 \
    name chemical_42_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_42_reload \
    op interface \
    ports { chemical_42_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 307 \
    name chemical_41_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_41_reload \
    op interface \
    ports { chemical_41_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 308 \
    name chemical_40_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_40_reload \
    op interface \
    ports { chemical_40_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 309 \
    name chemical_39_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_39_reload \
    op interface \
    ports { chemical_39_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 310 \
    name chemical_38_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_38_reload \
    op interface \
    ports { chemical_38_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 311 \
    name chemical_37_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_37_reload \
    op interface \
    ports { chemical_37_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 312 \
    name chemical_36_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_36_reload \
    op interface \
    ports { chemical_36_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 313 \
    name chemical_35_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_35_reload \
    op interface \
    ports { chemical_35_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 314 \
    name chemical_34_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_34_reload \
    op interface \
    ports { chemical_34_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 315 \
    name chemical_33_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_33_reload \
    op interface \
    ports { chemical_33_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 316 \
    name chemical_32_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_32_reload \
    op interface \
    ports { chemical_32_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 317 \
    name chemical_31_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_31_reload \
    op interface \
    ports { chemical_31_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 318 \
    name chemical_30_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_30_reload \
    op interface \
    ports { chemical_30_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 319 \
    name chemical_29_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_29_reload \
    op interface \
    ports { chemical_29_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 320 \
    name chemical_28_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_28_reload \
    op interface \
    ports { chemical_28_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 321 \
    name chemical_27_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_27_reload \
    op interface \
    ports { chemical_27_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 322 \
    name chemical_26_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_26_reload \
    op interface \
    ports { chemical_26_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 323 \
    name chemical_25_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_25_reload \
    op interface \
    ports { chemical_25_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 324 \
    name chemical_24_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_24_reload \
    op interface \
    ports { chemical_24_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 325 \
    name chemical_23_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_23_reload \
    op interface \
    ports { chemical_23_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 326 \
    name chemical_22_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_22_reload \
    op interface \
    ports { chemical_22_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 327 \
    name chemical_21_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_21_reload \
    op interface \
    ports { chemical_21_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 328 \
    name chemical_20_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_20_reload \
    op interface \
    ports { chemical_20_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 329 \
    name chemical_19_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_19_reload \
    op interface \
    ports { chemical_19_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 330 \
    name chemical_18_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_18_reload \
    op interface \
    ports { chemical_18_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 331 \
    name chemical_17_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_17_reload \
    op interface \
    ports { chemical_17_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 332 \
    name chemical_16_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_16_reload \
    op interface \
    ports { chemical_16_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 333 \
    name chemical_15_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_15_reload \
    op interface \
    ports { chemical_15_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 334 \
    name chemical_14_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_14_reload \
    op interface \
    ports { chemical_14_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 335 \
    name chemical_13_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_13_reload \
    op interface \
    ports { chemical_13_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 336 \
    name chemical_12_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_12_reload \
    op interface \
    ports { chemical_12_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 337 \
    name chemical_11_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_11_reload \
    op interface \
    ports { chemical_11_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 338 \
    name chemical_10_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_10_reload \
    op interface \
    ports { chemical_10_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 339 \
    name chemical_9_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_9_reload \
    op interface \
    ports { chemical_9_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 340 \
    name chemical_8_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_8_reload \
    op interface \
    ports { chemical_8_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 341 \
    name chemical_7_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_7_reload \
    op interface \
    ports { chemical_7_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 342 \
    name chemical_6_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_6_reload \
    op interface \
    ports { chemical_6_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 343 \
    name chemical_5_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_5_reload \
    op interface \
    ports { chemical_5_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 344 \
    name chemical_4_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_4_reload \
    op interface \
    ports { chemical_4_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 345 \
    name chemical_3_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_3_reload \
    op interface \
    ports { chemical_3_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 346 \
    name chemical_2_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_2_reload \
    op interface \
    ports { chemical_2_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 347 \
    name chemical_1_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_1_reload \
    op interface \
    ports { chemical_1_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 348 \
    name chemical_reload \
    type other \
    dir I \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_reload \
    op interface \
    ports { chemical_reload { I 48 vector } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 349 \
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
    id 350 \
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
    id 351 \
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
    id 352 \
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
    id 353 \
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
    id 354 \
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
    id 355 \
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
    id 356 \
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
    id 357 \
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
    id 358 \
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
    id 359 \
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
    id 360 \
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
    id 361 \
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
    id 362 \
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
    id 363 \
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
    id 364 \
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
    id 365 \
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
    id 366 \
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
    id 367 \
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
    id 368 \
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
    id 369 \
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
    id 370 \
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
    id 371 \
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
    id 372 \
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
    id 373 \
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
    id 374 \
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
    id 375 \
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
    id 376 \
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
    id 377 \
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
    id 378 \
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
    id 379 \
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
    id 380 \
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
    id 381 \
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
    id 382 \
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
    id 383 \
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
    id 384 \
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
    id 385 \
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
    id 386 \
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
    id 387 \
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
    id 388 \
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
    id 389 \
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
    id 390 \
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
    id 391 \
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
    id 392 \
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
    id 393 \
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
    id 394 \
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
    id 395 \
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
    id 396 \
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
    id 397 \
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
    id 398 \
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
    id 399 \
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
    id 400 \
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
    id 401 \
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
    id 402 \
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
    id 403 \
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
    id 404 \
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
    id 405 \
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
    id 406 \
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
    id 407 \
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
    id 408 \
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
    id 409 \
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
    id 410 \
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
    id 411 \
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
    id 412 \
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
    id 413 \
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
    id 414 \
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
    id 415 \
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
    id 417 \
    name chemical_200_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_200_out \
    op interface \
    ports { chemical_200_out { O 48 vector } chemical_200_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 418 \
    name chemical_199_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_199_out \
    op interface \
    ports { chemical_199_out { O 48 vector } chemical_199_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 419 \
    name chemical_198_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_198_out \
    op interface \
    ports { chemical_198_out { O 48 vector } chemical_198_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 420 \
    name chemical_197_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_197_out \
    op interface \
    ports { chemical_197_out { O 48 vector } chemical_197_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 421 \
    name chemical_196_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_196_out \
    op interface \
    ports { chemical_196_out { O 48 vector } chemical_196_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 422 \
    name chemical_195_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_195_out \
    op interface \
    ports { chemical_195_out { O 48 vector } chemical_195_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 423 \
    name chemical_194_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_194_out \
    op interface \
    ports { chemical_194_out { O 48 vector } chemical_194_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 424 \
    name chemical_193_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_193_out \
    op interface \
    ports { chemical_193_out { O 48 vector } chemical_193_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 425 \
    name chemical_192_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_192_out \
    op interface \
    ports { chemical_192_out { O 48 vector } chemical_192_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 426 \
    name chemical_191_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_191_out \
    op interface \
    ports { chemical_191_out { O 48 vector } chemical_191_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 427 \
    name chemical_190_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_190_out \
    op interface \
    ports { chemical_190_out { O 48 vector } chemical_190_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 428 \
    name chemical_189_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_189_out \
    op interface \
    ports { chemical_189_out { O 48 vector } chemical_189_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 429 \
    name chemical_188_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_188_out \
    op interface \
    ports { chemical_188_out { O 48 vector } chemical_188_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 430 \
    name chemical_187_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_187_out \
    op interface \
    ports { chemical_187_out { O 48 vector } chemical_187_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 431 \
    name chemical_186_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_186_out \
    op interface \
    ports { chemical_186_out { O 48 vector } chemical_186_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 432 \
    name chemical_185_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_185_out \
    op interface \
    ports { chemical_185_out { O 48 vector } chemical_185_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 433 \
    name chemical_184_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_184_out \
    op interface \
    ports { chemical_184_out { O 48 vector } chemical_184_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 434 \
    name chemical_183_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_183_out \
    op interface \
    ports { chemical_183_out { O 48 vector } chemical_183_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 435 \
    name chemical_182_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_182_out \
    op interface \
    ports { chemical_182_out { O 48 vector } chemical_182_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 436 \
    name chemical_181_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_181_out \
    op interface \
    ports { chemical_181_out { O 48 vector } chemical_181_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 437 \
    name chemical_180_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_180_out \
    op interface \
    ports { chemical_180_out { O 48 vector } chemical_180_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 438 \
    name chemical_179_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_179_out \
    op interface \
    ports { chemical_179_out { O 48 vector } chemical_179_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 439 \
    name chemical_178_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_178_out \
    op interface \
    ports { chemical_178_out { O 48 vector } chemical_178_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 440 \
    name chemical_177_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_177_out \
    op interface \
    ports { chemical_177_out { O 48 vector } chemical_177_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 441 \
    name chemical_176_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_176_out \
    op interface \
    ports { chemical_176_out { O 48 vector } chemical_176_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 442 \
    name chemical_175_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_175_out \
    op interface \
    ports { chemical_175_out { O 48 vector } chemical_175_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 443 \
    name chemical_174_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_174_out \
    op interface \
    ports { chemical_174_out { O 48 vector } chemical_174_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 444 \
    name chemical_173_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_173_out \
    op interface \
    ports { chemical_173_out { O 48 vector } chemical_173_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 445 \
    name chemical_172_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_172_out \
    op interface \
    ports { chemical_172_out { O 48 vector } chemical_172_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 446 \
    name chemical_171_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_171_out \
    op interface \
    ports { chemical_171_out { O 48 vector } chemical_171_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 447 \
    name chemical_170_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_170_out \
    op interface \
    ports { chemical_170_out { O 48 vector } chemical_170_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 448 \
    name chemical_169_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_169_out \
    op interface \
    ports { chemical_169_out { O 48 vector } chemical_169_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 449 \
    name chemical_168_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_168_out \
    op interface \
    ports { chemical_168_out { O 48 vector } chemical_168_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 450 \
    name chemical_167_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_167_out \
    op interface \
    ports { chemical_167_out { O 48 vector } chemical_167_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 451 \
    name chemical_166_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_166_out \
    op interface \
    ports { chemical_166_out { O 48 vector } chemical_166_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 452 \
    name chemical_165_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_165_out \
    op interface \
    ports { chemical_165_out { O 48 vector } chemical_165_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 453 \
    name chemical_164_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_164_out \
    op interface \
    ports { chemical_164_out { O 48 vector } chemical_164_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 454 \
    name chemical_163_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_163_out \
    op interface \
    ports { chemical_163_out { O 48 vector } chemical_163_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 455 \
    name chemical_162_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_162_out \
    op interface \
    ports { chemical_162_out { O 48 vector } chemical_162_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 456 \
    name chemical_161_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_161_out \
    op interface \
    ports { chemical_161_out { O 48 vector } chemical_161_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 457 \
    name chemical_160_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_160_out \
    op interface \
    ports { chemical_160_out { O 48 vector } chemical_160_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 458 \
    name chemical_159_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_159_out \
    op interface \
    ports { chemical_159_out { O 48 vector } chemical_159_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 459 \
    name chemical_158_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_158_out \
    op interface \
    ports { chemical_158_out { O 48 vector } chemical_158_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 460 \
    name chemical_157_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_157_out \
    op interface \
    ports { chemical_157_out { O 48 vector } chemical_157_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 461 \
    name chemical_156_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_156_out \
    op interface \
    ports { chemical_156_out { O 48 vector } chemical_156_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 462 \
    name chemical_155_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_155_out \
    op interface \
    ports { chemical_155_out { O 48 vector } chemical_155_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 463 \
    name chemical_154_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_154_out \
    op interface \
    ports { chemical_154_out { O 48 vector } chemical_154_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 464 \
    name chemical_153_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_153_out \
    op interface \
    ports { chemical_153_out { O 48 vector } chemical_153_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 465 \
    name chemical_152_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_152_out \
    op interface \
    ports { chemical_152_out { O 48 vector } chemical_152_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 466 \
    name chemical_151_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_151_out \
    op interface \
    ports { chemical_151_out { O 48 vector } chemical_151_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 467 \
    name chemical_150_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_150_out \
    op interface \
    ports { chemical_150_out { O 48 vector } chemical_150_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 468 \
    name chemical_149_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_149_out \
    op interface \
    ports { chemical_149_out { O 48 vector } chemical_149_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 469 \
    name chemical_148_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_148_out \
    op interface \
    ports { chemical_148_out { O 48 vector } chemical_148_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 470 \
    name chemical_147_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_147_out \
    op interface \
    ports { chemical_147_out { O 48 vector } chemical_147_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 471 \
    name chemical_146_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_146_out \
    op interface \
    ports { chemical_146_out { O 48 vector } chemical_146_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 472 \
    name chemical_145_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_145_out \
    op interface \
    ports { chemical_145_out { O 48 vector } chemical_145_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 473 \
    name chemical_144_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_144_out \
    op interface \
    ports { chemical_144_out { O 48 vector } chemical_144_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 474 \
    name chemical_143_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_143_out \
    op interface \
    ports { chemical_143_out { O 48 vector } chemical_143_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 475 \
    name chemical_142_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_142_out \
    op interface \
    ports { chemical_142_out { O 48 vector } chemical_142_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 476 \
    name chemical_141_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_141_out \
    op interface \
    ports { chemical_141_out { O 48 vector } chemical_141_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 477 \
    name chemical_140_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_140_out \
    op interface \
    ports { chemical_140_out { O 48 vector } chemical_140_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 478 \
    name chemical_139_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_139_out \
    op interface \
    ports { chemical_139_out { O 48 vector } chemical_139_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 479 \
    name chemical_138_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_138_out \
    op interface \
    ports { chemical_138_out { O 48 vector } chemical_138_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 480 \
    name chemical_137_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_137_out \
    op interface \
    ports { chemical_137_out { O 48 vector } chemical_137_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 481 \
    name chemical_136_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_136_out \
    op interface \
    ports { chemical_136_out { O 48 vector } chemical_136_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 482 \
    name chemical_135_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_135_out \
    op interface \
    ports { chemical_135_out { O 48 vector } chemical_135_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 483 \
    name chemical_134_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_chemical_134_out \
    op interface \
    ports { chemical_134_out { O 48 vector } chemical_134_out_ap_vld { O 1 bit } } \
} "
}

# Direct connection:
if {${::AESL::PGuard_autoexp_gen}} {
eval "cg_default_interface_gen_dc { \
    id 484 \
    name status_3_out \
    type other \
    dir O \
    reset_level 1 \
    sync_rst true \
    corename dc_status_3_out \
    op interface \
    ports { status_3_out { O 32 vector } status_3_out_ap_vld { O 1 bit } } \
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


