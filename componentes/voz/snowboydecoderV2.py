#!/usr/bin/env python
import collections
import pyaudio
import snowboydetect
import time
import wave
import os
import logging
import sys
import time


from array import array
from struct import pack
from sys import byteorder
from gtts import gTTS
from pydub import AudioSegment

import copy
from subprocess import call

import speech_recognition as sr

# obtain path to "demo.wav" in the same folder as this script
from os import path
AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "demo.wav")

logging.basicConfig()
logger = logging.getLogger("snowboy")
logger.setLevel(logging.INFO)
TOP_DIR = os.path.dirname(os.path.abspath(__file__))

RESOURCE_FILE = os.path.join(TOP_DIR, "resources/common.res")
DETECT_DING = os.path.join(TOP_DIR, "resources/ding.wav")
DETECT_DONG = os.path.join(TOP_DIR, "resources/dong.wav")
DETECT_IDU = os.path.join(TOP_DIR, "dime.wav")
PREGUNTA_PERSIANA = os.path.join(TOP_DIR, "pregunta_persiana.wav")
SUBE_PERSIANA = os.path.join(TOP_DIR, "sube_persiana.wav")
BAJA_PERSIANA = os.path.join(TOP_DIR, "baja_persiana.wav")
PARA_PERSIANA = os.path.join(TOP_DIR, "para_persiana.wav")
ERROR = os.path.join(TOP_DIR, "error.wav")


THRESHOLD = 4000 # audio levels not normalised.
CHUNK_SIZE = 1024
SILENT_CHUNKS = 1 * 44100 / 1024  # about 3sec
MAX_CHUNKS = 3 * 44100 / 1024
FORMAT = pyaudio.paInt16
FRAME_MAX_VALUE = 2 ** 15 - 1
NORMALIZE_MINUS_ONE_dB = 10 ** (-1.0 / 20)
RATE = 44100
CHANNELS = 1
TRIM_APPEND = RATE / 4


class RingBuffer(object):
    """Ring buffer to hold audio from PortAudio"""
    def __init__(self, size = 4096):
        self._buf = collections.deque(maxlen=size)

    def extend(self, data):
        """Adds data to the end of buffer"""
        self._buf.extend(data)

    def get(self):
        """Retrieves data from the beginning of buffer and clears it"""
        tmp = bytes(bytearray(self._buf))
        self._buf.clear()
        return tmp

def play_sound(msg):
   tts = gTTS(text=msg, lang='es')
   tts.save("prueba.mp3")
   song = AudioSegment.from_mp3("prueba.mp3")
   song.export("final.wav", format ="wav")
   os.system("aplay final.wav")


def play_audio_file_idu(fname):
    """Simple callback function to play a wave file. By default it plays
    a Ding sound.
    :param str fname: wave file name
    :return: None
    """
    ding_wav = wave.open(fname, 'rb')
    ding_data = ding_wav.readframes(ding_wav.getnframes())
    audio = pyaudio.PyAudio()
    stream_out = audio.open(
        format=audio.get_format_from_width(ding_wav.getsampwidth()),
        channels=ding_wav.getnchannels(),
        rate=ding_wav.getframerate(), input=False, output=True)
    stream_out.start_stream()
    stream_out.write(ding_data)
    time.sleep(0.3)
    stream_out.stop_stream()
    stream_out.close()
    audio.terminate()

def play_audio_file(fname=DETECT_DING):
    """Simple callback function to play a wave file. By default it plays
    a Ding sound.
    :param str fname: wave file name
    :return: None
    """
    ding_wav = wave.open(fname, 'rb')
    ding_data = ding_wav.readframes(ding_wav.getnframes())
    audio = pyaudio.PyAudio()
    stream_out = audio.open(
        format=audio.get_format_from_width(ding_wav.getsampwidth()),
        channels=ding_wav.getnchannels(),
        rate=ding_wav.getframerate(), input=False, output=True)
    stream_out.start_stream()
    stream_out.write(ding_data)
    time.sleep(0.3)
    stream_out.stop_stream()
    stream_out.close()
    audio.terminate()

