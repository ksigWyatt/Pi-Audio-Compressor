import tornado.ioloop
import tornado.web
import pyaudio
import sys
import os
from pydub import effects
from pydub import AudioSegment

def compress(seg):
    print "Compressing"
    chunk = AudioSegment.from_wav(seg)
    # returns AudioSegment object
    compressed = effects.compress_dynamic_range(chunk, threshold=-20.0, ratio=3.0,
                                                attack=10.0, release=100.0)
    return compressed

def record_and_compress():
    # chunks are recordings of 1024 bytes of data
    chunk = 1024
    sample_width = 2
    audio_format = pyaudio.paInt16
    channels = 2
    sample_rate = 44100  # in Hz
    # Set the record time to be 3 minutes that's about the length of a song
    recording_length = 10

    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(sample_width),
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    output=True,
                    frames_per_buffer=chunk)

    print("* recording")

    # for all the chunks that are in the array - stream them for compression
    for i in range(0, int(sample_rate / chunk * recording_length)):
        data = stream.read(chunk)
        stream.write(data, chunk)
        compressed = compress(data)

    # print compressed
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



