"""
test_app.py — Unit Tests for NutriGen
Run: pytest test_app.py -v
"""

import pytest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Patch MongoDB before importing app — no real DB connection needed for unit tests
with patch("pymongo.MongoClient"):
    from app import (
        app,
        calculate_bmi,
        get_bmi_category,
        calculate_calories,
        get_diet_type,
        get_meal_plan,
        get_tips,
    )


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


SAMPLE_MEAL = {
    "breakfast": {"foods": ["Oats", "Banana"],       "calories": 300},
    "lunch":     {"foods": ["Brown rice", "Dal"],     "calories": 450},
    "snack":     {"foods": ["Apple", "Almonds"],      "calories": 200},
    "dinner":    {"foods": ["Rotis", "Paneer"],       "calories": 400}
}

SAMPLE_TIPS = [
    "Drink 8 glasses of water.",
    "Avoid processed food.",
    "Exercise 30 minutes daily."
]


# ═══════════════════════════════════════════════════════════════
#  BMI TESTS
# ═══════════════════════════════════════════════════════════════

class TestCalculateBMI:

    def test_normal_weight_person(self):
        assert calculate_bmi(70, 175) == 22.9

    def test_underweight_person(self):
        assert calculate_bmi(45, 175) == 14.7

    def test_overweight_person(self):
        assert calculate_bmi(90, 175) == 29.4

    def test_obese_person(self):
        assert calculate_bmi(100, 170) == 34.6

    def test_returns_float(self):
        assert isinstance(calculate_bmi(70, 175), float)

    def test_rounded_to_one_decimal(self):
        result = calculate_bmi(68, 172)
        assert result == round(result, 1)

    def test_taller_person_lower_bmi(self):
        assert calculate_bmi(70, 190) < calculate_bmi(70, 160)

    def test_heavier_person_higher_bmi(self):
        assert calculate_bmi(100, 175) > calculate_bmi(60, 175)


# ═══════════════════════════════════════════════════════════════
#  BMI CATEGORY TESTS
# ═══════════════════════════════════════════════════════════════

class TestGetBMICategory:

    def test_underweight(self):
        assert get_bmi_category(17.0) == ("Underweight", "underweight")

    def test_normal_weight(self):
        assert get_bmi_category(22.0) == ("Normal weight", "normal")

    def test_overweight(self):
        assert get_bmi_category(27.0) == ("Overweight", "overweight")

    def test_obese(self):
        assert get_bmi_category(32.0) == ("Obese", "obese")

    def test_boundary_18_5_is_normal(self):
        assert get_bmi_category(18.5)[0] == "Normal weight"

    def test_boundary_25_is_overweight(self):
        assert get_bmi_category(25.0)[0] == "Overweight"

    def test_boundary_30_is_obese(self):
        assert get_bmi_category(30.0)[0] == "Obese"

    def test_returns_tuple_of_two(self):
        result = get_bmi_category(22.0)
        assert isinstance(result, tuple) and len(result) == 2

    def test_css_class_lowercase(self):
        _, css = get_bmi_category(22.0)
        assert css == css.lower()


# ═══════════════════════════════════════════════════════════════
#  CALORIE TESTS
# ═══════════════════════════════════════════════════════════════

