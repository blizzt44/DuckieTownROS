#!/usr/bin/env python3


import os
import rospy
from duckietown.dtros import DTROS, NodeType
from duckietown_msgs.msg import Twist2DStamped


# Twist command parameters
VELOCITY = 0.5  # linear m/s, forward (+)
OMEGA    = 0  # angular rad/s, CCW (+)


class TwistControlNode(DTROS):


   def __init__(self, node_name):
       super(TwistControlNode, self).__init__(node_name=node_name, node_type=NodeType.GENERIC)
       vehicle_name = os.environ['VEHICLE_NAME']
       twist_topic  = f"/{vehicle_name}/car_cmd_switch_node/cmd"
       self._v     = VELOCITY
       self._omega = OMEGA
       self._publisher = rospy.Publisher(twist_topic, Twist2DStamped, queue_size=1)


   def run(self):
       rate = rospy.Rate(10)
       #This was added
       counter = 0
       counter_2 = 0
       right_angle = 6 #this works for a pi/2 angle
       edge_length = 40 #40 is about 1m 
       while not rospy.is_shutdown():
           
           #MPC control  

           if counter > edge_length:
                self._v = 0.0
                if counter_2 < right_angle:
                    self._omega = 4.0
                    counter_2 += 1
                else:
                    self._omega = 0.0
                    self._v = 0.5
           message = Twist2DStamped(v=self._v, omega=self._omega)
           self._publisher.publish(message)
           rate.sleep()
           counter += 1
           
           rospy.loginfo(f"Publishing message: v = '{self._v}', omega = '{self._omega}'") 


   def on_shutdown(self):
       stop = Twist2DStamped(v=0.0, omega=0.0)
       self._publisher.publish(stop)


if __name__ == '__main__':
   node = TwistControlNode(node_name='twist_control_node')
   node.run()
   rospy.spin()