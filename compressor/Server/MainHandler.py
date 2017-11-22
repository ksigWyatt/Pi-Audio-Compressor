import tornado.ioloop
import tornado.web
import pyaudio
import wave
from pydub import effects
from pydub import AudioSegment
import numpy
import struct
import math
import audioop

def compress(seg):
    print "Compressing"
    chunk = seg
    # returns AudioSegment object
    compressed = effects.compress_dynamic_range(chunk, threshold=-20.0, ratio=3.0,
                                                attack=10.0, release=100.0)
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
    frames = []

    # for all the chunks that are in the array - stream them for compression
    for i in range(0, int(sample_rate / chunk * recording_length)):
        # data = samples from the stream <type 'str'>
        data = stream.read(chunk)
        audio_levels = audioop.rms(data, 2)

        #print value -- crashes if the value is == 0 so we must catch this
        if (audio_levels == 0):
            audio_levels = 1
            decibels = 20 * math.log10(audio_levels)
        else:
            decibels = 20 * math.log10(audio_levels)
        print decibels

        if decibels >= 100:
            print "Over 100 detected"
        #     print "Creating compressed file"
        #     wave_file = wave.open(f="compress.wav", mode="wb")
        #     wave_file.writeframes(data)
        #     frame_rate = wave_file.getframerate()
        #     print frame_rate
        #     wave_file.setnchannels(2)
        #
        #     # Create the proper file
        #     compressed = AudioSegment.from_raw(wave_file)
        #     compressed.max_possible_amplitude = 32768  # this is very important
        #     compressed.frame_rate = frame_rate
        #     compressed.channels = 2
        #     compressed.sample_width = 2
        #
        #     post_compression = compress(compressed)
            #     Send to the compressor

        # wave_data = AudioSegment.from_raw(data, sample_width=sample_width, frame_rate=sample_rate, channels=channels)
        # print type(wave_data)

        # This might work?
        # decoded = decimal.Decimal(numpy.fromstring(data, 'Float32'))
        # print decoded[0]


        # sound = AudioSegment.from_wav(file = decoded)


        # <NoneType>
        # stream.write(data, chunk))
        # compressed = compress(data)

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
