'''

    Name : Screen Recorder Module
    Version : 0.1
    Creator : Nitin Choudhury

    Last Edited : {
        Date : 10-06-2021
        Time : 16:29

    }

'''





import pyautogui
import cv2
import numpy as np
import time
import pyaudio
import wave
import concurrent.futures
import moviepy.editor as mpe
import os
import soundcard as sc



class Recorder:

    def __init__(self, vid_filename="tmp_scn.avi", ext_aud_filename="tmp_aud.wav", outfile="out.avi"):
        self.vid_filename = vid_filename
        self.ext_aud_filename = ext_aud_filename
        self.outfile = outfile
        self.stop_record = False

    def __extract_as_tuple__(self, string):
        string = string.split(',')
        tup = tuple(int(i) for i in string)

        return tup

    def __extract_filename__(self, file):
        ext = file.split('.')[-1]
        if ext != 'avi':
            file += '.avi'

        return file


    def screen_record(self, frame_size=(0, 0, pyautogui.size()[0], pyautogui.size()[1]), framerate=9.0, fourcc=cv2.VideoWriter_fourcc(*'XVID')):

        Xs = [0, 5, 6, 10, 0]
        Ys = [0, 10, 5, 3, 0]

        if type(frame_size) == str:
            frame_size = self.__extract_as_tuple__(frame_size)

        res_tuple = (frame_size[2]-frame_size[0], frame_size[3]-frame_size[1])
        filename = self.__extract_filename__(self.vid_filename)

        outVid = cv2.VideoWriter(filename, fourcc, framerate, res_tuple)
        init_time = time.time()
        while True:
            frame = pyautogui.screenshot(region=frame_size)

            mouseX, mouseY = pyautogui.position()

            np_frame = np.array(frame)
            np_frame = cv2.cvtColor(np_frame, cv2.COLOR_BGR2RGB)

            Xthis = [2*x+mouseX for x in Xs]
            Ythis = [2*y+mouseY for y in Ys]
            points = list(zip(Xthis, Ythis))
            points = np.array(points, 'int32')
            cv2.fillPoly(np_frame, [points], color=[255, 255, 250])
            cv2.polylines(np_frame, [points], isClosed=True, color=[0, 0, 0], thickness=1)

            outVid.write(np_frame)

            width = int(pyautogui.size()[0]/2)
            height = int(pyautogui.size()[1]/2)

            cv2.namedWindow("Screen Recorder", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Screen Recorder", width, height)

            cv2.imshow("Screen Recorder", np_frame)

            breakKeys = [ord('Q'), ord('q'), 27]
            if cv2.waitKey(1) in breakKeys:
                break

        self.stop_record = True
        end_time = time.time()

        outVid.release()
        cv2.destroyAllWindows()

        rec_duration = round(end_time - init_time)
        creds = {
            "filename" : filename,
            "frame_size" : frame_size,
            "resolution" : res_tuple,
            "frame_rate" : framerate,
            "fourcc" : fourcc,
            "recording_duration" : rec_duration
        }

        return creds

    def record_ext_audio(self, rec_format=pyaudio.paInt16, rec_channels=int(str(sc.default_speaker()).split()[-2].split('(')[-1]), rec_rate=44100, rec_input=True, rec_frames_per_buffer=1024):

        py_audio = pyaudio.PyAudio()
        rec = py_audio.open(format=rec_format, channels=rec_channels, rate=rec_rate, input=rec_input, frames_per_buffer=rec_frames_per_buffer)

        audio_frames = []

        init_time = time.time()

        try:
            while (self.stop_record==False):
                data = rec.read(rec_frames_per_buffer)
                audio_frames.append(data)

        except KeyboardInterrupt:
            pass

        rec.stop_stream()
        rec.close()
        py_audio.terminate()
        end_time = time.time()

        rec_time = int(end_time - init_time)

        wf = wave.open(self.ext_aud_filename, 'wb')
        wf.setnchannels(rec_channels)
        wf.setsampwidth(py_audio.get_sample_size(rec_format))
        wf.setframerate(rec_rate)
        wf.writeframes(b''.join(audio_frames))
        wf.close()

        metadata = {
            "filename" : self.ext_aud_filename,
            "format" : rec_format,
            "channel" : rec_channels,
            "rate" : rec_rate,
            "input" : rec_input,
            "frame per buffer" : rec_frames_per_buffer,
            "recording duration" : rec_time
        }

        return metadata




    def extAudVidMerger(self):
        vid_clip = mpe.VideoFileClip(self.vid_filename)
        aud_clip = mpe.AudioFileClip(self.ext_aud_filename)
        duration = min(vid_clip.duration, aud_clip.duration)
        vid_clip = vid_clip.subclip(0, duration)
        aud_clip = aud_clip.subclip(0, duration)

        fin_clip = vid_clip.set_audio(aud_clip)
        fin_clip.ipython_display()

        if self.outfile.split('.')[-1] != 'mp4':
            self.outfile += '.mp4'

        os.rename('./__temp__.mp4', self.outfile)

        metadata = {
            "filename" : self.outfile,
            "duration" : duration
        }

        vid_clip.close()
        aud_clip.close()

        return metadata

    def clean_env(self):
        flag = True

        try:
            os.remove(self.vid_filename)
            os.remove(self.ext_aud_filename)

        except PermissionError:
            flag = False

        return flag

    def rec_ScnExtAud(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            t1 = executor.submit(self.screen_record)
            t2 = executor.submit(self.record_ext_audio)

            vid_metadata = t1.result()
            aud_metadata = t2.result()

        output_metadata = self.extAudVidMerger()
        self.clean_env()

        return vid_metadata, aud_metadata, output_metadata


if __name__ == '__main__':
    outfile = input("ENTER OUTPUT FILENAME {example : Example.mp4} : ")
    recorder = Recorder(outfile=outfile)

    vid_metadata, aud_metadata, output_metadata = recorder.rec_ScnExtAud()
    print("VIDEO METADATA : ", vid_metadata)
    print("AUDIO METADATA : ", aud_metadata)
    print("OUTPUT METADATA : ", output_metadata)