import pyaudio

# Must keep for memory leaks - potential crashes
# chunks are recordings of 1024 bytes of data
chunk = 1024

audio_format = pyaudio.paInt16
channels = 2
sample_rate = 44100 # in Hz
# Set the record time to be 3 minutes that's about the length of a song
recording_length = 5 # 180

p = pyaudio.PyAudio()

stream = p.open(format = audio_format,
                channels = channels,
                rate = sample_rate,
                input = True,
                frames_per_buffer = chunk)

print("begin recording")

frames = []

# do not print anything in this func or else the audio will not sample properly
# Giving the audio a digitized sound
for i in range(0, int(sample_rate / chunk * recording_length)):
    data = stream.read(chunk)
    # Send data to compressor here as they are encoded - comes in as garbled compiled code in the terminal
    frames.append(data)

print("end recording")

# Frames returns array of signed integers represented by a hexadecimal escape sequence
# \x17\x03\x15\x0c\x17#\x15{\x15\xb5\x15q\x14M\x16\x9d\x14?\x163\x15y

stream.stop_stream()
stream.close()
p.terminate()