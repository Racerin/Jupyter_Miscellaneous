import pynput
import time
import sounddevice as sd

keyboard = pynput.keyboard.Controller()

time.sleep(3)
keyboard.press('a')
keyboard.release('a')

recordings= np.array([0])
sample = []
maxi = 0
def sdSetup():
    #https://python-sounddevice.readthedocs.io/en/0.3.7/#sounddevice.Stream
    global sample
    sample, fs = sf.read(r"C:\Users\Administrator\Dropbox\Python Codes\fishbit.wav")
    #sample = sample.astype('int8')
    sd.default.samplerate = fs
    print("sample format", sample.dtype)
    #sd.default.dtype = np.dtype('int8')
    sdThread = sd.Stream(channels=1, callback=sdCallback)
    sdThread.start()
    kl = keyboardListener(on_press=on_press, on_release=on_release)
    kl.start()
    kl.join()
def sdCallback(indata, outdata, frames, time, status):
    global recordings, sample, maxi
    #sd.sleep(1000)
    recordings = np.concatenate((recordings, indata.flatten()), axis=0)
    #print(recordings.size)
    #print(frames, time, status)
    #print("sample shape", sample.shape, "recordings shape", recordings.shape, "indata shape", indata.shape)
    if recordings.size > sample.size:
        #print("inside")
        corr = np.correlate(recordings, sample)
        holdmax = np.max(corr)
        if holdmax > maxi:
            maxi = holdmax
            print(maxi)