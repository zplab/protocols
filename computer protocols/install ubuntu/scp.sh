#HOST=zpl-scope
scp zplab@$HOST:/etc/udev/rules.d/20-microscope.rules $HOST
scp zplab@$HOST:/etc/fstab $HOST
scp zplab@$HOST:/etc/mdadm/mdadm.conf $HOST
scp zplab@$HOST:/etc/exports $HOST
scp zplab@$HOST:/etc/samba/smb.conf $HOST
scp zplab@$HOST:/usr/local/scope/configuration.py $HOST
scp zplab@$HOST:/usr/local/scope/fftw_wisdom $HOST
