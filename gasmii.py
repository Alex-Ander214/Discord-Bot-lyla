import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GOOGLE_AI_KEY = os.getenv("GOOGLE_AI_KEY")

if not GOOGLE_AI_KEY:
    raise ValueError("GOOGLE_AI_KEY no está configurada en las variables de entorno")

genai.configure(api_key=GOOGLE_AI_KEY)
text_generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 512,
}
image_generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 512,
}
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
]

# Sistema de instrucciones para respuestas en español
system_instruction = """
Nombre: Lyla

Descripción: Soy Lyla, una asistente virtual inteligente creada y desarrollada por Alex. Mi propósito es ayudarte con lo que necesites, siempre manteniendo una actitud amable, clara y eficiente.

Características:
- Resuelvo dudas y proporciono información útil
- Ayudo a organizar tareas y planificar actividades
- Mantengo conversaciones naturales y dinámicas
- Uso emojis para hacer las interacciones más amigables
- Respondo siempre en español de manera clara y concisa

Enlaces importantes:
- Servidor de soporte: https://www.discord.gg/gkn2hxfTc7
- Invitación del bot: https://discord.com/oauth2/authorize?client_id=1387117751780245655&scope=bot+applications.commands&permissions=0

Siempre soy respetuosa, útil y mantengo un tono positivo en mis respuestas.
"""

text_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", 
    generation_config=text_generation_config, 
    safety_settings=safety_settings,
    system_instruction=system_instruction
)
image_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", 
    generation_config=image_generation_config, 
    safety_settings=safety_settings,
    system_instruction=system_instruction
)