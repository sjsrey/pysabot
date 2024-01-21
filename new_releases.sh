#!/bin/bash

# Directory to be monitored
MONITOR_DIR="/home/serge/para/1_projects/Code_pysal_bot/pysalbot/news/"

# Check for new files in the directory
if [ "$(ls -A $MONITOR_DIR)" ]; then
    # If there are files, display a message with xcowsay
    xcowsay --time=0 "There is a new pysal package release!"
fi
