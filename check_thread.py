from PyQt5.QtCore import QThread, pyqtSignal
from pytube import *
import traceback

class check_thread (QThread) :
    msg = pyqtSignal (str)
    def __init__ (self , parent) :
        QThread.__init__(self)
        self.ui = parent

    def run (self) :
        print ("check_thread start")
        self.url = self.ui.lineEdit.text ()
        self.quality = self.ui.comboBox_2.currentText ()
        try :
            video = YouTube(self.url)
            if self.ui.checkBox.isChecked () :
                final_Audio = video.streams.get_by_itag(251)
                self.ui.label_12.setText (str(final_Audio.title))
                self.ui.label_13.setText (str(round(final_Audio.filesize/1000000,2)) + " mb")
            else :
                final_video = video.streams.get_by_resolution(self.quality)
                self.ui.label_12.setText (str(final_video.title))
                self.ui.label_13.setText (str(round(final_video.filesize/1000000,2)) + " mb")
        except Exception as err :
            self.msg.emit (str(err))
            traceback.print_exc ()