class TestCalculateCalories:

    def test_returns_positive_integer(self):
        result = calculate_calories(70, 175, 25, "male", "sedentary", "maintenance")
        assert result > 0
        assert isinstance(result, int)

    def test_male_female_different(self):
        male   = calculate_calories(70, 175, 25, "male",   "moderate", "maintenance")
        female = calculate_calories(70, 175, 25, "female", "moderate", "maintenance")
        assert male != female

    def test_weight_loss_subtracts_500(self):
        maintain = calculate_calories(70, 175, 25, "male", "moderate", "maintenance")
        loss     = calculate_calories(70, 175, 25, "male", "moderate", "weight_loss")
        assert loss == maintain - 500

    def test_weight_gain_adds_500(self):
        maintain = calculate_calories(70, 175, 25, "male", "moderate", "maintenance")
        gain     = calculate_calories(70, 175, 25, "male", "moderate", "weight_gain")
        assert gain == maintain + 500

    def test_extra_active_higher_than_sedentary(self):
        sed = calculate_calories(70, 175, 25, "male", "sedentary",    "maintenance")
        ext = calculate_calories(70, 175, 25, "male", "extra_active", "maintenance")
        assert ext > sed

    def test_older_person_fewer_calories(self):
        young = calculate_calories(70, 175, 25, "male", "moderate", "maintenance")
        old   = calculate_calories(70, 175, 60, "male", "moderate", "maintenance")
        assert old < young

    def test_all_activity_levels_positive(self):
        for level in ["sedentary", "light", "moderate", "very_active", "extra_active"]:
            result = calculate_calories(70, 175, 25, "male", level, "maintenance")
            assert result > 0

    def test_all_goals_work(self):
        for goal in ["weight_loss", "maintenance", "weight_gain"]:
            result = calculate_calories(70, 175, 25, "male", "moderate", goal)
            assert result > 0


# ═══════════════════════════════════════════════════════════════
#  DIET TYPE TESTS
# ═══════════════════════════════════════════════════════════════

class TestGetDietType:

    def test_weight_loss_always_low_calorie(self):
        for cat in ["Underweight", "Normal weight", "Overweight", "Obese"]:
            assert get_diet_type(cat, "weight_loss") == "Low Calorie Diet"

    def test_weight_gain_always_high_protein(self):
        for cat in ["Underweight", "Normal weight", "Overweight", "Obese"]:
            assert get_diet_type(cat, "weight_gain") == "High Protein Diet"

    def test_maintenance_underweight_high_protein(self):
        assert get_diet_type("Underweight", "maintenance") == "High Protein Diet"

    def test_maintenance_overweight_low_calorie(self):
        assert get_diet_type("Overweight", "maintenance") == "Low Calorie Diet"

    def test_maintenance_obese_low_calorie(self):
        assert get_diet_type("Obese", "maintenance") == "Low Calorie Diet"

    def test_maintenance_normal_balanced(self):
        assert get_diet_type("Normal weight", "maintenance") == "Balanced Diet"

    def test_returns_string(self):
        assert isinstance(get_diet_type("Normal weight", "maintenance"), str)


# ═══════════════════════════════════════════════════════════════
#  MONGODB FETCH TESTS (mocked)
# ═══════════════════════════════════════════════════════════════

class TestGetMealPlan:

    @patch("app.db")
    def test_returns_four_meals(self, mock_db):
        mock_db.meal_plans.find_one.return_value = {
            "diet_pref": "vegetarian",
            "diet_type": "Low Calorie Diet",
            **SAMPLE_MEAL
        }
        result = get_meal_plan("vegetarian", "Low Calorie Diet")
        assert set(result.keys()) == {"breakfast", "lunch", "snack", "dinner"}

    @patch("app.db")
    def test_each_meal_has_foods_and_calories(self, mock_db):
        mock_db.meal_plans.find_one.return_value = {**SAMPLE_MEAL}
        result = get_meal_plan("vegetarian", "Balanced Diet")
        for meal in ["breakfast", "lunch", "snack", "dinner"]:
            assert "foods" in result[meal]
            assert "calories" in result[meal]

    @patch("app.db")
    def test_raises_if_not_found(self, mock_db):
        mock_db.meal_plans.find_one.return_value = None
        with pytest.raises(ValueError, match="No meal plan found"):
            get_meal_plan("vegan", "Keto Diet")

    @patch("app.db")
    def test_queries_with_correct_fields(self, mock_db):
        mock_db.meal_plans.find_one.return_value = {**SAMPLE_MEAL}
        get_meal_plan("non_vegetarian", "High Protein Diet")
        mock_db.meal_plans.find_one.assert_called_once_with(
            {"diet_pref": "non_vegetarian", "diet_type": "High Protein Diet"},
            {"_id": 0}
        )

    @patch("app.db")
    def test_breakfast_calories_correct(self, mock_db):
        mock_db.meal_plans.find_one.return_value = {**SAMPLE_MEAL}
        result = get_meal_plan("vegetarian", "Low Calorie Diet")
        assert result["breakfast"]["calories"] == 300


