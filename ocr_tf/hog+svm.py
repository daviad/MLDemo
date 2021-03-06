import cv2
import os
import numpy as np
import time

from Data_my import *

class HogSvm(object):
    def __init__(self, train_path, test_path):
        self.svm = None
        self.train_data = Data_my(train_path, self.feature_func)
        self.test_data = Data_my(test_path, self.feature_func)

    def feature_func(self, src):
        img = cv2.imread(src, cv2.COLORSPACE_GRAY)
        # Hog
        # 1.设置一些参数
        win_size = (16, 20)
        win_stride = (16, 20)
        block_size = (8, 10)
        block_stride = (4, 5)
        cell_size = (4, 5)
        n_bins = 9

        # 2.创建hog
        hog = cv2.HOGDescriptor(win_size, block_size, block_stride, cell_size, n_bins)
        hist = hog.compute(img, winStride=win_stride, padding=(0, 0))
        return hist.T.tolist()[0]  # 当矩阵是1 * n维的时候，经常会有tolist()[0]

        # img2 = np.reshape(img, [1, -1]).tolist()[0]
        # return img2

    # 创建TrainData


    # SVM
    # 创建，设置参数
    def config_svm(self):
        self.svm = cv2.ml.SVM_create()
        self.svm.setType(cv2.ml.SVM_C_SVC)
        self.svm.setKernel(cv2.ml.SVM_LINEAR)
        self.svm.setC(1)
        self.svm.setGamma(0.00055556)

    # 训练
    def train(self):
        print('create train data...')
        train_data = self.train_data.build_feature_label_nparray()
        x = np.array(train_data[0], dtype=np.float32)
        y = np.array(train_data[1], dtype=np.int32)
        print('train svm...')
        start = time.clock()
        self.config_svm()
        train_data_set = cv2.ml.TrainData_create(x, cv2.ml.ROW_SAMPLE, y)
        self.svm.train(train_data_set)
        # 保存
        self.svm.save('svm.xml')
        end = time.clock()
        print('Running time: %.2f min' % ((end - start)/60))

    def predict(self, src):
        _svm = cv2.ml.SVM_load('svm.xml')
        des = self.feature_func(src)
        des = np.array(des, dtype=np.float32)
        p = _svm.predict(des.reshape(1, -1))
        print(p[1][0][0])
        pass

    def test(self):
        print('create test data...')
        test_data = self.test_data.build_feature_label_nparray()
        x = np.array(test_data[0], dtype=np.float32)
        y = np.array(test_data[1], dtype=np.int32)
        print('test svm...')
        start = time.clock()
        self.svm = cv2.ml.SVM_load('svm.xml')
        # 预测
        p = self.svm.predict(x)
        result = p[1]
        count = 0
        for i in range(0, result.size):
            if int(result[i][0]) == y[i]:
                count = count + 1

        precise = float(count)/float(result.size)
        print('precise:', precise)
        end = time.clock()
        print('Running time: %.2f min' % ((end - start)/60.0))
        # p[1][0][0]才是label


hogSVM = HogSvm('/Users/dingxiuwei/Downloads/tf_car_license_dataset/train_images/training-set', '/Users/dingxiuwei/Downloads/tf_car_license_dataset/train_images/validation-set/')
hogSVM.train()
# hogSVM.predict('/Users/dxw/Downloads/tf_car_license_dataset/train_images/training-set/26/1509808379_364_3_new_warped3.bmp')
hogSVM.test()
