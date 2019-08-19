# User Interface for Grasp Point Detection, using RealSense D435 depth camera and DexNet
# Using DexNet, Berkeleylab, take note of Licence

# for best results (currently) make pictures (webcam stream) from about 50-60cm straight from above the object
# config possibilitites in the gqcnn directory -> cfg/examples/ , for the normal grasp detection: policy.yaml, 
# for the suction grasp detection: suction_policy.yaml(and for the comparison two more config files, to individually enable/disable visualization steps). 
# you may change iterations, (crop)image_width/heights, gripper_width, detection distance parameters in suction config (to ignore the background, detection range scale is weird, third parameter is for the depth and it does not scale like one might expect, at least for my case)
# Author Dexter Frueh
import sys
import os
import numpy as np
import cv2
import pyrealsense2 as rs
import json
import png
import subprocess
import queue
import threading
from collections import deque
from PySide2 import QtCore, QtWidgets, QtGui
#import User Interface for MainWindow, created via QtCreator
from ui_mainwindow import Ui_MainWindow

#parameters
dexnet_loadpath = os.getcwd()+'/gqcnn_jeffbranch_adapted'

def test_advanced_mode():
    ## License: Apache 2.0. See LICENSE file in root directory.
    ## Copyright(c) 2017 Intel Corporation. All Rights Reserved.

    #####################################################
    ##          rs400 advanced mode tutorial           ##
    #####################################################

    # First import the library
    import time

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
        optionfile = os.getcwd()+"/garnichtsoschlechtesetting.json"
        #optionfile = "/home/jasy/FDexter/RealSense/garnichtsoschlechtesetting.json"
        #optionfile = "/home/jasy/FDexter/RealSense/holefilletc.json"
        with open(optionfile, "r") as read_file:
            settings = json.load(read_file)
            #settings = read_file
            print('camera configuration sucessfully loaded')
            #json_string = str(settings).replace('u', 'bla')
            if type(next(iter(settings))) != str:
                settings_ = {k.encode('utf-8'): v.encode("utf-8") for k, v in settings.items()}
                json_string = str(settings_).replace("'", '\"')
            else:
                json_string = str(settings).replace("'", '\"')
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

def preprocess_gq(color_im,depth_im,depth_im_mask = None):
    if depth_im_mask is not None:
        # to mask the relevant parts of the image, if a mask is available 
        depth_im = depth_im_dif
    #convert to pypng format
    color_im = (65535*((color_im*color_im.min()/color_im.ptp())).astype(np.uint16))
    color_im = np.reshape(color_im, (-1, color_im.shape[1]*3))
#    import matplotlib.pyplot as plt
#    plt.imshow(color_im)
#    plt.show()

    #convert depth scale
    inputresolution = 0.0001 #(meter/unit)
    outputresolution = 1 #(meter/unit)
    mind = .2
    maxd = 15
    array = depth_im[:]
    array_in_meters = array*inputresolution
    array_in_meters[array_in_meters < mind] = mind
    array_in_meters[array_in_meters > maxd] = maxd
    array_in_meters  += 0.2 #arbitrary altering the distances to compare better to the dex net trainingset, needs be undone after evaluating the quality
    array = array_in_meters/outputresolution
    depth_im = array[:]

    #save in dexnetfolder
    dexnet_filename_color = 'color_0.png'
    dexnet_filename_depth = 'depth_0.npy'
    png.from_array(color_im,'RGB').save(dexnet_loadpath+"/data/own/"+dexnet_filename_color)
    np.save(dexnet_loadpath+"/data/own/"+dexnet_filename_depth,np.array(depth_im,dtype = 'float'))
    #import src.gqcnn_jeffbranch.gqcnn.examples.policy as find_grip_dex
    #find_grip_dex.main()