class TestGetTips:

    @patch("app.db")
    def test_returns_list(self, mock_db):
        mock_db.tips.find_one.return_value = {"goal": "weight_loss", "tips": SAMPLE_TIPS}
        result = get_tips("weight_loss")
        assert isinstance(result, list)

    @patch("app.db")
    def test_returns_correct_tips(self, mock_db):
        mock_db.tips.find_one.return_value = {"goal": "weight_loss", "tips": SAMPLE_TIPS}
        result = get_tips("weight_loss")
        assert len(result) == 3

    @patch("app.db")
    def test_empty_list_if_goal_not_found(self, mock_db):
        mock_db.tips.find_one.return_value = None
        result = get_tips("unknown_goal")
        assert result == []

    @patch("app.db")
    def test_queries_by_goal(self, mock_db):
        mock_db.tips.find_one.return_value = {"goal": "maintenance", "tips": SAMPLE_TIPS}
        get_tips("maintenance")
        mock_db.tips.find_one.assert_called_once_with({"goal": "maintenance"}, {"_id": 0})


# ═══════════════════════════════════════════════════════════════
#  ROUTE TESTS
# ═══════════════════════════════════════════════════════════════

class TestRoutes:

    def test_home_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_home_contains_form(self, client):
        response = client.get("/")
        assert b"dietForm" in response.data or b"form" in response.data.lower()

    @patch("app.get_meal_plan", return_value=SAMPLE_MEAL)
    @patch("app.get_tips",      return_value=SAMPLE_TIPS)
    @patch("app.db")
    def test_generate_valid_returns_200(self, mock_db, mock_tips, mock_meal, client):
        mock_db.plans.insert_one.return_value = MagicMock()
        response = client.post("/generate", data={
            "name":      "Test User",
            "age":       "25",
            "gender":    "male",
            "height":    "175",
            "weight":    "70",
            "activity":  "moderate",
            "goal":      "weight_loss",
            "diet_pref": "vegetarian"
        })
        assert response.status_code == 200

    def test_generate_empty_name_shows_error(self, client):
        response = client.post("/generate", data={
            "name": "", "age": "25", "gender": "male",
            "height": "175", "weight": "70",
            "activity": "moderate", "goal": "weight_loss",
            "diet_pref": "vegetarian"
        })
        assert response.status_code == 200
        assert b"required" in response.data.lower() or b"error" in response.data.lower()

    def test_generate_invalid_age(self, client):
        response = client.post("/generate", data={
            "name": "Test", "age": "999", "gender": "male",
            "height": "175", "weight": "70",
            "activity": "moderate", "goal": "weight_loss",
            "diet_pref": "vegetarian"
        })
        assert response.status_code == 200

    def test_generate_invalid_height(self, client):
        response = client.post("/generate", data={
            "name": "Test", "age": "25", "gender": "male",
            "height": "10", "weight": "70",
            "activity": "moderate", "goal": "weight_loss",
            "diet_pref": "vegetarian"
        })
        assert response.status_code == 200

    def test_generate_invalid_weight(self, client):
        response = client.post("/generate", data={
            "name": "Test", "age": "25", "gender": "male",
            "height": "175", "weight": "5",
            "activity": "moderate", "goal": "weight_loss",
            "diet_pref": "vegetarian"
        })
        assert response.status_code == 200

    def test_generate_missing_goal(self, client):
        response = client.post("/generate", data={
            "name": "Test", "age": "25", "gender": "male",
            "height": "175", "weight": "70",
            "activity": "moderate", "goal": "",
            "diet_pref": "vegetarian"
        })
        assert response.status_code == 200

    def test_ping_route_exists(self, client):
        with patch("app.db") as mock_db:
            mock_db.client.admin.command.return_value = True
            response = client.get("/api/ping")
            assert response.status_code == 200
