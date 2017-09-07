#! /usr/bin/env python

# Collate outputs from system reporting commands into a mardown report pdf file
# this script must be run with sudo access (for now)

from datetime import datetime
from subprocess import check_output, CalledProcessError


cmds = [
    'df -h',
    'fdisk -l | grep Disk | grep /dev/sd',
    'fdisk -l',
    'ls -alh /dev/disk/by-uuid',
    'mount | grep /dev/sd'
]

def gen_preamble():
    s = '# LoFASM IV System Report\n\n'
    s += '## Date Updated: ' + datetime.now().strftime('%m/%d/%Y %H:%M:%S') + '\n\n'
    return s

def format_cmd_output(cmd):
    
    try:
        cmd_result = check_output(cmd, shell=True)
    except CalledProcessError:
        cmd_result = 'Command returned non-zero exit status (FAILED).'


    s = '## ' + cmd + ':\n'
    s += '```\n'
    s += cmd_result + '\n'
    s += '```\n\n'

    return s



if __name__ == '__main__':
    import argparse
    import os

    now_str = datetime.now().strftime('%Y%m%d_%H%M%S')

    p = argparse.ArgumentParser(description='Collate outputs from system reporting commands into a mardown report pdf file')
    p.add_argument('-o', '--output', type=str, default=os.path.join(os.getcwd(), 'system_report_'+now_str+'.md'),
                   dest='out',
                   help='output directory. default is current directory.')
    args = p.parse_args()


    with open(args.out, 'w') as fout:
        fout.write(gen_preamble())

        for cmd in cmds:
            fout.write(format_cmd_output(cmd))
        
    