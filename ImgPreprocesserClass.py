import cv2 as cv
import numpy as np
import os

class ImgPreprocesser():
    def __init__(self, filePath, contrastPath, cutPath):
        self.img = cv.imread(filePath, 1)        # 每个通道8 bit位深，共三个通道
        self.contrastPath = contrastPath
        self.cutPath = cutPath

    # 获取图片高度
    def getImgHeight(self):
        return self.img.shape[0]

    #图片预处理函数
    def contrast_cut(self):
        # 图片亮度对比度调整后存入相应目录 b：亮度偏移量，c：对比度的放大倍数
        rows, cols = self.img.shape[:2]
        blank = np.zeros([rows, cols, 3], self.img.dtype)
        contrast_img = cv.addWeighted(self.img, 2.2, blank, 1 - 2.2, -250)

        cv.imwrite(self.contrastPath, contrast_img)

        # 对于对比度调整过的图片进行大小调整，并存入相应目录：裁掉上1/2,取余下部分缩小至原来1/5
        h, w = contrast_img.shape[:2]
        sub = int(h / 2)
        img_cut = contrast_img[sub:]
        new_h = int(h / (2 * 5))
        new_w = int(w / 5)
        cut_img = cv.resize(img_cut, (new_w, new_h))

        cv.imwrite(self.cutPath, cut_img)
        




