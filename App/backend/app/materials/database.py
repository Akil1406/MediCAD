"""SQLite medical material database repository."""

import sqlite3
import json
from pathlib import Path
from ..models.materials import Material
from .catalog import MEDICAL_MATERIALS_CATALOG
from ..config import DEFAULT_DB_PATH


class MaterialDatabase:
    def __init__(self, db_path: Path | str | None = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_tables()
        self._seed_materials()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS materials (
                    material_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    common_trade_names TEXT NOT NULL,
                    family TEXT NOT NULL,
                    category TEXT NOT NULL,
                    density_g_cm3 REAL NOT NULL,
                    tensile_strength_mpa REAL NOT NULL,
                    yield_strength_mpa REAL,
                    elastic_modulus_mpa REAL NOT NULL,
                    flexural_modulus_mpa REAL,
                    elongation_at_break_pct REAL,
                    shore_hardness TEXT,
                    temperature_min_c REAL NOT NULL,
                    temperature_max_c REAL NOT NULL,
                    manufacturing_methods TEXT NOT NULL,
                    sterilization_compatibility TEXT NOT NULL,
                    chemical_resistance TEXT NOT NULL,
                    iso_10993_reference TEXT NOT NULL,
                    typical_applications TEXT NOT NULL,
                    source TEXT NOT NULL,
                    source_reference TEXT NOT NULL,
                    data_retrieval_date TEXT NOT NULL
                )
            """)
            conn.commit()

    def _seed_materials(self):
        with self._get_connection() as conn:
            for mat in MEDICAL_MATERIALS_CATALOG:
                conn.execute("""
                    INSERT OR REPLACE INTO materials (
                        material_id, name, common_trade_names, family, category,
                        density_g_cm3, tensile_strength_mpa, yield_strength_mpa,
                        elastic_modulus_mpa, flexural_modulus_mpa, elongation_at_break_pct,
                        shore_hardness, temperature_min_c, temperature_max_c,
                        manufacturing_methods, sterilization_compatibility,
                        chemical_resistance, iso_10993_reference, typical_applications,
                        source, source_reference, data_retrieval_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    mat.material_id,
                    mat.name,
                    json.dumps(mat.common_trade_names),
                    mat.family,
                    mat.category,
                    mat.density_g_cm3,
                    mat.tensile_strength_mpa,
                    mat.yield_strength_mpa,
                    mat.elastic_modulus_mpa,
                    mat.flexural_modulus_mpa,
                    mat.elongation_at_break_pct,
                    mat.shore_hardness,
                    mat.temperature_min_c,
                    mat.temperature_max_c,
                    json.dumps(mat.manufacturing_methods),
                    json.dumps(mat.sterilization_compatibility),
                    json.dumps(mat.chemical_resistance),
                    mat.iso_10993_biocompatibility_reference,
                    json.dumps(mat.typical_medical_applications),
                    mat.source,
                    mat.source_reference,
                    mat.data_retrieval_date
                ))
            conn.commit()

    def get_all_materials(self) -> list[Material]:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM materials ORDER BY name ASC")
            rows = cursor.fetchall()
            return [self._row_to_material(r) for r in rows]

    def get_material_by_id(self, material_id: str) -> Material | None:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM materials WHERE material_id = ?", (material_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_material(row)
            return None

    def _row_to_material(self, row: sqlite3.Row) -> Material:
        return Material(
            material_id=row["material_id"],
            name=row["name"],
            common_trade_names=json.loads(row["common_trade_names"]),
            family=row["family"],
            category=row["category"],
            density_g_cm3=float(row["density_g_cm3"]),
            tensile_strength_mpa=float(row["tensile_strength_mpa"]),
            yield_strength_mpa=float(row["yield_strength_mpa"]) if row["yield_strength_mpa"] is not None else None,
            elastic_modulus_mpa=float(row["elastic_modulus_mpa"]),
            flexural_modulus_mpa=float(row["flexural_modulus_mpa"]) if row["flexural_modulus_mpa"] is not None else None,
            elongation_at_break_pct=float(row["elongation_at_break_pct"]) if row["elongation_at_break_pct"] is not None else None,
            shore_hardness=row["shore_hardness"],
            temperature_min_c=float(row["temperature_min_c"]),
            temperature_max_c=float(row["temperature_max_c"]),
            manufacturing_methods=json.loads(row["manufacturing_methods"]),
            sterilization_compatibility=json.loads(row["sterilization_compatibility"]),
            chemical_resistance=json.loads(row["chemical_resistance"]),
            iso_10993_biocompatibility_reference=row["iso_10993_reference"],
            typical_medical_applications=json.loads(row["typical_applications"]),
            source=row["source"],
            source_reference=row["source_reference"],
            data_retrieval_date=row["data_retrieval_date"]
        )
