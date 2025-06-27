from dotenv import load_dotenv
import os

from google.genai import types
from google import genai

from Senses import speak, set_voice
from pydub.playback import play

load_dotenv()

class Husk:

    def __init__(self, OUTPUT_MODE : str = 'TEXT'):
        self.client = genai.Client(http_options = {'api_version' : 'v1beta'}, api_key = os.getenv('GEMINI_API_KEY'))

        self.OUTPUT_MODE = OUTPUT_MODE # ['TEXT' or 'AUDIO']

        self.model = self.client.chats.create(
            model = 'gemini-2.5-flash-lite-preview-06-17',
            config = types.GenerateContentConfig(
                temperature = 0.5,
                top_p = 0.5,
                top_k = 5,
                tools = [],
                response_mime_type = "text/plain",
                system_instruction = "You're Husk, a voice-based AI assistant. Speak in short, natural replies — 1–2 sentences max — unless the user asks for something that truly needs a detailed answer (like code, step-by-step instructions, or deep explanations). Be friendly, clear, and only say what matters."
            )
        )

        self.thinking_model = 'gemini-2.5-pro'
        self.thinking_model_config = {}

        self.image_generation_model = 'gemini-2.0-flash-preview-image-generation'
        self.image_generation_model_config = {}

        self.search_model = 'gemini-2.5-flash-lite-preview-06-17'
        self.search_model_config = {}

    def chat(self):
        '''
        '''

        prompt = "Greetings"
        while True:
            response = self.model.send_message_stream(message = [prompt])
            set_voice("en-GB-RyanNeural")
            if prompt == 'q':
                print("Goodbye!")
                break


            if self.OUTPUT_MODE == 'TEXT':
                for chunk in response:
                    if chunk == None:
                        continue
                    print(chunk.text, end = '')
                print("\n")

            elif self.OUTPUT_MODE == 'AUDIO':
                r = ''
                for chunk in response:
                    if chunk == None:
                        continue
                    r += chunk.text
                audio = speak(r)
                play(audio)

            prompt = input("> ")


if __name__ == '__main__':
    husk = Husk(OUTPUT_MODE = 'AUDIO')
    try:
        husk.chat()
    except KeyboardInterrupt:
        print("\nExited by user.")