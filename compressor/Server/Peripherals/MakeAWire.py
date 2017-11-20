import pyaudio


# Must keep for memory leaks - potential crashes
# chunks are recordings of 1024 bytes of data
chunk = 1024
sample_width = 2
audio_format = pyaudio.paInt16
channels = 2
sample_rate = 44100 # in Hz
# Set the record time to be 3 minutes that's about the length of a song
recording_length = 5 # 180

p = pyaudio.PyAudio()

stream = p.open(format = p.get_format_from_width(sample_width),
                channels = channels,
                rate = sample_rate,
                input = True,
                output = True,
                frames_per_buffer = chunk)

print("* recording")

for i in range(0, int(sample_rate / chunk * recording_length)):
    data = stream.read(chunk)
    stream.write(data, chunk)

print("* done")

stream.stop_stream()
stream.close()

p.terminate()