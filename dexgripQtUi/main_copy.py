# File: main.py
import sys
import PySide2
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QPushButton, QToolButton, QLineEdit, QMenu, QAction, QBoxLayout, QWidget, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QMainWindow
from PySide2.QtCore import QFile, QObject
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
       cameraview = CameraView("cameraview.ui")

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

               self.window.label.setText('Bla')
               self.window.label.setFrameStyle(self.window.label.Box)
               self.window.canvas.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
               self.window.plot = PlotCanvas(self.window, width=3, height=3)
               # create a layout inside the blank widget and add the matplotlib widget
               #layout = QVBoxLayout(self.window.canvas)
               #layout.addWidget(self.window.plot,1)
#               self.setCentralWidget(self.window)
              # self.resizeEvent = self.resizeEvent # .__get__(self, QMainWindow)
               self.setCentralWidget(self.window)
               self.show()

          # def resizeEvent(self,event):
           #        print("resize")
           #        QMainWindow.resizeEvent(self, event)
                   # _aspectRatio = 1.6
                   # resizeWidth = self.height() * _aspectRatio
                   # resizeHeight = self.height()
                   # if self.width() > resizeWidth+0.1:
                   #    self.resize(QSize(resizeWidth,resizeHeight))
                   # elif self.width() < resizeWidth-0.1:
                   #    self.resize(QSize(resizeWidth,resizeHeight))
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





           def plot(self):
                   data = [random.random() for i in range(10)]
                   ax = self.window.figure.add_subplot(111)
                   ax.plot(data, '*-')
                   self.window.canvas.draw()

           def btn_handler(self):
               pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
 #   window = CameraView("cameraview.ui")
    window = Window("mainwindow.ui")
 #   windowcam = CameraView("cameraview.ui")
    #mainwindow.show()

    #ui_file = QFile("cameraview.ui")
    #cameraview = loader.load(ui_file)
   # ui_file.close()
  #  mainwindow.pushButton.clicked.connect(cameraview.show())

 #   mainwindow.show()

    sys.exit(app.exec_())