def thread_dexnet(key):
    if key == 'grasp':
        dex_grasp_q  = queue.Queue()
        dex_grip_thr = threading.Thread(target = lambda q: q.put(calc_grasp()), args = (dex_grasp_q,))
        dex_grip_thr.start()
    elif key == 'suc':
        dex_suc_q  = queue.Queue()
        dex_suc_q = threading.Thread(target = lambda q: q.put(calc_suc()), args = (dex_suc_q,))
        dex_suc_q.start()
    elif key == 'both':
        dex_both_grasp_q  = queue.Queue()
        dex_both_grasp_t = threading.Thread(target = lambda q: q.put(calc_both_grasp()), args = (dex_both_grasp_q,))
        dex_both_grasp_t.start()
        dex_both_suc_q  = queue.Queue()
        dex_both_suc_t = threading.Thread(target = lambda q: q.put(calc_both_suc()), args = (dex_both_suc_q,))
        dex_both_suc_t.start()
        return dex_both_grasp_t, dex_both_grasp_q, dex_both_suc_t, dex_both_suc_q


def calc_grasp():
    python3_command = "python " + dexnet_loadpath + "/examples/policy.py"  # launch your python2 script using bash
    process = subprocess.call(python3_command.split())
    #output, error = process.communicate()  # receive output from the python2 script

def calc_suc():
    python3_command = "python " + dexnet_loadpath + "/examples/suction_policy.py"  # launch your python2 script using bash
    process = subprocess.call(python3_command.split())
    #output, error = process.communicate()

