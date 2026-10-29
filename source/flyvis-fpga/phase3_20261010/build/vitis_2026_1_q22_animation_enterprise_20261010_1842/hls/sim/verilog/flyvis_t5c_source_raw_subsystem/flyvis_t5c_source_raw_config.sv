//==============================================================
//Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2026.1.1 (64-bit)
//Tool Version Limit: 2026.06
//Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
//Copyright 2022-2026 Advanced Micro Devices, Inc. All Rights Reserved.
//
//==============================================================
`ifndef FLYVIS_T5C_SOURCE_RAW_CONFIG__SV                        
    `define FLYVIS_T5C_SOURCE_RAW_CONFIG__SV                    
                                                            
    class flyvis_t5c_source_raw_config extends uvm_object;            
                                                            
        int check_ena;                                      
        int cover_ena;                                      
        axi_pkg::axi_cfg gmem0_cfg;
        axi_pkg::axi_cfg control_cfg;

        `uvm_object_utils_begin(flyvis_t5c_source_raw_config)         
        `uvm_field_object(gmem0_cfg, UVM_DEFAULT);
        `uvm_field_object(control_cfg, UVM_DEFAULT);
        `uvm_field_int   (check_ena , UVM_DEFAULT)          
        `uvm_field_int   (cover_ena , UVM_DEFAULT)          
        `uvm_object_utils_end                               

        function new (string name = "flyvis_t5c_source_raw_config");
            super.new(name);                                
            gmem0_cfg = new("gmem0_cfg", 1);
            control_cfg = axi_pkg::axi_cfg::type_id::create("control_cfg");
        endfunction                                         
                                                            
    endclass                                                
                                                            
`endif                                                      
