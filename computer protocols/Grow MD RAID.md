# How to grow an MD RAID on Linux
Author: Zachary Pincus  
Date: 2017-11-18  
http://zplab.wustl.edu

1. identify drives in the RAID and their serial numbers
       lsblk -s -o NAME,SIZE,SERIAL /dev/mdXXX

2. open up computer and note position of drives with specified serial numbers

3. for each drive in the RAID:
    - remove the drive from the RAID in software:
    
          mdadm --fail /dev/mdXXX /dev/sdX1
          mdadm --remove /dev/mdXXX failed
    - remove the drive with the serial number corresponding to the name you just failed
    - replace with a new drive
    - find name of new drive: it should be the one not a part of anything with no filesystems
    
          lsblk -o NAME,FSTYPE,MOUNTPOINT,SIZE,SERIAL /dev/sd[a-z]
    - format the disk. If this is the first drive in the RAID, use `sgdisk` to make a partition table, verify the partition table, and back the table up for replicating to other disks:
    
          sgdisk -og -n 0:0:-400M -t 0:fd00 -c 0:"md RAID" /dev/sdX
          sgdisk -v /dev/sdX
          sgdisk -b ~/new_partition_table /dev/sdX
      For subsequent disks, just use the backed up table and verify:
      
          sgdisk -l ~/new_partition_table /dev/sdX
          sgdisk -v /dev/sdX
    - add the disk back to the array
    
          mdadm --add /dev/mdXXX /dev/sdX1

    - wait until the resync has finished
    
          cat /proc/mdstat

4. grow the array to use the new drives

       mdadm --grow /dev/mdXXX --backup-file=~/grow_backup --size=max

5. growing triggers a resync: wait until the resync has finished

       cat /proc/mdstat

6. check, resize, and re-check the filesystem:

       umount /mnt/XXXarray
       xfs_repair -n /dev/mdXXX
       mount /mnt/XXXarray

       xfs_growfs /mnt/XXXarray

       umount /mnt/XXXarray
       xfs_repair -n /dev/mdXXX
       mount /mnt/XXXarray