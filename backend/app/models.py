from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RunRecordCreate(BaseModel):
    date: str
    distance: float
    duration: int
    avg_pace: float
    avg_heart_rate: Optional[int] = None
    location: Optional[str] = ""
    weather: Optional[str] = ""
    feeling: Optional[str] = ""
    training_type: Optional[str] = ""
    gpx_data: Optional[str] = None


class RunRecordUpdate(BaseModel):
    date: Optional[str] = None
    distance: Optional[float] = None
    duration: Optional[int] = None
    avg_pace: Optional[float] = None
    avg_heart_rate: Optional[int] = None
    location: Optional[str] = None
    weather: Optional[str] = None
    feeling: Optional[str] = None
    training_type: Optional[str] = None
    gpx_data: Optional[str] = None


class RunRecordResponse(BaseModel):
    id: int
    date: str
    distance: float
    duration: int
    avg_pace: float
    avg_heart_rate: Optional[int] = None
    location: str
    weather: str
    feeling: str
    training_type: str
    gpx_data: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class RecordListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[RunRecordResponse]


class GpxParseResult(BaseModel):
    distance: float
    duration: int
    avg_pace: float
    points_count: int


class GoalCreate(BaseModel):
    year: int
    target_distance: float


class GoalUpdate(BaseModel):
    target_distance: Optional[float] = None


class GoalResponse(BaseModel):
    id: int
    year: int
    target_distance: float
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class GoalProgress(BaseModel):
    target_distance: float
    current_distance: float
    percentage: float
    monthly_progress: list[dict]


class SummaryResponse(BaseModel):
    total_distance: float
    total_runs: int
    avg_pace: float
    this_month_distance: float


class MonthlyStats(BaseModel):
    period: str
    distance: float
    runs: int
    avg_pace: float


class WeeklyStats(BaseModel):
    period: str
    distance: float
    runs: int
    avg_pace: float


class YearlyStats(BaseModel):
    period: str
    distance: float
    runs: int
    avg_pace: float


class PaceTrendItem(BaseModel):
    period: str
    avg_pace: float
    distance: float
    runs: int


class PersonalBest(BaseModel):
    category: str
    best_time: Optional[int] = None
    best_pace: Optional[float] = None
    date: Optional[str] = None
    record_id: Optional[int] = None


class PersonalBestsResponse(BaseModel):
    personal_bests: list[PersonalBest]


class TrainingTypeStatsItem(BaseModel):
    training_type: str
    runs: int
    distance: float
    avg_pace: float


class TrainingTypeStatsResponse(BaseModel):
    items: list[TrainingTypeStatsItem]
