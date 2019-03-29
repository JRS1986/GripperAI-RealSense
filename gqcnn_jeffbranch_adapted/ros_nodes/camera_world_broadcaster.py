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
#!/usr/bin/env python
import rospy
import tf2_ros
from geometry_msgs.msg import TransformStamped
from autolab_core import RigidTransform

if __name__ == '__main__':
	# initialize ROS node
	rospy.init_node('camera_to_world_tf_broadcaster')
	rospy.loginfo('Camera to World TF Broadcaster Initialized')

	# load RigidTransform
	rospy.loginfo('Loading T_camera_world')
	T_camera_world = RigidTransform.load('/home/autolab/Public/alan/calib/primesense_overhead/primesense_overhead_to_world.tf')

    # create broadcaster
	transform_broadcaster = tf2_ros.TransformBroadcaster()

    # create Stamped ROS Transform
	camera_world_transform = TransformStamped()
	camera_world_transform.header.stamp = rospy.Time.now()
	camera_world_transform.header.frame_id = 'primesense_overhead_rgb_optical_frame'
	camera_world_transform.child_frame_id = 'world'
       
	camera_world_transform.transform.translation.x = T_camera_world.translation[0]
	camera_world_transform.transform.translation.y = T_camera_world.translation[1]
	camera_world_transform.transform.translation.z = T_camera_world.translation[2]

	rospy.loginfo('X: ' + str(T_camera_world.translation[0]) + 'Y: ' + str(T_camera_world.translation[1]) + 'Z: ' + str(T_camera_world.translation[2]))
       
	q = T_camera_world.quaternion
	camera_world_transform.transform.rotation.x = q[1]
	camera_world_transform.transform.rotation.y = q[2]
	camera_world_transform.transform.rotation.z = q[3]
	camera_world_transform.transform.rotation.w = q[0]

	rospy.loginfo('qX: ' + str(q[1]) + 'qY: ' + str(q[2]) + 'qZ: ' + str(q[3]) + 'qW: ' + str(q[0]))

    # broadcast
	rospy.loginfo('Beginning Broadcast')
	while True:
		transform_broadcaster.sendTransform(camera_world_transform)