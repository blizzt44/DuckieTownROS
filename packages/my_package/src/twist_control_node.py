#!/usr/bin/env python3


import os
import rospy
import math
import json
from duckietown.dtros import DTROS, NodeType
from duckietown_msgs.msg import Twist2DStamped
from duckietown_msgs.msg import WheelEncoderStamped
from dt_communication_utils import DTCommunicationGroup
from std_msgs.msg import String
from dt_communication_utils import DTCommunicationGroup

vehicle_name = os.environ['VEHICLE_NAME']


#Which channel should the robot be on
if vehicle_name == "duck1":        
    group = DTCommunicationGroup('duck1_group', String)

elif vehicle_name == "duck2":
    group = DTCommunicationGroup('duck2_group', String)

elif vehicle_name == "duck4":
    group = DTCommunicationGroup('duck4_group', String)

else:
    rospy.loginfo_once(f"{vehicle_name} not found in database!")




# Twist command parameters
VELOCITY = 0.5  # linear m/s, forward (+)
OMEGA    = 0  # angular rad/s, CCW (+)


class TwistControlNode(DTROS):
   


   def __init__(self, node_name):
       super(TwistControlNode, self).__init__(node_name=node_name, node_type=NodeType.GENERIC)
       twist_topic  = f"/{vehicle_name}/car_cmd_switch_node/cmd"
       self._v     = VELOCITY
       self._omega = OMEGA
       self.position = None
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
       self.subscriber = group.Subscriber(self.callback)
       self.publisher = group.Publisher()
       self.fleet_pose = {}
       

   def callback_left(self, data):
       #Subscriber for the left wheel
       rospy.loginfo_once(f"Left encoder resolution: {data.resolution}")
       rospy.loginfo_once(f"Left encoder type: {data.type}")
       self._ticks_left = data.data

   def callback_right(self, data):
       #Subscriber for the right wheel
       rospy.loginfo_once(f"Right encoder resolution: {data.resolution}")
       rospy.loginfo_once(f"Right encoder type: {data.type}")
       self._ticks_right = data.data
       
   def callback(self,data,header):
        # 1. Access the raw string data

        message_dict = json.loads(data.data)
        rospy.loginfo_once(f"Got: {message_dict}")
        sender_id = message_dict.get("sender")
        

        if sender_id != self._vehicle_name and self.position == None:
            self.position = message_dict.get("init_pose")

        if sender_id != self._vehicle_name:
            self.fleet_pose = message_dict.get("fleet_pose")


        # # 2. Deserialize the string back into a dictionary
        # try: 
        #     data_dict = json.loads(raw_string)
            
        #     # 3. Access the values using dictionary keys
        #     vehicle_name = data_dict['name']
        #     vehicle_position = data_dict['position']
            
        #     #rospy.loginfo(f"Received from {vehicle_name}: Position is {vehicle_position}")
            
        #     # Example of using the values:
        #     # if vehicle_name == "duckiebot1":
        #     #     # Do something with vehicle_position
        #     #     ...

        # except json.JSONDecodeError as e:
        #     rospy.logerr(f"Failed to decode JSON from message: {e}")
        

   def run(self):
        
    rate = rospy.Rate(20)   
    turn_angle = math.pi
    edge_length = 0.5
    axis_length = 0.10
    switch_var = True 
    radius = 0.034
    wheel_circ = radius*2*math.pi
    Ntot = 135
    theta = 0
    while not rospy.is_shutdown():
        
        #MPC control should be added here 
        if self.position != None:
            rospy.loginfo_once(f"Pose is: {position}")

            if position[0] > edge_length:
                    self._v = 0.0
                    if position[2] < turn_angle:
                        self._omega = 2.0
                        
                    else:
                        self._omega = 0.0
                        self._v = 0.5
            message = Twist2DStamped(v=self._v, omega=self._omega)
            self._publisher.publish(message)
            
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
                        position = (position[0]+d*math.cos(theta),position[1]+d*math.sin(theta),theta) 
                        prev_left_motor_tick = left_motor_tick
                        prev_right_motor_tick = right_motor_tick


            payload = {
                    "sender": self._vehicle_name,
                    "name": self._vehicle_name,
                    "pose": position
                }

                # Dump it to a string and pass it to the 'data' field
            message_fleet = String(data=json.dumps(payload))
            self.publisher.publish(message_fleet)

                    # msg = (
                    #     f"Wheel encoder ticks [position]: "
                    #     f"{position}"
                    #     f" ,Publishing message: v = '{self._v}', omega = '{self._omega}'"
                    # ) 
                    # rospy.loginfo(msg)


            rate.sleep()
        else:
            position = self.position #x,y, theta
            payload = {
                    "sender": self._vehicle_name,
                    "name": self._vehicle_name,
                    "pose": position
                }

                # Dump it to a string and pass it to the 'data' field
            message_fleet = String(data=json.dumps(payload))
            self.publisher.publish(message_fleet)

   def on_shutdown(self):
       stop = Twist2DStamped(v=0.0, omega=0.0)
       self._publisher.publish(stop)
       #TODO: Add reset for the motor 

   def chicken_race(self):
        # 1. Setup Opponent
        if self._vehicle_name == "duck2":
            opp = "duck1"
        elif self._vehicle_name == "duck1":
            opp = "duck2"
        else:
            rospy.logwarn("I am not duck2 or duck4, who am I racing?")
            return

        # 2. Physics / Geometry Constants
        rate = rospy.Rate(20)
        edge_length = 0.5 # Seems unused, but kept
        axis_length = 0.10
        radius = 0.034
        wheel_circ = radius * 2 * math.pi
        Ntot = 135

        # 3. Initialize State Variables (CRITICAL FIX)
        # We assume start at 0,0,0. If self.position is set externally, use that.

        while self.position is None and not rospy.is_shutdown():
            # We must sleep here to give the Subscriber thread time 
            # to receive the message and run the callback!
            rospy.loginfo("Waiting for init_pose...")
            rate.sleep()

        current_x, current_y, current_theta = self.position
      
            
        # Encoder state
        prev_left_tick = None
        prev_right_tick = None

        rospy.loginfo("Starting Chicken Race...")

        while not rospy.is_shutdown():
            # --- A. Update Odometry (Dead Reckoning) ---
            # We only calculate if we have valid tick data
            if self._ticks_left is not None and self._ticks_right is not None:
                curr_left = self._ticks_left
                curr_right = self._ticks_right

                # If this is our very first loop, just store the ticks and skip math
                if prev_left_tick is None:
                    prev_left_tick = curr_left
                    prev_right_tick = curr_right
                else:
                    # Calculate change in ticks
                    d_left_ticks = curr_left - prev_left_tick
                    d_right_ticks = curr_right - prev_right_tick

                    # Convert ticks to distance (meters)
                    d_left_m = wheel_circ * (d_left_ticks / Ntot)
                    d_right_m = wheel_circ * (d_right_ticks / Ntot)

                    # Calculate center distance (d) and rotation (d_theta)
                    dist_center = (d_right_m + d_left_m) / 2.0
                    delta_theta = (d_right_m - d_left_m) / axis_length

                    # Update global pose
                    current_theta += delta_theta
                    current_x += dist_center * math.cos(current_theta)
                    current_y += dist_center * math.sin(current_theta)

                    # Update history for next loop
                    prev_left_tick = curr_left
                    prev_right_tick = curr_right
            
            # Update the class variable so other parts of code know where we are
            self.position = (current_x, current_y, current_theta)

            # --- B. Control Logic (The Race) ---
            # Check if we know where the opponent is
            if self.fleet_pose is not None and opp in self.fleet_pose:
                opp_pose = self.fleet_pose[opp]
                # ... rest of your code
                
                # Calculate distance to opponent
                dx = current_x - opp_pose[0]
                dy = current_y - opp_pose[1]
                duck_distance = math.sqrt(dx**2 + dy**2)

                # Control Policy
                if duck_distance > 0.4: # Increased safety buffer slightly
                    self._v = 0.5
                    if dy > 0.5:
                        self._omega = -1
                    elif dy < -0.5:
                        self._omega = 1
                    else:
                        self._omega = 0
                    
                    rospy.loginfo_throttle(1, f"Charging! Dist: {duck_distance:.2f}m")
                else:
                    self._v = 0.0
                    rospy.loginfo_throttle(1, f"Too close! Stopping. Dist: {duck_distance:.2f}m")
            else:
                # If we don't see the opponent, stay still or search?
                self._v = 0.0
                rospy.loginfo_throttle(3, f"Waiting for data from {opp}...")

            # Publish Motor Commands
            msg_cmd = Twist2DStamped(v=self._v, omega=self._omega)
            self._publisher.publish(msg_cmd)

            # --- C. Communication (Publishing Pose) ---
            # Create payload
            payload = {
                "sender": self._vehicle_name,
                "name": self._vehicle_name,
                # Convert tuple to list implicitly by JSON, or keep as tuple for internal use
                # Note: json.dumps handles lists better, but we pass tuple here
                "pose": (current_x, current_y, current_theta) 
            }

            # Serialize and Publish
            try:
                json_str = json.dumps(payload)
                self.publisher.publish(String(data=json_str))
            except Exception as e:
                rospy.logerr(f"JSON Error: {e}")

            rate.sleep()

