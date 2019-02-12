# Kubuntu installation for zplab microscopes

1. install Kubuntu with the following partition scheme on the system SSD:
  - 96 GB / btrfs
  - 34 GB swap
  - remaining /home ext4

2. Install basic tools:

       sudo apt-get update
       sudo apt-get install ssh
       sudo apt-get remove --purge libreoffice*
       sudo apt-get remove --purge mysql*
       sudo apt-get clean
       sudo apt-get autoremove
       sudo apt-get full-upgrade
       
3. Install video drivers. Use latest recommended (370 is example here):

       sudo add-apt-repository ppa:graphics-drivers/ppa
       sudo apt-get update
       sudo apt-get install nvidia-370

4. Install and configure `mdadm`, the RAID manager:

       sudo apt-get install mdadm
   Now edit `/etc/mdadm/mdadm.conf` to uncommment or add these lines:
   
       DEVICE partitions
       HOMEHOST <system>
       AUTO +homehost
       MAILADDR zpincus@wustl.edu
       MAILFROM mdadm@zpl-scope.wucon.wustl.edu
   (The `MAILFROM` line should reflect the scope's name obviously.)

5. If the RAID is pre-existing, assemble it:

       sudo mdadm --assemble --scan
   If the RAID is new, then:
     - For first disk, use `sgdisk` to make a partition table, verify it, and back it up
     
           sudo sgdisk -og -n 0:0:-400M -t 0:fd00 -c 0:"md RAID" /dev/sdX
           sudo sgdisk -v /dev/sdX
           sudo sgdisk -b ~/new_partition_table /dev/sdX
     - For subsequent disks, use the backed-up table:
     
           sudo sgdisk -l ~/new_partition_table /dev/sdX
           sudo sgdisk -v /dev/sdX
           
     - create the RAID:
     
           sudo mdadm --create --verbose /dev/md/ARRAYNAME --level=6 --raid-devices=8 /dev/sda1 /dev/sdb1 /dev/sdc1 /dev/sdd1 /dev/sde1 /dev/sdf1 /dev/sdg1 /dev/sdh1  

6. Install XFS:

       sudo apt-get install xfsprogs
   If the RAID is new, make an XFS filesystem on it: 
   
       sudo mkfs -t xfs /dev/md/ARRAYNAME

7. Make a mount-point for the RAID and add it to the FSTAB:

       sudo mkdir /mnt/ARRAYNAME
       lsblk -o uuid /dev/md/ARRAYNAME
   edit `/etc/fstab` to add:
   
       UUID=uuid /mnt/ARRAYNAME xfs noatime,inode64 0 2
   where `uuid` is replaced by the output of `lsblk` above

8. If NFS is desired (generally not):

       sudo apt-get install nfs-common
   First, edit `/etc/fstab` to add nfs mounts as desired, then make mount points, e.g.:
   
       OTHER_SCOPE_NAME:/mnt/OTHERARRAY /mnt/OTHERARRAY nfs noatime,intr,x-systemd.automount 0 2
   (TODO: is x-systemd.automount still necessary? As of 2016-11 it is required to allow nfs to mount on boot.)  
   Then make the mount point: 
      
       sudo mkdir /mnt/scopearray
   Next, enable the NFS server:
   
       sudo apt-get install nfs-kernel-server
   Edit `/etc/exports` to add (e.g.):
   
       /mnt/ARRAYNAME zpl-iscope(rw) zpl-scope(rw)
   And run:
   
       exportfs -a
       sudo mkdir /etc/systemd/system/nfs-server.service.d/
   Now copy `wait_for_dns.py` to `/etc/systemd/system/nfs-server.service.d/` and run:
   
       sudo systemctl edit --full nfs-server
   Add the following before other ExecStartPre lines:
   
       ExecStartPre=/usr/bin/python3 /etc/systemd/system/nfs-server.service.d/wait_for_dns.py

9. Install `zsh`:

       sudo apt-get install zsh
       chsh --shell `which zsh` zplab
   Copy `zshrc` file to `~/.zshrc`

10. Install SMB

        sudo apt-get install samba
    Edit `/etc/samba/smb.conf` to add or change:
    
        workgroup = ZPLAB
        server string = %h (zplab microscope)
        [homes]
           comment = Home Directories
           browseable = no
           writeable = yes
           veto files = /._*/.DS_Store/
           delete veto files = yes
        
        [purplearray]
           path = /mnt/ARRAYNAME
           browseable = yes
           writeable = yes
           veto files = /._*/.DS_Store/
           delete veto files = yes
    Run:
    
        sudo smbpasswd -a zplab
        sudo smbd reload

11. Enable RAID monitoring:

        sudo apt-get install msmtp msmtp-mta
        sudo cat > /etc/msmtprc << EOF
        account default
        host osmtp.wustl.edu
        from zplab@SCOPENAME.wustl.edu
        syslog LOG_MAIL
        EOF

        sudo apt-get install smartmontools
    Edit /etc/smartd.conf so that the first DEVICESCAN line reads:
    
        DEVICESCAN -H -l error -l selftest -f -s (O/../.././00|S/../.././12|L/../01/./06) -m zpincus@wustl.edu -M diminishing
    Then run:
    
        sudo service smartd start
        sudo service mdmonitor start

12. Install various useful tools and do some cleanup:

        sudo apt install libfftw3-dev libsdl2-2.0 screen minicom iftop nvidia-cuda-toolkit curl qpdfview git virtualbox automake
        cd ~
        rmdir Downloads Music Pictures Templates Videos Public

13. Install tools for making BRTFS snapshots.  
    Edit `/etc/fstab` to add special mount point for the BRTFS root (usually not exposed, as the linux root is the BTRFS subvolume called '@').
    
        UUID=uuid /mnt/btrfs-root btrfs defaults,subvol=/,noauto 0 1
    Note: UUID should is the same as the other btrfs UUID for the @ subvol in fstab  
    Run:
    
        sudo mkdir /mnt/btrfs-root/
        sudo mount /mnt/btrfs-root/
        sudo chmod go-rwx /mnt/btrfs-root
    Copy `snapshot.py` to `/usr/local/bin/snapshot` and run:
    
        sudo chown root:root /usr/local/bin/snapshot
        sudo chmod u+x /usr/local/bin/snapshot


14. Add zplab to dialout group (who can open ttys):

        sudo usermod -a -G dialout zplab

15. Install miniconda:

        wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
        sudo bash Miniconda3-latest-Linux-x86_64.sh -p /usr/local/miniconda3 -b
        rm Miniconda3-latest-Linux-x86_64.sh
    Now allow running miniconda programs with sudo (like pip):
    
        sudo visudo
    and add `/usr/local/miniconda3/bin` to `Defaults secure_path` line.
    Copy over `scope_env.yml` file and run:
    
        sudo pip install --upgrade pip
        sudo conda update conda
        export PIP_SRC="/usr/local/scope/py_src"
        sudo mkdir /usr/local/scope
        sudo -E conda env update -n root -f scope_env.yml
        sudo chown -R zplab:zplab /usr/local/scope
        rm $PIP_SRC/pip-delete-this-directory.txt
        for src_dir in $PIP_SRC/*/; do
            cd $src_dir
            git config user.name "Zachary Pincus"
            git config user.email "zpincus@gmail.com"
            cd ..
        done
        sudo pip install celiagg --global-option=--no-text-rendering
        sudo ris_widget --install-desktop-file
        ipython profile create
    Copy over `ipython_config.py` file to `~/.ipython/profile_default/ipython_config.py`
    
    Also install the worm segmentation tools. Copy over the latest release distribution (e.g. `worm_segmenter-1.zip`) and then run:
    
        unzip worm_segmenter-1.zip
        rm worm_segmenter-1.zip
        sudo pip install ./worm_segmenter-1
    
    Until zeromq 4.2.6 is released and available in conda, we need to custom build libzmq from github, to pick up some bugfixes:
    
        sudo apt install libtool
        commit=889ac2eb3dcf29be1b7bdae93f216d30fd2b9dfb
        curl -o libzmq.zip https://codeload.github.com/zeromq/libzmq/zip/$commit
        unzip libzmq.zip && rm libzmq.zip
        cd libzmq-$commit
        ./autogen.sh && ./configure && make -j8
        sudo make install
        cd ..
        rm -rf libzmq-$commit
        sudo pip uninstall pyzmq
        sudo pip install pyzmq --no-binary pyzmq

16. Install scope-server tools:

        sudo job_runner_check --install
        scope_job_runner add `which incubator_check`
    Copy `fftw_wisdom` over to `/usr/local/scope` if it was previously calculated **on this machine**. Then run `scope_server`, stop it, and edit
    the newly-created `/usr/local/scope/configuration.py` file as appropriate.

17. Install dropbox (from https://www.burgundywall.com/post/autostart-dropbox-on-fedora):

        cd ~ && wget -O - "https://www.dropbox.com/download?plat=lnx.x86_64" | tar xzf -
    Run dropboxd interactively to authorize:
    
        .dropbox-dist/dropboxd
    Install dropbox:
    
        wget -O .dropbox-dist/dropbox "https://www.dropbox.com/download?dl=packages/dropbox.py"
        chmod +x .dropbox-dist/dropbox
        mkdir -p ~/.config/systemd/user
        cat > ~/.config/systemd/user/dropbox.service << EOF
        [Unit]
        Description=dropbox agent
        After=network.target

        [Service]
        Restart=always
        ExecStart=/usr/bin/env %h/.dropbox-dist/dropboxd
        ExecStop=/usr/bin/env %h/.dropbox-dist/dropbox stop

        [Install]
        WantedBy=default.target
        EOF
    Load the new service into `systemd` and start it.
    
        systemctl --user daemon-reload
        systemctl --user enable dropbox.service
        systemctl --user start dropbox.service
        systemctl --user status dropbox.service
        .dropbox-dist/dropbox status
        echo "alias dropbox=.dropbox-dist/dropbox" >> .zshrc

18. Sort out `udev` rules for scope hardware:
    - Copy `udev-rules` to `/etc/udev/rules.d/20-microscope.rules`
    - Plug in USB TTY devices, run `dmesg` to see the vendor name and serial number, and add this to the rules file.
    - Test, e.g.: `udevadm test $(udevadm info -q path /dev/ttyACM0) |& grep symlink`
    - Then run `sudo udevadm trigger`

19. Install latest andor drivers, but not bitflow (not needed for USB cameras):

        cd "Dropbox/pincuslab-common/Hardware Manuals/Andor Zyla/andor-sdk3-3.13.30034.0"
        sudo ./install_andor
        sudo udevadm trigger

20. Configure persistent jumbo frames if using fiber-optic networking:
    Find out the interface name of the fiber optic card by using `ip link` (it should be the one with `state UP` in its line, with name like `enp101s0`).
    You could also figure it out by finding out the network interface(s) with the `ixgbe` driver:
    
        ls -l /sys/class/net/*/device/driver | grep ixgbe | cut -d"/" -f5
    
    Then run the below, setting the IFNAME variable correctly.
    
        sudo -s
        IFNAME=enp101s0 
        # or: IFNAME=$(ls -l /sys/class/net/*/device/driver | grep ixgbe | cut -d"/" -f5)
        cat > /etc/netplan/99-jumbo-frames.yaml  << EOF
        network:
          version: 2
          ethernets:
            $IFNAME:
              dhcp4: true
              mtu: 9000
        EOF
        netplan generate
        netplan apply
 
21. Install system tracking utilities and make a BTRFS snapshot:

        sudo apt-get install etckeeper
        sudo snapshot create base-system

22. From another computer, run `scp.sh` (after setting the `HOST` variable) to make a backup copy of all relevant config files for that microscope.
