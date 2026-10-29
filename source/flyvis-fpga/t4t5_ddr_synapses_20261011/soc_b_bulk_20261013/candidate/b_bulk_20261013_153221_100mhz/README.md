B bulk DDR ABI2 candidate, Vivado2026.1.1 xc7z020clg400-2,100MHz.
Local actual-BD simulation (with documented build-local native PS7 VIP DDRC scheduling repair) and routed timing only; board has not been operated.
Use FlyvisBBulk from arm_controller.py with an already loaded, separately authorized ABI2 overlay. ABI1 driver is incompatible.
All433880 original edges,16402 source states,5768 old-x and output candidates; source BRAM main/tail revision.
Flush edge/input/output caches before START; invalidate output only after DONE, RESULT_OK, no errors and idle transports. Partial results never COMMIT. Retain all CMA buffers until idle.
Exact implementation and system audits, performance context and SHA256 are in the parent release records.
