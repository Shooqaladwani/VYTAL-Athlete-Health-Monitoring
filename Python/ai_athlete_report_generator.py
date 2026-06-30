# The following code to create a dataframe and remove duplicated rows is always executed and acts as a preamble for your script: 

# dataset = pandas.DataFrame(HeartRate, SpO2, Adjusted_Temperature, Session_Duration, AlertFlag, HR_Peak_Player, HR_Percent_Peak)
# dataset = dataset.drop_duplicates()

# Paste or type your script code here:
import google.generativeai as genai
import matplotlib.pyplot as plt
import textwrap
import re
import pandas as pd

genai.configure(api_key="")
model = genai.GenerativeModel("gemini-2.5-flash")

df = dataset.copy()
df.columns = df.columns.str.strip()

for col in ["HeartRate", "SpO2", "Adjusted_Temperature", "Session_Duration"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

heart_rate = round(df["HeartRate"].mean(), 2)
spo2 = round(df["SpO2"].mean(), 2)
temperature = round(df["Adjusted_Temperature"].mean(), 2)
session_duration = round(df["Session_Duration"].mean(), 2)

alert_flag = "Alert" if df["AlertFlag"].astype(str).str.lower().eq("alert").any() else "Normal"

# =========================
# Scientific thresholds without HR Peak
# =========================

if heart_rate < 140:
    hr_status = "Safe"
    hr_color = "#16A34A"
    hr_note = "Heart rate is within a safe training range."
elif heart_rate < 170:
    hr_status = "Warning"
    hr_color = "#D97706"
    hr_note = "Heart rate indicates increased workload and requires monitoring."
else:
    hr_status = "Critical"
    hr_color = "#DC2626"
    hr_note = "Heart rate indicates high cardiovascular strain."

if 36.0 <= temperature <= 38.0:
    temp_status = "Safe"
    temp_color = "#16A34A"
    temp_note = "Core temperature is within the normal range."
elif 38.1 <= temperature <= 39.5:
    temp_status = "Warning"
    temp_color = "#D97706"
    temp_note = "Temperature indicates heat strain and requires monitoring."
else:
    temp_status = "Critical"
    temp_color = "#DC2626"
    temp_note = "Temperature indicates high heat-stress risk."

if 95 <= spo2 <= 100:
    spo2_status = "Safe"
    spo2_color = "#16A34A"
    spo2_note = "Oxygen saturation is normal."
elif 90 <= spo2 <= 94:
    spo2_status = "Warning"
    spo2_color = "#D97706"
    spo2_note = "Oxygen saturation is slightly reduced and should be monitored."
else:
    spo2_status = "Critical"
    spo2_color = "#DC2626"
    spo2_note = "Oxygen saturation is critically low."

statuses = [hr_status, temp_status, spo2_status]

if "Critical" in statuses or alert_flag == "Alert":
    overall_status = "CRITICAL"
    bg_color = "#FEF2F2"
    border_color = "#DC2626"
    title_color = "#991B1B"
elif "Warning" in statuses:
    overall_status = "WARNING"
    bg_color = "#FFFBEB"
    border_color = "#D97706"
    title_color = "#92400E"
else:
    overall_status = "SAFE"
    bg_color = "#ECFDF5"
    border_color = "#16A34A"
    title_color = "#166534"

prompt = f"""
You are a professional sports health analyst.

Use only these thresholds:

Heart Rate:
- Safe: less than 140 bpm
- Warning: 140 to less than 170 bpm
- Critical: 170 bpm or higher

Core Temperature:
- Safe: 36.0 to 38.0 °C
- Warning: 38.1 to 39.5 °C
- Critical: 39.6 °C or higher

SpO2:
- Safe: 95% to 100%
- Warning: 90% to 94%
- Critical: less than 90%

Selected data:
Heart Rate: {heart_rate} bpm
SpO2: {spo2}%
Core Temperature: {temperature} °C
Session Duration: {session_duration} min
Alert Flag: {alert_flag}

Classified results:
Heart Rate: {hr_status} - {hr_note}
Temperature: {temp_status} - {temp_note}
SpO2: {spo2_status} - {spo2_note}
Overall Risk: {overall_status}

Return this exact format:

Status:
One short sentence.

Key Findings:
- Finding 1
- Finding 2
- Finding 3

Recommendation:
One clear action.

Rules:
- Maximum 95 words.
- No diagnosis.
- No markdown tables.
- Do not mention HR Peak.
- Do not contradict the classified results.
"""

try:
    response = model.generate_content(prompt)
    text = response.text.strip()
except Exception:
    text = f"""
Status:
AI report could not be generated right now.

Key Findings:
- Heart Rate is {heart_rate} bpm and classified as {hr_status}.
- SpO2 is {spo2}% and classified as {spo2_status}.
- Temperature is {temperature} °C and classified as {temp_status}.

Recommendation:
Retry later or use a valid Gemini API key with available quota.
"""

text = re.sub(r"\*\*", "", text)
text = re.sub(r"\*", "•", text)
wrapped_text = "\n".join(textwrap.wrap(text, width=105))

fig, ax = plt.subplots(figsize=(14, 4.4))
ax.axis("off")
fig.patch.set_facecolor("#FFFFFF")
ax.set_facecolor("#FFFFFF")

card = plt.Rectangle(
    (0.02, 0.05), 0.96, 0.90,
    transform=ax.transAxes,
    facecolor=bg_color,
    edgecolor="#E5E7EB",
    linewidth=1.2
)
ax.add_patch(card)

accent = plt.Rectangle(
    (0.02, 0.05), 0.012, 0.90,
    transform=ax.transAxes,
    facecolor=border_color,
    edgecolor=border_color
)
ax.add_patch(accent)

ax.text(
    0.055, 0.86,
    "AI Athlete Health Interpretation",
    transform=ax.transAxes,
    fontsize=15,
    fontweight="bold",
    color=title_color,
    va="top"
)

ax.text(
    0.88, 0.86,
    overall_status,
    transform=ax.transAxes,
    fontsize=10.5,
    fontweight="bold",
    color="white",
    va="top",
    ha="center",
    bbox=dict(
        boxstyle="round,pad=0.45",
        facecolor=border_color,
        edgecolor=border_color
    )
)

metrics_line = (
    f"HR: {heart_rate} bpm ({hr_status})   |   "
    f"SpO₂: {spo2}% ({spo2_status})   |   "
    f"Temp: {temperature} °C ({temp_status})   |   "
    f"Session: {session_duration} min   |   "
    f"Alert: {alert_flag}"
)

ax.text(
    0.055, 0.71,
    metrics_line,
    transform=ax.transAxes,
    fontsize=9.8,
    color="#374151",
    va="top"
)

ax.text(
    0.055, 0.56,
    wrapped_text,
    transform=ax.transAxes,
    fontsize=10.8,
    color="#1F2937",
    va="top",
    linespacing=1.45
)

plt.tight_layout()
plt.show()