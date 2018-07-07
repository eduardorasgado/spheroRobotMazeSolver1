#! /usr/bin/env python
import rospy
import actionlib
from std_msgs.msg import Empty

from sphero_maze_runner.msg import SpheroMazeAction
from sphero_maze_runner.msg import SpheroMazeFeedback
from sphero_maze_runner.msg import SpheroMazeResult
from sphero_maze_runner.msg import SpheroMazeGoal

class mazeClient:
    PENDING = 0
    ACTIVE = 1
    DONE = 2
    WARN = 3
    RROR = 4
    
    def __init__(self, order, action_server_name="/sphero_maze_runner_actionserver", action=SpheroMazeAction):
        self.order = order
        self.action_server_name = action_server_name
        self.action = action
        
        self.nodo = rospy.init_node("sphero_maze_runner_client_node")
        self.client = actionlib.SimpleActionClient(self.action_server_name, self.action)
        
        self.waitingforServer(self.client)
        
        self.goalHandling(self.client, self.order)
        
        self.state_result = self.client.get_state()
        
        self.rate = rospy.Rate(4) #4 hz
        
        self.state_result = self.sphero_communication(self.state_result, self.client)
        
    def waitingforServer(self, client):
        rospy.loginfo("Waiting for action server..."+self.action_server_name)
        client.wait_for_server()
        rospy.loginfo("Action server found: "+self.action_server_name)
        
    def goalHandling(self, client, order):
        goal = SpheroMazeGoal()
        goal.goal.data = order
        client.send_goal(goal, feedback_cb=self.feedback_callback)
        
    def feedback_callback(self, feedback):
        coll = "Collision" if feedback.collision.data else "No collision"
        msg = '[Feddback] Sphero is moving, collision:...'+coll
        rospy.loginfo(msg)
        
    def sphero_communication(self, state_result, client):
        while state_result < self.DONE:
            rospy.loginfo("Receiving feedback")
            self.rate.sleep()
            state_result = client.get_state()
            msg = "The state_result is: "+str(state_result)
            rospy.loginfo(msg)
        return state_result
        
if __name__=='__main__':
    order = str(input("Ready? 'GO'/'NO': "))
    if order == "GO":
        mazeClient(order)
    else:
        print("Good bye!")