#! /usr/bin/env python
import rospy
from geometry_msgs.msg import Twist

class ControlSystemS(object):
    def __init__(self):
        self._publicador = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        self._my_vel = Twist()
        self.linear_speed = 0.05
        self.angular_speed= 0.5
        
    def doamove_in_direction(self, direction):
        
        #rospy.logerr("Is going to move now")
        if direction == "forwards":
            self._my_vel.linear.x = self.linear_speed
            self._my_vel.angular.z = 0.0
        elif direction == "right":
            self._my_vel.linear.x = 0.0
            self._my_vel.angular.z = self.angular_speed
        elif direction == "left":
            self._my_vel.linear.x = 0.0
            self._my_vel.angular.z = -self.angular_speed
        elif direction == "backwards":
            self._my_vel.linear.x = -self.linear_speed
            self._my_vel.angular.z = 0.0
        elif direction == "stop":
            self._my_vel.linear.x = 0.0
            self._my_vel.angular.z = 0.0
        else:
            pass
            
        self._publicador.publish(self._my_vel)
                
if __name__=="__main__":
    nodus = rospy.init_node("this__cmd_vel_node")
    spheroControl = ControlSystemS()
    
    rate = rospy.Rate(1)
    
    ctrl_c = False
    def shutdownhook():
        global ctrl_C
        global my_vel
        
        global pub
        
        rospy.loginfo("Time to stop")
        ctrl_c = True
        spheroControl.doamove_in_direction("stop")
        
    rospy.on_shutdown(shutdownhook)
    
    while not ctrl_c:
        spheroControl.doamove_in_direction("backwards")
        rate.sleep()