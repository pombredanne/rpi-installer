#!/usr/bin/python
"""Script for building SD card (Raspbian) image for Raspberry Pi.

This module will build a netinstaller image for Raspberry Pi using latest
Raspbian packages and flash it onto an SD card.
"""

from __future__ import print_function
import os
import subprocess
import sys
import time
import argparse
import logging

log = None
ok_ret_codes = [0]
CRTIME = time.strftime('%Y%m%d')


class _AttributeString(str):

    @property
    def stdout(self):
        return str(self)


def exit_if_failed(result):
    if result.failed:
        print('Failed!')
        sys.exit(1)


def question_yes_no(question, default='yes'):
    """Prompt a question."""
    valid = {'yes': 'yes', 'y': 'yes', 'ye': 'yes', 'no': 'no', 'n': 'no'}
    if not default:
        prompt = '[y/n]'
    elif default == 'yes':
        prompt = '[Y/n]'
    elif default == 'no':
        prompt = '[y/N]'
    else:
        raise ValueError('Invalid default answer: %s' % default)

    while 1:
        choice = raw_input('%s %s ' % (question, prompt)).lower()
        if default and not choice:
            return default
        elif choice in valid:
            return valid[choice]
        else:
            print('Please respond with "yes" or "no" (or "y" or "n").')


def list_devices():
    """List disk devices."""
    print(sudo('fdisk -l | grep -E "Disk /dev/"', capture=True))


def select_device():
    """Select disk device.

    Returns:
      Selected disk device.
    """
    verified = 'no'
    while verified is not 'yes':
        print('Select the "Disk" you would like the image being flashed to:')
        list_devices()
        device = raw_input('Enter your choice here (e.g. "mmcblk0" or "sdd"): ')
        if not device.startswith('/dev/'):
            device = '/dev/' + device
        if os.path.exists(device):
            print ('It is your own responsibility to ensure '
                   'there is no data loss!')
            print('Please backup your system before creating the image.')
            answer = question_yes_no(
                'Are you sure you want to install the image to '
                '"\033[31m%s\033[0m"?' % device, default='no')
            if answer == 'no':
                sys.exit(1)
            else:
                verified = 'yes'
        else:
            print('Device "%s" does not exist' % device)
    return device


def sudo(command, capture=False, shell=None):
    """Execute a local command with root priveleges."""
    sudo_prompt = 'sudo password:'
    sudo_prefix = 'sudo -S -p "%s" ' % sudo_prompt
    command = sudo_prefix + command
    return run(command, capture, shell)


def run(command, capture=False, shell=None):
    """Execute a local command."""
    log.debug('[localhost] run: ' + command)
    if capture:
        out_stream = subprocess.PIPE
        err_stream = subprocess.PIPE
    else:
        out_stream = None
        err_stream = None
    proc = subprocess.Popen(command, shell=True, stdout=out_stream,
                            stderr=err_stream, executable=shell)
    (stdout, stderr) = proc.communicate()

    out = _AttributeString(stdout.strip() if stdout else '')
    err = _AttributeString(stderr.strip() if stdout else '')
    out.command = command
    out.failed = False
    out.return_code = proc.returncode
    out.stderr = stderr
    if proc.returncode not in ok_ret_codes:
        out.failed = True
        print ('run() encountered an error (return code %s) '
               'while executing "%s"' % (proc.returncode, command))
    out.succeeded = not out.failed
    return out


def build():
    """Wrapper function around build scripts."""
    result = run('./clean.sh')
    exit_if_failed(result)
    result = run('./build.sh')
    exit_if_failed(result)
    result = sudo('./buildroot.sh')
    exit_if_failed(result)


def flash(dev):
    """Flash image onto device.

    Args:
      dev: The device where the image will be flashed to.
    """
    sudo("umount `mount | grep %s | cut -f1 -d ' '`" % dev)
    sha1 = run('git rev-parse --short @{0}', capture=True)
    img = 'raspbian-ua-netinst-%s-git%s.img' % (CRTIME, sha1)
    print('Copying "%s" to "%s"...' % (img, dev))
    result = sudo('dd if=%s of=%s bs=1M' % (img, dev))
    exit_if_failed(result)
    result = run('sync')
    exit_if_failed(result)


def parse_command_line():
    """Configure and parse our command line flags."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--debug',
        action='store_true',
        default=False,
        help='Enable debug messages.')
    return parser.parse_args(sys.argv[1:])


def configure_logging(debug=False):
    """Configure the log global and message format."""
    overall_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        format='%(message)s',
        level=overall_level)
    global log
    log = logging.getLogger('flashimage')


def main():
    """First build, then flash it onto the selected device."""
    config = parse_command_line()
    configure_logging(debug=config.debug)
    raw_input('Insert your SD card and press any key to continue...')
    build()
    dev = select_device()
    flash(dev)
    print('Done!')


if __name__ == '__main__':
    main()

