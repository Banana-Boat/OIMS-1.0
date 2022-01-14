import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt

class MyLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0
        self.pos0 = None
        self.pos1 = None
        self.flag = False
        self.isShow = True

    def paintEvent(self, event):
        super().paintEvent(event)

        # temp_pix = self.pixmap()
        painter_pix = QPainter(self)
        painter_pix.setPen(QPen(Qt.red, 3, Qt.SolidLine))

        if self.isShow == True:
            painter_pix.drawRect(self.x0, self.y0, abs(self.x1 - self.x0), abs(self.y1 - self.y0))

        painter_pix.end()

    def mousePressEvent(self, event):
        QLabel.mousePressEvent(self, event)
        self.flag = True
        self.isShow = True
        self.pos0 = event.globalPos()
        self.x0 = event.x()
        self.y0 = event.y()

    def mouseMoveEvent(self, event):
        QLabel.mouseMoveEvent(self, event)
        if self.flag:
            self.pos1 = event.globalPos()
            self.x1 = event.x()
            self.y1 = event.y()
            self.update()

    def mouseReleaseEvent(self, event):
        QLabel.mouseReleaseEvent(self, event)
        self.flag = False
        self.isShow = False

    def getRectGlobalPos(self):
        #返回绝对坐标
        poses = [(self.pos0.x(), self.pos0.y())]
        poses.append((self.pos1.x(), self.pos1.y()))
        return poses



class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.resize(600, 600)

        self.imgLabel = MyLabel(self)
        self.pix = QPixmap(r'./test_img/front/000000.jpg')
        self.imgLabel.setPixmap(self.pix)


if __name__ == "__main__":
    app = QApplication([])
    window = Window()
    window.show()

    sys.exit(app.exec_())