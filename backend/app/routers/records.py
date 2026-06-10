from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional
from app.database import get_connection
from app.models import RunRecordCreate, RunRecordUpdate, RunRecordResponse, RecordListResponse, GpxParseResult
from app.services.gpx_parser import parse_gpx

router = APIRouter(prefix="/api/records", tags=["跑步记录"])


@router.post("", response_model=RunRecordResponse)
def create_record(record: RunRecordCreate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO run_records (date, distance, duration, avg_pace, avg_heart_rate, location, weather, feeling, gpx_data)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (record.date, record.distance, record.duration, record.avg_pace,
         record.avg_heart_rate, record.location, record.weather, record.feeling, record.gpx_data)
    )
    conn.commit()
    record_id = cursor.lastrowid
    cursor.execute("SELECT * FROM run_records WHERE id = ?", (record_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row)


@router.get("", response_model=RecordListResponse)
def list_records(
    page: int = 1,
    page_size: int = 20,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    distance_min: Optional[float] = None,
    distance_max: Optional[float] = None,
    location: Optional[str] = None,
    weather: Optional[str] = None,
    sort_by: Optional[str] = "date",
    sort_order: Optional[str] = "desc",
):
    allowed_sort = {"date", "distance", "avg_pace", "duration"}
    if sort_by not in allowed_sort:
        sort_by = "date"
    if sort_order not in ("asc", "desc"):
        sort_order = "desc"

    conditions = []
    params = []
    if date_from:
        conditions.append("date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("date <= ?")
        params.append(date_to)
    if distance_min is not None:
        conditions.append("distance >= ?")
        params.append(distance_min)
    if distance_max is not None:
        conditions.append("distance <= ?")
        params.append(distance_max)
    if location:
        conditions.append("location LIKE ?")
        params.append(f"%{location}%")
    if weather:
        conditions.append("weather = ?")
        params.append(weather)

    where_clause = (" WHERE " + " AND ".join(conditions)) if conditions else ""

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM run_records{where_clause}", params)
    total = cursor.fetchone()[0]

    offset = (page - 1) * page_size
    cursor.execute(
        f"SELECT * FROM run_records{where_clause} ORDER BY {sort_by} {sort_order} LIMIT ? OFFSET ?",
        params + [page_size, offset]
    )
    rows = cursor.fetchall()
    conn.close()

    return RecordListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[dict(r) for r in rows]
    )


@router.get("/{record_id}", response_model=RunRecordResponse)
def get_record(record_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM run_records WHERE id = ?", (record_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="记录不存在")
    return dict(row)


@router.put("/{record_id}", response_model=RunRecordResponse)
def update_record(record_id: int, record: RunRecordUpdate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM run_records WHERE id = ?", (record_id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="记录不存在")

    updates = []
    params = []
    data = record.model_dump(exclude_unset=True)
    for key, value in data.items():
        updates.append(f"{key} = ?")
        params.append(value)

    if not updates:
        conn.close()
        return dict(existing)

    updates.append("updated_at = datetime('now')")
    params.append(record_id)
    cursor.execute(
        f"UPDATE run_records SET {', '.join(updates)} WHERE id = ?",
        params
    )
    conn.commit()
    cursor.execute("SELECT * FROM run_records WHERE id = ?", (record_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row)


@router.delete("/{record_id}")
def delete_record(record_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM run_records WHERE id = ?", (record_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="记录不存在")
    cursor.execute("DELETE FROM run_records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
    return {"message": "删除成功"}


@router.post("/gpx", response_model=GpxParseResult)
async def upload_gpx(file: UploadFile = File(...)):
    if not file.filename.endswith(".gpx"):
        raise HTTPException(status_code=400, detail="请上传GPX文件")
    content = await file.read()
    try:
        gpx_text = content.decode("utf-8")
        result = parse_gpx(gpx_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"GPX解析失败: {str(e)}")
