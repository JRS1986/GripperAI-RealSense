# File: main.py
import sys
import PySide2
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QPushButton, QToolButton, QLineEdit, QMenu, QAction, QBoxLayout, QWidget, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QMainWindow
from PySide2.QtCore import QFile, QObject, QSize
from PySide2.QtGui import QResizeEvent


import types


import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import random

class Window(QMainWindow):
    def __init__(self, ui_file, parent = None):
        super(Window, self).__init__(parent)
        ui_file = QFile(ui_file)
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()

        self.line = self.window.findChild(QLineEdit, 'lineEdit')

      #  btn = self.window.findChild(QPushButton, 'pushButton')
#        btn.clicked.connect(self.btn_handler)
        self.window.pushButton.clicked.connect(self.btn_handler)
       # tBtn = self.window.findChild(QToolButton,'toolButton')
        self.makeOptionButton()
       # self.window.resizeEvent = types.MethodType(self.window.resizeEvent, QResizeEvent)#.__get__(self.window, QMainWindow)
        self.window.show()

    def btn_handler(self):
       self.window.hide()
       cameraview = MyGui()
       cameraview.show()
       #CameraView("cameraview.ui")

    def makeOptionButton(self):
       self.menu = QMenu()
       self.testAction = QAction("Options", self)
       self.menu.addAction(self.testAction)
       self.window.toolButton.setMenu(self.menu)
       self.window.toolButton.setPopupMode(QToolButton.InstantPopup)

#class ResizeEvent(QObject):
#    def __init__(self, qresizeevent=None):
#        super(ResizeEvent, self).__init__() # <----
#        self.size = qresizeevent.size()
#        self.oldSize = qresizeevent.oldSize()


class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        #fig = Figure()
        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        #FigureCanvas.updateGeometry(self)
        self.plot()

    def plot(self):
        data = [random.random() for i in range(25)]
        ax = self.figure.add_subplot(111)
        ax.plot(data, 'r-')
        ax.set_title('PyQt Matplotlib Example')
        self.draw()


class CameraView(QMainWindow):
           def __init__(self, ui_file, parent = None):
               super(CameraView, self).__init__(parent)
               ui_file = QFile(ui_file)
               ui_file.open(QFile.ReadOnly)
               loader = QUiLoader()
               self.window = loader.load(ui_file, parent)
               ui_file.close()

             #  self.window.label.setText('Bla')
             #  self.window.label.setFrameStyle(self.window.label.Box)
               self.window.canvas.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
               self.window.plot = PlotCanvas(self.window, width=3, height=3)
               # create a layout inside the blank widget and add the matplotlib widget
               layout = QVBoxLayout(self.window.canvas)
               layout.addWidget(self.window.plot,1)
#               self.setCentralWidget(self.window)
               self.resizeEvent = self.resizeEvent # .__get__(self, QMainWindow)
               self.setCentralWidget(self.window)
               self.show()

           def resizeEvent(self, event):
                    print("resize")
                    _aspectRatio = 1.6
                    #print(event.oldSize().width(), event.size().width())
                    resizeWidth = max(self.height() * _aspectRatio, self.width())
                    resizeHeight = resizeWidth/_aspectRatio
                    #if self.width() > resizeWidth:
                    self.resize(QSize(resizeWidth,resizeHeight))
                    #elif self.height() < resizeHeight:
                     #  self.resize(QSize(resizeWidth,resizeHeight))
                    QMainWindow.resizeEvent(self, event)

                  # print('ok')
                  # QMainWindow.resizeEvent(self, event)



                  # if (contentsWidth > containerWidth ) {}
        #           void MyWindow::resizeEvent(QResizeEvent * /*resizeEvent*/)
         #          {
          #             int containerWidth = _myContainerWidget->width();
           #            int containerHeight = _myContainerWidget->height();
            #
             #          int contentsHeight = containerHeight ;
              #         int contentsWidth = containerHeight * _aspectRatio;
               #        if (contentsWidth > containerWidth ) {
                #           contentsWidth = containerWidth ;
                 #          contentsHeight = containerWidth / _aspectRatio;
                  #     }
                   #
                    #   resizeContents(contentsWidth, contentsHeight);
                     #}



           def setplot(self, PlotCanvas):
                self.window.plot

#           def plot(self):
#                   data = [random.random() for i in range(10)]
#                   ax = self.window.figure.add_subplot(111)
#                   ax.plot(data, '*-')
#                   self.window.canvas.draw()

           def btn_handler(self):
               pass


