from flask import Flask, request, jsonify
import pandas as pd
import os
from rapidfuzz import fuzz

app = Flask(__name__)

# ---------------------------
# Load CSV dataset
# ---------------------------
csv_file_path = r"C:\Users\anuve\OneDrive\HealthChat\Health\merged_disease_dataset.csv"
if not os.path.exists(csv_file_path):
    raise FileNotFoundError(f"CSV file not found at {csv_file_path}")

df = pd.read_csv(csv_file_path)
df.columns = [c.strip() for c in df.columns]  # remove extra spaces

# ---------------------------
# Language dictionaries
# ---------------------------
translations = {
    'en': {
        'symptoms': 'Symptoms',
        'precautions': 'Precautions',
        'risk_factors': 'Risk factors',
        'medicines': 'Medicines/Treatment',
        'possible_diseases': 'Possible diseases',
        'sorry': "Sorry, I couldn't understand your question.",
        'disclaimer': "I’m not a doctor. For serious or persistent symptoms, consult a healthcare professional immediately",
        'placeholder': "Ask about a disease or type your symptoms"
    },
    'hi': {
        'symptoms': 'लक्षण',
        'precautions': 'सावधानियाँ',
        'risk_factors': 'जोखिम कारक',
        'medicines': 'दवाएँ / उपचार',
        'possible_diseases': 'संभावित रोग',
        'sorry': "माफ़ कीजिए, मैं आपके प्रश्न को समझ नहीं पाया।",
        'disclaimer': "मैं डॉक्टर नहीं हूँ। गंभीर या लगातार लक्षण होने पर तुरंत स्वास्थ्य पेशेवर से परामर्श लें।",
        'placeholder': "किसी बीमारी के बारे में पूछें या अपने लक्षण लिखें"
    },
    'te': {
        'symptoms': 'లక్షణాలు',
        'precautions': 'జాగ్రత్తలు',
        'risk_factors': 'పరిస్థితి కారకాలు',
        'medicines': 'మార్గదర్శక ఔషధాలు/చికిత్స',
        'possible_diseases': 'సంభావ్య వ్యాధులు',
        'sorry': "క్షమించండి, నేను మీ ప్రశ్నను అర్థం చేసుకోలేకపోయాను.",
        'disclaimer': "నేను డాక్టర్ కాదు. తీవ్రమైన లేదా కొనసాగుతున్న లక్షణాల కోసం వెంటనే వైద్య నిపుణుడిని సంప్రదించండి.",
        'placeholder': "ఒక వ్యాధి గురించి అడగండి లేదా మీ లక్షణాలను టైప్ చేయండి"
    }
}

