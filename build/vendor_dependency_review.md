# Vendor dependencies: acquisition, identity and permission

Updated 2026-10-29. Official acquisition route verified; third-party redistribution permission remains unresolved. Public access to a download is not a new license grant.

## Obtain the original board resources

1. Open the [manufacturer's product page](https://www.alientek.com/Product_Details_17/38.html), then its product-resource link. The official [LingHangZhe ZYNQ 7010/7020 resource index](https://www.openedv.com/docs/boards/fpga/zdyz_linhanz%28V2%29.html) was readable on 2026-10-29.
2. Use its **资料盘 / A盘** link: https://pan.baidu.com/s/1vXxmhg_mZm_OVg4xQeiCVQ (the official page supplies extraction code `zdyz`). Obtain the vendor's 7020 OV5640/video-to-LCD reference matching your board. A live listing was checked; the full archive was not downloaded or accepted in this task. The newer Z20 product is not automatically the same reference.
3. Supply the extracted reference/build tree as `--vendor-dir`. It must contain the exact relative files in [portable/vendor_requirements.json](portable/vendor_requirements.json), including `base.bd`, `base.xdc`, `ov5640_lcd.tcl`, the `bd_xci/ip/` metadata and custom `ip_repo/` tree. Some files are derived by the accepted vendor-project preparation, not necessarily present directly in the downloaded archive. We have not proved that today's download reproduces those derived bytes.
4. Run the existing offline preparation command from `build/portable`: `python prepare.py --vendor-dir D:/vendor_camera --output D:/flyvis_build`. It validates all 56 dependency hashes and 58 neural RTL/image hashes before copying. It never launches Vivado or accesses a board. Missing or different bytes stop the command; do not edit expected hashes simply to accept a new download.
5. If the current vendor package differs, retain it and its license, ask the manufacturer for the matching OV5640/video2lcd reference revision, or establish a separately validated migration. Do not mix an unvalidated vendor revision into the accepted firmware identity. [Portable instructions](portable/README.md) give the separately authorized Vivado stages.

## License and clean-build limits

ALIENTEK headers in camera sources reserve rights. [The held-file inventory](../report/third_party_holds.json) identifies 28 source instances; team MIT licensing does not override them or automatically clear derived BIT/HWH. The official resource page and free download do not establish permission to republish the source. Keep the repository private until the public redistribution scope is resolved. No external vendor contact was sent.

PYNQ's [v2.7 license](https://github.com/Xilinx/PYNQ/blob/v2.7.0/LICENSE) and component notices apply to PYNQ-origin code. They do not license unrelated ALIENTEK camera modules. Exact third-party notices must be retained.

The accepted environment's identities and portable preparation checks exist. Fresh source-to-BIT reproduction from the current official download, alternate-machine Vivado verification and electrical signoff have not been executed. This acquisition route closes the missing source-locator documentation; it does not manufacture those validations or permissions.
