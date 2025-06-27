import re
import os
import emoji
import tempfile
from pydub import AudioSegment
from edge_tts import Communicate

abbreviations = {
    'eg': 'example',
    'etc': 'et cetera',
    'i.e.': 'that is',
    'ie': 'that is',
    'e.g.': 'for example',
    '(e.g.': 'for example',
    'vs': 'versus',
    'mr': 'mister',
    'mrs': 'missus',
    'dr': 'doctor',
    'prof': 'professor',
    'inc': 'incorporated',
    'ltd': 'limited',
    'dept': 'department',
    'st': 'street',
    'ave': 'avenue',
    'co': 'company',
    'corp': 'corporation',
    'jan': 'January',
    'feb': 'February',
    'mar': 'March',
    'apr': 'April',
    'jun': 'June',
    'jul': 'July',
    'aug': 'August',
    'sep': 'September',
    'oct': 'October',
    'nov': 'November',
    'dec': 'December',
    'asap': 'as soon as possible',
    'bday': 'birthday',
    'est': 'established',
    'hr': 'heart rate',
    'min': 'minute',
    'sec': 'second',
    'temp': 'temperature',
    'avg': 'average',
    'max': 'maximum',
    'min': 'minimum',
    'approx': 'approximately',
    'appt': 'appointment',
    'gov': 'government',
    'esp': 'especially',
    'info': 'information',
    'misc': 'miscellaneous',
    'amt': 'amount',
    'b/c': 'because',
    'w/': 'with',
    'w/o': 'without',
    'vs.': 'versus',
    'cm': 'centimeter',
    'kg': 'kilogram',
    'km': 'kilometer',
    'ml': 'milliliter',
    'mm': 'millimeter',
    'bp': 'blood pressure',
    'ecg': 'electrocardiogram',
    'eeg': 'electroencephalogram',
    'MRI': 'magnetic resonance imaging',
    'ct': 'computed tomography',
    'vp': 'vice president',
    'gm': 'general manager',
    'pr': 'public relations'
}

language_extensions = {
    "ahk": "ahk",
    "applescript": "applescript",
    "autoit": "au3",
    "bash" : "sh",
    "bat": "bat",
    "c": "c",
    "clojure": "clj",
    "coffeescript": "coffee",
    "cpp": "cpp",
    "crystal": "cr",
    "csharp": "cs",
    "dart": "dart",
    "d": "d",
    "fortran": "f",
    "fortran_fixed-form": "f",
    "fortran-modern": "f90",
    "fortranfreeform": "f90",
    "fsharp": "fs",
    "go": "go",
    "groovy": "groovy",
    "haskell": "hs",
    "haxe": "hx",
    "html": "html",
    "java": "java",
    "javascript": "js",
    "julia": "jl",
    "kit": "kit",
    "less": "less",
    "lisp": "lisp",
    "lua": "lua",
    "mojo": "mojo",
    "nim": "nim",
    "objective-c": "m",
    "ocaml": "ml",
    "pascal": "pas",
    "perl": "pl",
    "perl6": "p6",
    "php": "php",
    "powershell": "ps1",
    "python": "py",
    "r": "r",
    "racket": "rkt",
    "react": "jsx",
    "react-ts": "tsx",
    "ruby": "rb",
    "rust": "rs",
    "sass": "sass",
    "scala": "scala",
    "scheme": "scm",
    "scss": "scss",
    "shellscript": "sh",
    "sml": "sml",
    "swift": "swift",
    "text" : "txt",
    "typescript": "ts",
    "vbscript": "vbs",
    "v": "v",
    "vue": "vue",
    "zig": "zig",
    "" : "txt"
}

# voice = 'en-CA-LiamNeural' # pitch : -10 (male)
# voice = 'en-GB-RyanNeural'  # pitch : -20 (Best-male)
# voice = 'en-US-AnaNeural'  # pitch : +10 (child)
# voice = 'en-GB-MaisieNeural'  # pitch : +10 (child)
# voice = 'en-IE-EmilyNeural'  # pitch : +10, rate : +5 (female)
# voice = 'en-GB-SoniaNeural'  # pitch : +10 (female)
# voice = 'en-US-AvaNeural'  # pitch : +10 (Best-Female)

voice = "en-GB-RyanNeural"

def set_voice(name: str):
    global voice
    voice = name

def prepare_for_speech(text):
    def replace_abbreviations(text):
        for abbr, full_form in abbreviations.items():
            text = re.sub(rf'\b{re.escape(abbr)}\b', full_form, text, flags=re.IGNORECASE)
        return text

    code_file_counter = 1

    def save_code_block(match):
        nonlocal code_file_counter
        code_folder = os.path.join(os.path.dirname(__file__), '..', 'Codes')
        os.makedirs(code_folder, exist_ok=True)

        lang = (match.group(1) or '').strip().lower()
        code = match.group(2).strip()

        ext = language_extensions.get(lang, 'txt')
        filename = fr'{code_folder}\file_{code_file_counter}.{ext}'
        code_file_counter += 1

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(code)

        spoken_lang = lang if lang else 'text'
        return f"The {spoken_lang} code has been saved as `file_{code_file_counter - 1}.{ext}` in the Codes folder."

    text = re.sub(r'```(?:\s*([\w+-]+)\s*)?\n([\s\S]*?)```', save_code_block, text)
    text = replace_abbreviations(text.lower())
    text = re.sub(r'`([^`]*)`', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\(.*?\)', r'\1', text)
    text = re.sub(r'#+ ', '', text)
    text = re.sub(r'---', '', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    text = re.sub(r'> ', '', text)
    text = re.sub(r'\n+', '\n', text)
    text = text.strip().replace(r'\n', ' ').replace(r"\'", "'").replace(r'\"', '"')
    text = emoji.replace_emoji(text, replace="") 
    return text

def speak(text: str = "Sorry, I was unable to catch up to that. Can you tell me again?"):
    global voice
    text = prepare_for_speech(text=text)
    pitch = "+0Hz"
    rate = '+0%'

    if voice == 'en-US-AvaNeural': pitch = "+10Hz"
    elif voice == 'en-GB-SoniaNeural': pitch = "+10Hz"
    elif voice == 'en-IE-EmilyNeural':
        pitch = "+10Hz"
        rate = "+5%"
    elif voice == 'en-GB-MaisieNeural': pitch = "+10Hz"
    elif voice == 'en-US-AnaNeural': pitch = "+10Hz"
    elif voice == 'en-GB-RyanNeural': pitch = "-20Hz"
    elif voice == 'en-CA-LiamNeural': pitch = "-10Hz"

    try:
        communicate = Communicate(text, voice = voice, pitch = pitch, rate = rate)
        with tempfile.NamedTemporaryFile(suffix = ".mp3", delete = False) as temp_audio_file:
            temp_audio_path = temp_audio_file.name
            communicate.save_sync(temp_audio_path)
        return AudioSegment.from_file(temp_audio_path)
    
    except Exception as e:
        print(f"An error occurred during text-to-speech: {e}")

    finally:
        if 'temp_audio_path' in locals() and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)