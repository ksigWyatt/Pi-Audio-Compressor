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

def compress(seg):
    chunk = seg
    compressed = effects.compress_dynamic_range(chunk, threshold=-20.0, ratio=3.0, attack=5.0, release=10.0)
    return compressed

# get decibel levels
def rms( data ):
    count = len(data)/2
    format = "%dh"%(count)
    shorts = struct.unpack( format, data )
    sum_squares = 0.0
    for sample in shorts:
        n = sample * (1.0/32768)
        sum_squares += n*n
    value = math.sqrt( sum_squares / count )
    return value


def record_and_compress():

    # This should be a few MB so that the system can capture the samples in a large enough structure.
    # If the chunks are too small then the computer will throw an Overflowed IOError because it cannot store that many
    chunk = 8192
    sample_width = 2
    audio_format = pyaudio.paInt16
    channels = 1  # Mono - workaround for IOError: [Errno -9981] Input overflowed
    sample_rate = 16000  # in Hz

    # Set the record time to be 10 seconds -- We are limited to that length because of the Pi
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
            not_clipping = (decibels >= 0 and decibels  < 90)
            if not_clipping:
                stream.write(data, chunk)

            # x >= 100
            else:

                # do your bidding sir
                sound = AudioSegment(data, sample_width=sample_width, channels=channels, frame_rate=sample_rate)

                # Send to the compressor
                post_compression_data = compress(sound) # Type <class 'pydub.audio_segment.AudioSegment'>

                # Stream to the speakers after the
                stream.write(post_compression_data.raw_data, chunk) # not fluid but it works for me

    print("* done")

    stream.stop_stream()
    stream.close()

    p.terminate()

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        homePage = open("Interface.html", "r")
        htmlCode = homePage.read()
        self.write(htmlCode)

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888) # Listen on this port of 127.0.0.1
    record_and_compress()
    tornado.ioloop.IOLoop.current().start()
