from fastapi import APIRouter, Query
from app.models import (
    SummaryResponse, MonthlyStats, WeeklyStats,
    YearlyStats, PaceTrendItem, PersonalBestsResponse
)
from app.services.stats_service import (
    get_summary, get_monthly_stats, get_weekly_stats,
    get_yearly_stats, get_pace_trend, get_personal_bests
)

router = APIRouter(prefix="/api/stats", tags=["统计"])


@router.get("/summary", response_model=SummaryResponse)
def summary():
    return get_summary()


@router.get("/monthly", response_model=list[MonthlyStats])
def monthly(year: int = Query(...)):
    return get_monthly_stats(year)


@router.get("/weekly", response_model=list[WeeklyStats])
def weekly(year: int = Query(...), month: int = Query(...)):
    return get_weekly_stats(year, month)


@router.get("/yearly", response_model=list[YearlyStats])
def yearly():
    return get_yearly_stats()


@router.get("/pace-trend", response_model=list[PaceTrendItem])
def pace_trend(period: str = Query("monthly", enum=["monthly", "weekly", "yearly"])):
    return get_pace_trend(period)


@router.get("/personal-bests", response_model=PersonalBestsResponse)
def personal_bests():
    return {"personal_bests": get_personal_bests()}