# ---------------------------
# AI Chatbot logic
# ---------------------------
def get_info(user_input: str, lang='en'):
    t = translations.get(lang, translations['en'])
    text = user_input.lower().replace(',', ' ').replace(' and ', ' ').strip()

    # Detect disease name in user input
    disease_name = None
    diseases_lower = df['Disease'].str.lower().tolist()
    for d in diseases_lower:
        if d in text:
            disease_name = d
            break

    # Symptoms query
    if 'symptom' in text and disease_name:
        row = df[df['Disease'].str.lower() == disease_name]
        symptom_cols = [c for c in df.columns if 'Symptom' in c]
        symptoms = [str(row.iloc[0][c]) for c in symptom_cols if pd.notna(row.iloc[0][c])]
        return f"{t['symptoms']}: " + ', '.join(symptoms)

    # Precautions query
    if ('precaution' in text or 'prevent' in text) and disease_name:
        row = df[df['Disease'].str.lower() == disease_name]
        precaution_cols = [c for c in df.columns if 'Precaution' in c]
        precautions = [str(row.iloc[0][c]) for c in precaution_cols if pd.notna(row.iloc[0][c])]
        return f"{t['precautions']}: " + ', '.join(precautions)

    # Risk factors query
    if 'risk' in text and disease_name:
        row = df[df['Disease'].str.lower() == disease_name]
        risk_cols = [c for c in df.columns if 'risk' in c.lower()]
        risks = [str(row.iloc[0][c]) for c in risk_cols if pd.notna(row.iloc[0][c])]
        if risks:
            return f"{t['risk_factors']}: " + ', '.join(risks)
        else:
            return f"{t['risk_factors']} not found for this disease."

    # Medicines/Treatment query
    if ('medicine' in text or 'treatment' in text) and disease_name:
        row = df[df['Disease'].str.lower() == disease_name]
        med_cols = [c for c in df.columns if 'Medicine' in c or 'Treatment' in c]
        meds = [str(row.iloc[0][c]) for c in med_cols if pd.notna(row.iloc[0][c])]
        if meds:
            return f"{t['medicines']}: " + ', '.join(meds)
        else:
            return f"{t['medicines']} not found for this disease."

    # Free-text symptom search with fuzzy matching
    matched_diseases = []
    for _, r in df.iterrows():
        symptom_cols = [c for c in df.columns if 'Symptom' in c]
        disease_symptoms = ' '.join([str(r[c]).lower() for c in symptom_cols if pd.notna(r[c])])
        score = fuzz.partial_ratio(text, disease_symptoms)
        if score > 50:
            matched_diseases.append(r['Disease'])

    if matched_diseases:
        return f"{t['possible_diseases']}: " + ', '.join(sorted(set(matched_diseases)))

    return t['sorry']

# ---------------------------
# Flask Routes
# ---------------------------
@app.route('/', methods=['GET'])
def home():
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
    <title>HealthGuard</title>
    <style>
        body {{ font-family: Arial; background: #f4f4f4; display: flex; justify-content: center; padding-top: 40px; }}
        .chat-container {{ width: 450px; background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.2); }}
        h1 {{ text-align: center; text-decoration: underline; }}
        h4 {{ text-align: center; font-size: 12px; color: #555; }}
        #chat {{ height: 300px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; margin-bottom: 10px; }}
        #chat .user {{ color: blue; }}
        #chat .bot {{ color: green; }}
        select, input, button {{ width: 100%; padding: 10px; margin-top: 5px; border-radius: 5px; border: 1px solid #ccc; }}
    </style>
    </head>
    <body>
    <div class="chat-container">
        <h1>HealthGuard</h1>
        <h4 id="disclaimer">{translations['en']['disclaimer']}</h4>
        <select id="language" onchange="changeLanguage()">
            <option value="en">English</option>
            <option value="hi">हिन्दी</option>
            <option value="te">తెలుగు</option>
        </select>
        <div id="chat"></div>
        <input type="text" id="message" placeholder="{translations['en']['placeholder']}">
        <button onclick="sendMessage()">Send</button>
    </div>
    <script>
        let lang = 'en';
        const translations = {translations};
        function changeLanguage() {{
            lang = document.getElementById('language').value;
            document.getElementById('disclaimer').innerText = translations[lang]['disclaimer'];
            document.getElementById('message').placeholder = translations[lang]['placeholder'];
        }}

        function sendMessage() {{
            let msg = document.getElementById('message').value;
            if(msg.trim() === '') return;
            let chat = document.getElementById('chat');
            chat.innerHTML += '<div class="user">You: ' + msg + '</div>';
            fetch('/chat', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ message: msg, lang: lang }})
            }})
            .then(response => response.json())
            .then(data => {{
                chat.innerHTML += '<div class="bot">Bot: ' + data.reply + '</div>';
                chat.scrollTop = chat.scrollHeight;
            }});
            document.getElementById('message').value = '';
        }}
    </script>
    </body>
    </html>
    '''

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    lang = data.get('lang', 'en')
    reply = get_info(user_message, lang)
    return jsonify({'reply': reply})

# ---------------------------
# Run the Flask app
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)
