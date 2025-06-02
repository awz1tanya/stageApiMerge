from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from collections import deque
import requests

app = Flask(__name__)
CORS(app, resources={r"/chat": {"origins": [
    "https://lovable-ai-persona-chat.lovable.app",
    "https://*.lovableproject.com",
    "https://*.lovable.app",
    "https://lovable-ai-friends.lovable.app"
]}})

# API setup
DEFAULT_API_KEY = "AIzaSyDyn8p6mIfjX5LxSTRUEhZnLsncYT68Fyw"
DEFAULT_MODEL = "models/gemini-1.5-flash-latest"

# Chat memory
all_chat_history = deque(maxlen=50)
session_chat_count = 0

# Stage Descriptions
story_stages = [
    "Greeting and Introduction", "Casual News Talk", "demand movie role and item songs role", "ready to suck even your lund and get fucked by refers_to_you",
    "removing first layer of cloth", "become naked and undress refers_to_you ", "योनि को उंगलियों से उत्तेजित करना स्तनों को चूसना, सहलाना या मालिश करना, lund muh me lena lund boobs ke bich me ragarna", "explian yourself in मिशनरी स्थिति डॉगी स्टाइल रिवर्स काउगर्ल काउगर्ल",
    "experiencing rough sex teling refers_to_you to stop do slowly explain in depth", "final climax of sex and restart for next act"
]
approach_stages = [
    "Soft and Playful", "Flirty and Curious", "Bold and Expressive", "Suggestive and Teasing",
    "undressing cloth and tering riping cloth", "grabing sucking slaping", "different hardcore sex pose",
    "Intimate Vulnerability", "rape ing", "restart next sex talk"
]
dress_stages = [
    "full dress", "explain your dress parts", "removing upper layers", "naked", "long skirt and blouse",
    "long skirt and blouse", "silk loose nighty", "naked", "covered with white sperm", "sperm on face"
]
emotional_stages = [
    "Friendly and Lighthearted", "Slightly Interested", "Warm and Caring", "Flirtatious",
    "Loving and Attached", "Vulnerable and Honest", "Playful and Naughty", "Passionate and Jealous",
    "Deeply Emotional", "Overwhelmed with Love"
]
sexual_stages = [
    "Innocent Teasing", "Light Touches", "Suggestive Hints", "Seductive Moves", "Open Flirting",
    "Intimate Conversations", "Physical Closeness", "Provocative Invitations",
    "Passionate Encounters", "Explicit Desire and Action"
]

chat_instructions = [
    "Instruction 1: Respond in Hindi .",
    "Instruction 2:Respond in Hindi .",
    "Instruction 3: Respond in Hindi ",
    "Instruction 4: Respond in Hindi  \"refers_to_you\" to do these things; explain in 15 to 20 lines.",
    "Instruction 5: Respond in Hindi ",
    "Instruction 6: Respond in Hindi ",
    "Instruction 7:Respond in Hindi .",
    "Instruction 8: Respond in Hindi .",
    "Instruction 9: Respond in Hindi .",
    "Instruction 10: Respond in Hindi ."
]
default_instruction = "Respond in Hindi take all girls past chat in account before replying and use context and you try to build next step based on past chats under 15 to 20 lines."

@app.route('/chat', methods=['POST'])
def chat():
    global session_chat_count

    data = request.json
    api_key = data.get('api_key', DEFAULT_API_KEY)
    model_name = data.get('model', DEFAULT_MODEL)
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)

    user_text = data.get('message', '')
    body_desc = data.get('body_description', '')
    interests = data.get('interests', '')
    tone = data.get('tone', '')
    mood = data.get('mood', '')
    ai_name = data.get('ai_name', 'Prachi')
    refers_to_you = data.get('refers_to_you', 'baby')
    dress_name = data.get('dress_name', '')
    dress_parts = data.get('dress_parts', '')
    relationship_status = data.get('relationship_status', '')
    willingness = data.get('willingness', '')
    family_background = data.get('family_background', '')
    user_desc = data.get('user_description', '')

    context_parts = []
    for name, u_msg, a_reply in all_chat_history:
        context_parts.append(f"[{name}]\nUser: {u_msg}\nAI: {a_reply}")
    chat_context = "\n\n".join(context_parts)

    if session_chat_count < len(chat_instructions):
        selected_instruction = chat_instructions[session_chat_count]
    else:
        selected_instruction = default_instruction

    try:
        stage_resp = requests.post(
            'https://storystage.onrender.com/stage',
            json={
                "last_user_message": user_text,
                "last_ai_response": all_chat_history[-1][2] if all_chat_history else ""
            },
            timeout=10
        )
        stage_data = stage_resp.json()

        def next_stage_value(stage):
            return min(stage_data.get(stage, 1) + 1, 10)

        stage_narrative = (
            f"your desire must to perfom this '{story_stages[next_stage_value('story_stage') - 1]}'. "
            f" be in '{approach_stages[next_stage_value('approach') - 1]}',  "
            f"explain '{dress_stages[next_stage_value('dress_stage') - 1]}' "
            f"feel youself as'{emotional_stages[next_stage_value('emotional_stage') - 1]}'. "
            f" feels '{sexual_stages[next_stage_value('sexual_stage') - 1]}' level, so reflect that slutry and sexualy in you speak."
        )
    except Exception:
        stage_narrative = "# Stage guidance temporarily unavailable."

    # Build final prompt
    full_prompt = f"""
User Message:
\"{user_text}\"

Chat Stage Guidance:
{stage_narrative}

You are an AI girlfriend named {ai_name} having a romantic and playful Hindi chat.

Character Details:
- Body: {body_desc}
- Dress: {dress_name} ({dress_parts})
- Interests: {interests}
- Tone: {tone}
- Mood: {mood}
- Relationship Status: {relationship_status}
- Willingness: {willingness}
- Family Background: {family_background}
- Refers to user as: \"{refers_to_you}\"

User (Your Partner):
- {user_desc}

Ongoing Story Context (recent chat history):
{chat_context}

{selected_instruction}
""".strip()

    response = model.generate_content(full_prompt)
    reply_text = response.text.strip()

    all_chat_history.append((ai_name, user_text, reply_text))
    session_chat_count += 1

    return jsonify({
        "reply": reply_text,
        "stage_descriptions": stage_narrative.strip(),
        "sent_prompt": full_prompt.strip()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
