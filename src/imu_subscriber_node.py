#! /usr/bin/env python

import rospy
from sensor_msgs.msg import Imu

class imuReader:
    def __init__(self):
        self.pub = rospy.Subscriber('/sphero/imu/data3', Imu, self.callback)
        self._imudata = Imu()
        self._threshold = 5.00
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
        
    def obstacle_detection(self):
        """
        Detects in which four directions there is an obstacle that 
        made the robot crashed
        It is based on the IMU data
        Axis:
        ^y
        |
        z0-->x
        
        """
        #saving the acelerations
        x_accel = self._imudata.linear_acceleration.x
        y_accel = self._imudata.linear_acceleration.y
        z_accel = self._imudata.linear_acceleration.z
        
        axis_list = [x_accel, y_accel, z_accel]
        
        #looking for the major measure
        max_axis_index = axis_list.index(max(axis_list))
        #if that measure is positive or not
        positive = axis_list[max_axis_index] >= 0
        
        #if value is > than 7 then True
        significative_value = axis_list[max_axis_index] > self._threshold
        
        message = ""
        
        if significative_value:
            if max_axis_index == 0:
                # Winner is in the x axis, therefore its a side crash left/right
                rospy.logwarn("[X="+str(x_accel))
                rospy.loginfo("Y="+str(y_accel)+", Z="+str(z_accel)+"]")
                if positive:
                    message = "right"
                else:
                    message = "left"
            
            elif max_axis_index == 1:
                # Winner is the Y axis, therefore its a forn/back crash
                rospy.logwarn("[Y="+str(y_accel))
                rospy.loginfo("X="+str(x_accel)+", Z="+str(z_accel)+"]")
                if positive:
                    message = "front"
                else:
                    message = "back"
            elif max_axis_index == 2:
                # Z Axis is the winner, therefore its a crash that made it jump
                rospy.logwarn("[Z="+str(z_accel))
                rospy.loginfo("X="+str(x_accel)+", Y="+str(y_accel)+"]")
                
                if positive:
                    message = "up"
                else:
                    message = "down"
            else:
                message = "unknown_direction"
        else:
            rospy.loginfo("X="+str(x_accel)+"Y="+str(y_accel)+", Z="+str(z_accel)+"]")
            message = "nothing"
        
        return self.convert_to_dict(message)
        
    def convert_to_dict(self, message):
        detect_dict = {}
        
        # We consider that when there is a big Z axis component there has been a very big front crash
        detection_dict = {"front":(message=="front" or message=="up" or message=="down"),
                          "left":message=="left",
                          "right":message=="right",
                          "back":message=="back"}
                          
        return detection_dict


