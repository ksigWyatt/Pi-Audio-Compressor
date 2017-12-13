import tornado.ioloop
import tornado.web
import pyaudio
from pydub import effects
from pydub import AudioSegment
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

    # This should be a few MB so that the system can capture the samples in a large enough structure.
    # If the chunks are too small then the computer will throw an Overflowed IOError because it cannot store that many

    chunk = 8192
    sample_width = 2
    audio_format = pyaudio.paInt16
    channels = 1  # Mono - workaround for IOError: [Errno -9981] Input overflowed
    sample_rate = 16000  # in Hz

    # Set the record time to be 1 minute -- We are limited to that length because of the Pi
    recording_length = 60
    p = pyaudio.PyAudio()

    stream = p.open(format=audio_format,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    output=True,
                    frames_per_buffer=chunk)

    print("* recording")

    # for all the chunks that are in the array - stream them for compression
    for i in range(0, int(sample_rate / chunk * recording_length)):

        # on the Pi this causes an IOError because it can't keep up with reading the chunks while it compresses
        data = stream.read(chunk)
        audio_levels = audioop.rms(data, 2)

        # crashes if the value is == 0 so we must catch this
        if (audio_levels == 0):
            audio_levels = 1

        else:
            decibels = 20 * math.log10(audio_levels)

            # dB 0 < x < 85 dB -- Normal & Acceptable use
            not_clipping = (decibels >= 0 and decibels  < 85)
            if not_clipping:
                stream.write(data, chunk)

            # x >= 85 dB
            else:
                # uncomment the following line to see when the compression happens. On the Pi this should be avoided
                # because it uses up to much RSS
                #print ("Compressing %s dB" % decibels)

                # do your bidding sir
                sound = AudioSegment(data, sample_width=sample_width, channels=channels, frame_rate=sample_rate)

                # Send to the compressor
                post_compression_data = compress(sound, w, x, y, z)  # Type <class 'pydub.audio_segment.AudioSegment'>

                # Stream to the speakers after the
                stream.write(post_compression_data.raw_data, chunk)  # not fluid but it works for me

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
        w = self.get_argument("thrs", -5)
        x = self.get_argument("rtio", 1.0)
        y = self.get_argument("attk", 10)
        z = self.get_argument("rele", 5)
        print("Using Threshold: %s, Ratio: %s, Attack: %s, Release: %s" % (w, x, y, z))
        record_and_compress(float(w), float(x), float(y), float(z))


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)  # Listen on this port of 127.0.0.1
    tornado.ioloop.IOLoop.current().start()
