#!/usr/bin/env python3
import os
import pathlib
import subprocess
import contextlib
import datetime
import argparse
import traceback
import sys

BTRFS_MOUNT = pathlib.Path('/mnt/btrfs-root')
SNAP_DIR = 'snapshots'
DRY_RUN = False

@contextlib.contextmanager
def root_mounted(subvol):
    '''Context manager to mount and unmount the BTRFS root volume at BTRFS_MOUNT.

    Yields both the subvolume's location in the BTRFS root and the snapshot directory for the
    specified subvolume (usually @).
    '''
    unmount = False
    mountpoint = str(BTRFS_MOUNT)
    if not os.path.ismount(mountpoint):
        unmount = True
        subprocess.run(['mount', mountpoint], check=True)
    try:
        yield BTRFS_MOUNT/subvol, BTRFS_MOUNT/SNAP_DIR/subvol
    finally:
        if unmount:
            subprocess.run(['umount', mountpoint], check=True)

def isotoday():
    return datetime.date.today().isoformat()

def btrfs_subvol_run(subcommand, *args):
    '''Run the 'btrfs subvolume' command specified or if in DRY_RUN mode, print out the command.'''
    args = ['btrfs', 'subvolume'] + subcommand.split() + list(map(str, args))
    if DRY_RUN:
        print('DRY RUN:', ' '.join(args))
    else:
        subprocess.run(args, check=True)

def path_cmd(path, method, *args, **kws):
    if DRY_RUN:
        print('DRY RUN:', repr(path)+'.'+method, args, kws)
    else:
        getattr(path, method)(*args, **kws)

def snapshot_create(name, subvol):
    '''Take a read-only snapshot of the specified subvolume (usually @) and store it
    as BTRFS_ROOT/SNAP_DIR/subvolume/name.
    '''
    with root_mounted(subvol) as (src, snap_dir):
        if not snap_dir.exists():
            path_cmd(snap_dir, 'mkdir', parents=True)
        snap = snap_dir / name
        if snap.exists():
            raise ValueError('Snapshot "{}" already exists.'.format(name))
        btrfs_subvol_run('snapshot -r', src, snap)

def snapshot_list(subvol):
    '''List all snapshots of the specified subvolume (usually @) present in
    BTRFS_ROOT/SNAP_DIR/subvolume. Note if any 'defunct' snapshots are left at
    the root level, which remain from rollbacks and should be purged by finish-rollback.
    '''
    with root_mounted(subvol) as (src, snap_dir):
        some_snapshots = False
        if snap_dir.exists():
            for snap in sorted(snap_dir.iterdir()):
                if snap.is_dir():
                    some_snapshots = True
                    print(snap.name)
        post_rollback_dst = src.with_suffix('.defunct')
        if post_rollback_dst.exists():
            some_snapshots = True
            print("Found in-progress rollback subvolume. Run finish-rollback to remove.")
        if not some_snapshots:
            print('No snapshots found.')

def snapshot_delete(names, subvol):
    '''Delete the snapshot of the specified subvolume (usually @) located at
    BTRFS_ROOT/SNAP_DIR/subvolume/name.
    '''
    with root_mounted(subvol) as (src, snap_dir):
        for name in names:
            snap = snap_dir / name
            if not snap.exists():
                raise ValueError('Snapshot "{}" does not exist.'.format(name))
            btrfs_subvol_run('delete', snap)

def snapshot_rollback(name, subvol):
    '''Roll back to the named snapshot of the specified subvolume (usually @).

    This procedure is a bit tricky, as snapshots are made read-only for safety.
    First, a snapshot of the current state of the subvolume is stored at
    BTRFS_ROOT/SNAP_DIR/subvolume/before-rollback-[DATE]
    Next, rename the live subvolume from BTRFS_ROOT/subvolume to BTRFS_ROOT/subvolume.defunct.
    Finally, make a read-write snapshot of the (read-only) BTRFS_ROOT/SNAP_DIR/subvolume/name
    at BTRFS_ROOT/subvolume.
    Now all that remains to do is to reboot so that BTRFS_ROOT/subvolume.defunct is no longer
    the active filesystem, and delete it with the finish-rollback command.
    '''
    with root_mounted(subvol) as (src, snap_dir):
        pre_rollback_snap = snap_dir / 'before-rollback-{}'.format(isotoday())
        if pre_rollback_snap.exists():
            i = 1
            while True:
                new_pre_rollback_snap = pre_rollback_snap.with_suffix('.{}'.format(i))
                if not new_pre_rollback_snap.exists():
                    break
                i += 1
            pre_rollback_snap = new_pre_rollback_snap
        post_rollback_dst = src.with_suffix('.defunct')
        snap = snap_dir / name
        if not snap.exists():
            raise ValueError('Snapshot "{}" does not exist.'.format(name))
        if post_rollback_dst.exists():
            raise ValueError('Rollback already in progress! Run finish-rollback to complete, or revert-rollback to restore previous state.')
        print('Creating snapshot of current state as "{}"'.format(pre_rollback_snap.name))
        btrfs_subvol_run('snapshot -r', src, pre_rollback_snap)
        path_cmd(src, 'rename', post_rollback_dst)
        # NB: the named snapshot is read-only, so make a new, read/write snapshot as the src
        btrfs_subvol_run('snapshot', snap, src)
        print('To complete rollback, reboot and run finish-rollback command. To revert, run revert-rollback.')

