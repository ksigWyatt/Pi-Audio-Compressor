from pydub import effects
from pydub import AudioSegment

# seg Object:
# Max Amp: Float variable around 32768.0
# Frame Count: HZ frequency of Audio - usually 44.1 unless 48k was used
#
track = AudioSegment.from_wav("C:\Users\wyatt\Downloads\StillYoung-WhiteLabel(IsThisLove).wav")

# seg is the track - or each AudioSegment object that is streamed while compressed
# def compress(seg):
#     compressed = effects.compress_dynamic_range(seg, threshold = -20.0, ratio = 3.0,
#                                    attack = 10.0, release = 100.0)
#     export = AudioSegment.export(compressed, format="mp3")
#     export.write("Compressed.mp3")


# returns AudioSegment object
compressed = effects.compress_dynamic_range(seg=track, threshold=-20.0, ratio = 3.0,
                                    attack = 10.0, release = 100.0)

export = AudioSegment.export(compressed, format="mp3")
export.write("Compressed.mp3")