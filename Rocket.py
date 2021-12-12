from PyQt5.QtWidgets import QMainWindow , QApplication , QMessageBox , QFileDialog
from PyQt5.QtCore import  QThread , pyqtSignal , Qt
import sys , re , time , requests , os , traceback , webbrowser 
from os.path import exists
from pytube import YouTube
from main import Ui_MainWindow
os.environ["IMAGEIO_FFMPEG_EXE"] = ("ffmpeg/bin/ffmpeg.exe")
from moviepy.editor import *

class thread (QThread) :
    msg = pyqtSignal (str)
    def __init__(self , parent) :
        print ("init start")
        QThread.__init__ (self)
        self.ui = parent

    def run (self) :
        print ("thread Start ")
        self.url = self.ui.lineEdit.text ()
        self.quality = self.ui.comboBox_2.currentText()
        self.path = self.ui.path  
        if re.search ("facebook.com" , self.url) or re.search ("fb.com" , self.url):
            self.down_fb ()
        elif re.search ("youtu", self.url) :
            self.down_yt ()
        else : 
            self.msg.emit ("please Enter Correct Url .")

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

    def down_yt (self) :
        print ("down_yt")
        try :
            video = YouTube(self.url)
            if self.ui.checkBox.isChecked () :
                print ("is checked - mp3")
                final_Audio = video.streams.get_by_itag(251)
                self.ui.label_12.setText (str(final_Audio.title))
                self.ui.label_13.setText (str(round(final_Audio.filesize/1000000,2)) + " mb")
                file_exists = exists("{}/{}.mp3".format (self.path, final_Audio.title))
                if file_exists == True :
                    print ("file is exist")
                    self.msg.emit ("file is exist")

                elif file_exists == False :
                    audio_name = final_Audio.download (self.path)
                    self.ui.progressBar.setValue (50)
                    base_mp3  = os.path.splitext (audio_name)[0] + ".mp3"
                    self.convert (self.path,audio_name , base_mp3)
                    os.remove (audio_name)
                    self.ui.progressBar.setValue (100)
                    self.msg.emit ("Download Completed")
                    QThread.sleep (3)
                    self.ui.progressBar.setValue (0)
            else :
                print ("Not checked - mp4")
                final_video = video.streams.get_by_resolution(self.quality)
                self.ui.label_12.setText (str(final_video.title))
                self.ui.label_13.setText (str(round(final_video.filesize/1000000,2)) + " mb")
                QThread.sleep (1)
                file_exists = exists("{}/{}.mp4".format (self.path, final_video.title))
                if file_exists == True : 
                    self.msg.emit ("file is Exist")
                elif file_exists == False :
                    print ("False")
                    self.ui.progressBar.setValue (20)
                    final_video.download (self.path)
                    self.ui.progressBar.setValue (100)
                    self.msg.emit ("Download Completed")
                    QThread.sleep (3)
                    self.ui.progressBar.setValue (0)
            
        except Exception as err : 
            self.msg.emit (str(err))
            traceback.print_exc ()


    def convert (self , path,name_bef , name_aft) :
        Audio = AudioFileClip (os.path.join(path,name_bef))
        Audio.write_audiofile (os.path.join (path,name_aft))

class UI (QMainWindow , Ui_MainWindow) :
    def __init__ (self) :
        super (UI,self).__init__()
        self.setupUi (self)
        self.thread = thread (self)
        self.thread.msg.connect (self.msg_show)
        self.status = 0
        self.path = None
        self.Buttons ()
        self.UI ()
        self.show ()

        def moveWindow(event): 
            if  self.status == 1 :
                self.maximize_restore()
            if event.buttons() == Qt.LeftButton :
                self.move(self.pos()+event.globalPos()-self.dragPos)
                self.dragPos = event.globalPos()
                event.accept()
        self.frame_9.mouseMoveEvent = moveWindow

    def mousePressEvent(self,event):
        self.dragPos = event.globalPos()

    def UI (self) :
        self.setFixedSize (1100,800)
     #   self.tabWidget.tabBar().setVisible(False)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def Buttons (self) :
        self.pushButton_4.clicked.connect (self.close)
        self.pushButton_5.clicked.connect (self.maximize)
        self.pushButton_6.clicked.connect (self.showMinimized )
        self.pushButton_2.clicked.connect (self.browse)
        self.pushButton.clicked.connect (self.start_thread) #download butt
        self.pushButton_7.clicked.connect (self.show_prof)
        self.pushButton_8.clicked.connect (self.show_git)

    def start_thread (self) :
        if self.path == None  :
            QMessageBox.information (self , "Exception ", "please Select path")
        else :
            self.thread.start ()

    def msg_show (self , data) :
        QMessageBox.information (self , "Exception ", data)

    def show_prof (self) :
        webbrowser.open("https://www.facebook.com/mohamedsamir233/")

    def show_git (self) :
        webbrowser.open("https://github.com/mohamedsamir234")

    def browse (self) : 
        self.path = QFileDialog.getExistingDirectory (self,"Select Folder")
        self.lineEdit_2.setText (self.path)

    def maximize (self) :
        if self.isMaximized () :
            self.showNormal ()
        else :
            self.showMaximized () 

app = QApplication(sys.argv)
window = UI ()
app.exec_()