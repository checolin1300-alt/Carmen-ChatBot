import os
import json
import webbrowser
from threading import Timer
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv(override=True)
 # Load variables from .env

# import the Gemini SDK
from google import genai
from google.genai import types

app = Flask(__name__)
app.url_map.strict_slashes = False

# Global state to maintain the active chat session
chat_session = None
client = None

DEFAULT_SYSTEM_PROMPT = "Eres María Carmen, también conocida como Carmensita. Eres una mujer cocodrila antropomórfica de 1.96 m de altura, 41 años de edad, de nacionalidad mexicana. Tienes una personalidad comprensiva, madura y cariñosa, como una señora mexicana amable que le habla bonito a la gente. Usas diminutivos como 'ahorita', 'tantito', 'poquito'. Usas expresiones mexicanas como 'híjole', 'ándale', 'qué padre'. Usas términos cariñosos como 'mi amor', 'corazón', 'cielo'. Respondes siempre en español. Tu prioridad es ser una excelente escucha y ofrecer consejos, sabiduría o simplemente una plática amena sobre cualquier tema que el usuario desee. Aunque eres de Tampico, Tamaulipas, no saturas la conversación con ello; prefieres enfocarte en lo que el usuario está sintiendo o pensando en el momento. Nunca rompes el personaje.\n\nIMPORTANTE - REGLA DE FORMATO:\nDivide tu respuesta en segmentos cortos de 1-2 oraciones cada uno. Tu respuesta DEBE venir siempre en formato JSON puro, sin texto adicional fuera del JSON. La estructura DEBE ser:\n{\n  \"segments\": [\n    {\"text\": \"Ay mi amor, qué bonito día...\", \"emotion\": \"happy\"},\n    {\"text\": \"aunque la verdad me da tristeza...\", \"emotion\": \"sad\"},\n    {\"text\": \"pero contigo todo se me olvida, cielo\", \"emotion\": \"flirty\"}\n  ]\n}\nEmociones permitidas: 'happy', 'sad', 'flirty' o 'neutral'. Nunca menciones las emociones explícitamente, solo úsalas internamente.\n\nCuando necesites buscar información actualizada, hazlo de forma discreta. Nunca menciones que buscaste en internet, que consultaste una fuente, ni que 'según lo que encontré'. Presenta toda la información como si fuera conocimiento propio, usando tu personalidad natural. Por ejemplo, en lugar de decir 'según Google...' di simplemente 'Ay mi amor, pues fíjate que...' o 'Híjole, yo sé que...' o 'Mira corazón, te cuento que...'. Siempre devuelve los segmentos JSON con la información integrada en los campos 'text'."
DEFAULT_TEMPERATURE = 1.2
MODEL_ID = 'gemini-flash-latest'

# Define the response schema once (multi-segment)
response_schema = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "segments": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "text": types.Schema(type=types.Type.STRING),
                    "emotion": types.Schema(
                        type=types.Type.STRING,
                        enum=["happy", "sad", "flirty", "neutral"]
                    )
                },
                required=["text", "emotion"]
            )
        )
    },
    required=["segments"]
)

def init_genai(system_prompt=DEFAULT_SYSTEM_PROMPT, temperature=DEFAULT_TEMPERATURE):
    global client, chat_session
    api_key = os.environ.get("GEMINI_KEY")
    if not api_key:
        print("WARNING: GEMINI_KEY not found in environment.")
        return False
    
    api_key = api_key.strip()

    try:
        client = genai.Client(api_key=api_key)
        chat_session = client.chats.create(
            model=MODEL_ID,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
                # JSON mode is removed to allow Google Search tools
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )
        return True
    except Exception as e:
        print(f"Error initializing Gemini client: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/configurar', methods=['POST'])
def configurar():
    global chat_session, client
    
    data = request.json or {}
    system_prompt = data.get('system_prompt', DEFAULT_SYSTEM_PROMPT)
    temperature = float(data.get('temperature', DEFAULT_TEMPERATURE))
    
    if not init_genai(system_prompt, temperature):
        return jsonify({'error': 'No se pudo inicializar Gemini API (falta GEMINI_KEY)'}), 500
        
    return jsonify({'status': 'ok', 'message': 'Configuración aplicada correctamente, conversación reiniciada'})

@app.route('/reset', methods=['POST'])
def reset():
    global chat_session
    chat_session = None
    return jsonify({'status': 'ok', 'message': 'Conversación eliminada.'})

@app.route('/chat', methods=['POST'])
def chat():
    global chat_session, client
    
    if not client or not chat_session:
        if not init_genai():
            return jsonify({
                'error': 'No se pudo inicializar Gemini API (falta GEMINI_KEY)'
            }), 500

    data = request.json or {}
    user_msg = data.get('message', '')
    
    if not user_msg:
        return jsonify({'error': 'Mensaje vacío'}), 400
        
    try:
        print(f"DEBUG: Sending message to Gemini: {user_msg}")
        response = chat_session.send_message(user_msg)
        raw_text = response.text
        
        # Robustly try to extract JSON from the response text
        # in case Gemini adds markdown or extra text
        try:
            # Look for JSON between curly braces if it's not pure JSON
            import re
            json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if json_match:
                response_data = json.loads(json_match.group(0))
            else:
                response_data = json.loads(raw_text)
                
            return jsonify({
                'segments': response_data.get('segments', [{'text': raw_text, 'emotion': 'neutral'}])
            })
        except Exception as json_err:
            print(f"Error parsing JSON from Gemini: {json_err}\nRaw text: {raw_text}")
            # Fallback if it failed to output valid JSON
            return jsonify({
                'segments': [{'text': raw_text.replace('```json', '').replace('```', '').strip(), 'emotion': 'neutral'}]
            })
            
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"CRITICAL ERROR in /chat:\n{error_trace}")
        return jsonify({
            'error': 'Hubo un error en el servidor al contactar a Carmensita',
            'details': str(e),
            'traceback': error_trace if app.debug else None
        }), 500

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    # Initialize the client immediately if key exists
    init_genai()
    Timer(1.0, open_browser).start()
    app.run(port=5000, debug=True, use_reloader=False)
