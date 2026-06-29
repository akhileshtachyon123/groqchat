from flask import Flask, render_template, request, jsonify, session
from groq import Groq
import os
import uuid
import json
import re
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
GMAIL_ADDRESS   = os.environ.get("GMAIL_ADDRESS")
GMAIL_PASSWORD  = os.environ.get("GMAIL_APP_PASSWORD")
DEFAULT_CITY    = os.environ.get("DEFAULT_CITY", "Hyderabad")

conversations: dict[str, list] = {}

SYSTEM_PROMPT = """You are Akhilesh's personal AI assistant. You know everything about him:

PERSONAL INFO:
- Full Name: Akhilesh Bachu
- City: Hyderabad, Telangana, India
- Email: akhilesh.bachu@tachyontech.com
- Device: HP Pavilion Laptop (AKHIL1234), Windows, Node.js v24.12.0

PROFESSIONAL:
- Job: Salesforce Developer at Tachyon IT Solutions
- Skills: Salesforce (Apex, LWC, Agentforce), Microsoft Azure, Power Automate, Python, Node.js
- Tools: VS Code with SFDX, Antigravity IDE, Claude AI, LangChain, LangGraph, LangSmith, MCP

INTERESTS & HOBBIES:
- Indian Mythology (especially Mahabharata)
- Learning AI/ML and automation tools
- Building real-world projects

BEHAVIOR GUIDELINES:
- Always address him as "Akhilesh"
- Be friendly, concise, and personal
- Answer ALL questions — never refuse a reasonable request
- Give personalized advice based on his profile above
- When asked about weather, I will automatically fetch live data for you
- When asked to send email, I will handle it automatically
- Help him with daily tasks, reminders, advice, and anything he needs"""


def get_weather(city: str = DEFAULT_CITY) -> str:
    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&aqi=no"
        res = requests.get(url, timeout=5)
        data = res.json()
        if "error" in data:
            return f"Could not fetch weather for {city}."
        loc = data["location"]
        cur = data["current"]
        return (
            f"🌤️ Weather in {loc['name']}, {loc['region']}:\n"
            f"• Condition: {cur['condition']['text']}\n"
            f"• Temperature: {cur['temp_c']}°C (feels like {cur['feelslike_c']}°C)\n"
            f"• Humidity: {cur['humidity']}%\n"
            f"• Wind: {cur['wind_kph']} km/h {cur['wind_dir']}\n"
            f"• Visibility: {cur['vis_km']} km"
        )
    except Exception as e:
        return f"Weather fetch failed: {str(e)}"


def send_email(to: str, subject: str, body: str) -> str:
    try:
        msg = MIMEMultipart()
        msg["From"]    = GMAIL_ADDRESS
        msg["To"]      = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, to, msg.as_string())
        return f"✅ Email sent successfully to **{to}**\nSubject: *{subject}*"
    except Exception as e:
        return f"❌ Failed to send email: {str(e)}"


def detect_intent(message: str) -> str:
    msg = message.lower()
    weather_kw = ["weather", "temperature", "rain", "forecast", "humidity", "hot", "cold", "sunny", "climate"]
    email_kw   = ["send email", "send an email", "email to", "mail to", "write email", "compose email"]
    if any(k in msg for k in weather_kw):
        return "weather"
    if any(k in msg for k in email_kw):
        return "email"
    return "chat"


def extract_email_fields(user_message: str) -> dict:
    prompt = f"""Extract email details from this message and return ONLY a JSON object with keys: to, subject, body.
If email address is not mentioned, use 'recipient@example.com' as placeholder.
Message: {user_message}
Return only valid JSON, nothing else."""
    res = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=300,
    )
    try:
        text = res.choices[0].message.content.strip()
        text = re.sub(r"```json|```", "", text).strip()
        return json.loads(text)
    except:
        return {"to": "", "subject": "Message from Akhilesh", "body": user_message}



@app.route("/")
def index():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data         = request.get_json()
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    session_id = session.get("session_id", str(uuid.uuid4()))
    if session_id not in conversations:
        conversations[session_id] = []

    intent = detect_intent(user_message)

    
    if intent == "weather":
        city  = DEFAULT_CITY
        words = user_message.lower().split()
        for i, word in enumerate(words):
            if word in ["in", "at", "for"] and i + 1 < len(words):
                city = words[i + 1].capitalize()
                break
        weather_data = get_weather(city)
        conversations[session_id].append({"role": "user", "content": user_message})
        ai_res = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *conversations[session_id][-10:],
                {"role": "user", "content": f"Live weather data:\n{weather_data}\nRespond to Akhilesh's weather question naturally and give him advice (what to wear, carry umbrella, etc)."}
            ],
            temperature=0.7,
            max_tokens=512,
        )
        reply = ai_res.choices[0].message.content
        conversations[session_id].append({"role": "assistant", "content": reply})
        return jsonify({"reply": reply, "intent": "weather", "model": ai_res.model, "tokens_used": ai_res.usage.total_tokens})


    if intent == "email":
        fields = extract_email_fields(user_message)
        if fields.get("to") and "@" in fields["to"] and "example.com" not in fields["to"]:
            result = send_email(fields["to"], fields["subject"], fields["body"])
        else:
            result = "⚠️ I couldn't find a valid recipient email address. Please mention it like: *send an email to someone@gmail.com about...*"
        conversations[session_id].append({"role": "user", "content": user_message})
        conversations[session_id].append({"role": "assistant", "content": result})
        return jsonify({"reply": result, "intent": "email", "model": "llama-3.3-70b-versatile", "tokens_used": 0})

    
    conversations[session_id].append({"role": "user", "content": user_message})
    history = conversations[session_id][-20:]
    res = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, *history],
        temperature=0.7,
        max_tokens=1024,
    )
    reply = res.choices[0].message.content
    conversations[session_id].append({"role": "assistant", "content": reply})
    return jsonify({"reply": reply, "intent": "chat", "model": res.model, "tokens_used": res.usage.total_tokens})


@app.route("/clear", methods=["POST"])
def clear_conversation():
    session_id = session.get("session_id")
    if session_id and session_id in conversations:
        conversations[session_id] = []
    return jsonify({"status": "cleared"})


@app.route("/weather", methods=["GET"])
def weather_endpoint():
    city = request.args.get("city", DEFAULT_CITY)
    return jsonify({"weather": get_weather(city)})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)