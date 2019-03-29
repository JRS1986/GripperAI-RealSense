# -*- coding: utf-8 -*-
"""
Copyright ©2017. The Regents of the University of California (Regents). All Rights Reserved.
Permission to use, copy, modify, and distribute this software and its documentation for educational,
research, and not-for-profit purposes, without fee and without a signed licensing agreement, is
hereby granted, provided that the above copyright notice, this paragraph and the following two
paragraphs appear in all copies, modifications, and distributions. Contact The Office of Technology
Licensing, UC Berkeley, 2150 Shattuck Avenue, Suite 510, Berkeley, CA 94720-1620, (510) 643-
7201, otl@berkeley.edu, http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE. THE SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED
HEREUNDER IS PROVIDED "AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE
MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.
"""
"""
Script to run saved policy output from a user run
Author: Jeff Mahler
"""
import argparse
import logging
import IPython
import numpy as np
import os
import sys
import time

from autolab_core import RigidTransform, YamlConfig

from gqcnn import RgbdImageState, ParallelJawGrasp
from gqcnn import CrossEntropyRobustGraspingPolicy
from gqcnn import Visualizer as vis

if __name__ == '__main__':
    # set up logger
    logging.getLogger().setLevel(logging.DEBUG)

    # parse args
    parser = argparse.ArgumentParser(description='Run a saved test case through a GQ-CNN policy. For debugging purposes only.')
    parser.add_argument('test_case_path', type=str, default=None, help='path to test case')
    parser.add_argument('--config_filename', type=str, default='cfg/tools/run_policy.yaml', help='path to configuration file to use')
    parser.add_argument('--output_dir', type=str, default=None, help='directory to store output')
    args = parser.parse_args()
    test_case_path = args.test_case_path
    config_filename = args.config_filename
    output_dir = args.output_dir

    # make output dir
    if output_dir is not None and not os.path.exists(output_dir):
        os.mkdir(output_dir)
    
    # make relative paths absolute
    if not os.path.isabs(config_filename):
        config_filename = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                       '..',
                                       config_filename)

    # read config
    config = YamlConfig(config_filename)
    policy_config = config['policy']
        
    # load test case
    state_path = os.path.join(test_case_path, 'state')
    action_path = os.path.join(test_case_path, 'action')
    state = RgbdImageState.load(state_path)
    original_action = ParallelJawGrasp.load(action_path)

    # init policy
    policy = CrossEntropyRobustGraspingPolicy(policy_config)

    if policy_config['vis']['input_images']:
        vis.figure()
        if state.segmask is None:
            vis.subplot(1,2,1)
            vis.imshow(state.rgbd_im.color)
            vis.title('COLOR')
            vis.subplot(1,2,2)
            vis.imshow(state.rgbd_im.depth,
                       vmin=policy_config['vis']['vmin'],
                       vmax=policy_config['vis']['vmax'])
            vis.title('DEPTH')
        else:
            vis.subplot(1,3,1)
            vis.imshow(state.rgbd_im.color)
            vis.title('COLOR')
            vis.subplot(1,3,2)
            vis.imshow(state.rgbd_im.depth,
                       vmin=policy_config['vis']['vmin'],
                       vmax=policy_config['vis']['vmax'])
            vis.title('DEPTH')
            vis.subplot(1,3,3)
            vis.imshow(state.segmask)            
            vis.title('SEGMASK')
        filename = None
        if output_dir is not None:
            filename = os.path.join(output_dir, 'input_images.png')
        vis.show(filename)    

    # query policy
    policy_start = time.time()
    action = policy(state)
    logging.info('Planning took %.3f sec' %(time.time() - policy_start))

    # vis final grasp
    if policy_config['vis']['final_grasp']:
        vis.figure(size=(10,10))
        vis.subplot(1,2,1)
        vis.imshow(state.rgbd_im.depth,
                   vmin=policy_config['vis']['vmin'],
                   vmax=policy_config['vis']['vmax'])
        vis.grasp(original_action.grasp, scale=policy_config['vis']['grasp_scale'], show_center=False, show_axis=True, color='r')
        vis.title('Original (Q=%.3f)' %(original_action.q_value))
        vis.subplot(1,2,2)
        vis.imshow(state.rgbd_im.depth,
                   vmin=policy_config['vis']['vmin'],
                   vmax=policy_config['vis']['vmax'])
        vis.grasp(action.grasp, scale=policy_config['vis']['grasp_scale'], show_center=False, show_axis=True, color='r')
        vis.title('New (Q=%.3f)' %(action.q_value))
        filename = None
        if output_dir is not None:
            filename = os.path.join(output_dir, 'planned_grasp.png')
        vis.show(filename)
    
