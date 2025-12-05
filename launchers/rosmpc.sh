#!/bin/bash
source /environment.sh
dt-launchfile-init
rosrun ros_mpc mpc_on_duckie.py
dt-launchfile-join