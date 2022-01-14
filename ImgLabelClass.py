import sys
import os
from math import atan, degrees
from xml.etree.ElementTree import * 
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt


""" 为后期手动标注做准备，故重写QLabel """

class ImgLabel(QLabel):
    # 重写paintEvent事件
    def paintEvent(self, event):
        super().paintEvent(event)

    # 绘制量测标注
    def drawGraphics(self, img, data, scale):
        """
        sacrum标签记录一组xmin,ymin,xmax,ymax
        (sacrum是计算必需的，如果某张图没有检测到sacrum，在计算过程中会被跳过)
        得到骶1上缘线左上端点:
                    p0=(xmin,ymin)
        得到骶1上缘线右下端点:
                    p1=(xmax,ymax)
        得到骶1上缘线中点:
                    p3=((xmin+xmax)/2,(ymin+ymax)/2)
        ----------------------------------------------------------
        femoralhead标签记录一组xmin,ymin,xmax,ymax
        (只有1个股骨的按两坐标相同处理)
        得到两个股骨中心：
                    p5=((xmin1+xmax1)/2,(ymin1+ymax1)/2)
                    p6=((xmin2+xmax2)/2,(ymin2+ymax2)/2)
        得到两个股骨中心连线的中心：
                    p2=((xmin1+xmax1+xmin2+xmax2)/4,(ymin1+ymax1+ymin2+ymax2)/4)
        """

        painter = QPainter(img)         # 创建painter对象

        # 画线
        painter.setRenderHint(QPainter.Antialiasing, True)      # 抗锯齿
        painter.setPen(QPen(Qt.blue, 1, Qt.SolidLine))
        painter.drawLine(data['p0'][0], data['p0'][1], data['p1'][0], data['p1'][1])
        painter.drawLine(data['p2'][0], data['p2'][1], data['p3'][0], data['p3'][1])
        painter.drawLine(data['p2'][0], data['p2'][1], data['p2'][0], data['p2'][1] - 600 * scale)

        k01 = (data['p0'][1] - data['p1'][1]) / (data['p0'][0] - data['p1'][0])             # 骶骨上缘p0p1的斜率
        k01d = -1 / k01                                                                     # 垂线的斜率
        p01d = (data['p3'][0] - 300 * scale, int(data['p3'][1] - 300 * scale * k01d))       # 用来画垂线的点

        painter.drawLine(data['p3'][0], data['p3'][1], p01d[0], p01d[1])

        if data['p6'] != None:
            painter.drawLine(data['p5'][0], data['p5'][1], data['p6'][0], data['p6'][1])
            
        # 画点
        painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
        painter.setBrush(Qt.red)
        painter.drawPoint(0, 0)
        painter.drawEllipse(data['p0'][0], data['p0'][1], 2, 2)
        painter.drawEllipse(data['p1'][0], data['p1'][1], 2, 2)
        painter.drawEllipse(data['p3'][0], data['p3'][1], 2, 2)
        painter.drawEllipse(data['p2'][0], data['p2'][1], 2, 2)
        if data['p6'] != None:
            painter.drawEllipse(data['p5'][0], data['p5'][1], 2, 2)
            painter.drawEllipse(data['p6'][0], data['p6'][1], 2, 2)

        painter.end()

        return img

        


    
        