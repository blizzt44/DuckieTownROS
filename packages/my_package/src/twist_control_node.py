#!/usr/bin/env python3


import os
import rospy
import math
from duckietown.dtros import DTROS, NodeType
from duckietown_msgs.msg import Twist2DStamped
from duckietown_msgs.msg import WheelEncoderStamped


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
       self._vehicle_name = os.environ['VEHICLE_NAME']
       self._left_encoder_topic = f"/{self._vehicle_name}/left_wheel_encoder_node/tick"
       self._right_encoder_topic = f"/{self._vehicle_name}/right_wheel_encoder_node/tick"
       self._ticks_left = None
       self._ticks_right = None
       self.sub_left = rospy.Subscriber(
           self._left_encoder_topic,
           WheelEncoderStamped,
           self.callback_left
       )
       self.sub_right = rospy.Subscriber(
           self._right_encoder_topic,
           WheelEncoderStamped,
           self.callback_right
       )

   def callback_left(self, data):
       rospy.loginfo_once(f"Left encoder resolution: {data.resolution}")
       rospy.loginfo_once(f"Left encoder type: {data.type}")
       self._ticks_left = data.data

   def callback_right(self, data):
       rospy.loginfo_once(f"Right encoder resolution: {data.resolution}")
       rospy.loginfo_once(f"Right encoder type: {data.type}")
       self._ticks_right = data.data

   def run(self):
       rate = rospy.Rate(10)
       #This was added
       counter = 0
       counter_2 = 0
       right_angle = 6 #this works for a pi/2 angle
       edge_length = 40 #40 is about 1m 
       position = (0,0) #x,y
       axis_length = 10
       switch_var = True 
       radius = 0.034
       wheel_circ = radius*2*math.pi
       Ntot = 137
       theta = 0
       while not rospy.is_shutdown():
           
           #MPC control  

        #    if counter > edge_length:
        #         self._v = 0.0
        #         if counter_2 < right_angle:
        #             self._omega = 4.0
        #             counter_2 += 1
        #         else:
        #             self._omega = 0.0
        #             self._v = -0.5
           message = Twist2DStamped(v=self._v, omega=self._omega)
           self._publisher.publish(message)
           counter += 1
        
           if self._ticks_left is not None and self._ticks_right is not None:
                left_motor_tick =  self._ticks_left
                right_motor_tick = self._ticks_right
                dr = 0
                dl = 0
                d = 0
                if switch_var:
                    prev_left_motor_tick = left_motor_tick
                    prev_right_motor_tick = right_motor_tick
                    switch_var = False
                else: 
                    dNr = right_motor_tick - prev_right_motor_tick
                    dNl = left_motor_tick - prev_left_motor_tick
                    dr = wheel_circ*(dNr/Ntot)
                    dl = wheel_circ*(dNl/Ntot)
                    d = (dr + dl)/2 
                    dtheta = (dr-dl)/axis_length
                    theta += dtheta
                    position = (position[0]+d*math.cos(theta),position[1]+d*math.sin(theta)) 
                    prev_left_motor_tick = left_motor_tick
                    prev_right_motor_tick = right_motor_tick
                msg = (
                    f"Wheel encoder ticks [position]: "
                    f"{position}"
                    f" ,Publishing message: v = '{self._v}', omega = '{self._omega}'"
                ) 
                rospy.loginfo(msg)
           rate.sleep()
        

   def on_shutdown(self):
       stop = Twist2DStamped(v=0.0, omega=0.0)
       self._publisher.publish(stop)


if __name__ == '__main__':
   node = TwistControlNode(node_name='twist_control_node')
   node.run()
   rospy.spin()