# Use of SeaChest_Firmware update hard drive firmware
Author: Zachary Pincus  
Date: 2018-02-22  
http://zplab.wustl.edu

Assume the exceutable is `SeaChest_Firmware_240_1150_64`, and the firmware config file is `MP-SN04.CFS`, with this file with related firmware files in the working directory.

- Find the /dev/sdX to /dev/sgX mapping, if need be:

      sudo sg_map

- Find seagate drives to update:

      sudo ./SeaChest_Firmware_240_1150_64 --scan

- To get informmation about a particular drive (`dev/sg0` in this case):

      sudo ./SeaChest_Firmware_240_1150_64 -d /dev/sg0 -i

- To update the firmware:

      sudo ./SeaChest_Firmware_240_1150_64 -d /dev/sg0 --fwdlConfig MP-SN04.CFS