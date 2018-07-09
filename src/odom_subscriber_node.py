#! /usr/bin/env python

import rospy
from nav_msgs.msg import Odometry

class odomReader:
    def __init__(self):
        self.pub = rospy.Subscriber('odom', Odometry, self.callback)
        self._odomdata = Odometry()
        #self.rate = rospy.Rate(0.5) #2Hz
        #rospy.spin()
        
    def callback(self, msg):
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        #print("odometry measurements -> x: {}, y: {}".format(x, y))
        #self._odomdata.append(x)
        #self._odomdata.append(y)
        
        self._odomdata = msg
        
    def get_odomdata(self):
        return self._odomdata
        