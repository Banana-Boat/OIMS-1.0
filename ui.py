from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from ui_base import Ui_MainWindow

now_mouse_wei = 0  #光标位置 1左图像显示框 2右图像显示框 0其他区域


class MyQscrollArea(QScrollArea):
    def __init__(self, parent=None, num=None):
        super().__init__(parent)
        self.num = num

    def enterEvent(self, event):
        #print(self.num)
        global now_mouse_wei
        now_mouse_wei = self.num

    def leaveEvent(self, event):
        #print("leave")
        global now_mouse_wei
        now_mouse_wei = 0


class OIMS_Ui_MainWindow(QMainWindow, Ui_MainWindow):
    def setupUi(self):
        super().setupUi(self)

        self.scrollArea_front_image = MyQscrollArea(self.centralwidget, 1)

        self.scrollArea_front_image.setStyleSheet("")
        self.scrollArea_front_image.setWidgetResizable(True)
        self.scrollArea_front_image.setObjectName("scrollArea_front_image")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 455, 719))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea_front_image.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout_7.addWidget(self.scrollArea_front_image)

        self.scrollArea_side_image = MyQscrollArea(self.centralwidget, 2)

        self.scrollArea_side_image.setWidgetResizable(True)
        self.scrollArea_side_image.setObjectName("scrollArea_side_image")
        self.scrollAreaWidgetContents_3 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_3.setGeometry(QtCore.QRect(0, 0, 455, 719))
        self.scrollAreaWidgetContents_3.setObjectName("scrollAreaWidgetContents_3")
        self.scrollArea_side_image.setWidget(self.scrollAreaWidgetContents_3)
        self.horizontalLayout_7.addWidget(self.scrollArea_side_image)