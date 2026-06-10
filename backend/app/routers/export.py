from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import io
import json
import csv
from app.database import get_connection

router = APIRouter(prefix="/api/export", tags=["导出"])


@router.get("/csv")
def export_csv():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM run_records ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return StreamingResponse(
            iter([""]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=running_records.csv"}
        )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(rows[0].keys())
    for row in rows:
        writer.writerow(tuple(row))

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=running_records.csv"}
    )


@router.get("/json")
def export_json():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM run_records ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()

    data = [dict(r) for r in rows]
    content = json.dumps(data, ensure_ascii=False, indent=2)

    return StreamingResponse(
        iter([content]),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=running_records.json"}
    )