def snapshot_finish_rollback(subvol):
    '''Finish a rollback of the specified subvolume (usually @) by removing the
    BTRFS_ROOT/subvolume.defunct subvolume.'''
    with root_mounted(subvol) as (src, snap_dir):
        post_rollback_dst = src.with_suffix('.defunct')
        if not post_rollback_dst.exists():
            raise ValueError('No rollback in progress!')
        btrfs_subvol_run('delete', post_rollback_dst)

def snapshot_revert_rollback(subvol):
    '''Undo an in-progress rollback of the specified subvolume (usually @). This entails
    switching BTRFS_ROOT/subvolume.defunct (the pre-rollback state) and
    BTRFS_ROOT/subvolume (the post-rollback state). Once these are switched,
    reboot so that BTRFS_ROOT/subvolume.defunct (the old BTRFS_ROOT/subvolume) is no longer
    the active filesystem, and delete it with the finish-rollback command.
    '''
    with root_mounted(subvol) as (src, snap_dir):
        post_rollback_dst = src.with_suffix('.defunct')
        rollback_temp = src.with_suffix('.temp')
        if not post_rollback_dst.exists():
            raise ValueError('No rollback in progress!')
        # swap roles of src and post_rollback_dst, via a temp name
        path_cmd(src, 'rename', rollback_temp)
        path_cmd(post_rollback_dst, 'rename', src)
        path_cmd(rollback_temp, 'rename', post_rollback_dst)
        print('To complete reverting rollback, reboot and run finish-rollback command.')

def main(argv):
    parser = argparse.ArgumentParser(description='zplab btrfs snapshot tool')
    parser.add_argument('-d', '--debug', action='store_true', help='show full stack traces on error')
    parser.add_argument('--dry-run', action='store_true', help='do not run any btrfs commands, just print them')
    parser.add_argument('--subvol', default='@', help='subvolume to snapshot; usually @ or @home (default: %(default)s)')
    subparsers = parser.add_subparsers(help='sub-command help', dest='command')
    subparsers.required = True
    parser_create = subparsers.add_parser('create', help='create a named shapshot')
    parser_create.add_argument('name', nargs='?', default=isotoday(), help='(default: %(default)s)')
    parser_create.set_defaults(command=snapshot_create)
    parser_list = subparsers.add_parser('list', help='list existing snapshots')
    parser_list.set_defaults(command=snapshot_list)
    parser_delete = subparsers.add_parser('delete', help='delete a named shapshot')
    parser_delete.add_argument(dest='names', metavar='name', nargs='+')
    parser_delete.set_defaults(command=snapshot_delete)
    parser_rollback = subparsers.add_parser('rollback', help='rollback to a named shapshot, creating a "rollback" snapshot of the current state')
    parser_rollback.add_argument(dest='name')
    parser_rollback.set_defaults(command=snapshot_rollback)
    parser_finish = subparsers.add_parser('finish-rollback', help='finish in-progress rollback after reboot')
    parser_finish.set_defaults(command=snapshot_finish_rollback)
    parser_revert = subparsers.add_parser('revert-rollback', help='revert in-progress rollback')
    parser_revert.set_defaults(command=snapshot_revert_rollback)

    args = parser.parse_args(argv)

    if args.dry_run:
        global DRY_RUN
        DRY_RUN = True
    arg_dict = dict(vars(args))
    del arg_dict['debug']
    del arg_dict['dry_run']
    del arg_dict['command']
    try:
        args.command(**arg_dict)
    except Exception as e:
        if args.debug:
            traceback.print_exc(file=sys.stderr)
        else:
            sys.stderr.write(str(e)+'\n')
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv[1:]))

