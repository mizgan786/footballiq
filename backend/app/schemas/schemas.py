from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class PlayerSeasonOut(BaseModel):
    season: int
    league: Optional[str] = None
    club_id: Optional[int] = None
    club_name: Optional[str] = None
    age: Optional[float] = None
    appearances: Optional[int] = None
    minutes_played: Optional[int] = None
    goals: Optional[int] = None
    assists: Optional[int] = None
    goals_per_90: Optional[float] = None
    assists_per_90: Optional[float] = None
    yellow_cards: Optional[int] = None
    red_cards: Optional[int] = None
    market_value_in_eur: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class PlayerCardOut(BaseModel):
    """Compact shape for player-search list cards."""
    id: int
    name: str
    position: Optional[str] = None
    club_id: Optional[int] = None
    club_name: Optional[str] = None
    season: Optional[int] = None
    age: Optional[float] = None
    market_value_in_eur: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class ClubOut(BaseModel):
    id: int
    name: str
    domestic_competition_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PlayerDetailOut(BaseModel):
    id: int
    name: str
    position: Optional[str] = None
    sub_position: Optional[str] = None
    foot: Optional[str] = None
    height_in_cm: Optional[float] = None
    nationality: Optional[str] = None
    seasons: List[PlayerSeasonOut] = []

    model_config = ConfigDict(from_attributes=True)


class PredictRequest(BaseModel):
    age: float = Field(..., ge=14, le=45)
    sub_position: str
    foot: str = Field(..., pattern="^(left|right|both)$")
    league: str = Field(..., pattern="^(GB1|ES1|L1|IT1|FR1)$")
    appearances: int = Field(..., ge=0, le=70)
    minutes_played: int = Field(..., ge=0, le=6300)
    goals: int = Field(..., ge=0)
    assists: int = Field(..., ge=0)
    yellow_cards: int = Field(0, ge=0)
    red_cards: int = Field(0, ge=0)
    height_in_cm: Optional[float] = Field(None, description="Defaults to the median height for the given sub_position if omitted")
    club_id: Optional[int] = Field(None, description="If provided, uses that club's most recent prestige score")


class PredictResponse(BaseModel):
    predicted_value_eur: float
    model_used: str
    important_factors: List[str]
    disclaimer: str = (
        "This is a statistical estimate produced by a trained model, not an official "
        "or objectively correct player valuation."
    )


class ComparePlayerResult(BaseModel):
    id: int
    name: str
    position: Optional[str] = None
    sub_position: Optional[str] = None
    latest_season: PlayerSeasonOut
    predicted_value_eur: float
    difference_eur: float
    difference_pct: float


class CompareRequest(BaseModel):
    player_id_a: int
    player_id_b: int


class CompareResponse(BaseModel):
    player_a: ComparePlayerResult
    player_b: ComparePlayerResult


class AnalyticsSummaryOut(BaseModel):
    players_analyzed: int
    seasons_covered: List[int]
    average_market_value_eur: float
    highest_valued_player: PlayerCardOut
    model_r2: float


class ModelMetricsOut(BaseModel):
    model_name: str
    validation: dict
    test: dict


class ValueBucketOut(BaseModel):
    bucket: str
    count: int


class PositionValueOut(BaseModel):
    position: str
    avg_market_value_eur: float
    n: int


class AgeValuePointOut(BaseModel):
    age: float
    market_value_eur: float


class GoalsValuePointOut(BaseModel):
    goals: int
    market_value_eur: float


class ActualPredictedPointOut(BaseModel):
    actual_eur: float
    predicted_eur: float


class FeatureImportanceOut(BaseModel):
    feature: str
    importance: float


class AnalyticsChartsOut(BaseModel):
    market_value_distribution: List[ValueBucketOut]
    value_by_position: List[PositionValueOut]
    age_vs_value: List[AgeValuePointOut]
    goals_vs_value: List[GoalsValuePointOut]
    actual_vs_predicted: List[ActualPredictedPointOut]
    feature_importance: List[FeatureImportanceOut]


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = Field(default_factory=list, description="Prior turns, oldest first")


class ChatSource(BaseModel):
    source: str
    title: str


class ChatResponse(BaseModel):
    reply: str
    sources: List[ChatSource] = []
