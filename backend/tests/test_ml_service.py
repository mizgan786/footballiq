"""
Tests for the ML service: model loading, feature vector construction,
and basic prediction sanity checks (not exact-value assertions - the
model is trained on real data and can be retrained, so tests check
*shape and range*, not specific numbers).
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services import ml_service


def test_model_loaded():
    assert ml_service.PIPELINE is not None
    assert ml_service.MODEL_NAME in ("linear_regression", "ridge", "random_forest", "gradient_boosting", "xgboost")
    assert len(ml_service.FEATURE_COLUMNS) > 0


def test_build_feature_vector_shape():
    payload = {
        "age": 23, "sub_position": "Right Winger", "foot": "left", "league": "GB1",
        "appearances": 35, "minutes_played": 3000, "goals": 12, "assists": 10,
        "yellow_cards": 3, "red_cards": 0,
    }
    X = ml_service.build_feature_vector(payload, club_prestige_log=15.0, height_in_cm=178.0)
    assert list(X.columns) == ml_service.FEATURE_COLUMNS
    assert X.shape[0] == 1
    assert X["subpos_Right Winger"].iloc[0] == 1
    assert X["foot_left"].iloc[0] == 1
    assert X["league_GB1"].iloc[0] == 1
    # a sub-position/league/foot not present in this row should be 0, not missing
    assert X["subpos_Goalkeeper"].iloc[0] == 0
    assert X["league_ES1"].iloc[0] == 0


def test_build_feature_vector_unknown_category_does_not_crash():
    """An unseen sub_position (typo, future data drift) should fall back to
    all-zero dummy columns rather than raising - reindex(fill_value=0) handles this."""
    payload = {
        "age": 23, "sub_position": "Some New Role", "foot": "left", "league": "GB1",
        "appearances": 10, "minutes_played": 500, "goals": 1, "assists": 1,
        "yellow_cards": 0, "red_cards": 0,
    }
    X = ml_service.build_feature_vector(payload, club_prestige_log=14.0, height_in_cm=180.0)
    assert X.shape[0] == 1  # did not raise, produced a row


def test_predict_market_value_is_positive_and_reasonable():
    payload = {
        "age": 23, "sub_position": "Right Winger", "foot": "left", "league": "GB1",
        "appearances": 35, "minutes_played": 3000, "goals": 12, "assists": 10,
        "yellow_cards": 3, "red_cards": 0,
    }
    value = ml_service.predict_market_value(payload, club_prestige_log=16.0, height_in_cm=178.0)
    assert value > 0
    # sanity bound - no player-season in training data exceeds ~200M EUR,
    # so a well-behaved model shouldn't wildly extrapolate past that
    assert value < 300_000_000


def test_top_feature_names_returns_known_columns():
    names = ml_service.top_feature_names(5)
    assert len(names) == 5
    assert all(n in ml_service.FEATURE_COLUMNS for n in names)
