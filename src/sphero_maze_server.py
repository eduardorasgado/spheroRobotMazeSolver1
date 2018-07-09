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


class ControlSystemS(object):
    def __init__(self):
        self._publicador = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        self._my_vel = Twist()
        self.linear_speed = 0.05
        self.angular_speed= 0.5
        
    def doamove_in_direction(self, direction):
        
        #rospy.logerr("Is going to move now")
        if direction == "forward":
            self._my_vel.linear.x = self.linear_speed
            self._my_vel.angular.z = 0.0
        if direction == "back":
            self._my_vel.linear.x -self.linear_speed
            self._my_vel.angular.z = 0.0
        if direction == "stop":
            self._my_vel.linear.x = 0.0
            self._my_vel.angular.z = 0.0
        else:
            pass
            
        self._publicador.publish(self._my_vel)
                

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
        #initialize movement object
        self.spheroControl = ControlSystemS()
        
        #initialize odometry object
        odometrySphero = odomReader()
        odometrySphero1 = odometrySphero.get_odomdata()
        #initialize Imu reader object
        imuSphero = imuReader()
        imuSphero1 = imuSphero.get_odomdata()
        
        #print("odometry measurements -> x: {}, y: {}".format(odometrySphero[0], odometrySphero[1]))
        #print("Imu measurements -> orientation= x: {}, y: {}, z: {}, w: {}".format(imuSphero[0][0], imuSphero[0][1], imuSphero[0][2], imuSphero[0][3]))
        #print("Imu measurements -> angular velocity= x: {}, y: {}, z: {}".format(imuSphero[1][0], imuSphero[1][1], imuSphero[1][2]))
        print("{}".format(odometrySphero1))
        
        goalAchieve = False
        i = 0
        while i < 3 :
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
            #read odometry/Imu measurements
            #self.odometrySphero = odomReader()
            #self.imuSphero = imuReader()
            
            #robot goes forward
            self.spheroControl.doamove_in_direction("forward")
            
            #
            #for collision change to collision positive case
            self._feedback.collision.data = True
            
            self._as.publish_feedback(self._feedback)
            ####
            i +=1
            ####
            
            #applying timing
            time.sleep(1)
            #aplying frequency
            self.r.sleep()
            
        goalAchieve = True
        self.spheroControl.doamove_in_direction("stop")
        return goalAchieve
        

if __name__=='__main__':
    rospy.init_node("sphero_maze_runner_server_node")
    mazeServer()
    rospy.spin()