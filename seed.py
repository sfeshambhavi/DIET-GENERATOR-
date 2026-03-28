from pymongo import MongoClient
from dotenv import load_dotenv
import certifi
import ssl
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

def connect():
    strategies = [
        {"tlsCAFile": certifi.where()},
        {"tls": True, "tlsAllowInvalidCertificates": True},
        {"ssl": True, "ssl_cert_reqs": ssl.CERT_NONE},
        {},
    ]
    for kwargs in strategies:
        try:
            c = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, **kwargs)
            c.admin.command('ping')
            print(f"Connected with: {kwargs if kwargs else 'default'}")
            return c
        except Exception as e:
            print(f"Failed {kwargs}: {e}")
    raise RuntimeError("Could not connect to MongoDB.")

client = connect()
db = client["nutrigen"]

db.meal_plans.drop()
db.tips.drop()
print("Cleared collections.")

meal_plans = [
    {
        "diet_pref": "vegetarian", "diet_type": "Low Calorie Diet",
        "breakfast": {"foods": ["Oats porridge with skim milk", "1 banana", "Green tea (no sugar)"], "calories": 300},
        "lunch":     {"foods": ["1 cup brown rice", "Dal (lentil soup)", "Mixed vegetable sabzi", "1 small bowl curd"], "calories": 450},
        "snack":     {"foods": ["1 apple", "10 almonds", "1 glass buttermilk"], "calories": 200},
        "dinner":    {"foods": ["2 whole wheat rotis", "Palak paneer (small portion)", "Cucumber & tomato salad"], "calories": 400}
    },
    {
        "diet_pref": "vegetarian", "diet_type": "High Protein Diet",
        "breakfast": {"foods": ["Moong dal cheela (2 pieces)", "Low-fat paneer bhurji", "1 glass skimmed milk"], "calories": 450},
        "lunch":     {"foods": ["1 cup quinoa", "Rajma curry", "Sauteed vegetables", "1 bowl curd"], "calories": 600},
        "snack":     {"foods": ["Roasted chana (1 cup)", "1 glass protein shake", "1 banana"], "calories": 350},
        "dinner":    {"foods": ["3 whole wheat rotis", "Paneer tikka (grilled)", "Dal makhani", "Green salad"], "calories": 550}
    },
    {
        "diet_pref": "vegetarian", "diet_type": "Balanced Diet",
        "breakfast": {"foods": ["2 whole wheat toast", "Peanut butter", "1 boiled egg (or paneer slice)", "1 glass milk"], "calories": 400},
        "lunch":     {"foods": ["1 cup rice", "Mixed dal", "1 sabzi", "1 bowl curd", "Salad"], "calories": 550},
        "snack":     {"foods": ["Fruit chaat (seasonal fruits)", "1 cup green tea"], "calories": 200},
        "dinner":    {"foods": ["2 rotis", "Vegetable curry", "Small bowl dal", "Salad"], "calories": 450}
    },
    {
        "diet_pref": "non_vegetarian", "diet_type": "Low Calorie Diet",
        "breakfast": {"foods": ["2 boiled eggs", "1 slice whole wheat toast", "Black coffee or green tea"], "calories": 280},
        "lunch":     {"foods": ["Grilled chicken breast (150g)", "1 cup brown rice", "Steamed vegetables", "Lemon water"], "calories": 480},
        "snack":     {"foods": ["1 boiled egg", "1 apple", "10 almonds"], "calories": 200},
        "dinner":    {"foods": ["Baked fish (150g)", "2 whole wheat rotis", "Cucumber & tomato salad"], "calories": 420}
    },
    {
        "diet_pref": "non_vegetarian", "diet_type": "High Protein Diet",
        "breakfast": {"foods": ["3 scrambled eggs", "2 whole wheat toast", "1 glass milk", "1 banana"], "calories": 520},
        "lunch":     {"foods": ["Chicken curry (200g)", "1.5 cups brown rice", "Dal", "Salad"], "calories": 700},
        "snack":     {"foods": ["Boiled eggs (2)", "Protein shake", "Handful of nuts"], "calories": 400},
        "dinner":    {"foods": ["Grilled fish or chicken (200g)", "3 rotis", "Vegetable stir fry", "Green salad"], "calories": 600}
    },
    {
        "diet_pref": "non_vegetarian", "diet_type": "Balanced Diet",
        "breakfast": {"foods": ["2 eggs (any style)", "1 paratha", "1 glass milk", "Seasonal fruit"], "calories": 450},
        "lunch":     {"foods": ["Chicken or fish curry (150g)", "1 cup rice", "1 roti", "Salad", "Curd"], "calories": 600},
        "snack":     {"foods": ["1 boiled egg", "1 banana", "Green tea"], "calories": 220},
        "dinner":    {"foods": ["2 rotis", "Egg curry or grilled chicken", "Sabzi", "Salad"], "calories": 500}
    }
]

tips = [
    {
        "goal": "weight_loss",
        "tips": [
            "Drink at least 8-10 glasses of water daily to boost metabolism.",
            "Avoid sugary drinks, processed foods, and late-night snacking.",
            "Include 30-45 minutes of cardio at least 5 days a week.",
            "Eat slowly and mindfully - it takes 20 minutes to feel full.",
            "Sleep 7-8 hours daily; poor sleep increases hunger hormones.",
            "Replace refined carbs with whole grains like brown rice and oats."
        ]
    },
    {
        "goal": "weight_gain",
        "tips": [
            "Eat every 3-4 hours to maintain a calorie surplus throughout the day.",
            "Focus on calorie-dense foods like nuts, dairy, eggs, and legumes.",
            "Incorporate strength training 4-5 days a week to build muscle.",
            "Do not skip breakfast - it sets your calorie intake for the day.",
            "Add healthy fats like ghee, avocado, and peanut butter to meals.",
            "Track your meals to ensure you are consistently eating enough."
        ]
    },
    {
        "goal": "maintenance",
        "tips": [
            "Keep your meal timings consistent every day for better metabolism.",
            "Stay active with at least 30 minutes of movement daily.",
            "Include a variety of fruits and vegetables for micronutrients.",
            "Limit alcohol, junk food, and excess sodium in your diet.",
            "Do a monthly health check to track your weight and fitness.",
            "Stay hydrated - thirst is often mistaken for hunger."
        ]
    }
]

db.meal_plans.insert_many(meal_plans)
db.tips.insert_many(tips)
db.meal_plans.create_index([("diet_pref", 1), ("diet_type", 1)])
db.tips.create_index([("goal", 1)])

print(f"Inserted {len(meal_plans)} meal plans.")
print(f"Inserted {len(tips)} tip sets.")
print("MongoDB seeded successfully!")
