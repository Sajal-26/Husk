from faster_whisper import WhisperModel
import sounddevice as sd
import soundfile as sf
import numpy as np
import tempfile
import os

model = WhisperModel("small", device="cuda", compute_type="int8_float16")

def record_audio(silence_duration: int = 2, samplerate: int = 16000, silence_threshold: float = 0.2) -> np.ndarray:
    '''
        Records audio from the default input device until silence is detected.

        Args:
            silence_duration (int): Silence duration in seconds. Defaults to 2.
            samplerate (int): Audio samplerate. Defaults to 16000.
            silence_threshold (float): Silence detection threshold. Defaults to 0.02.

        Returns:
            np.ndarray: Recorded audio data.
    '''
    try:
        audio_chunks = []
        chunk_size = 1024
        recording_started = False

        with sd.InputStream(samplerate=samplerate, channels=1, dtype=np.float32) as stream:
            
            print(' '*50, end='\r')
            print("You can speak now...", end='\r')

            while True:
                indata, _ = stream.read(chunk_size)
                volume = np.max(np.abs(indata))

                if volume > silence_threshold:
                    recording_started = True
                    audio_chunks.append(indata)
                    print(' '*50, end='\r')
                    print("Recording....", end='\r')

                elif recording_started:
                    audio_chunks.append(indata)
                    silence_period = 0

                    while silence_period < silence_duration:
                        indata, _ = stream.read(chunk_size)
                        volume = np.max(np.abs(indata))

                        if volume > silence_threshold:
                            audio_chunks.append(indata)
                            silence_period = 0

                        else:
                            silence_period += chunk_size / samplerate

                    break
                
        print(' '*50, end='\r')
        recorded_audio = np.concatenate(audio_chunks, axis=0)
        audio_data = recorded_audio.flatten().astype(np.float32) / np.max(np.abs(recorded_audio))
        return audio_data

    except Exception as e:
        print(f"Error recording audio: {e}")
        return None
    
def listen():
    '''
        Listens to audio input, transcribes the speech, and returns the text.
    '''
    audio_data = record_audio()

    if audio_data is None or len(audio_data) == 0:
        return ""


    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
        sf.write(tmpfile.name, audio_data, 16000)

        try:
            segments, _ = model.transcribe(tmpfile.name, beam_size=5, vad_filter = True, temperature=[0.0])
            if not segments:
                return ""
        except Exception as e:
            print(f"Error during transcription: {e}")
            os.remove(tmpfile.name)
            return ""
    
    os.remove(tmpfile.name)
    text = ''.join([segment.text for segment in segments])

    return text