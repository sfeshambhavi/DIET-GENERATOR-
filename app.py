from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import certifi
import ssl
import os

load_dotenv()

app = Flask(__name__)
from prometheus_flask_exporter import PrometheusMetrics
metrics = PrometheusMetrics(app)

# ── MongoDB connection ────────────────────────────────────────────────────────
MONGO_URI = os.getenv("MONGO_URI")

def get_db():
    """Try multiple connection strategies until one works."""
    strategies = [
        # Strategy 1: certifi CA bundle
        {"tlsCAFile": certifi.where()},
        # Strategy 2: no TLS verification (fallback)
        {"tls": True, "tlsAllowInvalidCertificates": True},
        # Strategy 3: system certs
        {"ssl": True, "ssl_cert_reqs": ssl.CERT_NONE},
        # Strategy 4: plain connection
        {},
    ]

    for kwargs in strategies:
        try:
            c = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, **kwargs)
            c.admin.command('ping')
            print(f"[MongoDB] Connected with strategy: {kwargs}")
            return c["nutrigen"]
        except Exception as e:
            print(f"[MongoDB] Strategy {kwargs} failed: {e}")
            continue

    raise RuntimeError("All MongoDB connection strategies failed.")

db = get_db()   # ← CRITICAL: was missing before


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/api/ping')
def ping():
    try:
        db.client.admin.command('ping')
        return jsonify({"status": "MongoDB connected ✅"})
    except Exception as e:
        return jsonify({"status": "Failed ❌", "error": str(e)}), 500


def calculate_bmi(weight, height_cm):
    height_m = height_cm / 100
    return round(weight / (height_m ** 2), 1)


def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight", "underweight"
    elif bmi < 25:
        return "Normal weight", "normal"
    elif bmi < 30:
        return "Overweight", "overweight"
    else:
        return "Obese", "obese"


def calculate_calories(weight, height_cm, age, gender, activity, goal):
    if gender == "male":
        bmr = (10 * weight) + (6.25 * height_cm) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height_cm) - (5 * age) - 161

    multipliers = {
        "sedentary":    1.2,
        "light":        1.375,
        "moderate":     1.55,
        "very_active":  1.725,
        "extra_active": 1.9
    }
    tdee = bmr * multipliers.get(activity, 1.2)

    if goal == "weight_loss":
        tdee -= 500
    elif goal == "weight_gain":
        tdee += 500

    return round(tdee)


def get_diet_type(bmi_category, goal):
    if goal == "weight_loss":
        return "Low Calorie Diet"
    elif goal == "weight_gain":
        return "High Protein Diet"
    else:
        if bmi_category == "Underweight":
            return "High Protein Diet"
        elif bmi_category in ["Overweight", "Obese"]:
            return "Low Calorie Diet"
        else:
            return "Balanced Diet"


def get_meal_plan(diet_pref, diet_type):
    doc = db.meal_plans.find_one(
        {"diet_pref": diet_pref, "diet_type": diet_type},
        {"_id": 0}
    )
    if not doc:
        raise ValueError(f"No meal plan found for diet_pref='{diet_pref}', diet_type='{diet_type}'")
    return {
        "breakfast": doc["breakfast"],
        "lunch":     doc["lunch"],
        "snack":     doc["snack"],
        "dinner":    doc["dinner"]
    }


def get_tips(goal):
    doc = db.tips.find_one({"goal": goal}, {"_id": 0})
    if not doc:
        return []
    return doc.get("tips", [])


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    errors = {}

    name      = request.form.get('name', '').strip()
    age       = request.form.get('age', '')
    gender    = request.form.get('gender', '')
    height    = request.form.get('height', '')
    weight    = request.form.get('weight', '')
    activity  = request.form.get('activity', '')
    goal      = request.form.get('goal', '')
    diet_pref = request.form.get('diet_pref', '')

    if not name:
        errors['name'] = 'Name is required.'
    try:
        age = int(age)
        if age <= 0 or age > 120:
            errors['age'] = 'Enter a valid age between 1 and 120.'
    except (ValueError, TypeError):
        errors['age'] = 'Age must be a number.'

    if not gender:
        errors['gender'] = 'Please select a gender.'

    try:
        height = float(height)
        if height < 50 or height > 300:
            errors['height'] = 'Enter a valid height (50-300 cm).'
    except (ValueError, TypeError):
        errors['height'] = 'Height must be a number.'

    try:
        weight = float(weight)
        if weight < 10 or weight > 500:
            errors['weight'] = 'Enter a valid weight (10-500 kg).'
    except (ValueError, TypeError):
        errors['weight'] = 'Weight must be a number.'

    if not activity:
        errors['activity'] = 'Please select an activity level.'
    if not goal:
        errors['goal'] = 'Please select a fitness goal.'
    if not diet_pref:
        errors['diet_pref'] = 'Please select a diet preference.'

    if errors:
        return render_template('index.html', errors=errors)

    bmi = calculate_bmi(weight, height)
    bmi_category, bmi_class = get_bmi_category(bmi)
    calories  = calculate_calories(weight, height, age, gender, activity, goal)
    diet_type = get_diet_type(bmi_category, goal)

    meal_plan = get_meal_plan(diet_pref, diet_type)
    tips      = get_tips(goal)

    goal_labels = {
        "weight_loss": "Weight Loss",
        "weight_gain": "Weight Gain",
        "maintenance": "Maintenance"
    }
    pref_labels = {
        "vegetarian":     "Vegetarian",
        "non_vegetarian": "Non-Vegetarian"
    }

    result = {
        "name":            name,
        "bmi":             bmi,
        "bmi_category":    bmi_category,
        "bmi_class":       bmi_class,
        "calories":        calories,
        "diet_type":       diet_type,
        "diet_pref_label": pref_labels.get(diet_pref, diet_pref),
        "goal_label":      goal_labels.get(goal, goal),
        "meal_plan":       meal_plan,
        "tips":            tips
    }

    try:
        db.plans.insert_one({
            "createdAt": datetime.utcnow(),
            "userProfile": {
                "name":     name,
                "age":      age,
                "gender":   gender,
                "height":   height,
                "weight":   weight,
                "activity": activity,
                "goal":     goal,
                "dietPref": diet_pref
            },
            "generatedPlan": {
                "bmi":         bmi,
                "bmiCategory": bmi_category,
                "calories":    calories,
                "dietType":    diet_type,
                "mealPlan":    meal_plan,
                "tips":        tips
            }
        })
    except Exception as e:
        print(f"[MongoDB] Failed to save plan: {e}")

    return render_template('result.html', result=result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)