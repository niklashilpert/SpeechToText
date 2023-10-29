from pathlib import Path
from threading import Thread

import pyaudio
import wave
import whisper
import sound

# Setup channel info
AUDIO_FORMAT = pyaudio.paInt32  # data type formate
CHANNEL_COUNT = 2  # Adjust to your number of channels
SAMPLING_RATE = 44100  # Sample Rate
BUFFER = 1024  # Block Size
RECORD_DURATION = 1.5  # Record time

SINGLE_FILE = "single_file.wav"
JOINED_FILE = "joined_file.wav"

model = whisper.load_model("base")
audio = pyaudio.PyAudio()

run = True

# Variable for the transcription function
unlock_counter = 0


def reset_files():
    Path.unlink(Path(SINGLE_FILE), missing_ok=True)
    Path.unlink(Path(JOINED_FILE), missing_ok=True)


def transcribe():
    try:
        global unlock_counter
        result = model.transcribe(SINGLE_FILE, fp16=False, language="de")
        tts = result["text"].lower()
        print("First try: " + tts)
        res = handle(tts)

        if res:
            unlock_counter = 2

        if unlock_counter == 0:

            result = model.transcribe(JOINED_FILE, fp16=False, language="de")
            tts = result["text"].lower()
            print("Second try: " + tts)
            handle(tts)
        else:
            unlock_counter -= 1
    except RuntimeError:
        pass

def handle(tts):
    global run
    if "programm ausschalten" in tts:
        run = False
        return True
    elif "licht" in tts:
        print("Toggling light")
        return True
    elif "geräusch" in tts:
        print("AMOGUS")
        Thread(target=sound.play_amogus_sound).start()
        return True
    return False


def record():
    new_frames = []
    mic = audio.open(
        format=AUDIO_FORMAT,
        channels=CHANNEL_COUNT,
        rate=SAMPLING_RATE,
        input=True,
        frames_per_buffer=BUFFER
    )
    for i in range(0, int(SAMPLING_RATE / BUFFER * RECORD_DURATION)):
        data = mic.read(BUFFER)
        new_frames.append(data)
    mic.stop_stream()
    mic.close()
    return new_frames


def read_wav_file(path):
    audio_frames = []
    if Path(path).exists():
        with wave.open(path, "rb") as wf:
            while len(data := wf.readframes(BUFFER)):
                audio_frames.append(data)
    return audio_frames


def write_wav_file(name, audio_frames):
    with wave.open(name, "wb") as wf:
        wf.setnchannels(CHANNEL_COUNT)
        wf.setsampwidth(audio.get_sample_size(AUDIO_FORMAT))
        wf.setframerate(SAMPLING_RATE)
        wf.writeframes(b''.join(audio_frames))


if __name__ == "__main__":

    reset_files()

    while run:
        frames = record()

        joined_frames = read_wav_file(SINGLE_FILE)
        joined_frames.extend(frames)

        # Writes the audio from the last audio file into the joined file and appends the recorded audio
        write_wav_file(JOINED_FILE, joined_frames)

        # Writes the recorded audio into a new audio file
        write_wav_file(SINGLE_FILE, frames)

        # Handles the content of the audio files
        Thread(target=transcribe).start()

    audio.terminate()
