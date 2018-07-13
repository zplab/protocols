# Basic rsync usage

### General command line usage
`rsync --recursive --times --human-readable [[user@]host:]src [[user@]host:]dst`

### Useful options in some cases:
- `--size-only` (only compares files by size, not modification date)
- `--delete` (delete items from dest that do not exist in src)
- `--itemize-changes` (be very clear about what's changing)
- `--dry-run` (just print what would happen)
- `--info=progress2` (linux only, shows total progress percent)
- `--verbose`

**Note** when specifying src, a trailing slash after a directory name means "copy the contents of src into dst" rather than "copy src into dst".

### Running an rsync daemon on the cluster (a bit faster)
1. Set up the basic configuration files (make sure to replace `some-password-here` with an actual password)
        password=your-password-here
        cat > ~/rsync.conf << EOF
        pid file = /home/$USER/rsync.pid
        log file = /home/$USER/rsync.log
        secrets file = /home/$USER/rsync.secrets
        port = 8082
        use chroot = false

        [home]
            path = /home/$USER
            read only = false
            auth users = $USER
            
        [scratch]
            path = /scratch/$USER
            read only = false
            auth users = $USER
        EOF
        cat > ~/rsync.secrets << EOF
        $USER:$password
        EOF
        chmod go-r ~/rsync.secrets
    (You only need to do this once...)
2. Next, run the `rsync` daemon on a login or data transfer node in the cluster. Without the `--no-detatch` option, the `rsync` daemon will run in the background, listening for connections until you kill it with `kill \`cat ~/rsync.pid\``. With `--no-detatch`, it runs in the foreground until you kill it with control-c.
        rsync --daemon --config=~/rsync.config --no-detatch 
3. Then transfer files, more or less as ususal:
        rsync [options] --port=8082 src_files user@chpc_host::home/path/to/dst/
    The 'user' should be your CHPC user, and 'chpc_host' should be the login or data transfer node on which you are running the rsync daemon. The first word after the double-colon is 'home' or 'scratch' depending on which "shared directory" (specified in the config file) you want to transfer to.
