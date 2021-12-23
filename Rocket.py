from PyQt5.QtWidgets import QMainWindow , QApplication , QMessageBox , QFileDialog
from PyQt5.QtCore import  Qt
import sys , webbrowser , os
from os.path import exists
os.environ["IMAGEIO_FFMPEG_EXE"] = ("ffmpeg/bin/ffmpeg.exe")
from download_thread import *
from check_thread import *
from main import Ui_MainWindow

class UI (QMainWindow , Ui_MainWindow) :
    def __init__ (self) :
        super (UI,self).__init__()
        self.setupUi (self)
        self.download_thread = download_thread (self)
        self.check_thread = check_thread (self)
        self.download_thread.msg.connect (self.msg_show)
        self.check_thread.msg.connect (self.msg_show)
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
        self.pushButton_9.clicked.connect (self.check_thread.start) #check butt
        self.pushButton_7.clicked.connect (self.show_prof)
        self.pushButton_8.clicked.connect (self.show_git)

    def start_thread (self) :
        if self.path == None  :
            QMessageBox.information (self , "Exception ", "please Select path")
        else :
            self.download_thread.start ()

    def msg_show (self , data) :
        QMessageBox.information (self , "Alert ", data)

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