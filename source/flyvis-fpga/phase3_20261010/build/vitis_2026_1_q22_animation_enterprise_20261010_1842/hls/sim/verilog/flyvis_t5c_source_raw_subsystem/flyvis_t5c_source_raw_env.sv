//==============================================================
//Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2026.1.1 (64-bit)
//Tool Version Limit: 2026.06
//Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
//Copyright 2022-2026 Advanced Micro Devices, Inc. All Rights Reserved.
//
//==============================================================
`ifndef FLYVIS_T5C_SOURCE_RAW_ENV__SV                                                                                   
    `define FLYVIS_T5C_SOURCE_RAW_ENV__SV                                                                               
                                                                                                                    
                                                                                                                    
    class flyvis_t5c_source_raw_env extends uvm_env;                                                                          
                                                                                                                    
        flyvis_t5c_source_raw_virtual_sequencer flyvis_t5c_source_raw_virtual_sqr;                                                      
        flyvis_t5c_source_raw_config flyvis_t5c_source_raw_cfg;                                                                         
                                                                                                                    
        axi_pkg::axi_env#(64,4,8,3,1) axi_master_gmem0;
        axi_pkg::axi_env#(6,4,4,3,1) axi_lite_control;
                                                                                                                    
        flyvis_t5c_source_raw_reference_model   refm;                                                                         
                                                                                                                    
        flyvis_t5c_source_raw_subsystem_monitor subsys_mon;                                                                   
                                                                                                                    
        `uvm_component_utils_begin(flyvis_t5c_source_raw_env)                                                                 
        `uvm_field_object (refm, UVM_DEFAULT | UVM_REFERENCE)                                                       
        `uvm_field_object (flyvis_t5c_source_raw_virtual_sqr, UVM_DEFAULT | UVM_REFERENCE)                                    
        `uvm_field_object (flyvis_t5c_source_raw_cfg        , UVM_DEFAULT)                                                    
        `uvm_component_utils_end                                                                                    
                                                                                                                    
        function new (string name = "flyvis_t5c_source_raw_env", uvm_component parent = null);                              
            super.new(name, parent);                                                                                
        endfunction                                                                                                 
                                                                                                                    
        extern virtual function void build_phase(uvm_phase phase);                                                  
        extern virtual function void connect_phase(uvm_phase phase);                                                
        extern virtual task          run_phase(uvm_phase phase);                                                    
                                                                                                                    
    endclass                                                                                                        
                                                                                                                    
    function void flyvis_t5c_source_raw_env::build_phase(uvm_phase phase);                                                    
        super.build_phase(phase);                                                                                   
        flyvis_t5c_source_raw_cfg = flyvis_t5c_source_raw_config::type_id::create("flyvis_t5c_source_raw_cfg", this);                           
                                                                                                                    

        flyvis_t5c_source_raw_cfg.gmem0_cfg.set_default();
        flyvis_t5c_source_raw_cfg.gmem0_cfg.drv_type = axi_pkg::SLAVE;
        flyvis_t5c_source_raw_cfg.gmem0_cfg.reset_level = axi_pkg::RESET_LEVEL_LOW;
        flyvis_t5c_source_raw_cfg.gmem0_cfg.write_latency_mode = TRANSACTION_FIRST;
        flyvis_t5c_source_raw_cfg.gmem0_cfg.read_latency_mode = TRANSACTION_FIRST;
        uvm_config_db#(axi_pkg::axi_cfg)::set(this, "axi_master_gmem0*", "cfg", flyvis_t5c_source_raw_cfg.gmem0_cfg);
        axi_master_gmem0 = axi_pkg::axi_env#(64,4,8,3,1)::type_id::create("axi_master_gmem0", this);

        flyvis_t5c_source_raw_cfg.control_cfg.set_default();
        flyvis_t5c_source_raw_cfg.control_cfg.drv_type = axi_pkg::MASTER;
        flyvis_t5c_source_raw_cfg.control_cfg.reset_level = axi_pkg::RESET_LEVEL_LOW;
        uvm_config_db#(axi_pkg::axi_cfg)::set(this, "axi_lite_control*", "cfg", flyvis_t5c_source_raw_cfg.control_cfg);
        axi_lite_control = axi_pkg::axi_env#(6,4,4,3,1)::type_id::create("axi_lite_control", this);



        refm = flyvis_t5c_source_raw_reference_model::type_id::create("refm", this);


        uvm_config_db#(flyvis_t5c_source_raw_reference_model)::set(this, "*", "refm", refm);


        `uvm_info(this.get_full_name(), "set reference model by uvm_config_db", UVM_LOW)


        subsys_mon = flyvis_t5c_source_raw_subsystem_monitor::type_id::create("subsys_mon", this);


        flyvis_t5c_source_raw_virtual_sqr = flyvis_t5c_source_raw_virtual_sequencer::type_id::create("flyvis_t5c_source_raw_virtual_sqr", this);
        `uvm_info(this.get_full_name(), "build_phase done", UVM_LOW)
    endfunction


    function void flyvis_t5c_source_raw_env::connect_phase(uvm_phase phase);
        super.connect_phase(phase);


        if(flyvis_t5c_source_raw_cfg.gmem0_cfg.drv_type==axi_pkg::MASTER ||flyvis_t5c_source_raw_cfg.gmem0_cfg.drv_type==axi_pkg::SLAVE)
            flyvis_t5c_source_raw_virtual_sqr.gmem0_sqr = axi_master_gmem0.vsqr;
        axi_master_gmem0.item_wtr_port.connect(subsys_mon.gmem0_wtr_imp);
        axi_master_gmem0.item_rtr_port.connect(subsys_mon.gmem0_rtr_imp);
        uvm_callbacks#(axi_pkg::axi_state, axi_pkg::axi_state_cbs)::add(axi_master_gmem0.state, refm.axi_memaccess_cb_gmem0);
        if(flyvis_t5c_source_raw_cfg.control_cfg.drv_type==axi_pkg::MASTER ||flyvis_t5c_source_raw_cfg.control_cfg.drv_type==axi_pkg::SLAVE)
            flyvis_t5c_source_raw_virtual_sqr.control_sqr = axi_lite_control.vsqr;
        axi_lite_control.item_wtr_port.connect(subsys_mon.control_wtr_imp);
        axi_lite_control.item_rtr_port.connect(subsys_mon.control_rtr_imp);
        refm.flyvis_t5c_source_raw_cfg = flyvis_t5c_source_raw_cfg;
        `uvm_info(this.get_full_name(), "connect phase done", UVM_LOW)
    endfunction


    task flyvis_t5c_source_raw_env::run_phase(uvm_phase phase);
        `uvm_info(this.get_full_name(), "flyvis_t5c_source_raw_env is running", UVM_LOW)
    endtask


`endif
