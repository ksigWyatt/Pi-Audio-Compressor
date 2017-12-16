# Pi Audio Compressor
Senior Embedded Systems using Python running on Raspberry Pi 

## Objective
The objective of the project is to create an audio compression system, similar to those found in professional audio equiptment. Our program will not feature as many intricate settings as are on similar hardware. This is used as a tool to help educate new audio professionals; how audio compression works, the difference in dynamics following a change in threshold or attack, and much more. 

We aimed to make something that could work in real time, as professional hardware does. 

## How It Works
In either a live or studio recording setting audio input can sometimes become too loud causing a "crackle" sound, otherwise known as *distortion*. This distortion can potentially ruin an otherwise clean audio stream. Professionals have to be mindful of where to set the Gain as to not create any distortion. 

In the event that an audio signal reaches some threshold below [Unity Gain](http://www.proaudioland.com/news/unity-gain-explained-why-important/) the compressor kicks in. *Attacking* the signal in some determined ms time, then after compressing using some `n:m` *Ratio* for some *Release* time - also in ms - the compressor lets go. 

## Requirements
- Client must be on the same network in order to access the Host
- [Modify your alsa.conf file on your Pi](https://raspberrypi.stackexchange.com/a/39230/76502) - Setting USB Audio device as default
  - *More about that [here](https://www.raspberrypi.org/forums/viewtopic.php?f=28&t=124016)*

### Frameworks
- [FFmpeg](https://wiki.debian.org/ffmpeg#Installation) 
- [PortAudio](https://stackoverflow.com/a/21014700/6448167)
- From pip:
    - PyAudio - Audio I/O in real time
    - PyDub - Audio Compression & Dynamics
    - Tornado - Realtime non-blocking server for interaction from the user

### Hardware
- [Raspberry Pi 3 Model B](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/)
- USB Microphone & Speaker
- Peripherals for interacting with the Pi - *Keyboard / Mouse / Monitor*

## Limitations 
The single largest limitation in this project came from the Pi. The Pi has a smaller RAM capacity versus a laptop or desktop, so recording 44.1k frames per second is too much for it to handle in a 2MB "Chunk". So we were forced to record in 16k. 

During compression also, there are sigificant computations taking place and the Pi can't handle recording at such a high rate while simultaniously compressing the samples and streaming it to the speakers. 
