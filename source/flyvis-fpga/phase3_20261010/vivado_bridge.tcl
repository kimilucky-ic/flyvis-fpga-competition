# Task-owned, project-free Vivado 2026.1.1 MCP session. No Hardware Manager calls.
puts "FLYVIS_VIVADO_VERSION=[version -short]"
set flyvis_parts [get_parts -quiet *7z020*]
puts "FLYVIS_ZYNQ7020_PARTS=$flyvis_parts"
if {![info exists ::vmcp::core::started] || !$::vmcp::core::started} {
    source -notrace {C:/Users/hzy72/.vivado-mcp/tcl/vivado_server.tcl}
}
puts "FLYVIS_MCP_BRIDGE_READY"
vwait ::flyvis_bridge_shutdown
::vmcp::server::stop
exit
