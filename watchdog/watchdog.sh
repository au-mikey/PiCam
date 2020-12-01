#!/bin/bash

target=$1
gateway=$(route -n | grep 'UG[ \t]' | awk '{print $2}')
logfile=/opt/PiCam/watchdog/watchdog.log

if [ -z "$target" ]
then
    echo "No target identified"
    target=$gateway
    echo "target = $gateway"
fi

while true
do

    #sleep 300

    count=$(ping -c 1 $target | grep icmp* | wc -l )

    if [ $count -eq 0 ]
    then
        echo "`date` - Uh-Oh! Unable to connect to $gateway, we will reboot now"
        echo "`date` - Uh-Oh! Unable to connect to $gateway, we will reboot now" >> $logfile
        reboot

    else
        echo "`date` - Yes! We have a connection to $gateway!"
        #echo "`date` - Yes! We have a connection to $gateway!" >> $logfile

    fi

    sleep 300

done
