#!/bin/bash
source /environment.sh
dt-launchfile-init
rosrun ros_mpc test.py
dt-launchfile-join