#!/bin/bash

# Quick bash script to make the building and running of code on the robots easier
export DOCKER_API_VERSION=1.41

echo "Select duck (default 2)"
read robot
echo "Select launcher (default rosmpc)"
read launcher

if [ "$robot" = "" ]; then
   robot="duck2"
fi

if [ "$launcher" = "" ]; then
   launcher="rosmpc"
fi

dts devel build -H $robot -f
dts devel run -H $robot -L $launcher