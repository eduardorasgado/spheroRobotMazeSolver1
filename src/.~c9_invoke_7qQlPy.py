#! /usr/bin/env python
import rospy
import actionlib
from geometry_msgs.msg import Twist
from std_msgs.msg import Empty

#messages from action
from sphero_maze_runner.msg import SpheroMazeAction
from sphero_maze_runner.msg import SpheroMazeFeedback
from sphero_maze_runner.msg import SpheroMazeResult

from odom_subscriber_node import odomReader
from imu_subscriber_node import imuReader

import time

class ControlSystem:
    def __init__(self, pub=None):
        self.pub = rospy.Publisher('/cmd_vel', Twist, queue_size=4)
        self.rate = rospy.Rate(4)
        
    def doamove(self, timing,linearist,angularist):
        my_vel = Twist()
        my_vel.linear.x = linearist
        my_vel.angular.z = angularist
        rospy.logerr("Is going to move now")
        self.publish_cmd_vel(my_vel)
        
        time.sleep(timing)
        
        self.stop(my_vel)
        
    def publish_cmd_vel(self, my_vel):
        connections = self.pub.get_num_connections()
        conected = False
        while not conected:
            if connections > 0:
                try:
                    rospy.loginfo("Moving....")
                    self.pub.publish(my_vel)
                    rospy.loginfo("Action published")
                    return True
                    conected == True
                except:
                    rospy.logwarn("A fucking error!: 1")
            else:
                rospy.logwarn("A fucking error!: 2")
                self.rate.sleep()
            
    def stop(self, my_vel):
        my_vel.linear.x = 0
        my_vel.linear.y = 0
        my_vel.linear.z = 0
        
        my_vel.angular.z = 0
        
        self.pub.publish(my_vel)
        rospy.loginfo("Sphero stopped")
        self.rate.sleep()
                

class mazeServer:
    _feedback = SpheroMazeFeedback()
    _result = SpheroMazeResult()
    
    def __init__(self, pub=None, serverName="/sphero_maze_runner_actionserver", action=SpheroMazeAction):
        self.pub = pub
        self.serverName = serverName
        self.action = action
        self.r = rospy.Rate(4) #4 hz
        self._as = actionlib.SimpleActionServer(serverName, self.action, self.goal_callback, False)
        self._as.start()
        
    def goal_callback(self, goal):
        #handler for goal
        
        #collision flag initializer
        self._feedback.collision.data = False
        
        #starting
        rospy.loginfo("Sphero bot is moving...")
        success = False
        if goal.goal.data == "GO":
            success = self.missionHandler()
            
        #Everythig finished
        self._result = Empty()
        if success:
            rospy.loginfo("Mission Finished")
        else:
            rospy.loginfo("MissionFailed")
        self._as.set_succeeded(self._result)
    
    def missionHandler(self):
        #core of the movements logic
        goalAchieve = False
        while not goalAchieve:
            #check if not cancelled
            if self._as.is_preempt_requested():
                rospy.loginfo("The goal has been cancelled/preempted")
                #set a cancelled goal
                self._as.set_preempted()
                return False
            #for collision case
            self._feedback.collision.data = False
            
            #here goes the logical movements
            """
            here goes the logical movements
            here goes the logical movements
            here goes the logical movements
            """
            spheroControl = ControlSystem()
            spheroControl.doamove(5, 0.1, 0)
            #
            #for collision change to collision positive case
            self._feedback.collision.data = True
            
            self._as.publish_feedback(self._feedback)
            ####
            goalAchieve = True
            ####
            #applying frequency
            self.r.sleep()
        
        return goalAchieve
        

if __name__=='__main__':
    rospy.init_node("sphero_maze_runner_server_node")
    mazeServer()
    rospy.spin()