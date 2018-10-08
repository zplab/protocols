#HOST=zpl-scope
for HOST in zpl-scope zpl-iscope zpl-purple zpl-9000
do
    if [ ! -d $HOST ]
    then
        mkdir $HOST
    fi
    scp zplab@$HOST:/etc/udev/rules.d/20-microscope.rules $HOST
    scp zplab@$HOST:/etc/fstab $HOST
    scp zplab@$HOST:/etc/mdadm/mdadm.conf $HOST
    scp zplab@$HOST:/etc/samba/smb.conf $HOST
    scp zplab@$HOST:/usr/local/scope/configuration.py $HOST
    scp zplab@$HOST:/usr/local/scope/fftw_wisdom $HOST
    scp zplab@$HOST:/etc/netplan/99-jumbo-frames.yaml $HOST
done