import cv2
import numpy as np
import sys
import pyrealsense2 as rs
#from PyQt5 import QtWidgets, QtCore
from PySide2 import QtCore, QtWidgets, QtGui
def test_advanced_mode():
    ## License: Apache 2.0. See LICENSE file in root directory.
    ## Copyright(c) 2017 Intel Corporation. All Rights Reserved.

    #####################################################
    ##          rs400 advanced mode tutorial           ##
    #####################################################

    # First import the library
    import time
    import json

    DS5_product_ids = ["0AD1", "0AD2", "0AD3", "0AD4", "0AD5", "0AF6", "0AFE", "0AFF", "0B00", "0B01", "0B03", "0B07"]

    def find_device_that_supports_advanced_mode() :
        ctx = rs.context()
        ds5_dev = rs.device()
        devices = ctx.query_devices();
        for dev in devices:
            if dev.supports(rs.camera_info.product_id) and str(dev.get_info(rs.camera_info.product_id)) in DS5_product_ids:
                if dev.supports(rs.camera_info.name):
                    print("Found device that supports advanced mode:", dev.get_info(rs.camera_info.name))
                return dev
        raise Exception("No device that supports advanced mode was found")

    try:
        dev = find_device_that_supports_advanced_mode()
        advnc_mode = rs.rs400_advanced_mode(dev)
        print("Advanced mode is", "enabled" if advnc_mode.is_enabled() else "disabled")

        # Loop until we successfully enable advanced mode
        while not advnc_mode.is_enabled():
            print("Trying to enable advanced mode...")
            advnc_mode.toggle_advanced_mode(True)
            # At this point the device will disconnect and re-connect.
            print("Sleeping for 5 seconds...")
            time.sleep(5)
            # The 'dev' object will become invalid and we need to initialize it again
            dev = find_device_that_supports_advanced_mode()
            advnc_mode = rs.rs400_advanced_mode(dev)
            print("Advanced mode is", "enabled" if advnc_mode.is_enabled() else "disabled")
        optionfile = "/home/jasy/FDexter/RealSense/garnichtsoschlechtesetting.json"
        #optionfile = "/home/jasy/FDexter/RealSense/holefilletc.json"
        with open(optionfile, "r") as read_file:
            print('oh')
            settings = json.load(read_file)
            #settings = read_file
            print(settings)
            #json_string = str(settings).replace('u', 'bla')
            if type(next(iter(settings))) != str:
                settings_ = {k.encode('utf-8'): v.encode("utf-8") for k, v in settings.items()}
            json_string = str(settings_).replace("'", '\"')
            advnc_mode.load_json(json_string)
       # # Get each control's current value
        #print("Depth Control: \n", advnc_mode.get_depth_control())
       # print("RSM: \n", advnc_mode.get_rsm())
       # print("RAU Support Vector Control: \n", advnc_mode.get_rau_support_vector_control())
       # print("Color Control: \n", advnc_mode.get_color_control())
       # print("RAU Thresholds Control: \n", advnc_mode.get_rau_thresholds_control())
       # print("SLO Color Thresholds Control: \n", advnc_mode.get_slo_color_thresholds_control())
       # print("SLO Penalty Control: \n", advnc_mode.get_slo_penalty_control())
       # print("HDAD: \n", advnc_mode.get_hdad())
       # print("Color Correction: \n", advnc_mode.get_color_correction())
       # print("Depth Table: \n", advnc_mode.get_depth_table())
       # print("Auto Exposure Control: \n", advnc_mode.get_ae_control())
       # print("Census: \n", advnc_mode.get_census())
    except Exception as e:
        print(e)
        pass

class videoThread(QtCore.QThread):

    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
    # Start streaming
    pip_profile = pipeline.start(config)
    vidSignal_col = QtCore.Signal(np.ndarray)
    vidSignal_dep = QtCore.Signal(np.ndarray)
    #test_advanced_mode()

    def __init__(self):
        super(videoThread,self).__init__()

    def run(self):
        play = True
        while play:
            frames = self.pipeline.wait_for_frames()
            print('ho')
            cframe = frames.get_color_frame()
            cframe = np.asanyarray(cframe.get_data())
            dframe = frames.get_depth_frame()
            dframe = np.asanyarray(dframe.get_data())
            #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # adjust width en height to the preferred values
           # image = QtGui.QImage(frame.tostring(),frame.shape[1],frame.shape[0],QtGui.QImage.Format_RGB888)
            #self.emit(QtCore.SIGNAL('newImage(QImage)'), image)
            # switch RGB and BGR for the color frame
            # and map the depth values to a RBG image
            dframe= cv2.applyColorMap(
                cv2.convertScaleAbs(dframe, alpha=0.03),
                cv2.COLORMAP_BONE)
            self.vidSignal_col.emit(cframe)
            self.vidSignal_dep.emit(dframe)
            QtCore.QThread.msleep(10)
class MyGui(QtWidgets.QMainWindow):
    """
       My gui implementation
    """
    def __init__(self):
        super(MyGui,self).__init__()
        #uic.loadUi(template,self)
        self.centW = QtWidgets.QWidget()
        self.setCentralWidget(self.centW)
        self.label = QtWidgets.QLabel()
        self.label.setText('hi')
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        #self.centralWidget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self.centW)
        layout.addWidget(self.label)
        #video stream
        self.video = videoThread()
        self.video.start()
        #self.video.vidSignal_col.connect(self.setFrame)
        self.video.vidSignal_dep.connect(self.setFrame)
        #my label is named label
#        self.label.connect(self.video,QtCore.SIGNAL('newImage(QImage)'),self.setFrame)

    @QtCore.Slot()
    def setFrame(self,frame):
        frame = np.array(frame[...,::-1])
        Qframe = QtGui.QImage(frame.data,frame.shape[1],frame.shape[0],QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(Qframe)
        self.label.setPixmap(pixmap)

    def set_frame_as_label_pixmap(self,frame,label):
        Qframe = QtGui.QImage(frame.data,frame.shape[1],frame.shape[0],QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(Qframe)
        label.setPixmap(pixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)
 #   window = CameraView("cameraview.ui")
    mygui = MyGui()
    mygui.show()
    window = Window("mainwindow.ui")
 #   windowcam = CameraView("cameraview.ui")
    #mainwindow.show()

    #ui_file = QFile("cameraview.ui")
    #cameraview = loader.load(ui_file)
   # ui_file.close()
  #  mainwindow.pushButton.clicked.connect(cameraview.show())

 #   mainwindow.show()
    sys.exit(app.exec_())
