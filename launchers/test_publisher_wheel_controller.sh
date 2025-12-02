#!/bin/bash
source /environment.sh
dt-launchfile-init
rosrun my_package test_publisher_wheel_controller.py
dt-launchfile-join