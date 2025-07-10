from dotenv import load_dotenv
import time
import os

from google.genai import types
from google import genai

from Senses import speak, set_voice, listen
from pydub.playback import _play_with_simpleaudio
import sounddevice as sd
import numpy as np

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
        set_voice("en-GB-RyanNeural")
        
        while True:
            response = self.model.send_message_stream(message = [prompt])
            if prompt.lower() == 'exit.':
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
                    try:
                        r += chunk.text
                        print(chunk.text, end="")
                    except:
                        pass
                print()
                audio = speak(r)
                playback = _play_with_simpleaudio(audio)

                with sd.InputStream(samplerate=16000, channels=1, dtype=np.float32) as stream:
                    while playback.is_playing():
                        indata, _ = stream.read(1024)
                        volume = np.max(np.abs(indata))

                        if volume > 0.2:
                            playback.stop()
                            break
                        time.sleep(0.1)

            prompt = listen()
            print("> ", prompt)


if __name__ == '__main__':
    husk = Husk(OUTPUT_MODE = 'AUDIO')
    try:
        husk.chat()
    except KeyboardInterrupt:
        print("\nExited by user.")