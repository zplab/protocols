# Kubuntu installation for zplab microscopes

1. install Kubuntu from a USB drive:
  - Download the latest LTS release ISO file and transfer it to a USB drive:
    - If on Kubuntu, run `usb-creator-kde` (may need to install with `apt` first) to transfer the ISO to the USB drive.
    - If on a Mac, you can use Etcher to do this.
    - In either case, do **not** use UNetbootin, which can't make UEFI-bootable drives. This is now the preferred option, and it can be difficult to boot with BIOS-mode USB disks nowadays.
  - Reboot the target machine and select the USB disk (select the UEFI OS partition, if it appears).
  - Install Kubuntu, using the following partition scheme on the system SSD:
    - 200 MB EFI partition
    - 256 GB / btrfs
    - remaining /home ext4
    - Install bootloader on whole SSD device (rather than a specific partition)

2. Install basic tools:

       sudo apt update
       sudo apt install ssh
       sudo apt remove --purge libreoffice*
       sudo apt remove --purge mysql*
       sudo apt clean
       sudo apt autoremove
       sudo apt full-upgrade
       
3. Install video drivers. Use latest recommended (440 is example here):

       sudo add-apt-repository ppa:graphics-drivers/ppa
       sudo apt update
       sudo apt install nvidia-driver-440

4. Install and configure `mdadm`, the RAID manager:

       sudo apt install mdadm
   Now edit `/etc/mdadm/mdadm.conf` to uncommment or add these lines:
   
       DEVICE partitions
       HOMEHOST <system>
       AUTO +homehost
       MAILADDR zpincus@wustl.edu
       MAILFROM mdadm@zpl-scope.wucon.wustl.edu
       
   The `MAILFROM` line should reflect the scope's name obviously. If an existing RAID was found, comment it out the line adding it by UUID. We'll just use partition scanning to find RAID devices.

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
    
    (where `ARRAYNAME` is replaced by whatever (lower-case) name for the array you desire)
6. Install XFS:

       sudo apt install xfsprogs
   If the RAID is new, make an XFS filesystem on it: 
   
       sudo mkfs -t xfs /dev/md/ARRAYNAME

7. Make a mount-point for the RAID and add it to the FSTAB:

       sudo mkdir /mnt/ARRAYNAME
       lsblk -o uuid /dev/md/ARRAYNAME
   edit `/etc/fstab` to add:
   
       UUID=uuid /mnt/ARRAYNAME xfs noatime,inode64 0 2
   where `uuid` is replaced by the output of `lsblk` above. Now mount the
   array and make it read/write by zplab:
   
       sudo mount /mnt/ARRAYNAME
       sudo chown -R zplab:zplab /mnt/ARRAYNAME
       sudo chmod -R 775 /mnt/ARRAYNAME
   
