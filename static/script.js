document.addEventListener('DOMContentLoaded', () => {

    // ── Live BMI Preview ──────────────────────────────────────────
    const heightInput = document.getElementById('height');
    const weightInput = document.getElementById('weight');
    const bmiValue    = document.getElementById('bmiValue');
    const bmiCategory = document.getElementById('bmiCategory');
    const bmiMarker   = document.getElementById('bmiBarMarker');
  
    function calcBMI() {
      if (!heightInput || !weightInput) return;
      const h = parseFloat(heightInput.value);
      const w = parseFloat(weightInput.value);
      if (!h || !w || h <= 0 || w <= 0) {
        if (bmiValue)    bmiValue.textContent    = '—';
        if (bmiCategory) bmiCategory.textContent = '';
        if (bmiMarker)   bmiMarker.style.left    = '0%';
        return;
      }
      const heightM = h / 100;
      const bmi = (w / (heightM * heightM)).toFixed(1);
      if (bmiValue) bmiValue.textContent = bmi;
  
      let category = '';
      let markerPct = 0;
      const b = parseFloat(bmi);
  
      if (b < 18.5) {
        category = 'Underweight';
        markerPct = Math.min((b / 18.5) * 20, 20);
        if (bmiCategory) { bmiCategory.style.background = '#dbeafe'; bmiCategory.style.color = '#1e40af'; }
      } else if (b < 25) {
        category = 'Normal weight';
        markerPct = 20 + ((b - 18.5) / 6.5) * 30;
        if (bmiCategory) { bmiCategory.style.background = '#d1fae5'; bmiCategory.style.color = '#065f46'; }
      } else if (b < 30) {
        category = 'Overweight';
        markerPct = 50 + ((b - 25) / 5) * 25;
        if (bmiCategory) { bmiCategory.style.background = '#fef3c7'; bmiCategory.style.color = '#92400e'; }
      } else {
        category = 'Obese';
        markerPct = Math.min(75 + ((b - 30) / 10) * 25, 97);
        if (bmiCategory) { bmiCategory.style.background = '#fee2e2'; bmiCategory.style.color = '#991b1b'; }
      }
  
      if (bmiCategory) bmiCategory.textContent = category;
      if (bmiMarker)   bmiMarker.style.left    = markerPct + '%';
    }
  
    if (heightInput) heightInput.addEventListener('input', calcBMI);
    if (weightInput) weightInput.addEventListener('input', calcBMI);
  
    // ── Form Validation ───────────────────────────────────────────
    const form = document.getElementById('dietForm');
    if (!form) return;
  
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      if (validateForm()) form.submit();
    });
  
    function validateForm() {
      let isValid = true;
  
      function setError(fieldId, message) {
        const errEl = document.getElementById(fieldId + '-error');
        const input = document.getElementById(fieldId);
        if (errEl) errEl.textContent = message;
        if (input && input.tagName === 'INPUT') {
          if (message) input.classList.add('invalid');
          else         input.classList.remove('invalid');
        }
      }
  
      // Name
      const name = document.getElementById('name');
      if (!name.value.trim()) { setError('name', 'Please enter your name.'); isValid = false; }
      else                    { setError('name', ''); }
  
      // Age
      const age = document.getElementById('age');
      const ageVal = parseInt(age.value);
      if (!age.value || isNaN(ageVal) || ageVal <= 0 || ageVal > 120) { setError('age', 'Enter a valid age (1–120).'); isValid = false; }
      else { setError('age', ''); }
  
      // Gender
      const gender = document.getElementById('gender');
      if (!gender.value) { setError('gender', 'Please select your gender.'); isValid = false; }
      else               { setError('gender', ''); }
  
      // Height
      const height = document.getElementById('height');
      const hVal = parseFloat(height.value);
      if (!height.value || isNaN(hVal) || hVal < 50 || hVal > 300) { setError('height', 'Enter a valid height (50–300 cm).'); isValid = false; }
      else { setError('height', ''); }
  
      // Weight
      const weight = document.getElementById('weight');
      const wVal = parseFloat(weight.value);
      if (!weight.value || isNaN(wVal) || wVal < 10 || wVal > 500) { setError('weight', 'Enter a valid weight (10–500 kg).'); isValid = false; }
      else { setError('weight', ''); }
  
      // Activity
      const activity = document.querySelector('input[name="activity"]:checked');
      const activityErr = document.getElementById('activity-error');
      if (!activity) { if (activityErr) activityErr.textContent = 'Please select your activity level.'; isValid = false; }
      else           { if (activityErr) activityErr.textContent = ''; }
  
      // Goal
      const goal = document.querySelector('input[name="goal"]:checked');
      const goalErr = document.getElementById('goal-error');
      if (!goal) { if (goalErr) goalErr.textContent = 'Please select your fitness goal.'; isValid = false; }
      else       { if (goalErr) goalErr.textContent = ''; }
  
      // Diet Preference
      const pref = document.querySelector('input[name="diet_pref"]:checked');
      const prefErr = document.getElementById('diet_pref-error');
      if (!pref) { if (prefErr) prefErr.textContent = 'Please select vegetarian or non-vegetarian.'; isValid = false; }
      else       { if (prefErr) prefErr.textContent = ''; }
  
      if (!isValid) {
        const firstError = form.querySelector('.error-msg:not(:empty)');
        if (firstError) firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
      return isValid;
    }
  
    // Real-time blur validation
    document.getElementById('name')?.addEventListener('blur', function() {
      const e = document.getElementById('name-error');
      if (!this.value.trim()) { e.textContent = 'Please enter your name.'; this.classList.add('invalid'); }
      else { e.textContent = ''; this.classList.remove('invalid'); }
    });
  
    document.getElementById('age')?.addEventListener('blur', function() {
      const e = document.getElementById('age-error');
      const v = parseInt(this.value);
      if (!this.value || isNaN(v) || v <= 0 || v > 120) { e.textContent = 'Enter a valid age (1–120).'; this.classList.add('invalid'); }
      else { e.textContent = ''; this.classList.remove('invalid'); }
    });
  
    document.getElementById('height')?.addEventListener('blur', function() {
      const e = document.getElementById('height-error');
      const v = parseFloat(this.value);
      if (!this.value || isNaN(v) || v < 50 || v > 300) { e.textContent = 'Enter a valid height (50–300 cm).'; this.classList.add('invalid'); }
      else { e.textContent = ''; this.classList.remove('invalid'); }
    });
  
    document.getElementById('weight')?.addEventListener('blur', function() {
      const e = document.getElementById('weight-error');
      const v = parseFloat(this.value);
      if (!this.value || isNaN(v) || v < 10 || v > 500) { e.textContent = 'Enter a valid weight (10–500 kg).'; this.classList.add('invalid'); }
      else { e.textContent = ''; this.classList.remove('invalid'); }
    });
  
  });