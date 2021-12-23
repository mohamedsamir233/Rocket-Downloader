from PyQt5.QtCore import  QThread , pyqtSignal 
import re , time , requests , os , traceback 
from os.path import exists
from pytube import YouTube , Playlist
from moviepy.editor import *

class download_thread (QThread) :
    msg = pyqtSignal (str)
    def __init__(self , parent) :
        QThread.__init__ (self)
        self.ui = parent

    def run (self) :
        print ("download_thread start")
        self.url = self.ui.lineEdit.text ()
        self.quality = self.ui.comboBox_2.currentText()
        self.path = self.ui.path  
        if re.search ("facebook.com.+" , self.url) or re.search ("fb.com.+" , self.url):
            self.down_fb ()

        elif re.search ("youtube.com.+" , self.url) :
            if self.ui.checkBox_2.isChecked () : 
                self.playlist_down ()
            else :
                self.down_yt ()
        
        else : 
            self.msg.emit ("please Enter Correct Url .")

    def down_yt (self) :
        print ("down_yt")
        try :
            video = YouTube(self.url , on_progress_callback= self.Handle_progress)
            video.register_on_progress_callback(self.Handle_progress)
            if self.ui.checkBox.isChecked () :
                print ("is checked - mp3")
                final_Audio = video.streams.get_by_itag(251)
                self.size = final_Audio.filesize
                file_exists = exists("{}/{}.mp3".format (self.path, final_Audio.title))
                if file_exists == True :
                    self.msg.emit ("file is exist")

                else :
                    self.ui.progressBar.setValue (20)
                    audio_name = final_Audio.download (self.path)
                    self.ui.progressBar.setValue (50)
                    base_mp3  = os.path.splitext (audio_name)[0] + ".mp3"
                    self.convert (self.path,audio_name , base_mp3)
                    os.remove (audio_name)
                    self.ui.progressBar.setValue (100)
                    self.msg.emit ("Download Completed")
                    QThread.sleep (2)
                    self.ui.progressBar.setValue (0)
            else :
                print ("Not checked - mp4")
                final_video = video.streams.get_by_resolution(self.quality)
                self.size = final_video.filesize
                file_exists = exists("{}/{}.mp4".format (self.path, final_video.title))
                if file_exists == True : 
                    self.msg.emit ("file is Exist")
                elif file_exists == False :
                    print ("False")
                    self.ui.progressBar.setValue (20)
                    final_video.download (self.path)
                    self.ui.progressBar.setValue (100)
                    self.msg.emit ("Download Completed")
                    QThread.sleep (2)
                    self.ui.progressBar.setValue (0)
            
        except Exception as err : 
            self.msg.emit (str(err))
            traceback.print_exc ()

    def Handle_progress (self , stream , chunk , bytes_remaining) : 
        total = self.size
        progress = (total - bytes_remaining)*100 / total
        self.ui.progressBar.setValue (progress)

    def playlist_down (self) : 
        try :
            playlist = Playlist(self.url)
            full_path = os.path.join (self.path , time.strftime ("playlist_%H%M%S"))
            print (full_path)
            for url , video in zip(playlist.video_urls,playlist.videos) : 
                final_video = YouTube(url , self.Handle_progress).streams.get_by_resolution (self.quality)
                self.size = final_video.filesize
                self.ui.label_12.setText (str(video.title))
                self.ui.label_13.setText (str(round(final_video.filesize/1000000,2)) + " mb")
                QThread.sleep (1)
                self.ui.progressBar.setValue (20)
                final_video.download (full_path)
                self.ui.progressBar.setValue (100)
                QThread.sleep (2)
                self.ui.progressBar.setValue (0)

            self.msg.emit ("Playlist Download Completed :)")
        except Exception as err :
            self.msg.emit (str (err))
            traceback.print_exc ()
            

    def down_fb (self) : 
        loading = 0
        print ("down_fb")
        try :
            html = requests.get(self.url)
            if self.quality == "360p" :
                print ("fb - 360p")
                sd_url = re.search ('sd_src:"(.+?)"',html.text)[1]
                file_size_request = requests.get(sd_url,stream=True)
                fsize = int(file_size_request.headers ["Content-length"])
                with open (r"{}/{}".format (self.path,time.strftime("video_%H_%M_%S.mp4")), "wb") as f :
                    for data in file_size_request.iter_content (chunk_size = 2048) :
                        f.write (data)
                        percentage = int(loading/fsize*100)
                        loading+= len(data)
                        self.ui.progressBar.setValue (percentage)

                    self.msg.emit ("Download Completed")
                    QThread.sleep (2)
                    self.ui.progressBar.setValue (0)

            else :
                print ("fb - 720p")
                hd_url = re.search ('hd_src:"(.+?)"',html.text)[1]
                file_size_request = requests.get(hd_url,stream=True)
                fsize = int(file_size_request.headers["Content-length"])
                with open (r"{}/{}".format (self.path,time.strftime("video_%H_%M_%S.mp4")), "wb") as f :
                    for data in file_size_request.iter_content (chunk_size=2048) :
                        f.write (data)
                        percentage = int(loading/fsize*100)
                        loading+= len(data)
                        self.ui.progressBar.setValue (percentage)

                    self.msg.emit ("Download Completed")
                    QThread.sleep (2)
                    self.ui.progressBar.setValue (0)
        except Exception as err : 
            self.msg.emit (str(err))
            traceback.print_exc ()


    def convert (self , path,name_bef , name_aft) :
        Audio = AudioFileClip (os.path.join(path,name_bef))
        Audio.write_audiofile (os.path.join (path,name_aft))