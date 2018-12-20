# Tape Backup Protocol
Author: Zachary Pincus  
Date: 2018-12-18
http://zplab.wustl.edu


`zpl-purple` has an [LTO Ultrium 6 tape drive](https://en.wikipedia.org/wiki/Linear_Tape-Open) installed. For planning how much to put on any one tape, the uncompressed capacity of LTO-6 tapes is 2.5 TB. (Higher "compressed capacities" are advertised, but compression won't actually get us anything for PNG images which are already compressed.) 

Note that tapes are strictly for offline data storage; they are not random-access storate. Thus the procedure is to dump a set of files to a tape using the `tar` utility and store the tape until the files are needed again. At that point, you need to restore either all or a subset of those files to a hard drive to make use of them. 

Also, while only `zpl-purple` has the tape drive, you can use it to back up or restore files from other computers on the network. Just use `smb` to mount the shared directory on `zpl-purple` and follow the instructions below.

### Tape labeling

Tapes should be labeled as follows (using 5/8×3" Avery durable labels -- **not lab tape!** -- and permanent marker):
1) Your name.
2) Name(s) of directory/directories backed up.
3)  `YYYY-MM-DD` [ISO 8601 date](https://en.wikipedia.org/wiki/ISO_8601) if not part of directory name.
4) Brief description of data.
5) Tape number (`x of y`) in the case that multiple tapes are used for a given `tar` archive (see below).

### How to create and restore files with `tar`

**Important:** Don't try to back up multiple `tar` archives on a single tape. It's possible, but not worth the trouble. You can put multiple experiment directories in a single archive, though. Do strive to mostly fill up tapes (i.e. don't back up only 100 GB of files onto a 2.5 TB tape), but no need to go to extremes. Tapes are relatively cheap, so choose a backup strategy that makes sense over one that fills all tapes to capacity.

1) Insert a tape into the drive, and double-check that compression is disabled:

       sudo tapeinfo -f /dev/st0 | grep DataCompEnabled
       
    If the output is `DataCompEnabled: yes` then you need to disable compression:

       sudo mt-st -f /dev/st0 compression 0

2) Move to the directory immediately *above* the directory you wish to back up (so that you can give `tar` a relative path, making life easier). E.g. if you need to back up `/mnt/purplearray/zpincus/experiment_1`, then:

       cd /mnt/purplearray/zpincus

3) Create a `tar` archive of the directory or directories to be compressed:

       sudo tar -cvMf /dev/st0 experiment_1

   or 

       sudo tar -cvMf /dev/st0 experiment_1 experiment_2 [...]

   The `-M` flag means that if the tape runs out of room, you will be prompted to eject the tape and put a new one in to continue the archiving. (See below for ejecting.)
   
4) Eject the tape:

       sudo mt-st -f /dev/st0 offiline

   **Make sure to label the tape *immediately* after ejecting it!** This is doubly important when a single archive is spread across multiple tapes: you really don't want get the tape numbers confused: to restore the data, you'll need to insert the tapes in the correct order.

5) Make sure the archive still looks good. Re-insert the tape, then run:

       sudo tar -dMf /dev/st0 experiment_1 [experiment_2 ...]

   This will run tar in file-list diff mode, noting any differences between the archive and the disk in terms of file name and size. (If multiple tapes are used, you'll be prompted to insert them as needed.)

6) To list the contents of an archive:

       sudo tar -tMf /dev/st0

7) To extract an archive:

       sudo tar -xvMf /dev/st0 -C /path/to/extraction/point

   If the archive was compressed as above with a relative path to `experiment_1`, then the output files will be in `/path/to/extraction/point/experiment_1/`.

   If the `-C /path/to/extraction/point` part is omitted, files will be extracted to the working directory.

   To extract specific subdirectories, list their names (exactly as specified in a listing of the tar archive) at the end of the command line, e.g.:
   
       sudo tar -xvMf /dev/st0 experiment_1/dir_1 experiment_1/dir_2/sub_3 [...]
    
    (This works with the `-C` option too.)
   
Most of the above is standard `tar` usage, with the only wrinkle being the use of `/dev/st0` and the `-M` option. Consult the [`tar` man page](http://manpages.ubuntu.com/manpages/cosmic/man1/tar.1.html) for more details, or any number of online tutorials.

