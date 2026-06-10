from fastapi import APIRouter, HTTPException
from app.database import get_connection
from app.models import GoalCreate, GoalUpdate, GoalResponse, GoalProgress
from app.services.stats_service import get_goal_progress

router = APIRouter(prefix="/api/goals", tags=["年度目标"])


@router.get("", response_model=list[GoalResponse])
def list_goals():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM goals ORDER BY year DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.post("", response_model=GoalResponse)
def create_goal(goal: GoalCreate):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO goals (year, target_distance) VALUES (?, ?)",
            (goal.year, goal.target_distance)
        )
        conn.commit()
        goal_id = cursor.lastrowid
        cursor.execute("SELECT * FROM goals WHERE id = ?", (goal_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row)
    except Exception:
        conn.close()
        raise HTTPException(status_code=400, detail="该年度目标已存在")


@router.put("/{goal_id}", response_model=GoalResponse)
def update_goal(goal_id: int, goal: GoalUpdate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM goals WHERE id = ?", (goal_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="目标不存在")

    updates = []
    params = []
    data = goal.model_dump(exclude_unset=True)
    for key, value in data.items():
        updates.append(f"{key} = ?")
        params.append(value)

    if not updates:
        cursor.execute("SELECT * FROM goals WHERE id = ?", (goal_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row)

    updates.append("updated_at = datetime('now')")
    params.append(goal_id)
    cursor.execute(f"UPDATE goals SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    cursor.execute("SELECT * FROM goals WHERE id = ?", (goal_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row)


@router.get("/{goal_id}/progress", response_model=GoalProgress)
def goal_progress(goal_id: int):
    result = get_goal_progress(goal_id)
    if result is None:
        raise HTTPException(status_code=404, detail="目标不存在")
    return result


@router.get("/year/{year}/progress", response_model=GoalProgress)
def goal_progress_by_year(year: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM goals WHERE year = ?", (year,))
    goal = cursor.fetchone()
    conn.close()
    if not goal:
        raise HTTPException(status_code=404, detail="该年度目标不存在")
    result = get_goal_progress(goal[0])
    if result is None:
        raise HTTPException(status_code=404, detail="目标不存在")
    return result
