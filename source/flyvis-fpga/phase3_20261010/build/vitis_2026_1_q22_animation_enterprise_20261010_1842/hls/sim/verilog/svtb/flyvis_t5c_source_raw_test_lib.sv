//==============================================================
//Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2026.1.1 (64-bit)
//Tool Version Limit: 2026.06
//Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
//Copyright 2022-2026 Advanced Micro Devices, Inc. All Rights Reserved.
//
//==============================================================
`ifndef FLYVIS_T5C_SOURCE_RAW_TEST_LIB__SV                                    
    `define FLYVIS_T5C_SOURCE_RAW_TEST_LIB__SV                                
                                                                          
    `include "uvm_macros.svh"                                           
                                                                          
    class flyvis_t5c_source_raw_test_lib extends uvm_test;                          
                                                                          
        flyvis_t5c_source_raw_env top_env;                                          
                                                                          
        `uvm_component_utils(flyvis_t5c_source_raw_test_lib)                        
                                                                          
        function new (string name, uvm_component parent = null);          
            super.new(name, parent);                                      
        endfunction                                                       
                                                                          
        virtual function void build_phase(uvm_phase phase);               
            super.build_phase(phase);                                     
            top_env = flyvis_t5c_source_raw_subsystem_pkg::flyvis_t5c_source_raw_env::type_id::create("top_env", this);
            uvm_config_db#(uvm_object_wrapper)::set(                      
                    this,                                                 
                    "top_env.flyvis_t5c_source_raw_virtual_sqr.run_phase",        
                    "default_sequence",                                 
                    flyvis_t5c_source_raw_subsys_test_sequence_lib::type_id::get()  
                );                                                        
            `uvm_info(this.get_full_name(), "build_phase done", UVM_LOW)
        endfunction                                                       
        virtual function void end_of_elaboration_phase(uvm_phase phase);  
            uvm_root top = uvm_root::get();                               
            top.print_topology();                                         
        endfunction                                                       
    endclass                                                              
                                                                          
`endif                                                                    
