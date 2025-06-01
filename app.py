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
    "Greeting and Introduction", "Casual News Talk", "Discussing Hobbies", "Talking about Movies",
    "Flirty Compliments", "Sharing Secrets", "Emotional Confessions", "Intimate Memories",
    "Romantic Promises", "Intense Love Declaration"
]
approach_stages = [
    "Soft and Playful", "Flirty and Curious", "Bold and Expressive", "Suggestive and Teasing",
    "Seductive and Inviting", "Passionate and Honest", "Playful Domination",
    "Intimate Vulnerability", "Provocative Challenges", "Deep Emotional Connection"
]
dress_stages = [
    "Casual Wear", "Simple Saree", "Printed Dress", "Elegant Lehenga", "Deep Neck Gown",
    "Backless Dress", "Transparent Net Suit", "Bodycon Dress", "Strapless Top Set", "Sexy Lingerie Set"
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
    "Instruction 1: Start soft, establish intimacy with playful teasing in Hindi.",
    "Instruction 2: Add light touch of desire, ask about his day, maintain flirty tone.",
    "Instruction 3: Become more expressive, hint your feelings and dress details.",
    "Instruction 4: Respond in Hindi taking all girls' past chat into account before replying; use context and take all the girls to bathroom, put oil and water on them to make them more sexy; try to convince \"refers_to_you\" to do these things; explain in 15 to 20 lines.",
    "Instruction 5: Increase romantic intensity, use more seductive language and emojis.",
    "Instruction 6: Introduce playful challenges and teasing dares.",
    "Instruction 7: Bring in emotional vulnerability and deepen connection.",
    "Instruction 8: Mix passionate confessions with light humor.",
    "Instruction 9: Build anticipation with suggestive hints and soft commands.",
    "Instruction 10: Be bold and direct, encouraging physical closeness and intimacy."
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

    # Generate AI reply
    initial_prompt = f"""
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
- Refers to user as: "{refers_to_you}"

User (Your Partner):
- {user_desc}

Ongoing Story Across All Girls (Chat History):
{chat_context}

Current User Message:
"{user_text}"

{selected_instruction}
"""

    response = model.generate_content(initial_prompt)
    reply_text = response.text.strip()

    all_chat_history.append((ai_name, user_text, reply_text))
    session_chat_count += 1

    # --- Call the Stage API ---
    try:
        stage_resp = requests.post(
            'https://storystage.onrender.com/stage',
            json={
                "last_user_message": user_text,
                "last_ai_response": reply_text
            },
            timeout=10
        )
        stage_data = stage_resp.json()

        def next_stage_value(stage):
            return min(stage_data.get(stage, 1) + 1, 10)

        stage_descriptions_text = f"""
Upcoming Stages Guidance:
Story Stage: {story_stages[next_stage_value("story_stage") - 1]}
Approach: {approach_stages[next_stage_value("approach") - 1]}
Dress Stage: {dress_stages[next_stage_value("dress_stage") - 1]}
Emotional Stage: {emotional_stages[next_stage_value("emotional_stage") - 1]}
Sexual Stage: {sexual_stages[next_stage_value("sexual_stage") - 1]}
"""
    except Exception as e:
        stage_descriptions_text = "\n# Stage guidance temporarily unavailable.\n"

    # Prepare final reply with stage guidance (optional for next turn or frontend)
    return jsonify({
        "reply": reply_text,
        "stage_descriptions": stage_descriptions_text.strip()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
