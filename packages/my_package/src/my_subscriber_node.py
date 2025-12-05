#!/usr/bin/env python3

import rospy
from duckietown.dtros import DTROS, NodeType
from std_msgs.msg import String
from dt_communication_utils import DTCommunicationGroup
import os

group = DTCommunicationGroup('my_group', String)

class MySubscriberNode(DTROS):

    def __init__(self, node_name):
        # # initialize the DTROS parent class
        super(MySubscriberNode, self).__init__(node_name=node_name, node_type=NodeType.GENERIC)
        # # construct subscriber
        # self.sub = rospy.Subscriber('chatter', String, self.callback)
        self.subscriber = group.Subscriber(self.callback)
        self.publisher = group.Publisher()
        self._vehicle_name = os.environ['VEHICLE_NAME']

    def callback(self, data, header):
        rospy.loginfo("I heard '%s'", data.data,)
    
    def run(self):
       rate = rospy.Rate(10)  # 1 Hz
       message = String(data=f"Hello from {self._vehicle_name}!")
       while not rospy.is_shutdown():
           rospy.loginfo(f"Publishing message: '{message}'")
           self.publisher.publish(message)
           rate.sleep()

if __name__ == '__main__':
    # create the node
    node = MySubscriberNode(node_name='my_subscriber_node')
    node.run()
    # keep spinning
    rospy.spin()