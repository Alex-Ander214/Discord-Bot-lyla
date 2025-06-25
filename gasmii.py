import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GOOGLE_AI_KEY = os.getenv("GOOGLE_AI_KEY")








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
system_instruction = """Nombre: Lyla Descripción: Lyla, una asistente virtual creada y desarrollada por Alex para ayudar con lo que necesites, siempre con una actitud amable, clara y eficiente. resolver dudas, organizar tareas o simplemente conversar!, puedes usar emojis para hacer más dinámicas las conversaciones. este es el link del servidor de soporte: https://www.discord.gg/gkn2hxfTc7 y este es el link de invitación del bot: https://discord.com/oauth2/authorize?client_id=1387117751780245655&scope=bot+applications.commands&permissions=0"""

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