#    def chicken_race(self):
        
#         if self._vehicle_name == "duck2":
#             opp = "duck4"
#         elif self._vehicle_name == "duck4":
#             opp = "duck2"
#         else:
#             rospy.logwarn("I am not duck2 or duck4, look at code!")
#             return
       
#         rate = rospy.Rate(20)   
#         axis_length = 0.10
#         radius = 0.034
#         wheel_circ = radius*2*math.pi
#         Ntot = 135
#         theta = 0


#         while not rospy.is_shutdown():
            
#             #MPC control should be added here 
#             if self.position != None and self.fleet_pose[opp] != None:
#                 opp_pose = self.fleet_pose[opp]
#                 rospy.loginfo_once(f"Pose is: {position}")
#                 duck_dx = self.position[0] - opp_pose[0]
#                 duck_dy = self.position[1] - opp_pose[1]

#                 duck_distance = math.sqrt(duck_dx**2+duck_dy**2)

#                 if duck_distance > 0.2:
#                     self._v = 0.5
#                 else:
#                     self._v = 0
    
#                 message = Twist2DStamped(v=self._v, omega=self._omega)
#                 self._publisher.publish(message)
                
#                 if self._ticks_left is not None and self._ticks_right is not None:
#                         left_motor_tick =  self._ticks_left
#                         right_motor_tick = self._ticks_right
#                         dr = 0
#                         dl = 0
#                         d = 0
#                         if switch_var:
#                             prev_left_motor_tick = left_motor_tick
#                             prev_right_motor_tick = right_motor_tick
#                             switch_var = False
#                         else: 
#                             dNr = right_motor_tick - prev_right_motor_tick
#                             dNl = left_motor_tick - prev_left_motor_tick
#                             dr = wheel_circ*(dNr/Ntot)
#                             dl = wheel_circ*(dNl/Ntot)
#                             d = (dr + dl)/2 
#                             dtheta = (dr-dl)/axis_length
#                             theta += dtheta
#                             position = (position[0]+d*math.cos(theta),position[1]+d*math.sin(theta),theta) 
#                             prev_left_motor_tick = left_motor_tick
#                             prev_right_motor_tick = right_motor_tick


#                 payload = {
#                         "sender": self._vehicle_name,
#                         "name": self._vehicle_name,
#                         "pose": position
#                     }

#                     # Dump it to a string and pass it to the 'data' field
#                 message_fleet = String(data=json.dumps(payload))
#                 self.publisher.publish(message_fleet)

#                         # msg = (
#                         #     f"Wheel encoder ticks [position]: "
#                         #     f"{position}"
#                         #     f" ,Publishing message: v = '{self._v}', omega = '{self._omega}'"
#                         # ) 
#                         # rospy.loginfo(msg)


#                 rate.sleep()
#             else:
#                 position = self.position #x,y, theta
#                 payload = {
#                         "sender": self._vehicle_name,
#                         "name": self._vehicle_name,
#                         "pose": position
#                     }

#                     # Dump it to a string and pass it to the 'data' field
#                 message_fleet = String(data=json.dumps(payload))
#                 self.publisher.publish(message_fleet)





if __name__ == '__main__':
   node = TwistControlNode(node_name='twist_control_node')
   node.chicken_race()
   rospy.spin()