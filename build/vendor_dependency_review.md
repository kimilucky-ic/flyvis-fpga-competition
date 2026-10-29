# Vendor dependency review

Status: redistribution permission unresolved for ALIENTEK camera IP. This document does not grant a license.

The actual build uses56 identified files listed in portable/vendor_requirements.json. The local matched reference directory is the vendor tree from the previously accepted build; the portable preparation checks its identities before any copying. Required custom components include cmos_sensor,rgb2lcd,axi_dynclk and interface metadata. AMD catalog IP is reconstructed with the licensed toolchain, not replaced by lookalike source.

Local headers in cmos_capture_data.v and rgb2lcd.v identify 正点原子,2018–2028,and “All rights reserved”. No explicit redistribution grant was found in the inspected headers. The original official resource locator is https://www.openedv.com/thread-301505-1-1.html ; access timed out during this review, so current contents,download access and redistribution terms were not verified. Use the board vendor's original product-resource channel or ask the vendor for the permission/official repository; do not infer an MIT grant from a free download.

PYNQ upstream has its own BSD3-Clause and per-component licenses: https://github.com/Xilinx/PYNQ/blob/v2.7.0/LICENSE . The related dynamic-clock source is publicly available at https://github.com/Xilinx/PYNQ/blob/v2.7.0/boards/ip/axi_dynclk_v1_0/src/mmcme2_drp.v . This establishes a source locator, not byte identity between all local vendor files and upstream. Per-file notices must be retained and checked before copying; the PYNQ root license does not authorize unrelated ALIENTEK camera modules.

Publication must hold any third-party source/derived hardware artifact whose redistribution scope has not been resolved. The source snapshot may contain older vendor copies; adding a root MIT license does not cure them. Before release, run a file-level origin/permission review and either retain permitted source with required notices or provide a documented legal dependency acquisition route. Do not remove an essential dependency and claim the repository is self-contained.

No network request to a board,no device operation,and no vendor source replacement or new RTL was performed in this review.
