from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ============================================
#  MODULE 3 & 4: BMI + Calorie Calculations
# ============================================

def calculate_bmi(weight, height_cm):
    height_m = height_cm / 100
    bmi = weight / (height_m ** 2)
    return round(bmi, 1)

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

    activity_multipliers = {
        "sedentary":    1.2,
        "light":        1.375,
        "moderate":     1.55,
        "very_active":  1.725,
        "extra_active": 1.9
    }
    tdee = bmr * activity_multipliers.get(activity, 1.2)

    if goal == "weight_loss":
        tdee -= 500
    elif goal == "weight_gain":
        tdee += 500

    return round(tdee)

# ============================================
#  MODULE 5: Diet Type Recommendation
# ============================================

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

# ============================================
#  MODULE 6: Meal Plan Generation
# ============================================

MEAL_PLANS = {
    "vegetarian": {
        "Low Calorie Diet": {
            "breakfast": {
                "foods": ["Oats porridge with skim milk", "1 banana", "Green tea (no sugar)"],
                "calories": 300
            },
            "lunch": {
                "foods": ["1 cup brown rice", "Dal (lentil soup)", "Mixed vegetable sabzi", "1 small bowl curd"],
                "calories": 450
            },
            "snack": {
                "foods": ["1 apple", "10 almonds", "1 glass buttermilk"],
                "calories": 200
            },
            "dinner": {
                "foods": ["2 whole wheat rotis", "Palak paneer (small portion)", "Cucumber & tomato salad"],
                "calories": 400
            }
        },
        "High Protein Diet": {
            "breakfast": {
                "foods": ["Moong dal cheela (2 pieces)", "Low-fat paneer bhurji", "1 glass skimmed milk"],
                "calories": 450
            },
            "lunch": {
                "foods": ["1 cup quinoa", "Rajma curry", "Sautéed vegetables", "1 bowl curd"],
                "calories": 600
            },
            "snack": {
                "foods": ["Roasted chana (1 cup)", "1 glass protein shake", "1 banana"],
                "calories": 350
            },
            "dinner": {
                "foods": ["3 whole wheat rotis", "Paneer tikka (grilled)", "Dal makhani", "Green salad"],
                "calories": 550
            }
        },
        "Balanced Diet": {
            "breakfast": {
                "foods": ["2 whole wheat toast", "Peanut butter", "1 boiled egg (or paneer slice)", "1 glass milk"],
                "calories": 400
            },
            "lunch": {
                "foods": ["1 cup rice", "Mixed dal", "1 sabzi", "1 bowl curd", "Salad"],
                "calories": 550
            },
            "snack": {
                "foods": ["Fruit chaat (seasonal fruits)", "1 cup green tea"],
                "calories": 200
            },
            "dinner": {
                "foods": ["2 rotis", "Vegetable curry", "Small bowl dal", "Salad"],
                "calories": 450
            }
        }
    },
    "non_vegetarian": {
        "Low Calorie Diet": {
            "breakfast": {
                "foods": ["2 boiled eggs", "1 slice whole wheat toast", "Black coffee or green tea"],
                "calories": 280
            },
            "lunch": {
                "foods": ["Grilled chicken breast (150g)", "1 cup brown rice", "Steamed vegetables", "Lemon water"],
                "calories": 480
            },
            "snack": {
                "foods": ["1 boiled egg", "1 apple", "10 almonds"],
                "calories": 200
            },
            "dinner": {
                "foods": ["Baked fish (150g)", "2 whole wheat rotis", "Cucumber & tomato salad"],
                "calories": 420
            }
        },
        "High Protein Diet": {
            "breakfast": {
                "foods": ["3 scrambled eggs", "2 whole wheat toast", "1 glass milk", "1 banana"],
                "calories": 520
            },
            "lunch": {
                "foods": ["Chicken curry (200g)", "1.5 cups brown rice", "Dal", "Salad"],
                "calories": 700
            },
            "snack": {
                "foods": ["Boiled eggs (2)", "Protein shake", "Handful of nuts"],
                "calories": 400
            },
            "dinner": {
                "foods": ["Grilled fish or chicken (200g)", "3 rotis", "Vegetable stir fry", "Green salad"],
                "calories": 600
            }
        },
        "Balanced Diet": {
            "breakfast": {
                "foods": ["2 eggs (any style)", "1 paratha", "1 glass milk", "Seasonal fruit"],
                "calories": 450
            },
            "lunch": {
                "foods": ["Chicken or fish curry (150g)", "1 cup rice", "1 roti", "Salad", "Curd"],
                "calories": 600
            },
            "snack": {
                "foods": ["1 boiled egg", "1 banana", "Green tea"],
                "calories": 220
            },
            "dinner": {
                "foods": ["2 rotis", "Egg curry or grilled chicken", "Sabzi", "Salad"],
                "calories": 500
            }
        }
    }
}

# ============================================
#  MODULE: Health Tips
# ============================================

TIPS = {
    "weight_loss": [
        "Drink at least 8–10 glasses of water daily to boost metabolism.",
        "Avoid sugary drinks, processed foods, and late-night snacking.",
        "Include 30–45 minutes of cardio at least 5 days a week.",
        "Eat slowly and mindfully — it takes 20 minutes to feel full.",
        "Sleep 7–8 hours daily; poor sleep increases hunger hormones.",
        "Replace refined carbs with whole grains like brown rice and oats."
    ],
    "weight_gain": [
        "Eat every 3–4 hours to maintain a calorie surplus throughout the day.",
        "Focus on calorie-dense foods like nuts, dairy, eggs, and legumes.",
        "Incorporate strength training 4–5 days a week to build muscle.",
        "Don't skip breakfast — it sets your calorie intake for the day.",
        "Add healthy fats like ghee, avocado, and peanut butter to meals.",
        "Track your meals to ensure you're consistently eating enough."
    ],
    "maintenance": [
        "Keep your meal timings consistent every day for better metabolism.",
        "Stay active with at least 30 minutes of movement daily.",
        "Include a variety of fruits and vegetables for micronutrients.",
        "Limit alcohol, junk food, and excess sodium in your diet.",
        "Do a monthly health check to track your weight and fitness.",
        "Stay hydrated — thirst is often mistaken for hunger."
    ]
}

# ============================================
#  ROUTES
# ============================================

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
    except ValueError:
        errors['age'] = 'Age must be a number.'

    if not gender:
        errors['gender'] = 'Please select a gender.'

    try:
        height = float(height)
        if height < 50 or height > 300:
            errors['height'] = 'Enter a valid height (50–300 cm).'
    except ValueError:
        errors['height'] = 'Height must be a number.'

    try:
        weight = float(weight)
        if weight < 10 or weight > 500:
            errors['weight'] = 'Enter a valid weight (10–500 kg).'
    except ValueError:
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
    calories = calculate_calories(weight, height, age, gender, activity, goal)
    diet_type = get_diet_type(bmi_category, goal)
    meal_plan = MEAL_PLANS[diet_pref][diet_type]

    goal_labels = {
        "weight_loss": "Weight Loss",
        "weight_gain": "Weight Gain",
        "maintenance": "Maintenance"
    }
    pref_labels = {
        "vegetarian":     "🥦 Vegetarian",
        "non_vegetarian": "🍗 Non-Vegetarian"
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
        "tips":            TIPS.get(goal, [])
    }

    return render_template('result.html', result=result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)