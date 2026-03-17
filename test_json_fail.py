import json
import re

raw_text = """
{
"segments": [
{
"text": "Híjole, pareces estarme saludando seguido, mi amor.",
"emotion": "neutral"
},
{
"text": "¿Necesitas algo en especial o solo pasabas a saludarme un poquito más?",
"emotion": "happy"
},
{
"text": "Ándale, dime con confianza, que aquí estoy para ti.",
"emotion": "neutral"
}
]
}
"""

def test_parse(text):
    print(f"Testing text length: {len(text)}")
    clean_text = text.strip()
    try:
        json_match = re.search(r'\{.*\}', clean_text, re.DOTALL)
        if json_match:
            print("Regex match found!")
            json_to_parse = json_match.group(0)
            data = json.loads(json_to_parse)
            print("Successfully parsed with regex match!")
            return data
        else:
            print("No regex match.")
            data = json.loads(clean_text)
            return data
    except Exception as e:
        print(f"FAILED: {e}")
        return None

test_parse(raw_text)
