# Import the necessary modules.
import tkinter as tk
import tkinter.messagebox
import pyaudio
import wave
import os
import threading

class RecAUD:
    def __init__(self,topic_names ,chunk=3024, frmat=pyaudio.paInt16, channels=2, rate=44100):
        # Start Tkinter and set Title
        self.topic_names = topic_names
        self.sentences = []
        self.audio_name = None
        self.file_output = None
        self.url = None
        self.cur_sentence = -1
        self.main = tk.Tk()
        self.main.geometry('600x300')
        self.main.title('Voice Recording')

        self.CHUNK = chunk
        self.FORMAT = frmat
        self.CHANNELS = channels
        self.RATE = rate
        self.frames = []
        self.state = 0 #0 -> recording/ 1 -> stop


        self.playing_theard = None
        self.stream = pyaudio.PyAudio().open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
        

        self.TopFrame = tk.Frame(self.main)
        self.MidFrame = tk.Frame(self.main)
        self.BottomFrame = tk.Frame(self.main)
        self.TopFrame.pack()
        self.MidFrame.pack()
        self.BottomFrame.pack()
        

        self.topic_var = tk.StringVar(self.main)
        self.topic_var.set('Pick subject')
        self.topic_var.trace('w', self.changetopic)
        self.topicPopup = tk.OptionMenu(self.TopFrame, self.topic_var, *topic_names)
        
        # sentence label
        self.sentence_title = tk.Label(self.TopFrame, text= "Sentence:")
        self.sentence_label = tk.Label(self.TopFrame, text= "------------------", wraplength=600)
        self.topicPopup.grid(row=0,column=0, padx=50, pady=5)
        self.sentence_title.grid(row=1, column = 0 , columnspan =1)
        self.sentence_label.grid(row=2, column = 0 , columnspan =1, pady=5)

        # button
        self.next = tk.Button(self.MidFrame, width=10, text='Next ->', command=lambda: self.nextSentence())
        self.pre = tk.Button(self.MidFrame, width=10, text='<- Previous', command=lambda: self.preSentence())
        self.strt_rec = tk.Button(self.MidFrame, width=10, text='Start Record', command=lambda: self.start_record())
        self.stop_rec = tk.Button(self.MidFrame, width=10, text='Stop Record', command=lambda: self.stop_record())

        self.pre.grid(row=1, column=0, pady = 5, padx = 5)
        self.next.grid(row=1, column=4, pady = 5 ,padx = 5)
        self.strt_rec.grid(row=1, column=1, pady = 5, padx = 5)
        self.stop_rec.grid(row=1, column=2, pady = 5 ,padx = 5)
        
        # status
        self.status_title = tk.Label(self.BottomFrame, text = "State:")
        self.status_label = tk.Label(self.BottomFrame, text = "")
        self.status_title.grid(row = 0, column = 0, pady = 5)
        self.status_label.grid(row = 1, column = 0, pady = 5)

        tk.mainloop()

    def changetopic(self, *args):
        self.sentence_label = tk.Label(self.TopFrame, text= "------------------", wraplength=600)

        topic_name = self.topic_var.get()
        fin = open("/".join(["data",topic_name ,"data.txt"]), "r", encoding="utf-8")
        self.url = fin.readline()
        self.sentences = fin.readlines()

        # khởi tạo array ghi lại trạng thái câu đã được gh âm?
        self.record_tags = [False for i in range(len(self.sentences))]

        
        self.cur_sentence = -1
        fin.close()

        # check/ make output
        if self.file_output:
            self.file_output.close()
        output_folder = "/".join(["output",topic_name])
        if not os.path.exists(output_folder):
            os.makedirs(output_folder,exist_ok=True)
        # mở file output
        self.file_output = open("/".join(["output",topic_name ,"output.txt"]), "w" , encoding="utf-8")
        self.status_label['text'] = 'Current Subject:  ' + topic_name
    
    def nextSentence(self):
        topic_name = self.topic_var.get()
        if topic_name == 'Pick subject':
            return
        if self.cur_sentence >= len(self.sentences) - 1: # record all sentence -> write output
            if self.file_output.closed:
                return
            self.file_output.write(self.url)

            for sentence in self.sentences:

                index = self.sentences.index(sentence)

                if self.record_tags[index]:
                    audio_name =  topic_name + "-" + str(index) + ".wav"
                else:
                    audio_name = topic_name + ""    

                self.file_output.write(audio_name + "\n")
                self.file_output.write(sentence)

            self.file_output.close()
            self.status_label['text'] = 'Finish subject: ' + topic_name
            return

        #next sentence
        self.cur_sentence += 1
        file_path = "/".join(["output",topic_name , str(self.cur_sentence) +".wav"])
        status = 'Sentence: ' + str(self.cur_sentence) + "/" + str(len(self.sentences) -1)
        if os.path.exists(file_path):
            self.record_tags[self.cur_sentence] = True
            status += " Recorded"
        self.status_label['text'] = status
        self.sentence_label['text']= self.sentences[self.cur_sentence]
    
    def preSentence(self):
        if self.topic_var.get() == 'Pick Subject':
            return

        if self.cur_sentence > 0:
            self.cur_sentence -= 1
            self.sentence_label['text']= self.sentences[self.cur_sentence]
            topic_name = self.topic_var.get()
            file_path = "/".join(["output",topic_name ,topic_name + "-" + str(self.cur_sentence) +".wav"])
            status = 'Sentence: ' + str(self.cur_sentence) + "/" + str(len(self.sentences) -1)
            if os.path.exists(file_path):
                self.record_tags[self.cur_sentence] = True
                status += " Recorded"
            self.status_label['text'] = status
            self.sentence_label['text']= self.sentences[self.cur_sentence]


    def start_record(self):
        if self.cur_sentence == -1:
            return      
        self.status_label['text'] = 'Recording line: ' + str(self.cur_sentence) + "/" + str(len(self.sentences) -1)
        self.state = 1
        self.frames = []
        stream = pyaudio.PyAudio().open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
        while self.state == 1:
            data = stream.read(self.CHUNK)
            self.frames.append(data)
            self.main.update()
        stream.close()
        # get topic name
        topic_name = self.topic_var.get()
        # open wav file
        wf = wave.open("/".join(["output",topic_name , topic_name + "-" + str(self.cur_sentence) +".wav"]), 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()

    def stop_record(self):
        if self.st == 0:
            return
        self.state = 0
        self.record_tags[self.cur_sentence] = True
        self.status_label['text'] = 'Recorded line: ' + str(self.cur_sentence) + "/" + str(len(self.sentences) -1)

topic_names = []
for (paths, dirs, files) in os.walk("data/."):
    for dirname in dirs:
        topic_names.append(dirname)

guiAUD = RecAUD(topic_names)