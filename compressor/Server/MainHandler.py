import tornado.ioloop
import tornado.web
import pyaudio
import wave
from pydub import effects
from pydub import AudioSegment
import os
import struct
import math
import audioop


def compress(seg, w, x, y, z):
    chunk = seg
    compressed = effects.compress_dynamic_range(chunk, w, x, y, z)
    return compressed


# get decibel levels
def rms(data):
    count = len(data) / 2
    format = "%dh" % (count)
    shorts = struct.unpack(format, data)
    sum_squares = 0.0
    for sample in shorts:
        n = sample * (1.0 / 32768)
        sum_squares += n * n
    value = math.sqrt(sum_squares / count)
    return value


def record_and_compress(w, x, y, z):
    # chunks are recordings of 2048 bytes of data
    # This should be a few MB so that the system can capture the samples in a large enough structure.
    # If the chunks are too small then the computer will throw an Overflowed IOError because it cannot store that many

    chunk = 2048
    sample_width = 2
    audio_format = pyaudio.paInt16
    channels = 1  # Mono - workaround for IOError: [Errno -9981] Input overflowed
    sample_rate = 44100  # in Hz

    # Set the record time to be 3 minutes that's about the length of a song
    recording_length = 60
    p = pyaudio.PyAudio()

    # Stream object <type 'instance'>
    stream = p.open(format=audio_format,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    output=True,
                    frames_per_buffer=chunk)

    print("* recording")

    # for all the chunks that are in the array - stream them for compression
    for i in range(0, int(sample_rate / chunk * recording_length)):

        # data = samples from the stream <type 'str'>
        data = stream.read(chunk)
        audio_levels = audioop.rms(data, 2)

        # crashes if the value is == 0 so we must catch this
        if (audio_levels == 0):
            audio_levels = 1

        else:
            decibels = 20 * math.log10(audio_levels)

            # dB 0 < x < 100 -- Normal & Acceptable use
            not_clipping = (decibels >= 0 and decibels + 50 < 100)
            if not_clipping:
                stream.write(data, chunk)

            # x >= 100
            else:
                chunk_temp = chunk

                # do your bidding sir
                wave_file = wave.open(f="compress.wav(%s)" % i, mode="wb")
                wave_file.setnchannels(channels)
                wave_file.setsampwidth(sample_width)
                wave_file.setframerate(sample_rate)
                wave_file.writeframesraw(data)
                wave_file.close()

                # Create the proper file
                compressed = AudioSegment.from_wav("compress.wav(%s)" % i)
                os.remove("compress.wav(%s)" % i)  # delete it quickly

                # Send to the compressor
                post_compression_data = compress(compressed, w, x, y,
                                                 z)  # Type <class 'pydub.audio_segment.AudioSegment'>

                # Stream to the speakers after the
                stream.write(post_compression_data.raw_data, chunk_temp)  # not fluid but it works for me

    print("* done")

    stream.stop_stream()
    stream.close()

    p.terminate()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        homePage = open("Interface.html", "r")
        htmlCode = homePage.read()
        self.write(htmlCode)
        self.finish()

    # runs compression after the page loads fully
    def on_finish(self):  # checks the url for form arguments
        w = self.get_argument("thrs", 0)
        x = self.get_argument("rtio", 1)
        y = self.get_argument("attk", 0.1)
        z = self.get_argument("rele", 0.1)
        record_and_compress(float(w), float(x), float(y), float(z))


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)  # Listen on this port of 127.0.0.1
    tornado.ioloop.IOLoop.current().start()
