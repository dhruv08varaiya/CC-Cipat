from fastapi import APIRouter, HTTPException, Query
from pathlib import Path
import json
import pandas as pd
from typing import Optional, List, Dict, Any

router = APIRouter()
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
SYNTHETIC_DIR = BACKEND_DIR / "data" / "synthetic"
REPORTS_DIR = BACKEND_DIR / "reports"

@router.get("/list")
def list_datasets():
    """List all synthetic banking datasets and their file info."""
    datasets = []
    if SYNTHETIC_DIR.exists():
        for csv_file in sorted(SYNTHETIC_DIR.glob("*.csv")):
            datasets.append({
                "table_name": csv_file.stem,
                "filename": csv_file.name,
                "size_bytes": csv_file.stat().st_size
            })
    return datasets

@router.get("/statistics")
def get_dataset_statistics():
    """Return precomputed dataset statistics from Stage 2."""
    stats_file = REPORTS_DIR / "dataset_statistics.json"
    if stats_file.exists():
        with open(stats_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@router.get("/preview/{table_name}")
def preview_dataset(
    table_name: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """Paginated preview of synthetic banking table data."""
    csv_file = SYNTHETIC_DIR / f"{table_name}.csv"
    if not csv_file.exists():
        raise HTTPException(status_code=404, detail=f"Dataset table '{table_name}' not found.")

    try:
        # Read header and total lines for count
        total_rows = sum(1 for _ in open(csv_file, "r", encoding="utf-8")) - 1
        skip = (page - 1) * page_size
        df = pd.read_csv(csv_file, skiprows=range(1, skip + 1) if skip > 0 else None, nrows=page_size)
        return {
            "table_name": table_name,
            "total_rows": total_rows,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_rows + page_size - 1) // page_size,
            "columns": list(df.columns),
            "data": df.fillna("").to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
