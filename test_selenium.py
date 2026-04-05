import pytest
import time
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager


BASE_URL = os.environ.get("APP_URL", "http://localhost:5001")


# ─────────────────────────────────────────
# DRIVER FIXTURE
# ─────────────────────────────────────────

@pytest.fixture(scope="module")
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")               # ← REQUIRED in CI
    options.add_argument("--disable-dev-shm-usage")    # ← REQUIRED in CI
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,900")

    service = Service(ChromeDriverManager().install())

    drv = webdriver.Chrome(service=service, options=options)
    drv.implicitly_wait(10)

    yield drv
    drv.quit()


# ─────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────

def fill_form(driver, data):
    driver.get(BASE_URL)
    wait = WebDriverWait(driver, 10)

    for field_id, value in data.get("inputs", {}).items():
        el = wait.until(EC.presence_of_element_located((By.ID, field_id)))
        el.clear()
        el.send_keys(str(value))

    for field_id, value in data.get("selects", {}).items():
        Select(driver.find_element(By.ID, field_id)).select_by_value(value)

    for name, value in data.get("radios", {}).items():
        radio = driver.find_element(By.CSS_SELECTOR, f"input[name='{name}'][value='{value}']")
        driver.execute_script("arguments[0].click();", radio)


def click_submit(driver):
    wait = WebDriverWait(driver, 10)
    btn = wait.until(EC.element_to_be_clickable((By.ID, "submitBtn")))
    driver.execute_script("arguments[0].scrollIntoView(true);", btn)
    driver.execute_script("arguments[0].click();", btn)


VALID_FORM = {
    "inputs":  {"name": "Rahul Test", "age": "28", "height": "175", "weight": "72"},
    "selects": {"gender": "male"},
    "radios":  {"activity": "moderate", "goal": "weight_loss", "diet_pref": "vegetarian"},
}


# ─────────────────────────────────────────
# HOME PAGE TESTS
# ─────────────────────────────────────────

class TestHomePage:

    def test_page_title(self, driver):
        driver.get(BASE_URL)
        assert "NutriGen" in driver.title

    def test_form_present(self, driver):
        driver.get(BASE_URL)
        form = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dietForm"))
        )
        assert form

    def test_logo_visible(self, driver):
        driver.get(BASE_URL)
        logo = driver.find_element(By.CSS_SELECTOR, ".logo-text")
        assert "NutriGen" in logo.text

    def test_all_sections_visible(self, driver):
        driver.get(BASE_URL)
        labels = driver.find_elements(By.CSS_SELECTOR, ".section-number")
        assert len(labels) == 3

    def test_submit_button_present(self, driver):
        driver.get(BASE_URL)
        btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "submitBtn"))
        )
        assert btn is not None


# ─────────────────────────────────────────
# BMI PREVIEW TESTS
# ─────────────────────────────────────────

class TestBMIPreview:

    def test_bmi_updates_on_input(self, driver):
        driver.get(BASE_URL)
        driver.find_element(By.ID, "height").send_keys("175")
        driver.find_element(By.ID, "weight").send_keys("70")
        WebDriverWait(driver, 5).until(
            lambda d: d.find_element(By.ID, "bmiValue").text.strip() != ""
        )
        bmi_val = driver.find_element(By.ID, "bmiValue").text
        assert float(bmi_val) > 0

    def test_bmi_category_shows(self, driver):
        driver.get(BASE_URL)
        driver.find_element(By.ID, "height").send_keys("175")
        driver.find_element(By.ID, "weight").send_keys("70")
        WebDriverWait(driver, 5).until(
            lambda d: d.find_element(By.ID, "bmiCategory").text.strip() != ""
        )
        cat = driver.find_element(By.ID, "bmiCategory").text
        assert cat in ["Underweight", "Normal weight", "Overweight", "Obese"]


# ─────────────────────────────────────────
# VALIDATION TESTS
# ─────────────────────────────────────────

class TestFormValidation:

    def test_empty_form_shows_errors(self, driver):
        driver.get(BASE_URL)
        click_submit(driver)
        time.sleep(0.5)
        errors = driver.find_elements(By.CSS_SELECTOR, ".error-msg")
        visible = [e for e in errors if e.text.strip() != ""]
        assert len(visible) > 0


# ─────────────────────────────────────────
# FORM SUBMISSION TESTS
# ─────────────────────────────────────────

class TestFormSubmission:

    def test_valid_submission_reaches_result_page(self, driver):
        fill_form(driver, VALID_FORM)
        click_submit(driver)
        WebDriverWait(driver, 10).until(EC.url_contains("generate"))
        assert "meal" in driver.page_source.lower()

    def test_result_shows_user_name(self, driver):
        fill_form(driver, VALID_FORM)
        click_submit(driver)
        name_el = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".result-name"))
        )
        assert "Rahul Test" in name_el.text

    def test_result_shows_bmi_card(self, driver):
        fill_form(driver, VALID_FORM)
        click_submit(driver)
        card = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".bmi-card"))
        )
        assert card

    def test_result_shows_meal_plan(self, driver):
        fill_form(driver, VALID_FORM)
        click_submit(driver)
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".meal-card"))
        )
        meals = driver.find_elements(By.CSS_SELECTOR, ".meal-card")
        assert len(meals) >= 1

    def test_result_shows_tips(self, driver):
        fill_form(driver, VALID_FORM)
        click_submit(driver)
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".tip-card"))
        )
        tips = driver.find_elements(By.CSS_SELECTOR, ".tip-card")
        assert len(tips) >= 1