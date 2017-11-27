import tornado.ioloop
import tornado.web
import pyaudio
import wave
from pydub import effects
from pydub import AudioSegment
from pydub.playback import play
import os
import struct
import math
import audioop

def compress(seg):
    chunk = seg
    compressed = effects.compress_dynamic_range(chunk, threshold=-20.0, ratio=3.0,
                                                attack=5.0, release=10.0)
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
    # chunks are recordings of 1024 bytes of data
    chunk = 1024
    sample_width = 2
    audio_format = pyaudio.paInt16
    channels = 2
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
            decibels = 20 * math.log10(audio_levels)
        else:
            decibels = 20 * math.log10(audio_levels)
            # Not 0 < x < 100 -- Normal & Acceptable use
            not_clipping = (decibels >= 0 and decibels + 30 < 100)
            if not_clipping:
                decibels = 20 * math.log10(audio_levels)
                stream.write(data, chunk)
            # x >= 100
            else:
                chunk_temp = chunk
                # do your bidding sir
                wave_file = wave.open(f="compress.wav(%s)" %i, mode="wb")
                wave_file.setnchannels(2)
                wave_file.setsampwidth(sample_width)
                wave_file.setframerate(sample_rate)
                wave_file.writeframesraw(data)
                wave_file.close()

                # Create the proper file
                compressed = AudioSegment.from_wav("compress.wav(%s)" %i)
                os.remove("compress.wav(%s)" %i) # delete it quickly

                # Send to the compressor
                post_compression_data = compress(compressed) # Type <class 'pydub.audio_segment.AudioSegment'>

                # Stream to the speakers after the
                stream.write(compressed.raw_data, chunk_temp) # not fluid but it works for me

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