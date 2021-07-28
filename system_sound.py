import soundcard as sc
import pyaudio


def showMic():
    all_mics = [' '.join(str(dev).split()[1:-2]) for dev in sc.all_microphones()]
    return all_mics

def selectMic(option):
    py_audio = pyaudio.PyAudio()
    mics = showMic()

    print(mics[0])

    for i in range(py_audio.get_device_count()):
        dev = py_audio.get_device_info_by_index(i)['name']
        print(i, dev)

    # return aud_dev_index

if __name__ == '__main__':
    print(showMic())
    option = int(input("\nOption : "))

    print(selectMic(option))