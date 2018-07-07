#! /usr/bin/env python

import rospy
from nav_msgs.msg import Odometry

class odomReader:
    def __init__(self):
        self.pub = rospy.Subscriber('odom', Odometry, self.callback)
        self.rate = rospy.Rate(4) #2Hz
        #rospy.spin()
        
    def callback(self, msg):
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        
        return [x, y]
        