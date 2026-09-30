from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn

app = FastAPI(title="BMI Calculator", description="Clean and responsive BMI Calculator API & UI")

class BMIRequest(BaseModel):
    weight: float = Field(..., gt=0, description="Weight in kg or lbs")
    height: float = Field(..., gt=0, description="Height in cm or inches")
    unit: str = Field("metric", description="'metric' (kg, cm) or 'imperial' (lbs, inches)")

class BMIResponse(BaseModel):
    bmi: float
    category: str
    advice: str

def calculate_bmi_value(weight: float, height: float, unit: str) -> float:
    if unit.lower() == "metric":
        # weight in kg, height in cm
        height_m = height / 100.0
        if height_m == 0:
            raise HTTPException(status_code=400, detail="Height cannot be zero")
        return weight / (height_m ** 2)
    elif unit.lower() == "imperial":
        # weight in lbs, height in inches
        if height == 0:
            raise HTTPException(status_code=400, detail="Height cannot be zero")
        return (weight / (height ** 2)) * 703
    else:
        raise HTTPException(status_code=400, detail="Invalid unit. Use 'metric' or 'imperial'.")

def get_bmi_category(bmi: float) -> tuple[str, str]:
    if bmi < 18.5:
        return "Underweight", "Consider consulting a healthcare provider about healthy ways to gain weight."
    elif 18.5 <= bmi < 25:
        return "Normal weight", "Great job! Maintain a balanced diet and regular physical activity."
    elif 25 <= bmi < 30:
        return "Overweight", "Consider incorporating more physical activity and balanced nutrition into your routine."
    else:
        return "Obese", "Consult a healthcare provider for personalized guidance on achieving a healthier weight."

@app.post("/api/calculate", response_model=BMIResponse)
def api_calculate_bmi(data: BMIRequest):
    bmi = calculate_bmi_value(data.weight, data.height, data.unit)
    bmi_rounded = round(bmi, 1)
    category, advice = get_bmi_category(bmi_rounded)
    return BMIResponse(bmi=bmi_rounded, category=category, advice=advice)

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BMI Calculator</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 text-slate-800 min-h-screen flex flex-col justify-between">
    <div class="max-w-md w-full mx-auto mt-12 p-6 bg-white rounded-xl shadow-md border border-slate-100">
        <h1 class="text-2xl font-bold text-center text-indigo-600 mb-2">BMI Calculator</h1>
        <p class="text-sm text-center text-slate-500 mb-6">Check your Body Mass Index quickly and easily.</p>
        
        <div class="flex mb-6 bg-slate-100 p-1 rounded-lg">
            <button onclick="setUnit('metric')" id="btn-metric" class="flex-1 py-2 text-sm font-medium rounded-md bg-white text-indigo-600 shadow-sm transition-all">Metric (kg/cm)</button>
            <button onclick="setUnit('imperial')" id="btn-imperial" class="flex-1 py-2 text-sm font-medium rounded-md text-slate-600 transition-all">Imperial (lbs/in)</button>
        </div>

        <form id="bmi-form" onsubmit="calculateBMI(event)" class="space-y-4">
            <div>
                <label id="label-weight" class="block text-sm font-medium text-slate-700 mb-1">Weight (kg)</label>
                <input type="number" step="any" id="weight" required class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500">
            </div>
            <div>
                <label id="label-height" class="block text-sm font-medium text-slate-700 mb-1">Height (cm)</label>
                <input type="number" step="any" id="height" required class="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500">
            </div>
            <button type="submit" class="w-full bg-indigo-600 text-white font-medium py-2.5 rounded-lg hover:bg-indigo-700 transition-colors shadow-md shadow-indigo-100">Calculate BMI</button>
        </form>

        <div id="result" class="mt-6 hidden p-4 rounded-lg bg-indigo-50 border border-indigo-100">
            <h2 class="text-lg font-semibold text-indigo-900 mb-1">Your Result</h2>
            <p class="text-3xl font-extrabold text-indigo-600" id="bmi-value">--</p>
            <p class="font-medium text-slate-700 mt-1" id="bmi-category">--</p>
            <p class="text-xs text-slate-500 mt-2" id="bmi-advice">--</p>
        </div>
    </div>

    <footer class="text-center py-6 text-xs text-slate-400">
        Powered by FastAPI & Tailwind CSS
    </footer>

    <script>
        let currentUnit = 'metric';

        function setUnit(unit) {
            currentUnit = unit;
            const btnMetric = document.getElementById('btn-metric');
            const btnImperial = document.getElementById('btn-imperial');
            const lblWeight = document.getElementById('label-weight');
            const lblHeight = document.getElementById('label-height');

            if (unit === 'metric') {
                btnMetric.className = 'flex-1 py-2 text-sm font-medium rounded-md bg-white text-indigo-600 shadow-sm transition-all';
                btnImperial.className = 'flex-1 py-2 text-sm font-medium rounded-md text-slate-600 transition-all';
                lblWeight.innerText = 'Weight (kg)';
                lblHeight.innerText = 'Height (cm)';
            } else {
                btnImperial.className = 'flex-1 py-2 text-sm font-medium rounded-md bg-white text-indigo-600 shadow-sm transition-all';
                btnMetric.className = 'flex-1 py-2 text-sm font-medium rounded-md text-slate-600 transition-all';
                lblWeight.innerText = 'Weight (lbs)';
                lblHeight.innerText = 'Height (inches)';
            }
        }

        async function calculateBMI(event) {
            event.preventDefault();
            const weight = parseFloat(document.getElementById('weight').value);
            const height = parseFloat(document.getElementById('height').value);

            try {
                const response = await fetch('/api/calculate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ weight, height, unit: currentUnit })
                });

                if (!response.ok) throw new Error('Calculation failed');

                const data = await response.json();
                
                document.getElementById('bmi-value').innerText = data.bmi;
                document.getElementById('bmi-category').innerText = data.category;
                document.getElementById('bmi-advice').innerText = data.advice;
                document.getElementById('result').classList.remove('hidden');
            } catch (err) {
                alert('Please check your inputs and try again.');
            }
        }
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