class HotwordDetector(object):
    """
    Snowboy decoder to detect whether a keyword specified by `decoder_model`
    exists in a microphone input stream.
    :param decoder_model: decoder model file path, a string or a list of strings
    :param resource: resource file path.
    :param sensitivity: decoder sensitivity, a float of a list of floats.
                              The bigger the value, the more senstive the
                              decoder. If an empty list is provided, then the
                              default sensitivity in the model will be used.
    :param audio_gain: multiply input volume by this factor.
    """
    def __init__(self, decoder_model,
                 resource=RESOURCE_FILE,
                 sensitivity= [],
                 audio_gain=1):

        def audio_callback(in_data, frame_count, time_info, status):
            self.ring_buffer.extend(in_data)
            play_data = chr(0) * len(in_data)
            return play_data, pyaudio.paContinue

        tm = type(decoder_model)
        ts = type(sensitivity)
        if tm is not list:
            decoder_model = [decoder_model]
        if ts is not list:
            sensitivity = [sensitivity]
        model_str = ",".join(decoder_model)

        self.detector = snowboydetect.SnowboyDetect(
            resource_filename=resource.encode(), model_str=model_str.encode())
        self.detector.SetAudioGain(audio_gain)
        self.num_hotwords = self.detector.NumHotwords()

        if len(decoder_model) > 1 and len(sensitivity) == 1:
            sensitivity = sensitivity*self.num_hotwords
        if len(sensitivity) != 0:
            assert self.num_hotwords == len(sensitivity), \
                "number of hotwords in decoder_model (%d) and sensitivity " \
                "(%d) does not match" % (self.num_hotwords, len(sensitivity))
        sensitivity_str = ",".join([str(t) for t in sensitivity])
        if len(sensitivity) != 0:
            self.detector.SetSensitivity(sensitivity_str.encode())

        self.ring_buffer = RingBuffer(
            self.detector.NumChannels() * self.detector.SampleRate() * 5)
        self.audio = pyaudio.PyAudio()
        self.stream_in = self.audio.open(
            input=True, output=False,
            format=self.audio.get_format_from_width(
                self.detector.BitsPerSample() / 8),
            channels=self.detector.NumChannels(),
            rate=self.detector.SampleRate(),
            frames_per_buffer=2048,
            stream_callback=audio_callback)


    def start(self, detected_callback=play_audio_file,
              interrupt_check=lambda: False,
              sleep_time=0.03):
        """
        Start the voice detector. For every `sleep_time` second it checks the
        audio buffer for triggering keywords. If detected, then call
        corresponding function in `detected_callback`, which can be a single
        function (single model) or a list of callback functions (multiple
        models). Every loop it also calls `interrupt_check` -- if it returns
        True, then breaks from the loop and return.
        :param detected_callback: a function or list of functions. The number of
                                  items must match the number of models in
                                  `decoder_model`.
        :param interrupt_check: a function that returns True if the main loop
                                needs to stop.
        :param float sleep_time: how much time in second every loop waits.
        :return: None
        """
        if interrupt_check():
            logger.debug("detect voice return")
            return

        tc = type(detected_callback)
        if tc is not list:
            detected_callback = [detected_callback]
        if len(detected_callback) == 1 and self.num_hotwords > 1:
            detected_callback *= self.num_hotwords

        assert self.num_hotwords == len(detected_callback), \
            "Error: hotwords in your models (%d) do not match the number of " \
            "callbacks (%d)" % (self.num_hotwords, len(detected_callback))

        logger.debug("detecting...")

        while True:
            if interrupt_check():
                logger.debug("detect voice break")
                break
            data = self.ring_buffer.get()
            if len(data) == 0:
                time.sleep(sleep_time)
                continue

            ans = self.detector.RunDetection(data)
            if ans == -1:
                logger.warning("Error initializing streams or reading audio data")
            elif ans > 0:
                message = "Keyword " + str(ans) + " detected at time: "
                message += time.strftime("%Y-%m-%d %H:%M:%S",
                                         time.localtime(time.time()))

		logger.info(message)

		#os.system("play dime.wav")
            play_audio_file_idu(DETECT_IDU)
		#play_sound("Lo siento, no te entiendo")
		"Records from the microphone and outputs the resulting data to 'path'"
       		sample_width, data = self.record()
        	data = pack('<' + ('h' * len(data)), *data)

        	wave_file = wave.open('demo.wav', 'wb')
        	wave_file.setnchannels(CHANNELS)
        	wave_file.setsampwidth(sample_width)
        	wave_file.setframerate(RATE)
        	wave_file.writeframes(data)
        	wave_file.close()

                message = "Mensaje recibido! "
                message += time.strftime("%Y-%m-%d %H:%M:%S",
                                         time.localtime(time.time()))
                logger.info(message)

		# Record Audio
		r = sr.Recognizer()
		with sr.AudioFile(AUDIO_FILE) as source:
		 #   print("Say something!")
		    audio = r.record(source)
 
		# Speech recognition using Google Speech Recognition
		try:
		    # for testing purposes, we're just using the default API key
		    # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
		    # instead of `r.recognize_google(audio)`
            msg = r.recognize_google(audio, language="es-ES")
            print("You said: " + msg)
            msg = msg.split( )

            if "sube" in msg and "persiana" in msg:
                play_audio_file_idu(PREGUNTA_PERSIANA)
                sample_width, data = self.record()
                data = pack('<' + ('h' * len(data)), *data)

                wave_file = wave.open('demo.wav', 'wb')
                wave_file.setnchannels(CHANNELS)
                wave_file.setsampwidth(sample_width)
                wave_file.setframerate(RATE)
                wave_file.writeframes(data)
                wave_file.close()

                # Record Audio
                r = sr.Recognizer()
                with sr.AudioFile(AUDIO_FILE) as source:
                audio = r.record(source)

                try:
                    msg = r.recognize_google(audio, language="es-ES")
                    print("You said: " + msg)
                    msg = msg.split( )

                    if "poco" in msg:
                        play_audio_file_idu(SUBE_PERSIANA)
                        call(["curl", "http://root:opticalflow@192.168.0.101/arduino/command/blindup"])
                        time.sleep(5)
                        call(["curl", "http://root:opticalflow@192.168.0.101/arduino/command/blindstop"])

                    if "toda" in msg or "todo" in msg:
                        play_audio_file_idu(SUBE_PERSIANA)
                        call(["curl", "http://root:opticalflow@192.168.0.101/arduino/command/blindup"])

                    if "mitad" in msg:
                        play_audio_file_idu(SUBE_PERSIANA)
                        call(["curl", "http://root:opticalflow@192.168.0.101/arduino/command/blindup"])
                        time.sleep(10)
                        call(["curl", "http://root:opticalflow@192.168.0.101/arduino/command/blindstop"])
                except sr.UnknownValueError:
                    play_audio_file_idu(ERROR)
                except sr.RequestError as e:
                    print("Could not request results from Google Speech Recognition service; {0}".format(e))


            if "baja" in msg and "persiana" in msg:
                play_audio_file_idu(PREGUNTA_PERSIANA)
                sample_width, data = self.record()
                data = pack('<' + ('h' * len(data)), *data)

                wave_file = wave.open('demo.wav', 'wb')
                wave_file.setnchannels(CHANNELS)
                wave_file.setsampwidth(sample_width)
                wave_file.setframerate(RATE)
                wave_file.writeframes(data)
                wave_file.close()

                # Record Audio
                r = sr.Recognizer()
                with sr.AudioFile(AUDIO_FILE) as source:
                audio = r.record(source)

                try:
                    msg = r.recognize_google(audio, language="es-ES")
                    print("You said: " + msg)
                    msg = msg.split( )

                    if "poco" in msg:
                        play_audio_file_idu(BAJA_PERSIANA)
                        call(["curl", "http://root:opticalflow@192.168.0.101/arduino/command/blinddown"])
                        time.sleep(5)
                        call(["curl", "http://root:opticalflow@192.168.0.101/arduino/command/blindstop"])

                    if "toda" in msg or "todo" in msg:
                        play_audio_file_idu(BAJA_PERSIANA)
                        call(["curl", "http://root:opticalflow@192.168.0.101/arduino/command/blinddown"])

                    if "mitad" in msg:
                        play_audio_file_idu(BAJA_PERSIANA)
                        call(["curl", "http://root:opticalflow@192.168.0.101/arduino/command/blinddown"])
                        time.sleep(10)
                        call(["curl", "http://root:opticalflow@192.168.0.101/arduino/command/blindstop"])

                except sr.UnknownValueError:
                    play_audio_file_idu(ERROR)
                except sr.RequestError as e:
                    print("Could not request results from Google Speech Recognition service; {0}".format(e))

		    if "hora" in msg and "es" in msg:
			    ahora = time.strftime("%X")
			    play_sound(ahora)    

		except sr.UnknownValueError:
		    play_audio_file_idu(ERROR)
		except sr.RequestError as e:
		    print("Could not request results from Google Speech Recognition service; {0}".format(e))


        #        callback = detected_callback[ans-1]	
         #       if callback is not None:
          #          callback()

        logger.debug("finished.")

    def terminate(self):
        """
        Terminate audio stream. Users cannot call start() again to detect.
        :return: None
        """
        self.stream_in.stop_stream()
        self.stream_in.close()
        self.audio.terminate()

    def is_silent(self,data_chunk):
        """Returns 'True' if below the 'silent' threshold"""
        return max(data_chunk) < THRESHOLD

    def normalize(self, data_all):
        """Amplify the volume out to max -1dB"""
        # MAXIMUM = 16384
        normalize_factor = (float(NORMALIZE_MINUS_ONE_dB * FRAME_MAX_VALUE)
                            / max(abs(i) for i in data_all))

        r = array('h')
        for i in data_all:
            r.append(int(i * normalize_factor))
        return r

    def trim(self, data_all):
        _from = 0
        _to = len(data_all) - 1
        for i, b in enumerate(data_all):
            if abs(b) > THRESHOLD:
                _from = max(0, i - TRIM_APPEND)
                break

        for i, b in enumerate(reversed(data_all)):
            if abs(b) > THRESHOLD:
                _to = min(len(data_all) - 1, len(data_all) - 1 - i + TRIM_APPEND)
                break

        return copy.deepcopy(data_all[_from:(_to + 1)])

    def record(self):
        """Record a word or words from the microphone and 
        return the data as an array of signed shorts."""

        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=True, frames_per_buffer=CHUNK_SIZE)

        silent_chunks = 0
        audio_started = False
        data_all = array('h')

        while True :
            # little endian, signed short
            data_chunk = array('h', stream.read(CHUNK_SIZE))
            if byteorder == 'big':
                data_chunk.byteswap()
            data_all.extend(data_chunk)

            silent = self.is_silent(data_chunk)

            if audio_started:
                if silent:
                    silent_chunks += 1
                    if silent_chunks > SILENT_CHUNKS:
                        break
                else: 
                    silent_chunks = 0
            elif not silent:
                audio_started = True              
    
        sample_width = p.get_sample_size(FORMAT)
        stream.stop_stream()
        stream.close()
        p.terminate()

        data_all = self.trim(data_all)  # we trim before normalize as threshhold applies to un-normalized wave (as well as is_silent() function)
        data_all = self.normalize(data_all)
        return sample_width, data_all
