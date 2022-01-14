import sys, os, re
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from collections import OrderedDict
from math import atan, degrees
from xml.etree.ElementTree import * 
from time import time

import ui
from ui import OIMS_Ui_MainWindow
from ImgLabelClass import ImgLabel
from ImgPreprocesserClass import ImgPreprocesser


class OIMS(OIMS_Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi()

        # 全局变量定义
        self.frontParamSet = {                                      # 正面图的相关变量
            'dirPath': "",                                          # 文件夹路径
            'contrastDirPath': r'./temp_data/img/front_contrast/',  # 对比度调整后的保存路径
            'cutDirPath': r'./temp_data/img/front_cut/',            # 裁剪后保存路径
            'fileDict': OrderedDict(),                              # 文件列表，采用顺序字典，便于查找（键名为文件名，键值为字典）
            # {
            #   "isMeasured": True,                 是否已检测
            #   "scale": 1.0                        缩放比例（原图 : 控件尺寸）
            #   "originHeight": 7000,               原图高度
            #   "measureResult": {                  检测结果数据
            #       "sacrum": [],
            #       "femoralhead1": [],
            #       "femoralhead2": [] 
            #   }
            # }
            'curFilename': "",                                      # 当前打开的文件文件名
            'selectedListWidgetItem': None,                         # 当前选择的QListWidgetItem
            'scrollArea_image': self.scrollArea_front_image,        # 图片显示区控件
            'imgLabel': ImgLabel(),                                 # 图片Label
            'img': QPixmap(),                                       # 图片Image             或许可以删掉？
            'listWidget_file': self.listWidget_front_file           # 文件列表控件
        }
        self.sideParamSet = {                                   # 侧面图的相关变量
            'dirPath': "",
            'contrastDirPath': r'./temp_data/img/side_contrast/',
            'cutDirPath': r'./temp_data/img/side_cut/',
            'fileDict': OrderedDict(),
            'curFilename': "",
            'selectedListWidgetItem': None,
            'scrollArea_image': self.scrollArea_side_image,
            'imgLabel': ImgLabel(),
            'img': QPixmap(),
            'listWidget_file': self.listWidget_side_file
        }

        self.xmlData = None           # 解析后的XML数据（键名为文件名，键值为字典）,类型为OrderDict
        # {
        #   "sacrum": [],
        #   "femoralhead1": [],
        #   "femoralhead2": [] 
        # }

        self.frontListWidgetMenu = QMenu()                                          # ListWidget控件右击显示的菜单
        self.action_closefile_front = self.frontListWidgetMenu.addAction('关闭')    # 菜单项
        self.sideListWidgetMenu = QMenu()
        self.action_closefile_side = self.sideListWidgetMenu.addAction('关闭')

        self.operStack = []       # 对图片文件的操作栈

        self.ctrlPressed = False  # ctrl是否响应
        self.ctrlEsc = True
        self.frontScale = 1       # 缩放倍数    是否可以归入frontParamSet？
        self.sideScale = 1
        self.zoom2_or_shrink2 = 0
        self.BuildConnection()

    # 连接信号与槽函数
    def BuildConnection(self):
        # 菜单栏选项
        self.action_select_frontdir.triggered.connect(self.SelectFrontDir)
        self.action_select_sidedir.triggered.connect(self.SelectSideDir)
        self.action_zoom.triggered.connect(self.Zoom2)
        self.action_shrink.triggered.connect(self.Shrink2)
        self.action_full_screen.triggered.connect(self.FullScreen)

        # 顶部工具栏按钮
        self.pushButton_select_frontdir.clicked.connect(self.SelectFrontDir)
        self.pushButton_select_sidedir.clicked.connect(self.SelectSideDir)
        self.pushButton_measure.clicked.connect(self.Measure)

        # # ListWidget控件列表项
        self.listWidget_front_file.itemDoubleClicked.connect(self.DoubleClickListWidgetItem)
        self.listWidget_front_file.customContextMenuRequested.connect(self.ShowListWidgetMenu)  # 控件内右击显示菜单
        self.listWidget_side_file.itemDoubleClicked.connect(self.DoubleClickListWidgetItem)
        self.listWidget_side_file.customContextMenuRequested.connect(self.ShowListWidgetMenu)
        self.action_closefile_front.triggered.connect(self.CloseFile)                           # 右击显示的菜单中“关闭”菜单项
        self.action_closefile_side.triggered.connect(self.CloseFile)

    # 选择正面图文件夹
    def SelectFrontDir(self):
        self.SelectInputDir(self.frontParamSet)

    # 选择侧面图文件夹
    def SelectSideDir(self):
        self.SelectInputDir(self.sideParamSet)

    def Print(self):
        pass

    def Undo(self):
        pass

    def Redo(self):
        pass

    # 自动量测
    def Measure(self):
        self.xmlData = self.parseXML(r'./temp_data/xml/result.xml', self.sideParamSet)      # 解析测试XML文件
        self.calResult(self.sideParamSet)           # 根据XML数据计算
        self.ShowImage(self.sideParamSet)           # 刷新当前展示的内容
        QMessageBox.information(self, '提示', '自动量测已完成！')

    def Zoom2(self):
        pm = QPixmap('./zoom.png')  #设置放大光标
        pm1 = pm.scaled(20, 20)
        cursor = QCursor(pm1, 0, 0)
        self.setCursor(cursor)
        self.zoom2_or_shrink2 = 1

    def Shrink2(self):
        pm = QPixmap('./shrink.png')  #设置缩小光标
        pm1 = pm.scaled(20, 20)
        cursor = QCursor(pm1, 0, 0)
        self.setCursor(cursor)
        self.zoom2_or_shrink2 = -1

    # 全屏
    def FullScreen(self):
        self.showFullScreen()
        self.ctrlEsc = False
        for i in range(5):
            self.Zoom_Shrink(all=True, f=1)

        #全屏时隐藏其他部件
        self.frame.hide()
        self.frame_2.hide()
        self.groupBox.hide()
        self.groupBox_2.hide()
        self.verticalLayout_4.hide()

    def ShowHelp(self):
        pass

    # 双击ListWidget控件列表项，选择被展示的图片
    def DoubleClickListWidgetItem(self):
        if (self.sender() == self.listWidget_front_file):
            paramSet = self.frontParamSet
        else:
            paramSet = self.sideParamSet
        
        if paramSet['selectedListWidgetItem'] != None:
            oldItem = paramSet['selectedListWidgetItem']
            oldItem.setBackground(Qt.white)
        
        selectedItem = paramSet['listWidget_file'].selectedItems()[0]
        selectedItem.setBackground(Qt.lightGray)
        paramSet['selectedListWidgetItem'] = selectedItem

        filename = selectedItem.text().split(' ')[1]
        paramSet['curFilename'] = filename
        self.ShowImage(paramSet)

    # ListWidget控件列表项右击显示菜单栏
    def ShowListWidgetMenu(self):
        if (self.sender() == self.listWidget_front_file):
            if (len(self.listWidget_front_file.selectedItems()) > 0):
                self.frontListWidgetMenu.exec_(QCursor.pos())  # 菜单显示前,将它移动到鼠标点击的位置
        else:
            if (len(self.listWidget_side_file.selectedItems()) > 0):
                self.sideListWidgetMenu.exec_(QCursor.pos())

    def wheelEvent(self, event):
        if self.frontParamSet['img'].isNull():
            return
        if self.ctrlPressed:
            delta = event.angleDelta()
            oriention = delta.y() / 8
            if oriention < 0:  #向前滚轮时放大
                self.Zoom_Shrink(f=-1)
            else:  #向后滚轮时缩小
                    self.Zoom_Shrink(f=1)

    def keyReleaseEvent(self, QKeyEvent):
        self.ctrlPressed = False

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_Control:
            self.ctrlPressed = True
        if QKeyEvent.key() == Qt.Key_Escape:  #按下esc时退出当前的所有状态
            self.setCursor(Qt.ArrowCursor)
            self.zoom2_or_shrink2 = 0
            if self.ctrlEsc == False:
                self.ctrlEsc = True
                self.frame.show()
                self.frame_2.show()
                self.groupBox.show()
                self.groupBox_2.show()
                self.verticalLayout_4.show()
                self.showNormal()
                for i in range(5):
                    self.Zoom_Shrink(all=True, f=-1)

    def mousePressEvent(self, event):
        if self.zoom2_or_shrink2 == 1:
            self.Zoom_Shrink(f=1)
            return
        if self.zoom2_or_shrink2 == -1:
            self.Zoom_Shrink(f=-1)
            return

    # 根据XmlData计算关键点的坐标、骨盆参数，将计算结果存入全局变量
    def calResult(self, paramSet):
        xml = self.xmlData

        for name in list(xml.keys()):
            p0 = (xml[name]['sacrum'][0], xml[name]['sacrum'][1])
            p1 = (xml[name]['sacrum'][2], xml[name]['sacrum'][3])
            p3 = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
            p5 = ((xml[name]['femoralhead1'][0] + xml[name]['femoralhead1'][2]) / 2,
                    (xml[name]['femoralhead1'][1] + xml[name]['femoralhead1'][3]) / 2)

            if xml[name]['femoralhead2'] != None:
                p6 = ((xml[name]['femoralhead2'][0] + xml[name]['femoralhead2'][2]) / 2,
                        (xml[name]['femoralhead2'][1] + xml[name]['femoralhead2'][3]) / 2)
                p2 = ((p5[0] + p6[0]) / 2, (p5[1] + p6[1]) / 2)
            else:
                p6 = None
                p2 = p5

            ss = round(degrees(atan((p1[1] - p0[1]) / (p1[0] - p0[0]))), 2)
            pt = round(90.0 - degrees(atan((p3[1] - p2[1]) / (p3[0] - p2[0]))), 2)
            pi = ss + pt

            paramSet['fileDict'][name]['measureResult'] = {
                "p0": p0,
                "p1": p1,
                "p2": p2,
                "p3": p3,
                "p6": p6,
                "p5": p5,
                "ss": ss,
                "pt": pt,
                "pi": pi
            }

            paramSet['fileDict'][name]['isMeasured'] = True

    # 解析XML文件，传入文件路径，返回OrderDict对象
    def parseXML(self, xmlPath, paramSet):
        root = parse(xmlPath).getroot()

        res = OrderedDict()
        for img in list(root):
            name = img.find('name').text
            scale = paramSet['fileDict'][name]['scale']
            height = paramSet['fileDict'][name]['originHeight']

            sacrum_list = []
            sacrum = img.find('sacrum')
            sacrum_list.append(self.restoreX(list(sacrum)[0].text, scale))
            sacrum_list.append(self.restoreY(list(sacrum)[1].text, scale, height))
            sacrum_list.append(self.restoreX(list(sacrum)[2].text, scale))
            sacrum_list.append(self.restoreY(list(sacrum)[3].text, scale, height))

            femoralhead1_list = []
            femoralhead1 = img.find('femoralhead1')
            femoralhead1_list.append(self.restoreX(list(femoralhead1)[0].text, scale))
            femoralhead1_list.append(self.restoreY(list(femoralhead1)[1].text, scale, height))
            femoralhead1_list.append(self.restoreX(list(femoralhead1)[2].text, scale))
            femoralhead1_list.append(self.restoreY(list(femoralhead1)[3].text, scale, height))

            femoralhead2 = img.find('femoralhead2')
            if femoralhead2 != None:            # 第二个股骨头可能不存在
                femoralhead2_list = []
                femoralhead2_list.append(self.restoreX(list(femoralhead2)[0].text, scale))
                femoralhead2_list.append(self.restoreY(list(femoralhead2)[1].text, scale, height))
                femoralhead2_list.append(self.restoreX(list(femoralhead2)[2].text, scale))
                femoralhead2_list.append(self.restoreY(list(femoralhead2)[3].text, scale, height))

            res[name] = {
                "sacrum": sacrum_list,
                "femoralhead1": femoralhead1_list,
                "femoralhead2": femoralhead2_list if femoralhead2 != None else None
            }
        
        return res

    # 还原x坐标
    def restoreX(self, x, scale):
        res = int(x) * 5 * scale
        return int(res)
    
    # 还原y坐标
    def restoreY(self, y, scale, originHeight):
        res = (int(y) * 5 + originHeight / 2) * scale
        return int(res)

    # 选择导入文件夹（打开首张图片、渲染文件列表）
    def SelectInputDir(self, paramSet):
        fd = QtWidgets.QFileDialog()
        dir = fd.getExistingDirectory(caption='选择文件夹')
        if dir == '':
            return
        paramSet['dirPath'] = dir + '/'
        paramSet['fileDict'].clear()        # 清空文件列表

        if dir:
            tempFileList = []
            for filename in os.listdir(dir):
                if filename.endswith(('.bmp', '.png', '.jpg', '.jpeg')):
                    tempFileList.append(filename)

            # 进度条创建
            progress = QProgressDialog('文件夹内容加载中...', '取消', 0, len(tempFileList))
            progress.setFixedSize(350, 120)
            progress.setWindowTitle('请稍后')
            progress.setWindowFlags(Qt.WindowCloseButtonHint)
            progress.setMinimumDuration(2)
            progress.setWindowModality(Qt.WindowModal)
            i = 0

            for filename in tempFileList:
                if (~paramSet['fileDict'].__contains__(filename)):
                    # 图片预处理器
                    preprocesser = ImgPreprocesser(dir + '/' + filename,        
                                                    paramSet['contrastDirPath'] + filename,
                                                    paramSet['cutDirPath'] + filename)        
                    height = preprocesser.getImgHeight()
                    preprocesser.contrast_cut()

                    paramSet['fileDict'][filename] = {
                        "isMeasured": False,
                        "originHeight": height,
                        "scale": (paramSet['scrollArea_image'].height() - 5) / height
                    }
                    # 进度条内容修改
                    i += 1
                    progress.setValue(i)
                    if progress.wasCanceled():
                        paramSet['dirPath'] = ''
                        paramSet['fileDict'].clear()
                        return
                            
                            
        if (len(paramSet['fileDict']) > 0):         
            paramSet['curFilename'] = list(paramSet['fileDict'].keys())[0]          # 打开最后加入的图片
            self.ShowImage(paramSet)
            self.ShowFileList(paramSet)                                             # 显示文件列表

    # 展示某一个图片内容  filename：打开文件的文件名
    def ShowImage(self, paramSet):
        self.ctrlPressed = False
        filename = paramSet['curFilename']

        if paramSet['fileDict'].__contains__(filename):
            img = QPixmap(paramSet['contrastDirPath'] + filename)

            img = img.scaled(img.width() * paramSet['fileDict'][filename]['scale'],     # 将图片缩小至控件的尺寸，图片长宽比不变
                                paramSet['scrollArea_image'].height() - 5, 
                                Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

            resultTextLabel = QLabel()      # 存放量测结果的Label
            if paramSet['fileDict'][filename]['isMeasured'] == True:    # 如果该图片已被量测，则在上面绘制检测结果并在右上区域显示参数
                paramSet['imgLabel'].drawGraphics(img, paramSet['fileDict'][filename]['measureResult'], 
                                                paramSet['fileDict'][filename]['scale'])

                data = paramSet['fileDict'][filename]['measureResult']
                resultTextLabel.setText('SS = ' + str(data['ss']) +
                                                '\nPT = ' + str(data['pt']) +
                                                '\nPI = ' + str(data['pi']))
            

            paramSet['imgLabel'].setPixmap(img)
            paramSet['imgLabel'].setAlignment(Qt.AlignCenter)
            paramSet['img'] = img

            self.scrollArea_result.setWidget(resultTextLabel)       # 将量测结果的Label加载入对应区域
            paramSet['scrollArea_image'].setWidget(paramSet['imgLabel'])

    # 显示已打开的图片文件列表
    def ShowFileList(self, paramSet):
        paramSet['listWidget_file'].clear()             # 清空原有ListWiget

        if (len(paramSet['fileDict']) > 0):
            curFilename = paramSet['curFilename']
            i = 1
            for fileName in paramSet['fileDict'].keys():
                item = QListWidgetItem()

                if curFilename == fileName:             # 标识当前打开的列表项
                    paramSet['selectedListWidgetItem'] = item
                    item.setBackground(Qt.lightGray)

                item.setText(str(i) + ". " + fileName)
                item.setToolTip(paramSet['dirPath'] + fileName)

                paramSet['listWidget_file'].addItem(item)
                i = i + 1

    # 关闭单个或多个已打开的文件
    def CloseFile(self):
        if (self.sender() == self.action_closefile_front):
            paramSet = self.frontParamSet
        else:
            paramSet = self.sideParamSet

        for item in paramSet['listWidget_file'].selectedItems():
            paramSet['fileDict'].pop(item.toolTip())

        if (len(paramSet['fileDict']) > 0):             # 打开最后一张图片
            paramSet['curFilename'] = list(paramSet['fileDict'].keys())[-1]
            self.ShowImage(paramSet)
        else:
            paramSet['imgLabel'].clear()

        self.ShowFileList(paramSet)

    def Zoom_Shrink(self, all=None, f=1):  #f -1缩小 1放大
        if self.frontParamSet['img'].isNull() and self.sideParamSet['img'].isNull():  #判断当前是否有图片
            return
        if ui.now_mouse_wei == 0:  #判断光标是否在有效部件范围内
            return
        bei = 1 + 0.1 * f  #倍数
        if all:  #同时放大
            transform = QTransform()  # PyQt5
            self.frontScale *= bei
            transform.scale(self.frontScale, self.frontScale)
            img1 = self.frontParamSet['img'].transformed(transform)
            # 相应的matrix改为transform
            self.frontParamSet['imgLabel'].setPixmap(img1)
            transform = QTransform()  # PyQt5
            self.sideScale *= bei
            transform.scale(self.sideScale, self.sideScale)
            img1 = self.sideParamSet['img'].transformed(transform)
            # 相应的matrix改为transform
            self.sideParamSet['imgLabel'].setPixmap(img1)
            return

        if ui.now_mouse_wei == 1:
            transform = QTransform()  # PyQt5
            self.frontScale *= bei
            transform.scale(self.frontScale, self.frontScale)
            img1 = self.frontParamSet['img'].transformed(transform)
            # 相应的matrix改为transform
            self.frontParamSet['imgLabel'].setPixmap(img1)
        else:
            transform = QTransform()  # PyQt5
            self.sideScale *= bei
            transform.scale(self.sideScale, self.sideScale)
            img1 = self.sideParamSet['img'].transformed(transform)
            # 相应的matrix改为transform
            self.sideParamSet['imgLabel'].setPixmap(img1)
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = OIMS()
    mainWindow.show()
    sys.exit(app.exec_())