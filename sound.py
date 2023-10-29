import wave, pyaudio


def play_amogus_sound():
    CHUNK = 1024

    with wave.open("AMOGUS.wav", 'rb') as wf:
        # Instantiate PyAudio and initialize PortAudio system resources (1)
        p = pyaudio.PyAudio()

        # Write to single file

        # Open stream (2)
        s = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                   channels=wf.getnchannels(),
                   rate=wf.getframerate(),
                   output=True)

        # Play samples from the wave file (3)
        while len(data := wf.readframes(CHUNK)):  # Requires Python 3.8+ for :=
            s.write(data)

        # Close stream (4)
        s.close()


        # Release PortAudio system resources (5)
        p.terminate()