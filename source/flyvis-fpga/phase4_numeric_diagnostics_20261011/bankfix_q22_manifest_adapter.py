"""Separately versioned local release gate for the bankfix Q22 candidate.

Fixes the frozen adapter's bitstream/bit key mismatch without editing that
adapter or its comparison. It does not adapt the EvidenceStepDriver return
schema, authorize a board operation, or establish a live PL connection.
"""
from pathlib import Path

from pynq_h_backend_adapter import PynqHBackendAdapter, sha_file
from q22_host_coordinator import TransactionError


FROZEN_COMPARISON = "a2f36bb961934225ee16ce5fa75ddf4e6671913fcad3cb557bb47afc4171ac54"
FROZEN_NUMERIC_PROFILE = "7e3d373e0ee34bb0f5df81e81a2f338b165747aeb57f8f91d296543bb96c2ca9"


class PreparedBankfixQ22Adapter(PynqHBackendAdapter):
    def init__(self, *args, hls_source_root, **kwargs):
        self.hls_source_root = Path(hls_source_root).resolve()
        super().init__(*args, **kwargs)

    def _validate_release_manifest(self):
        import json
        if self.identity.get("comparison_id") != FROZEN_COMPARISON:
            raise TransactionError("PL_IDENTITY", "this prepared adapter only binds the frozen Phase4 Q22 comparison")
        if self.expected_firmware.get("numeric_profile_sha256") != FROZEN_NUMERIC_PROFILE:
            raise TransactionError("PL_IDENTITY", "this prepared adapter cannot bind a Q24 or another numeric profile")
        if sha_file(self.soc_manifest_path) != self.expected_firmware["soc_manifest_sha256"]:
            raise TransactionError("PL_IDENTITY", "SoC release manifest changed after preparation")
        manifest = json.loads(self.soc_manifest_path.read_text(encoding="utf-8"))
        if manifest.get("status") != "FULL_SOC_BIT_HWH_READY_BOARD_NOT_AUTHORIZED":
            raise TransactionError("PL_IDENTITY", "release manifest is not an eligible local candidate")
        files = manifest.get("files", {})
        # Manifest field names and firmware field names are distinct.
        for record_key, firmware_key in (("bitstream", "bit_sha256"), ("hwh", "hwh_sha256")):
            row = files.get(record_key, {})
            expected = self.expected_firmware[firmware_key]
            if row.get("sha256") != expected:
                raise TransactionError("PL_IDENTITY", record_key + " identity differs from the selected release")
            p = self.soc_manifest_path.parent / row.get("path", "")
            if not p.is_file() or sha_file(p) != expected:
                raise TransactionError("PL_IDENTITY", record_key + " file bytes differ from the selected release")
        rows = {Path(row["path"]).name: row for row in files.get("hls_sources_and_roms", [])}
        for name, key in (("flyvis_t5c_source_raw.cpp", "hls_c_sha256"),
                          ("flyvis_t5c_constants_q22.hpp", "rom_sha256")):
            row = rows.get(name, {})
            expected = self.expected_firmware[key]
            if row.get("sha256") != expected:
                raise TransactionError("PL_IDENTITY", name + " identity differs from the comparison")
            # These source records are relative to P3 in the release generator.
            p = self.hls_source_root / row.get("path", "")
            if not p.is_file() or sha_file(p) != expected:
                raise TransactionError("PL_IDENTITY", name + " source bytes differ from the comparison")
        return manifest
