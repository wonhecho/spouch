import cv2
import sys
import numpy as np
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
import qimage2ndarray

class ShowVideo(QtCore.QObject):

    flag = 0

    camera = cv2.VideoCapture(0,cv2.CAP_DSHOW)
    camera.set(3,320)
    camera.set(4,240)
    camera2 = cv2.VideoCapture(1,cv2.CAP_DSHOW)
    camera2.set(3,320)
    camera2.set(4,240)
    camera3 = cv2.VideoCapture(2,cv2.CAP_DSHOW)
    camera3.set(3,320)
    camera3.set(4,240) 

    ret, image = camera.read()


    height, width = image.shape[:2]

    VideoSignal1 = QtCore.pyqtSignal(QtGui.QImage)
    VideoSignal2 = QtCore.pyqtSignal(QtGui.QImage)
    VideoSignal3 = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, parent=None):
        super(ShowVideo, self).__init__(parent)

    @QtCore.pyqtSlot()
    def startVideo(self):
        global frame
        fourcc = cv2.VideoWriter_fourcc(*'DIVX')
        out = cv2.VideoWriter('C:/Users/WONHEECHO/qt/save.avi', fourcc, 25.0, (320, 240))
        fgbg = cv2.createBackgroundSubtractorMOG2(varThreshold=500)
        out2 = cv2.VideoWriter('C:/Users/WONHEECHO/qt/cam1.avi', fourcc, 25.0, (320, 240))
        out3 = cv2.VideoWriter('C:/Users/WONHEECHO/qt/cam2.avi', fourcc, 25.0, (320, 240))
            

        run_video = True
        while run_video:
            
            ret, frame = self.camera.read()
            color_swapped_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            qt_image1 = QtGui.QImage(color_swapped_frame.data,
                                    self.width,
                                    self.height,
                                    color_swapped_frame.strides[0],                                  
                                    QtGui.QImage.Format_RGB888)
            fgmask = fgbg.apply(frame)
            nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(fgmask)
            for index, centroid in enumerate(centroids):
                if stats[index][0] == 0 and stats[index][1] == 0:
                    continue
                if np.any(np.isnan(centroid)):
                    continue
                x, y, width, height, area = stats[index]
                centerX, centerY = int(centroid[0]), int(centroid[1])

                if area > 200:
                    # cv2.circle(frame, (centerX, centerY), 1, (0, 255, 0), 2)
                    # cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 0, 255))
                    self.flag = 1
                
            yourQImage=qimage2ndarray.array2qimage(frame)

            self.VideoSignal1.emit(qt_image1)
            out.write(frame)
            # self.VideoSignal1.emit(yourQImage)
                 


            if self.flag:
                ret, frame = self.camera2.read()
                # if frame.isNull():
                #     print("Viewer Dropped frame!")
                
                color_swapped_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                qt_image2 = QtGui.QImage(color_swapped_frame.data,
                                    self.width,
                                    self.height,
                                    color_swapped_frame.strides[0],                                  
                                    QtGui.QImage.Format_RGB888)
                self.VideoSignal2.emit(qt_image2)
                out2.write(frame)

                
                ret2,frame2 = self.camera3.read()
                color_swapped_frame = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
                qt_image3 = QtGui.QImage(color_swapped_frame.data,
                                    self.width,
                                    self.height,
                                    color_swapped_frame.strides[0],                                  
                                    QtGui.QImage.Format_RGB888)
                self.VideoSignal3.emit(qt_image3)
                out3.write(frame2)

            if self.flag==2:
            
                out2.release()
                out3.release()
                self.flag = 0          
                
            loop = QtCore.QEventLoop()
            QtCore.QTimer.singleShot(25, loop.quit) #25 ms
            loop.exec_()

    @QtCore.pyqtSlot()
    def detect(self):
        self.flag = 2
        

class ImageViewer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ImageViewer, self).__init__(parent)
        self.image = QtGui.QImage()
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawImage(0, 0, self.image)
        self.image = QtGui.QImage()

    def initUI(self):
        self.setWindowTitle('Test')

    @QtCore.pyqtSlot(QtGui.QImage)
    def setImage(self, image):
        if image.isNull():
            print("Viewer Dropped frame!")

        self.image = image
        if image.size() != self.size():
            self.setFixedSize(image.size())
        self.update()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)


    thread = QtCore.QThread()
    thread.start()
    vid = ShowVideo()
    vid.moveToThread(thread)

    thread2 = QtCore.QThread()
    thread2.start()
    vid = ShowVideo()
    vid.moveToThread(thread2)

    image_viewer1 = ImageViewer()
    image_viewer2 = ImageViewer()
    image_viewer3 = ImageViewer()

    vid.VideoSignal1.connect(image_viewer1.setImage)
    vid.VideoSignal2.connect(image_viewer2.setImage)
    vid.VideoSignal3.connect(image_viewer3.setImage)
    

    push_button1 = QtWidgets.QPushButton('Start')
    push_button2 = QtWidgets.QPushButton('Record Stop')
    push_button1.clicked.connect(vid.startVideo)
    push_button2.clicked.connect(vid.detect)

    vertical_layout = QtWidgets.QVBoxLayout()
    horizontal_layout = QtWidgets.QHBoxLayout()
    horizontal_layout.addWidget(image_viewer1)
    horizontal_layout.addWidget(image_viewer2)
    vertical_layout.addLayout(horizontal_layout)
    vertical_layout.addWidget(image_viewer3)
    vertical_layout.addWidget(push_button1)
    vertical_layout.addWidget(push_button2)

    layout_widget = QtWidgets.QWidget()
    layout_widget.setLayout(vertical_layout)

    main_window = QtWidgets.QMainWindow()
    main_window.setCentralWidget(layout_widget)
    main_window.show()
    sys.exit(app.exec_())
