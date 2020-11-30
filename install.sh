#!/bin/bash

sudo chmod +x initCam.sh
sudo chmod +x watchdog.sh
sudo cp systemFiles/* /etc/systemd/system/
sudo systemctl enable initCam.service
sudo systemctl enable rtspStream.service
sudo systemctl start initCam.service
sudo systemctl start rtspStream.service
sudo echo */5 * * * * sudo /opt/rtspStream/watchdog.sh >> /etc/crontab
