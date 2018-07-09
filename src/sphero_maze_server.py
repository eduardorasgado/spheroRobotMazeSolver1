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
        
        
        #Call the MAIN section to movements and logic
        if goal.goal.data == "GO":
            success = self.missionHandler()
        
            
        #Everythig finished
        self._result = Empty()
        if success:
            rospy.loginfo("Mission Finished")
        else:
            rospy.loginfo("MissionFailed")
        self._as.set_succeeded(self._result)
        
    def sensorsActing(self):
        #initialize odometry object
        odometrySphero = odomReader()
     
        #initialize Imu reader object
        imuSphero = imuReader()
        
        return [odometrySphero, imuSphero]
        
    def crash_direction(self, detection_dict):
        
        for key, value in detection_dict.iteritems():
            #print "{} -> {}".format(key, value)
            if value:
                return key
        return False
    
    def missionHandler(self):
        #core of the movements logic
        #initialize movement object
        spheroControl = ControlSystemS()
        
        #for crash handler
        self.detection_dict = {"front":False, "left":False, "right":False, "back":False}
        odometrySphero, imuSphero = self.sensorsActing()
        
        #CRASH DETECTOR------------
        self.detection_dict = imuSphero.obstacle_detection()
        print(self.detection_dict)
        
        #see what side did it crash
        what_side = self.crash_direction(self.detection_dict)
        if not what_side:
            print "NO CRASH"
        else:
            print what_side
        
        goalAchieve = False
        i = 0
        #for keep tracking same movement condition
        message = ""
        
        while i < 10 :
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
        
            #CRASH DETECTOR------------
            self.detection_dict = imuSphero.obstacle_detection()
            print(self.detection_dict)
            
            #see what side did it crash
            what_side = self.crash_direction(self.detection_dict)
            if not what_side:
                print "NO CRASH"
            else:
                print what_side
                #for collision change to collision positive case
                self._feedback.collision.data = True
            #---------------------
            
            #robot goes forward
            #self.spheroControl.doamove_in_direction("forward")
            
            #robot reacts to IMU
            message = self.direction_to_move(self.detection_dict)
            spheroControl.doamove_in_direction(message)
            
            self._as.publish_feedback(self._feedback)
            ####
            i +=1
            ####
            
            #applying timing
            time.sleep(1)
            #aplying frequency
            self.r.sleep()
        
        #CRASH DETECTOR------------
        self.detection_dict = imuSphero.obstacle_detection()
        print(self.detection_dict)
        
        #see what side did it crash
        what_side = self.crash_direction(self.detection_dict)
        if not what_side:
            print "NO CRASH"
        else:
            print what_side
        
        goalAchieve = True
        #STOP THE ROBOT
        spheroControl.doamove_in_direction("stop")
        return goalAchieve
        
    def direction_to_move(self, detection_dict):
        message= ""
        #movement logic after a shock or crash
        if not detection_dict["front"]:
            message = "forwards"
        
        else:
            if not detection_dict["back"]:
                    message = "backwards"
            else:
                if not detection_dict["left"]:
                    message = "left"
                else:
                    if not detection_dict["right"]:
                        message = "right"
                    else:
                        message = "stop"

        print "Message: ->>>>>>>>>>"+message
        return message
        

if __name__=='__main__':
    rospy.init_node("sphero_maze_runner_server_node")
    mazeServer()
    rospy.spin()