## Uses Licensed DexNet and GQCNN,  BerkeleyLabs

## Copyright(c) 2015-2017 Intel Corporation. All Rights Reserved.

###############################################
##      Open CV and Numpy integration        ##
###############################################
from __future__ import print_function
import pyrealsense2 as rs
import numpy as np
import cv2
import os
import matplotlib.pyplot as plt
import src.gqcnn_jeffbranch.gqcnn.examples.policy as find_grip_dex
import src.gqcnn_jeffbranch.gqcnn.examples.suction_policy as find_suc_dex
import ggcnn.run_ggcnn as find_grip_gg
import src.gqcnn.data.scale_depthim as scale_depthim
import threading
import Queue
from return_difference import dif




def calc_grip_gqcnn(color_frame,depth_frame,depth_im_dif = None):
    color_im, depth_im  = np.asanyarray(color_frame.get_data(),dtype='uint8'), np.asanyarray(depth_frame.get_data(), dtype ='float')
    if depth_im_dif is not None:
        depth_im = depth_im_dif
    # quick adaption to match workspace
    depth_im = depth_im[100:-100,200:-200]
    color_im = color_im[100:-100,200:-200]
    depth_im = scale_depthim.scale_depthimg_to_fit_dexnet(depth_im)
    dexnet_loadpath = '/home/jasy/FDexter/catkin_ws/src/gqcnn_jeffbranch/gqcnn/data/own/'
    dexnet_filename_color = 'color_0.png'
    dexnet_filename_depth = 'depth_0.npy'
    import png
    png.from_array(color_im,'RGB').save(dexnet_loadpath + dexnet_filename_color)
    np.save(dexnet_loadpath+dexnet_filename_depth,np.array(depth_im,dtype = 'float'))
    find_grip_dex.main()

def calc_suc_gqcnn(color_frame,depth_frame, depth_im_masked=None):
    color_im, depth_im  = np.asanyarray(color_frame.get_data(),dtype='uint8'), np.asanyarray(depth_frame.get_data(), dtype ='float')
    if depth_im_masked is not None:
        depth_im = depth_im_masked
    depth_im = scale_depthim.scale_depthimg_to_fit_dexnet(depth_im)
    dexnet_loadpath = '/home/jasy/FDexter/catkin_ws/src/gqcnn_jeffbranch/gqcnn/data/own/'
    dexnet_filename_color = 'color_0.png'
    dexnet_filename_depth = 'depth_0.npy'
    import png
    png.from_array(color_im,'RGB').save(dexnet_loadpath + dexnet_filename_color)
    np.save(dexnet_loadpath+dexnet_filename_depth,np.array(depth_im,dtype = 'float'))
    print('checkpoint1')
    find_suc_dex.main()#(color_im,depth_im)

def calc_grip_ggcnn(color_im,depth_im):
    return find_grip_gg.main(color_im,depth_im)
    f = plt.figure()
    ax = f.gca()
    f.show()
    update_ggcnn = False
    que = Queue.Queue()
        path = '../catkin_ws/src/gqcnn/data/own/realsense/'

        #keypress event handler
        keypress = cv2.waitKey(10) & 0xff
            ppx = 318.75
            ppy = 239.54
            fx = 383.1
            fy = 383.1

        elif keypress == ord('r'):
            calc_grip_gqcnn(color_frame,depth_frame)
        elif keypress == ord('t'):
            calc_suc_gqcnn(color_frame,depth_frame)


        elif keypress == ord('g'):
            color_im, depth_im  = np.asanyarray(color_frame.get_data(),dtype='uint8'), np.asanyarray(depth_frame.get_data(), dtype ='float')
            depth_im = scale_depthim.scale_depthimg_to_fit_dexnet(depth_im)
            calc_grip_ggcnn(color_im, depth_im)
            depth_im = scale_depthim.scale_depthimg_to_fit_dexnet(depth_im)
            t = threading.Thread(target= lambda q, arg1, arg2: q.put(calc_grip_ggcnn(arg1, arg2)), args=(que, color_im,depth_im))
            t.start()
            update_ggcnn = True
        elif keypress == ord('a'):
        #klappt nicht so ganz, 
            dexq = Queue.Queue()
            calc_grip_gqcnn(color_frame,depth_frame)
            calc_suc_gqcnn(color_frame,depth_frame)
            continue
            dex_grip_thr = threading.Thread(target = lambda q, arg1, arg2: q.put(calc_grip_gqcnn(arg1,arg2)), args = (dexq,color_frame,depth_frame))
            dex_suc_thr = threading.Thread(target = lambda q, arg1, arg2: q.put(calc_suc_gqcnn(arg1,arg2)), args = (dexq,color_frame,depth_frame))
            dex_suc_thr = threading.Thread(target = calc_suc_gqcnn, args = (color_frame,depth_frame))
            dexq.get()
        elif keypress == ord('d'):
            if first_pic is not None:
                color_im, depth_im  = np.asanyarray(color_frame.get_data(),dtype='uint8'), np.asanyarray(depth_frame.get_data(), dtype ='float')
                second_pic = depth_im
                depth_dif = dif(first_pic,second_pic)
                #calc_grip_gqcnn(color_frame,depth_frame,depth_dif)
                calc_suc_gqcnn(color_frame,depth_frame,depth_dif)
            color_im, depth_im  = np.asanyarray(color_frame.get_data(),dtype='uint8'), np.asanyarray(depth_frame.get_data(), dtype ='float')
            first_pic = depth_im

        if update_ggcnn:
            if not t.isAlive():
                color_im, depth_im  = np.asanyarray(color_frame.get_data(),dtype='uint8'), np.asanyarray(depth_frame.get_data(), dtype ='float')
                #returned_imgs = calc_grip_ggcnn(color_im,depth_im)
                ggcnn_return = que.get()

                if ggcnn_return != 'ups':
                    ggcnn_points = ggcnn_return['points_out']
                    ggcnn_angle = ggcnn_return['ang_out']
                    ggcnn_width = ggcnn_return['width_out']
                    f.clf()
                    find_grip_gg.plot_output(color_im, depth_im, ggcnn_points, ggcnn_angle, ggcnn_width, fig = f)
                f.canvas.draw()
                t = threading.Thread(target= lambda q, arg1, arg2: q.put(calc_grip_ggcnn(arg1, arg2)), args=(que, color_im,depth_im))
                t.start()

        # Show images
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        #cv2.imshow('RealSense', images)
        cv2.waitKey(1)
        #plt.show()
        #        play = False

#except Exception as e:
#    print(e)
#finally:
#    pipeline.stop()
