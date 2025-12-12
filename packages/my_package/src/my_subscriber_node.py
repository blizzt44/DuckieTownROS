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

FLEET = ["duck1", "duck2", "duck4"]
INIT_POSE = {
    "duck1": [0,0,0],
    "duck2": [0,0,0],
    "duck4": [2,0,math.pi]
}

class WatchtowerNode(DTROS):

    def __init__(self, node_name):
        super(WatchtowerNode, self).__init__(node_name=node_name, node_type=NodeType.GENERIC)

        self._vehicle_name = os.environ['VEHICLE_NAME']

        # Subscribers to robot groups
        self.sub1 = duck1_group.Subscriber(self.callback)
        self.sub2 = duck2_group.Subscriber(self.callback)
        self.sub4 = duck4_group.Subscriber(self.callback)

        # Publishers to robots
        self.pub1 = duck1_group.Publisher()
        self.pub2 = duck2_group.Publisher()
        self.pub4 = duck4_group.Publisher()

        # Store live fleet pose (start with initial positions)
        self.fleet_pose = dict(INIT_POSE)

    def callback(self, data, header):
        """
        Receives pose updates from robots
        """
        msg = json.loads(data.data)
        sender = msg.get("sender")
        pose = msg.get("pose")

        if sender in FLEET and pose is not None:
            rospy.loginfo(f"Robot {sender} updated pose {pose}")
            self.fleet_pose[sender] = pose   # update ONLY this robot

    def run(self):
        rate = rospy.Rate(10)

        sent_init = False  # we send init_pose only once

        while not rospy.is_shutdown():

            for bot, pub in [("duck1", self.pub1), ("duck2", self.pub2), ("duck4", self.pub4)]:

                payload = {
                    "sender": self._vehicle_name,
                    "fleet_pose": self.fleet_pose
                }

                # send init_pose once
                if not sent_init:
                    payload["init_pose"] = INIT_POSE[bot]

                pub.publish(String(data=json.dumps(payload)))

            sent_init = True

            rospy.loginfo(f"Published fleet_pose: {self.fleet_pose}")
            rate.sleep()

if __name__ == "__main__":
    node = WatchtowerNode("watchtower_node")
    node.run()
    rospy.spin()
