import cv2
import numpy as np
import sys
import pyrealsense2 as rs
#from PyQt5 import QtWidgets, QtCore
from PySide2 import QtCore, QtWidgets, QtGui
import threading

class ShowVideo(QtCore.QObject):
    ##camera = cv2.VideoCapture(camera_port)
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
    # Start streaming
    pip_profile = pipeline.start(config)
    # not implemented here : test_advanced_mode()
    videoSignal = QtCore.Signal(np.ndarray)

    def __init__(self, parent = None):
        super(ShowVideo, self).__init__(parent)


    @QtCore.Slot()
    def startVideo(self):
        run_video = True

        while run_video:
            self.frames = self.pipeline.wait_for_frames()
            color_frame = self.frames.get_color_frame()
            image = np.asanyarray(color_frame.get_data())

            # OpenCV stores data in Blue-Green-Red format. 
            # Qt stores data in Red-Green-Blue format. The cmd swaps to
            # the right format
            color_swapped_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
       #     cv2.imshow('firstframe', color_swapped_image)

            # Need to make a QImage.
            qt_image = QtGui.QImage(color_swapped_image.tostring(), color_swapped_image.shape[1], color_swapped_image.shape[0],color_swapped_image.strides[0], QtGui.QImage.Format_RGB888)#, 
                                   # color_swapped_image.cols, 
                                   # color_swapped_image.rows,
                                   # color_swapped_image.step,
                                   # QtGui.QImage.Format_RGB888)

            qt_image.ndarray = color_swapped_image
            self.videoSignal.emit(qt_image)
            #run_video = False

class ImageViewer(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(ImageViewer, self).__init__(parent)
        self.image = QtGui.QImage()
        self.image_fr = QtWidgets.QLabel()

    def paintEvent(self, event):
        #painter = QtGui.QPainter()
        #painter.drawImage(0,0, self.image)
        pix = QtGui.QPixmap.fromImage(self.image)
        self.image_fr.setPixmap(pix)


    def initUI(self):
        self.setGeometry(600, 500, 300, 220)
        self.setWindowTitle('Test')
        self.show(image)

    @QtCore.Slot(QtGui.QImage)
    def setImage(self, image):
        self.image = image
        self.paintEvent(0)

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    # let's make instances of our two custom classes that we created
    image_viewer = ImageViewer()
    image_viewer.show()
    #vid = ShowVideo()
    # Now let's connect the signal/slots of the two instances of
    # our custom classes together
    #vid.videoSignal.connect(image_viewer.setImage)
    #vid.startVideo()
    # I'm adding a button for ease to start the actual video capture
    # You could also use timers to start it automatically?
    #push_button = QtWidgets.QPushButton("Start")

    # need to connect the button to our `startVideo` command
    #push_button.clicked.connect(vid.startVideo)

    # Ok, so we made a button, but how do we get it to pop up?
    # Use a layout
    #vertical_layout = QtWidgets.QVBoxLayout()

    # need to add the two widgets that we want, ImageViewer 
    # and QPushButton to the layout that we just made
    #vertical_layout.addWidget(image_viewer)
    #vertical_layout.addWidget(push_button)

    # Qt is a little odd in the fact that we need a widget
    # to set the layout to. Can't just set the QMainWindow 
    # layout directly. So I create a "LayoutWidget" 
    # here and set the layout to the layout we just made
    #layout_widget = QtWidgets.QWidget()
    #layout_widget.setLayout(vertical_layout)

    # Now let's create our main window, and set the central widget to 
    # the layout WIDGET that we just created
#    main_window = QtWidgets.QMainWindow()
#    main_window.setCentralWidget(image_viewer)

    # make sure to call the show method on QMainWindow if you want to 
    # see anything
#    main_window.show()

    # and this is the magic sauce that adds in a loop
    sys.exit(app.exec_())
