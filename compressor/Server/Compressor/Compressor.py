from pydub import effects
from pydub import AudioSegment


# seg Object:
# Max Amp: Float variable around 32768.0
# Frame Count: HZ frequency of Audio - usually 44.1 unless 48k was used
#
# seg is the track - or each AudioSegment object that is streamed while compressed

def compress(seg):
    print "Compressing"
    fileName = ""
    chunk = AudioSegment.from_wav(seg)
    # returns AudioSegment object
    compressed = effects.compress_dynamic_range(chunk, threshold=-20.0, ratio=3.0,
                                                attack=10.0, release=100.0)

    compressed.export('(%s)_Pydub_compressed.mp3' % fileName, format="mp3")
    print chunk.get_array_of_samples()
    return seg










