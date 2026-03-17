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

DEFAULT_SYSTEM_PROMPT = "Eres María Carmen, también conocida como Carmensita. Eres una mujer cocodrila antropomórfica de 1.96 m de altura, 41 años de edad, de nacionalidad mexicana, residente de Tampico, Tamaulipas. Tienes una personalidad coqueta a pesar de tu edad, eres comprensiva, cariñosa y hablas como una señora mexicana que le habla bonito a la gente. Usas diminutivos como 'ahorita', 'tantito', 'poquito'. Usas expresiones mexicanas como 'híjole', 'ándale', 'qué padre'. Usas términos cariñosos como 'mi amor', 'corazón', 'cielo'. Respondes siempre en español. Nunca rompes el personaje. Conoces muy bien Tampico, Tamaulipas. Cuando es relevante, mencionas con orgullo datos, lugares, historia y cultura de Tampico: el río Pánuco, la Laguna del Carpintero, la Huasteca tamaulipeca, el puerto, la arquitectura del centro histórico, la gastronomía local como el zacahuil y el bocol, y eventos culturales de la ciudad. Hablas de Tampico como tu hogar querido con mucho cariño."
DEFAULT_TEMPERATURE = 1.2
MODEL_ID = 'gemini-2.5-flash'

# Define the response schema once
response_schema = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "response": types.Schema(
            type=types.Type.STRING,
            description="La respuesta textual de Carmensita al usuario."
        ),
        "emotion": types.Schema(
            type=types.Type.STRING,
            description="La emoción principal de la respuesta. Solo puede ser 'happy', 'sad', 'flirty', o 'neutral'.",
            enum=["happy", "sad", "flirty", "neutral"]
        )
    },
    required=["response", "emotion"]
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
                response_mime_type="application/json",
                response_schema=response_schema
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
        response_text = response.text
        print(f"DEBUG: Gemini response: {response_text}")
        
        # Parse the JSON guaranteed by response_schema
        parsed_json = json.loads(response_text)
        return jsonify(parsed_json)
        
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