8. Add a swapfile (the default swapfile on the BTRFS root won't work, so we need to put it on the ext4 /home mount)

       sudo -s
       swapon --show # should show no swap in use
       fallocate -l 6G /home/swapfile
       chmod 600 /home/swapfile
       mkswap /home/swapfile
       swapon /home/swapfile
       pico /etc/fstab # edit /swapfile to /home/swapfile
       rm /swapfile
       swapon --show

9. Install `zsh`:

       sudo apt install zsh
       chsh --shell `which zsh` zplab
       cat > ~/.zshrc << 'EOF'
       setopt hist_ignore_dups
       setopt append_history
       HISTSIZE=100000
       SAVEHIST=100000
       HISTFILE=~/.zsh_history

       autoload -U history-search-end
       zle -N history-beginning-search-backward-end history-search-end
       zle -N history-beginning-search-forward-end history-search-end

       bindkey -e
       bindkey "${key[Up]}" history-beginning-search-backward-end
       bindkey "${key[Down]}" history-beginning-search-forward-end

       autoload -U colors && colors
       prompt="%{$bold_color$fg[red]%}[%{$fg[blue]%}%n@%m:%{$fg[green]%}%25<..<%~%<<%{$fg[red]%}]%{$fg[green]%}%(!.#.>)%{$reset_color%} "

       setopt correct
       export SPROMPT="Correct %{$fg_bold[red]%}%R%{$reset_color%} to %{$fg_bold[green]%}%r%{$reset_color%}? ([No], Yes, Abort, Edit) "

       autoload -Uz compinit && compinit

       alias ls='ls --color=auto'
       alias grep='grep --color=auto'
       alias fgrep='fgrep --color=auto'
       alias egrep='egrep --color=auto'
       EOF

10. Install SMB

        sudo apt install samba
        
    Edit `/etc/samba/smb.conf` to add or change (where again, `ARRAYNAME` is replaced by the actual name of the disk array to share):
    
        workgroup = ZPLAB
        server string = %h (zplab microscope)
        [homes]
           comment = Home Directories
           browseable = no
           writeable = yes
           veto files = /._*/.DS_Store/
           delete veto files = yes
        
        [ARRAYNAME]
           path = /mnt/ARRAYNAME
           browseable = yes
           writeable = yes
           veto files = /._*/.DS_Store/
           delete veto files = yes
    Run:
    
        sudo smbpasswd -a zplab
        sudo smbd reload

11. Enable RAID monitoring:

        sudo apt install msmtp msmtp-mta
        sudo cat > /etc/msmtprc << EOF
        account default
        host osmtp.wustl.edu
        from zplab@${HOST}.wustl.edu
        syslog LOG_MAIL
        EOF

        sudo apt install smartmontools
    Edit /etc/smartd.conf so that the first DEVICESCAN line reads:
    
        DEVICESCAN -H -l error -l selftest -f -s (O/../.././00|S/../.././12|L/../01/./06) -m zpincus@wustl.edu -M diminishing
    Then run:
    
        sudo service smartd start
        sudo service mdmonitor start

12. Install various useful tools and do some cleanup:

        sudo apt install libfftw3-dev libsdl2-2.0 screen minicom iftop curl qpdfview git virtualbox automake
        cd ~
        rmdir Downloads Music Pictures Templates Videos Public

13. Install tools for making BRTFS snapshots.  
    Edit `/etc/fstab` to add special mount point for the BRTFS root (usually not exposed, as the linux root is the BTRFS subvolume called '@').
    
        UUID=uuid /mnt/btrfs-root btrfs defaults,subvol=/,noauto 0 1
    Note: UUID should is the same as the other btrfs UUID for the @ subvol in fstab  
    Run:
    
        sudo -s
        mkdir /mnt/btrfs-root/
        mount /mnt/btrfs-root/
        chmod go-rwx /mnt/btrfs-root
    Copy `snapshot.py` to `/usr/local/bin/snapshot` and set the permissions:
    
        curl -o /usr/local/bin/snapshot https://raw.githubusercontent.com/zplab/protocols/master/computer%20protocols/install%20ubuntu/snapshot.py
        chown root:root /usr/local/bin/snapshot
        chmod u+x /usr/local/bin/snapshot

14. Add zplab to dialout group (who can open ttys):

        sudo usermod -a -G dialout zplab

15. Install miniconda:

        wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
        sudo bash Miniconda3-latest-Linux-x86_64.sh -p /usr/local/miniconda3 -b
        rm Miniconda3-latest-Linux-x86_64.sh
        source /usr/local/miniconda3/bin/activate
        conda init zsh
    Now allow running miniconda programs with sudo (like pip):
    
        sudo visudo
    and add `/usr/local/miniconda3/bin` to `Defaults secure_path` line.
        
    Next, keep miniconda from always showing that we're using the `base` environment:
    
        sudo -s
        mkdir -p /usr/local/miniconda3/etc/conda/activate.d
        cat > /usr/local/miniconda3/etc/conda/activate.d/remove_base_ps1.sh << 'EOF'
        PS1="$(echo $PS1 | sed 's/(base) //')"
        EOF
    
    Create our default conda environment:
            
        sudo pip install --upgrade pip
        sudo conda update conda
        export PIP_SRC="/usr/local/scope/py_src"
        sudo mkdir /usr/local/scope
        cat > scope_env.yml << EOF
        channels:
            - defaults
            - conda-forge

        dependencies:
            - python>=3.6
            - ipython
            - numpy
            - scipy
            - scikit-learn
            - pyopengl
            - cython
            - cffi
            - pyfftw
            - python-daemon
            - pyserial
            - zeromq>=4.2.6
            - pyzmq
            - python-blosc
            - pip
            - pip:
                - PyQt5
                - matplotlib
                - scikit-image
                - qtconsole
                - PySDL2
                - git+https://github.com/zplab/freeimage-py
                - git+https://github.com/zplab/zplib
                - git+https://github.com/zplab/RisWidget
                - git+https://github.com/zplab/SharedMemoryBuffer
                - git+https://github.com/zplab/IOTool#subdirectory=py
                - -e git+https://github.com/zplab/rpc-scope#egg=scope
                - -e git+https://github.com/zplab/elegant#egg=elegant
        EOF
        
        sudo -E conda env update -n base -f scope_env.yml
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
        cat > ~/.ipython/profile_default/ipython_config.py << EOF
        c.TerminalIPythonApp.display_banner = False
        c.TerminalInteractiveShell.confirm_exit = False
        c.TerminalInteractiveShell.display_completions = 'readlinelike'
        EOF
    
    Also install the worm segmentation tools. Copy over the latest release distribution (e.g. `worm_segmenter-1.zip`) and then run:
    
        unzip worm_segmenter-1.zip
        rm worm_segmenter-1.zip
        sudo pip install ./worm_segmenter-1
    
16. Install scope-server tools:

        sudo job_runner_check --install
        scope_job_runner add `which incubator_check`
    Copy `fftw_wisdom` over to `/usr/local/scope` if it was previously calculated **on this machine**. Then run `scope_server`, stop it, and edit
    the newly-created `/usr/local/scope/configuration.py` file as appropriate.

17. Sort out `udev` rules for scope hardware:
      
        cat > /etc/udev/rules.d/20-microscope.rules << EOF
        ## Make descriptive symlinks in /dev to various microscopy devices
        # Leica microscope
        SUBSYSTEM=="tty", ATTRS{product}=="USB <-> Serial", ATTRS{manufacturer}=="FTDI", SYMLINK+="ttyScope"

        # Lumencor Spectra lamp
        SUBSYSTEM=="tty", ATTRS{product}=="FT232R USB UART", ATTRS{manufacturer}=="FTDI", ATTRS{serial}=="A506OLA5", SYMLINK+="ttySpectra"

        # PolyScience circulator
        SUBSYSTEM=="tty", ATTRS{product}=="VNC1-A As Slave", ATTRS{manufacturer}=="FTDI", SYMLINK+="ttyCirculator"

        # IOTool interface box
        SUBSYSTEM=="tty", ATTRS{product}=="IOTool", ATTRS{manufacturer}=="zplab.wustl.edu", ATTRS{serial}=="0xFFFA", SYMLINK+="ttyIOTool"

        # Humidity controller
        SUBSYSTEM=="tty", ATTRS{product}=="USB-RS232 Cable", ATTRS{manufacturer}=="FTDI", ATTRS{serial}=="FT1XDRGS", SYMLINK+="ttyHumidifier"
        EOF
    
    - To customize the rule file as needed, plug in USB TTY devices, run `dmesg` to see the vendor name and serial number, and add this to the rules file.
    - Test, e.g.: `udevadm test $(udevadm info -q path /dev/ttyACM0) |& grep symlink`
    - Then run `sudo udevadm trigger`

18. Install latest andor drivers, but not bitflow (not needed for USB cameras).

    First, download the latest [Andor SDK](https://wustl.box.com/s/3jvw5rou1ttv0ecd7t4bbla8m1l60mde) and install:
    
        unzip andor-sdk3-*
        rm andor-sdk3-*.zip
        cd andor-sdk3-*
        sudo ./install_andor
        sudo udevadm trigger
        rm -r andor-sdk3-*

19. Configure persistent jumbo frames if using fiber-optic networking:
    Find out the interface name of the fiber optic card by using `ip link` (it should be the one with `state UP` in its line, with name like `enp101s0`).
    You could also figure it out by finding out the network interface(s) with the `ixgbe` or `atlantic` driver, e.g.:
    
        ls -l /sys/class/net/*/device/driver | grep -E 'atlantic|ixgbe' | cut -d"/" -f5
    
    Then run the below, setting the IFNAME variable correctly.
    
        sudo -s
        IFNAME=enp101s0 
        # or: IFNAME=$(ls -l /sys/class/net/*/device/driver | grep -E 'atlantic|ixgbe' | cut -d"/" -f5)
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

20. *(optional)* Install CUDA tools per the [NVIDIA install guide](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html). 
    
    First, make sure you have the appropriate header files for building kernel modules:

        sudo apt install linux-headers-$(uname -r)
    
    Then follow the instructions here: https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&target_distro=Ubuntu&target_version=1804&target_type=debnetwork. **NB: change the `target_version` parameter to whatever LTS release you are using; the link above is only for 18.04**. For the record, the instructions for 18.04 look like this:
    
        wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-ubuntu1804.pin
        sudo mv cuda-ubuntu1804.pin /etc/apt/preferences.d/cuda-repository-pin-600
        sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/7fa2af80.pub
        sudo add-apt-repository "deb http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/ /"
        sudo apt update
        sudo apt -y install cuda

    Then add `export PATH=/usr/local/cuda/bin:${PATH}` to the `.zshrc` file. To test the CUDA install, the following should be a rough guide:
    
        nvidia-smi # should give expected driver and CUDA versions
        nvcc --version # should show expected version
        systemctl status nvidia-persistenced.service # service should be active
        cuda-install-samples-10.2.sh ~
        cd NVIDIA_CUDA-10.2_Samples/1_Utilities/deviceQuery
        make
        ./deviceQuery
        cd ../bandwidthTest
        make
        ./bandwidthTest --device=all
    
    To install `nvidia-docker`, first install Docker per the [official instructions](https://docs.docker.com/install/linux/docker-ce/ubuntu/) then install Nvidia-docker per [its instructions](https://github.com/NVIDIA/nvidia-docker/blob/master/README.md).
    
    Last, install pytorch using pip (*not conda*, as conda wants to install its own CUDA tools version):
        
        sudo pip install torch torchvision
    
21. Install system tracking utilities and make a BTRFS snapshot:

        sudo apt install etckeeper
        sudo snapshot create base-system

22. From another computer, run `scp.sh` (after setting the `HOST` variable) to make a backup copy of all relevant config files for that microscope.
