blink-jenkins
=============

Display current state of a Jenkins instance using a blink(1).

This script will periodically poll a Jenkins server and display the state using the blink(1), from 
ThingM (http://www.kickstarter.com/projects/thingm/blink1-the-usb-rgb-led). It will display blue if 
all jobs built successfully, yellow if one or more jobs have issues, and red if one or more have failed.
It will also blink if one or more jobs are currently building.

Simply run this file (in a screen/tmux session for now, perhaps), passing it the --host parameter 
to tell it where your Jenkins instance lives. You may also pass the `--user` and `--password` parameters
if your Jenkins instance requires basic authentication. Jobs to ignore, or on which to ignore the
`anime` attribute, are currently specified in the script itself.
