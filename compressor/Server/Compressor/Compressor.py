from pydub import effects

def compress(seg):
    effects.compress_dynamic_range(seg, threshold = -20.0, ratio = 3.0,
                                   attack = 10.0, release = 100.0)