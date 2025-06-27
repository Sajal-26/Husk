from faster_whisper import WhisperModel

# Whisper model setup
model = WhisperModel("small", device="cuda", compute_type="float16")

