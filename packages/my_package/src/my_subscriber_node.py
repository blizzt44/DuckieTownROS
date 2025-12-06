#!/usr/bin/env python3

import rospy
from duckietown.dtros import DTROS, NodeType
from std_msgs.msg import String
from dt_communication_utils import DTCommunicationGroup
import os
import json
import math

       
duck1_group = DTCommunicationGroup('duck1_group', String)

duck2_group = DTCommunicationGroup('duck2_group', String)

duck4_group = DTCommunicationGroup('duck4_group', String)

fleet = ["duck1","duck2","duck4"]
init_pose = [[0,0,0], [2.5,0,math.pi], [2,0,0]]


class MySubscriberNode(DTROS):

    def __init__(self, node_name):  
        # # initialize the DTROS parent class
        super(MySubscriberNode, self).__init__(node_name=node_name, node_type=NodeType.GENERIC)
        # # construct subscriber
        # self.sub = rospy.Subscriber('chatter', String, self.callback)
        self.duck1_subscriber = duck1_group.Subscriber(self.callback)
        self.duck1_publisher = duck1_group.Publisher()
        self.duck2_subscriber = duck2_group.Subscriber(self.callback)
        self.duck2_publisher = duck2_group.Publisher()
        self.duck4_subscriber = duck4_group.Subscriber(self.callback)
        self.duck4_publisher = duck4_group.Publisher()
        self._vehicle_name = os.environ['VEHICLE_NAME']
        self.fleet_pose = {"duck1": init_pose[0], "duck2":init_pose[1], "duck4":init_pose[2]}


    def callback(self, data, header):
        message_dict = json.loads(data.data)
        
        sender_id = message_dict.get("sender")
        msg_pose = message_dict.get("pose")

        if sender_id != self._vehicle_name:
            rospy.loginfo(f"'{sender_id}' at '{msg_pose}'")
            self.fleet_pose[sender_id] = msg_pose

        
    
    def run(self):
       rate = rospy.Rate(10)  # 1 Hz
     
       while not rospy.is_shutdown():
            
            #Initialization for the bots continously
            
            payload_duck1 = {
            "sender": self._vehicle_name,
            "reciver": "duck1",
            "init_pose": init_pose[0],
            "fleet_pose": self.fleet_pose
            }
            duck1_msg = String(data=json.dumps(payload_duck1))
            self.duck1_publisher.publish(duck1_msg)

            payload_duck2 = {
            "sender": self._vehicle_name,
            "reciver": "duck2",
            "init_pose": init_pose[1],
            "fleet_pose": self.fleet_pose
            }
            duck2_msg = String(data=json.dumps(payload_duck2))
            self.duck2_publisher.publish(duck2_msg)


            payload_duck4 = {
            "sender": self._vehicle_name,
            "reciver": "duck4",
            "init_pose": init_pose[2],
            "fleet_pose": self.fleet_pose
            }
            duck4_msg = String(data=json.dumps(payload_duck4))
            self.duck4_publisher.publish(duck4_msg)

            rospy.loginfo("Published fleet pose")       


            rate.sleep()
            

           
            

if __name__ == '__main__':
    # create the node
    node = MySubscriberNode(node_name='my_subscriber_node')
    node.run()
    # keep spinning
    rospy.spin()