import sqlite3
from app.database import get_connection


def get_summary() -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(SUM(distance), 0), COUNT(*) FROM run_records")
    row = cursor.fetchone()
    total_distance = row[0]
    total_runs = row[1]

    cursor.execute("SELECT COALESCE(AVG(avg_pace), 0) FROM run_records")
    avg_pace = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COALESCE(SUM(distance), 0) FROM run_records WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now')"
    )
    this_month_distance = cursor.fetchone()[0]
    conn.close()

    return {
        "total_distance": round(total_distance, 2),
        "total_runs": total_runs,
        "avg_pace": round(avg_pace, 2),
        "this_month_distance": round(this_month_distance, 2)
    }


def get_monthly_stats(year: int) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT strftime('%m', date) as month,
                  COALESCE(SUM(distance), 0),
                  COUNT(*),
                  COALESCE(AVG(avg_pace), 0)
           FROM run_records
           WHERE strftime('%Y', date) = ?
           GROUP BY month
           ORDER BY month""",
        (str(year),)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {"period": f"{year}-{row[0]}", "distance": round(row[1], 2), "runs": row[2], "avg_pace": round(row[3], 2)}
        for row in rows
    ]


def get_weekly_stats(year: int, month: int) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    month_str = f"{year}-{month:02d}"
    cursor.execute(
        """SELECT strftime('%W', date) as week,
                  COALESCE(SUM(distance), 0),
                  COUNT(*),
                  COALESCE(AVG(avg_pace), 0)
           FROM run_records
           WHERE strftime('%Y-%m', date) = ?
           GROUP BY week
           ORDER BY week""",
        (month_str,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {"period": f"{year}-W{row[0]}", "distance": round(row[1], 2), "runs": row[2], "avg_pace": round(row[3], 2)}
        for row in rows
    ]


def get_yearly_stats() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT strftime('%Y', date) as year,
                  COALESCE(SUM(distance), 0),
                  COUNT(*),
                  COALESCE(AVG(avg_pace), 0)
           FROM run_records
           GROUP BY year
           ORDER BY year"""
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {"period": row[0], "distance": round(row[1], 2), "runs": row[2], "avg_pace": round(row[3], 2)}
        for row in rows
    ]


def get_pace_trend(period: str = "monthly") -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    if period == "weekly":
        cursor.execute(
            """SELECT strftime('%Y-W%W', date) as p,
                      COALESCE(AVG(avg_pace), 0),
                      COALESCE(SUM(distance), 0),
                      COUNT(*)
               FROM run_records
               GROUP BY p ORDER BY p"""
        )
    elif period == "yearly":
        cursor.execute(
            """SELECT strftime('%Y', date) as p,
                      COALESCE(AVG(avg_pace), 0),
                      COALESCE(SUM(distance), 0),
                      COUNT(*)
               FROM run_records
               GROUP BY p ORDER BY p"""
        )
    else:
        cursor.execute(
            """SELECT strftime('%Y-%m', date) as p,
                      COALESCE(AVG(avg_pace), 0),
                      COALESCE(SUM(distance), 0),
                      COUNT(*)
               FROM run_records
               GROUP BY p ORDER BY p"""
        )
    rows = cursor.fetchall()
    conn.close()
    return [
        {"period": row[0], "avg_pace": round(row[1], 2), "distance": round(row[2], 2), "runs": row[3]}
        for row in rows
    ]


def get_personal_bests() -> list[dict]:
    categories = [
        {"name": "5K", "min_dist": 4.5, "max_dist": 5.5},
        {"name": "10K", "min_dist": 9.5, "max_dist": 10.5},
        {"name": "半马", "min_dist": 20.0, "max_dist": 22.0},
        {"name": "全马", "min_dist": 41.0, "max_dist": 43.0},
    ]
    conn = get_connection()
    cursor = conn.cursor()
    results = []

    for cat in categories:
        cursor.execute(
            """SELECT duration, avg_pace, date, id
               FROM run_records
               WHERE distance BETWEEN ? AND ?
               ORDER BY duration ASC
               LIMIT 1""",
            (cat["min_dist"], cat["max_dist"])
        )
        row = cursor.fetchone()
        if row:
            results.append({
                "category": cat["name"],
                "best_time": row[0],
                "best_pace": round(row[1], 2),
                "date": row[2],
                "record_id": row[3]
            })
        else:
            results.append({
                "category": cat["name"],
                "best_time": None,
                "best_pace": None,
                "date": None,
                "record_id": None
            })

    conn.close()
    return results


def get_goal_progress(goal_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, year, target_distance FROM goals WHERE id = ?", (goal_id,))
    goal = cursor.fetchone()
    if not goal:
        conn.close()
        return None

    year = goal[1]
    target_distance = goal[2]

    cursor.execute(
        "SELECT COALESCE(SUM(distance), 0) FROM run_records WHERE strftime('%Y', date) = ?",
        (str(year),)
    )
    current_distance = cursor.fetchone()[0]

    cursor.execute(
        """SELECT strftime('%m', date) as month, COALESCE(SUM(distance), 0)
           FROM run_records
           WHERE strftime('%Y', date) = ?
           GROUP BY month ORDER BY month""",
        (str(year),)
    )
    rows = cursor.fetchall()
    monthly_progress = [{"month": row[0], "distance": round(row[1], 2)} for row in rows]
    conn.close()

    percentage = round((current_distance / target_distance) * 100, 2) if target_distance > 0 else 0

    return {
        "target_distance": target_distance,
        "current_distance": round(current_distance, 2),
        "percentage": percentage,
        "monthly_progress": monthly_progress
    }
