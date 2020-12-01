#!/bin/bash

sudo apt-get install vlc -y
sudo chmod +x initCam.sh
sudo chmod +x watchdog/watchdog.sh
sudo cp systemFiles/* /etc/systemd/system/
sudo systemctl enable initCam.service
sudo systemctl enable PiCamWeb.service
sudo systemctl enable PiCamWatchdog.service
sudo systemctl start initCam.service
sudo systemctl start PiCamWeb.service
sudo systemctl start PiCamWatchdog.service
