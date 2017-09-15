#! /usr/bin/env python

# Collate outputs from system reporting commands into a mardown report pdf file
# this script must be run with sudo access (for now)

# !!! DANGEROUS !!!: this script is executed with root privileges

from datetime import datetime
from subprocess import Popen, PIPE
import os
from lofasm import getConfig

class SubSystemReport(object):
    def __init__(self, cmd='', title=''):
        '''
        if cmd is given then shell mode is assumed. 
        otherwise the run() function must be overloaded by the 
        instance to achieve the desired behavior. run() 
        must populate stdout and stderr members.
        '''

        assert cmd or title, "Either cmd or title must be set!"

        self.title = title if title else cmd
        self.shell = True if cmd else False
        self.cmd = cmd
        self.stdout = ''
        self.stderr = ''
            
    def run(self):
        self.stdout, self.stderr = self._execute_cmd()
    
    def _execute_cmd(self):
        '''
        execute shell command and return output as a string

        Returns
        =======
        output: tuple
            (stdout, stderr)
        '''
        cmd = self.cmd
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        return p.communicate()
    

class FullSystemReport(object):
    def __init__(self, cfgpath="/home/controller/.lofasm/lofasm.cfg"):

        cfg = getConfig(cfgpath) # read configuration file and load into memory
        self.station = cfg['station_id'] if cfg.has_key('station_id') else "None"
        self.cfg = cfg
        self.reportList = [] # elements must be a SubSystemReport instance
        self._buf = '' # write buffer


    def _gen_preamble(self):
        tstamp = datetime.now()
        now = tstamp.strftime('%m/%d/%Y %H:%M:%S')
        self.timestamp = tstamp
        s = '# LoFASM {} System Report\n\n'.format(self.station) 
        s += '# Date Created: ' + now + ' UTC\n\n'
        return s

    def _format_report_entry(self, report):
        '''
        encapsulate subsystem report results into a markdown code block.

        Parameters
        ======
        report: SubSystemReport instance
            SubSystemReport object whose execution results will be formatted

        Returns
        ======
        result: str
            string with original data encapsulated.
        '''

        (pout, perr) = report.stdout, report.stderr
        s = '## ' + report.title + ':\n'
        s += '```\n'
        s += pout+'\n\n' if pout else '**NO STDOUT GENERATED**\n\n'
        s += perr+'\n\n' if perr else 'No Errors Generated.\n\n'
        s += '```\n\n'
        return s

    def generate_report(self):
        '''
        generate full report and save in memory as a string
        '''
        buf = ''
        buf += self._gen_preamble()
        for rep in self.reportList:
            rep.run() # place results in rep.stdout and rep.stderr
            buf += self._format_report_entry(rep)
        self._buf += buf

    def save(self, outdir=''):
        sn = str(self.station) if self.station else '0'
        fname = self.timestamp.strftime('%m%d%y_%H%M%S')+'_'+sn+'.md'
                
        with open(os.path.join(outdir, fname), 'w') as f:
            f.write(self._buf)
    


#         # ping roach
#         # check active bof file
#         # check incoming packets
#         # check if recording data
#         #############################
#         # waterplot (24 hour)
#         # sky plot (fast)
#         subsystems['lofasm'] = [
#             [str(self.cfg), 'LoFASM Recorder Configuration']
#         ]


#         # diagnostic shell commands. 
#         # !!! DANGEROUS !!!: this file is executed with root privileges

SHELLCMDS = ['df -h',
             'fdisk -l | grep Disk | grep /dev/sd',
             'fdisk -l',
             'ls -alh /dev/disk/by-uuid',
             'mount | grep /dev/sd']


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser(
        description='Collate outputs from system reporting commands into a mardown report pdf file')
    p.add_argument('-o', '--output', type=str, default=os.getcwd(),
                   dest='out',
                   help='output directory. default is current directory.')
    args = p.parse_args()


    subReports = [SubSystemReport(x) for x in SHELLCMDS]
    fullReport = FullSystemReport()
    fullReport.reportList = subReports
    fullReport.generate_report()
    fullReport.save(outdir=args.out)