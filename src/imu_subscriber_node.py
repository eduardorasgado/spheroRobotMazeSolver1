#! /usr/bin/env python

import rospy
from sensor_msgs.msg import Imu

class imuReader:
    def __init__(self):
        self.pub = rospy.Subscriber('/sphero/imu/data3', Imu, self.callback)
        self._imudata = Imu()
        #self.rate = rospy.Rate(0.5)
        #rospy.spin()
        
    def callback(self, msg):
        orientation_x = msg.orientation.x
        orientation_y = msg.orientation.y
        orientation_z = msg.orientation.z
        orientation_w = msg.orientation.w
        
        angular_vel_x = msg.angular_velocity.x
        angular_vel_y = msg.angular_velocity.y
        angular_vel_z = msg.angular_velocity.z
        
        #print("Imu measurements -> orientation= x: {}, y: {}, z: {}, w: {}".format(orientation_x, orientation_y, orientation_z, orientation_w))
        #print("Imu measurements -> angular velocity= x: {}, y: {}, z: {}".format(angular_vel_x, angular_vel_y, angular_vel_z))
        
        #self._odomdata = [[orientation_x, orientation_y, orientation_z, orientation_w] , [angular_vel_x, angular_vel_y, angular_vel_z]]
        self._imudata = msg
        
    def get_odomdata(self):
        return self._imudata
        