def calc_both_grasp():
    python3_command = "python " + dexnet_loadpath + "/examples/policy_both.py"  # launch your python2 script using bash
    process = subprocess.Popen(python3_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    print('output: ', output)
    output = output.decode('ascii')
    output = ''.join( c for c in output if  c not in '()' ).split(',')
    try:
        output = [float(v) for v in output]
    except:
        print('No grasp found')
        return [0,0,0,0,0,0,0]
    print(output)
    return output

def calc_both_suc():
    python3_command = "python " + dexnet_loadpath + "/examples/suction_policy_both.py"  # launch your python2 script using bash
    process = subprocess.Popen(python3_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    print('output: ', output)
    output = output.decode('ascii')
    output = ''.join( c for c in output if  c not in '()' ).split(',')
    try:
        output = [float(v) for v in output]
    except:
        print('No suction point found')
        return [0,0,0,0,0]
    return output

class Mock(object):
    ''' Mock Object (fE to handle some attributes) '''
    def __init__(self, **kwArgs):
        self.__dict__.update(kwArgs)

class depthProcessor(QtCore.QThread):
    dframeSignal = QtCore.Signal(object)

    def __init__(self):
        super(depthProcessor,self).__init__()
        self.framequeue = deque()
        self.depth_frame = None
        self.temporal = rs.temporal_filter()

    @QtCore.Slot()
    def collect(self,frame):
        print('processor meldet: collected!')
        if len(self.framequeue) > 10:
            self.framequeue.popleft()
            self.return_dframe()
        self.framequeue.append(frame)
        for fr_x in self.framequeue:
            self.depth_frame = self.temporal.process(fr_x)

    def return_dframe(self):
        self.dframeSignal.emit(self.depth_frame)
       # QtCore.QThread.msleep(30)

class dexnetThread(QtCore.QThread):
    #someSignal = QtCore.Signal(object)

    def __init__(self):
        super(dexnetThread,self).__init__()

    @QtCore.Slot()
    def run_dexnet_grasp(self):
        #color_im =self.colorlabel.image
        #depth_im =self.depthlabel.nparray
        print('gotit!') 
        python3_command = "python "+os.getcwd()+"/policy.py"  # launch your python2 script
        #python3_command = "python /home/jasy/FDexter/catkin_ws/src/gqcnn_jeffbranch/gqcnn/examples/policy.py"  
        # launch your python2 script using bash
        process= subprocess.call(python3_command.split())
        output, error = process.communicate()  # receive output from the python2 script
        print(output,error)

class videoThread(QtCore.QThread):
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)

    # Start streaming
    pip_profile = pipeline.start(config)
    vidSignal_col = QtCore.Signal(np.ndarray)
    vidSignal_dep = QtCore.Signal(np.ndarray)
    vidSignal_dep_raw = QtCore.Signal(np.ndarray)
    vidSignal_col_raw = QtCore.Signal(np.ndarray)
    #vidSignal_dep_filter = QtCore.Signal(object)
    test_advanced_mode()

    def __init__(self):
        super(videoThread, self).__init__()
        self.framequeue = deque()
        self.depth_frame = None

    def tempfilter(self,frame):
        self.temporal = rs.temporal_filter()
        if len(self.framequeue) > 10:
            self.framequeue.popleft()
        self.framequeue.append(frame)
        for fr_x in self.framequeue:
            self.depth_frame = self.temporal.process(fr_x)
    def preprocess_depth_frame(self, depth_frame):
        decimation = rs.decimation_filter()
        depth_image = decimation.process(depth_frame)
        spatial = rs.spatial_filter()
        #filtered_depth = spatial.process(depth_frame)
        spatial.set_option(rs.option.filter_magnitude, 5)
        spatial.set_option(rs.option.filter_smooth_alpha, 1)
        spatial.set_option(rs.option.filter_smooth_delta, 50)
        spatial.set_option(rs.option.holes_fill, 3)
        depth_frame = spatial.process(depth_frame)
        return depth_frame

    def run(self):
        play = True
        while play:
            frames = self.pipeline.wait_for_frames()
            cframe = frames.get_color_frame()
            cframe = np.asanyarray(cframe.get_data())
            dframe = frames.get_depth_frame()
            self.tempfilter(dframe)
            if self.depth_frame is not None:
                print('jap')
                dframe = self.depth_frame
            #preprocess images , scaling, adjusting ... 

            dframe = self.preprocess_depth_frame(dframe)
            dframe = np.asanyarray(dframe.get_data())
            #relevant_area = [top,left,bot,right]
            relevant_area = np.array([180,400,-220,-400])
            borderdist = 96
            border_delta = np.array([-borderdist,-borderdist,+borderdist,+borderdist])
            relevant_area = relevant_area + border_delta
            # I don't know why, but it needs an area dividable by 4
            relevant_area = relevant_area - np.mod(relevant_area,4)
            dframe_relevant_area = np.array(dframe[relevant_area[0]:relevant_area[2],relevant_area[1]:relevant_area[3]])
            cframe_relevant_area = np.array(cframe[relevant_area[0]:relevant_area[2],relevant_area[1]:relevant_area[3]])
            #print(cframe_relevant_area.shape, dframe_relevant_area.shape)
            #print(dframe_relevant_area.shape)
            self.vidSignal_dep_raw.emit(dframe_relevant_area)
            self.vidSignal_col_raw.emit(cframe_relevant_area)
            dframe = cv2.applyColorMap(
                cv2.convertScaleAbs(dframe, alpha=0.03),
                cv2.COLORMAP_BONE)
            dframeboundaries = cv2.rectangle(dframe, (400,180),(dframe.shape[1]-400,dframe.shape[0]-220), (255,0,0),2)
            #cframe = cframe[180:-220,400:-400]
            self.vidSignal_col.emit(cframe)
            print(dframe.shape)
            self.vidSignal_dep.emit(dframe)
            QtCore.QThread.msleep(30)

class CameraView(QtWidgets.QMainWindow):
    """
       My gui implementation
    """
    dexnetSignal = QtCore.Signal()

    def __init__(self):
        super(CameraView,self).__init__()
        self.setWindowTitle("Gripper View - Camera View")
        self.centW = QtWidgets.QWidget()
        self.centW.setObjectName("centw")
        self.centW.setStyleSheet("""
                                 QWidget#centw {
                                                 background-color:black;
                                                }
                                 QPushButton   {
                                                margin: 0;
                                                padding: 8px 8px;

                                                white-space: nowrap;
                                                text-decoration: none !important;
                                                text-transform: none;

                                                color: #CCCCCC;
                                                border: 0 none;
                                                border-radius: 4px;

                                                font-size: 13px;
                                                font-weight: 500;
                                                line-height: 1.3;

                                                color: #202129;
                                                background-color: #f2f2f2;

                                                }

                                QPushButton:hover {
                                                    color: #202129;
                                                    background-color: #e1e2e2;
                                                    opacity: 1;
                                                  }



                                                    }


""")
        #                                         color:#0091DC;
        self.setCentralWidget(self.centW)
        self.colorlabel = QtWidgets.QLabel()
        self.depthlabel = QtWidgets.QLabel()
        self.colorlabel.setMinimumSize(1, 1)
        self.depthlabel.setMinimumSize(1, 1)
        self.colorlabel.w = 1
        self.colorlabel.h = 1
        self.depthlabel.w = 1
        self.depthlabel.h = 1

        self.graspviewlabel = QtWidgets.QLabel()
        self.graspviewlabel.setMinimumSize(1, 1)


        self.run_net1_button = QtWidgets.QPushButton('find and evaluate possible grasp positions')
        self.run_net2_button = QtWidgets.QPushButton('find and evaluate possible suction positions')
        self.run_compare_button = QtWidgets.QPushButton('find best grip')

        self.run_net1_button.clicked.connect(self.run_dexnet_grasp)
        self.run_net2_button.clicked.connect(self.run_dexnet_suc)

        self.run_compare_button.clicked.connect(self.run_both_and_compare)

        spacer = QtWidgets.QSpacerItem(20,30,QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Minimum)

        self.buttons = QtWidgets.QWidget()

        self.buttonlayout = QtWidgets.QGridLayout(self.buttons)
        self.buttonlayout.addWidget(self.run_net1_button,0,0)
        self.buttonlayout.addWidget(self.run_net2_button,0,1)
        self.buttonlayout.addWidget(self.run_compare_button,0,2)

        self.layout = QtWidgets.QGridLayout(self.centW)
        #self.showcolorframe = True # False
        self.showcolorframe = True
        self.showgraspsample = False
        self.resized = False
        self.checkqueue_gr = False
        self.checkqueue_suc = False
        self.grasp_drawn = False
        self.suc_drawn = False
        self.statustext_drawn = False

        if self.showcolorframe:
            self.layout.addWidget(self.colorlabel, 0, 0)
            self.layout.addWidget(self.depthlabel, 0, 1)
            self.layout.addWidget(self.buttons, 1, 0, 1, 2)
            self.layout.addWidget(self.graspviewlabel, 2,1,2,2)
        else:
            self.layout.addWidget(self.depthlabel, 0, 0)
            self.layout.addWidget(self.buttons, 1, 0)
            self.layout.addWidget(self.graspviewlabel, 2,0)

        self.depthlabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.colorlabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.graspviewlabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.graspviewlabel.setAlignment(QtCore.Qt.AlignCenter)
        self.buttons.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

        #video stream
        self.video = videoThread()
        self.video.start()
        self.video.vidSignal_col.connect(lambda f: self.set_frame_to_label(f,self.colorlabel,self.colorlabel.w, self.colorlabel.h))
        self.video.vidSignal_dep.connect(lambda f: self.set_frame_to_label(f,self.depthlabel,self.depthlabel.w, self.depthlabel.h))
        self.video.vidSignal_dep_raw.connect(self.collect_dframe_nparray)
        self.video.vidSignal_col_raw.connect(self.collect_cframe_nparray)
        self.video.vidSignal_dep.connect(self.check_queue)

        #self.dexnet = dexnetThread()
        #self.dexnet.start()
        #self.dexnetSignal.connect(self.dexnet.run_dexnet_grasp)

    def collect_dframe_nparray(self, dframe):
        self.depthlabel.nparray = dframe

    def collect_cframe_nparray(self, cframe):
        self.colorlabel.nparray = cframe

    def set_graspviewpixmap(self, frame, samesizelabel):
        label = self.graspviewlabel
        label.image = frame
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        frame = cv2.applyColorMap(
                cv2.convertScaleAbs(frame, alpha=.03),
                cv2.COLORMAP_BONE)
        Qframe = QtGui.QImage(frame.data,frame.shape[1],frame.shape[0],QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(Qframe)
        label.ori_pixmap = pixmap
        pixmap = pixmap.scaled(samesizelabel.size(),QtCore.Qt.KeepAspectRatio)
        label.setPixmap(pixmap)
        self.showgraspsample = True
        newsize=QtCore.QSize(self.size())
        oldsize=QtCore.QSize(self.size())
        myResizeEvent = QtGui.QResizeEvent(newsize,oldsize)
        QtCore.QCoreApplication.postEvent(self, myResizeEvent)

    def run_both_and_compare(self,dframe):
        if self.checkqueue_gr or self.checkqueue_suc:
            print('passing')
            return
        if hasattr(self, 'pose_suc'):
            del self.pose_suc
            self.suc_drawn = False
        if hasattr(self, 'pose_grasp'):
            del self.pose_grasp 
            self.grasp_drawn = False
        config_grasp = os.getcwd() + '/policy_both.yaml'
        config_suc = os.getcwd()+'/suction_policy_both.yaml'
        #config_grasp = '/home/jasy/FDexter/catkin_ws/src/gqcnn_jeffbranch/gqcnn/cfg/examples/policy_both.yaml'
        #config_suc = '/home/jasy/FDexter/catkin_ws/src/gqcnn_jeffbranch/gqcnn/cfg/examples/suction_policy_both.yaml'
        color_im = self.colorlabel.nparray
        depth_im = self.depthlabel.nparray
        print(depth_im.shape)
        import ruamel.yaml
        yaml = ruamel.yaml.YAML()
        with open(config_grasp) as fp:
            data = yaml.load(fp)
            print(data)
        with open(config_suc) as fp:
            data = yaml.load(fp)
            print(data)
        print(data['detection'])
        data['detection']['image_width'] = depth_im.shape[1]
        data['detection']['image_height'] = depth_im.shape[0]
        #with open(config_suc, 'w') as fp:
        #    yaml.dump(data, fp)
        self.set_graspviewpixmap(depth_im,self.depthlabel)
        preprocess_gq(color_im, depth_im)
        self.t_gr, self.q_gr, self.t_suc, self.q_suc = thread_dexnet('both')

        self.checkqueue_gr = True
        self.checkqueue_suc = True

    def check_queue(self,_):
        if hasattr(self,'checkqueue_suc'):
            if self.checkqueue_suc == True and hasattr(self,'q_gr'):
                if self.t_suc.is_alive() == False:
                    print('vv')
                    pose_suc = self.q_suc.get()
                    self.pose_suc = Mock()
                    self.pose_suc.q = pose_suc[0]
                    self.pose_suc.x = pose_suc[1]
                    self.pose_suc.y = pose_suc[2]
                    self.checkqueue_suc = False
                    print('youhou! 2')
        if hasattr(self,'checkqueue_gr'):
            if self.checkqueue_gr == True and hasattr(self,'q_gr'):
                if self.t_gr.is_alive() == False:
                    print('vv')
                    pose_grasp = self.q_gr.get()
                    self.pose_grasp = Mock()
                    self.pose_grasp.q = pose_grasp[0]
                    self.pose_grasp.x = pose_grasp[1]
                    self.pose_grasp.y = pose_grasp[2]
                    self.pose_grasp.x2 = pose_grasp[3]
                    self.pose_grasp.y2 = pose_grasp[4]
                    self.pose_grasp.vector = [pose_grasp[3]-pose_grasp[1],pose_grasp[4]-pose_grasp[2]]
                    self.checkqueue_gr = False
                    print('youhou!')

    def run_dexnet_suc(self,dframe):
        color_im =self.colorlabel.nparray
        depth_im =self.depthlabel.nparray
        preprocess_gq(color_im, depth_im)
        thread_dexnet('suc')

    def run_dexnet_grasp(self,dframe):
        color_im =self.colorlabel.nparray
        depth_im =self.depthlabel.nparray
        preprocess_gq(color_im, depth_im)
        thread_dexnet('grasp')

        #self.dexnetSignal.emit()
#/home/jasy/FDexter/catkin_ws/src/gqcnn_jeffbranch/gqcnn/examples/policy.py
        #python3_command = "python /home/jasy/FDexter/catkin_ws/src/gqcnn_jeffbranch/gqcnn/examples/policy.py"  # launch your python2 script using bash
        #process= subprocess.call(python3_command.split())
        # process = subprocess.Popen(python3_command.split(), stdout=subprocess.PIPE)
        #output, error = process.communicate()  # receive output from the python2 script
        #print(output,error)

    def resizeEvent(self, event):
             print("resize")
             if hasattr(self,'counter'):
                if self.counter == 2:
                    self.resized = True
                self.counter += 1
             else:
                 self.counter = 0
                 self.resized = False
             if hasattr(self.depthlabel,'initsize'):
                 aspectratio = self.depthlabel.w/self.depthlabel.h
                 if self.showcolorframe == True:
                     self.layout.setRowMinimumHeight(0,self.buttons.width()/2/aspectratio)
                     if self.showgraspsample == True:
                        self.layout.setRowMinimumHeight(2,self.buttons.width()/2/aspectratio)
                 else:
                     self.layout.setRowMinimumHeight(0,self.buttons.width()/aspectratio)
                     if self.showgraspsample == True:
                        self.layout.setRowMinimumHeight(2,self.buttons.width()/aspectratio)
             QtWidgets.QMainWindow.resizeEvent(self, event)

    @QtCore.Slot()
    def setFrame(self,frame):
        frame = np.array(frame[...,::-1])
        Qframe = QtGui.QImage(frame.data,frame.shape[1],frame.shape[0],QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(Qframe)
        self.label.setPixmap(pixmap)

    def set_frame_to_label(self,frame,label, w = None, h= None):
        label.image = frame
        frame = np.array(frame[...,::-1])
        Qframe = QtGui.QImage(frame.data,frame.shape[1],frame.shape[0],QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(Qframe)
        if not hasattr(label, 'initsize'):
            label.initsize = True
            label.w = frame.shape[1]
            label.h = frame.shape[0]
        if self.resized == False:
            label.resize(label.w/2,label.h/2)
            self.resize(self.layout.sizeHint())
            # v Hacky workaround to trigger resizeevent at startup and trigger correct formatting...
            newsize=QtCore.QSize(self.size())
            oldsize=QtCore.QSize(self.size())
            myResizeEvent = QtGui.QResizeEvent(newsize,oldsize)
            QtCore.QCoreApplication.postEvent(self, myResizeEvent)
        pixmap = pixmap.scaled(label.size(),QtCore.Qt.KeepAspectRatio)
        label.setPixmap(pixmap)
        m_paintFlags = QtGui.QPainter.RenderHints(
                                            QtGui.QPainter.TextAntialiasing)
        if self.showgraspsample:
            gvpixmap = self.graspviewlabel.ori_pixmap
            gvpixmap = gvpixmap.scaled(label.size(),QtCore.Qt.KeepAspectRatio,transformMode=QtCore.Qt.SmoothTransformation)
            self.graspviewlabel.setPixmap(gvpixmap)

        if not self.statustext_drawn and self.showgraspsample==True:
            self.statustext_drawn = True
            gvpixmap = self.graspviewlabel.ori_pixmap
            #gvpixmap = self.graspviewlabel.pixmap()
            painter = QtGui.QPainter(gvpixmap)
            painter.setRenderHints(m_paintFlags)
            painter.setPen(QtGui.QColor("black"))
            painter.setBrush(QtGui.QColor("black"))
            if hasattr(self,'pose_grasp') and hasattr(self,'pose_suc') and self.showgraspsample == True:
                painter.drawText(10,20, "Evaluated Gripping Points")
            else:
                painter.drawText(10,20, "Calculating Best Grip")
            self.graspviewlabel.ori_pixmap = gvpixmap
            gvpixmap = gvpixmap.scaled(label.size(),QtCore.Qt.KeepAspectRatio,transformMode=QtCore.Qt.SmoothTransformation)
            self.graspviewlabel.setPixmap(gvpixmap)
            painter.end()
        if not self.grasp_drawn and hasattr(self,'pose_grasp') and self.showgraspsample == True:
            self.grasp_drawn = True
            gvpixmap = self.graspviewlabel.ori_pixmap
            #gvpixmap = self.graspviewlabel.pixmap()
            painter = QtGui.QPainter(gvpixmap)
            painter.setRenderHints(m_paintFlags)
            painter.setPen(QtGui.QColor(20,20,200))
            painter.setBrush(QtGui.QColor(20,20,200))
            print(self.pose_grasp.x, self.pose_grasp.y)
            painter.drawText(self.pose_grasp.x + 20, self.pose_grasp.y, "parallel_grasp: " + str(self.pose_grasp.q))
            painter.drawLine(self.pose_grasp.x2+self.pose_grasp.vector[0]*0.08 ,self.pose_grasp.y2+self.pose_grasp.vector[1]*0.08, self.pose_grasp.x-self.pose_grasp.vector[0]*0.08, self.pose_grasp.y - self.pose_grasp.vector[1]*0.08)
            painter.drawEllipse(self.pose_grasp.x2+self.pose_grasp.vector[0]*0.08-5,self.pose_grasp.y2+self.pose_grasp.vector[1]*0.08-5,10,10)
            painter.drawEllipse(self.pose_grasp.x-self.pose_grasp.vector[0]*0.08-5,self.pose_grasp.y - self.pose_grasp.vector[1]*0.08-5,10,10)
           # gvpixmap = QtGui.QPixmap.fromImage(gvpixmap)
           # gvpixmap = gvpixmap.scaled(self.graspviewlabel.size(),QtCore.Qt.KeepAspectRatio)
            self.graspviewlabel.ori_pixmap = gvpixmap
            gvpixmap = gvpixmap.scaled(label.size(),QtCore.Qt.KeepAspectRatio,transformMode=QtCore.Qt.SmoothTransformation)
            self.graspviewlabel.setPixmap(gvpixmap)
            #self.graspviewlabel.setPixmap(QtGui.QPixmap.fromImage((gvpixmap))
            painter.end()
        if not self.suc_drawn and hasattr(self,'pose_suc') and self.showgraspsample == True:
            self.suc_drawn = True
            print('has grasp attrib and graspimage ---------------------------------------------')
            gvpixmap = self.graspviewlabel.ori_pixmap
            painter = QtGui.QPainter(gvpixmap)
            painter.setRenderHints(m_paintFlags)
            painter.setPen(QtGui.QColor(100,20,200))
            painter.setBrush(QtGui.QColor(100,20,200))
            painter.drawEllipse(self.pose_suc.x-5, self.pose_suc.y-5, 10, 10)
            painter.drawText(self.pose_suc.x + 20, self.pose_suc.y, "suction_grasp: "+str(self.pose_suc.q))
            print(self.pose_suc.x, self.pose_suc.y)

            self.graspviewlabel.ori_pixmap = gvpixmap
            gvpixmap = gvpixmap.scaled(self.graspviewlabel.size(),QtCore.Qt.KeepAspectRatio)
            self.graspviewlabel.setPixmap(gvpixmap)
            painter.end()
        if self.suc_drawn and self.grasp_drawn:
            self.suc_drawn= False
            self.grasp_drawn= False
            del self.pose_suc
            del self.pose_grasp 


        #label.setPixmap(pixmap)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent = None): #, ui_file, parent = None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.btn_handler)
    def btn_handler(self):
       self.close()
       self.camview = CameraView()
       self.camview.show()

    def makeOptionButton(self):
       self.menu = QMenu()
       self.testAction = QAction("Options", self)
       self.menu.addAction(self.testAction)
       self.toolButton.setMenu(self.menu)
       self.toolButton.setPopupMode(QToolButton.InstantPopup)

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
    app = QtWidgets.QApplication(sys.argv)
    # to display start Window
    #window = MainWindow()
    print('hi')
    #to display the CameraView right away
    window = CameraView()
    window.show()
    sys.exit(app.exec_())
