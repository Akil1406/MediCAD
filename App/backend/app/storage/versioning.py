"""Design version comparison and difference calculator."""

import json
from typing import Any


class VersionComparator:
    @staticmethod
    def compute_diff(version_a: dict, version_b: dict) -> dict[str, Any]:
        spec_a = json.loads(version_a["specification_json"]) if isinstance(version_a["specification_json"], str) else version_a["specification_json"]
        spec_b = json.loads(version_b["specification_json"]) if isinstance(version_b["specification_json"], str) else version_b["specification_json"]

        all_keys = set(spec_a.keys()).union(set(spec_b.keys()))
        differences = {}

        for k in sorted(all_keys):
            val_a = spec_a.get(k)
            val_b = spec_b.get(k)
            if val_a != val_b:
                differences[k] = {
                    "from_version": version_a.get("version_number"),
                    "from_value": val_a,
                    "to_version": version_b.get("version_number"),
                    "to_value": val_b,
                    "delta": (val_b - val_a) if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)) else None
                }

        return {
            "design_id": version_a.get("design_id"),
            "base_version": version_a.get("version_number"),
            "target_version": version_b.get("version_number"),
            "changed_parameters_count": len(differences),
            "differences": differences
        }
