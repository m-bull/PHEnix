'''Implementation of the Mapper class using Minimap2 (Heng Li) mapper.

:Date: 18 July, 2018
:Author: Matt Bull
'''
from collections import OrderedDict
import logging
import os
import shlex
from subprocess import Popen, PIPE
import subprocess
import tempfile

from phe.mapping import Mapper


class Minimap2Mapper(Mapper):
    '''Minimap2 mapper developed by Heng Li.'''

    _default_options = "-t 1"
    """Default options for the mapper."""
    _cmd = "minimap2"
    """Command for calling mapper."""

    name = "minimap2"
    """Plain text name of the mapper."""

    def __init__(self, cmd_options=None):
        """Constructor for minimap2 mapper."""

        if not cmd_options:
            cmd_options = self._default_options

        super(Minimap2Mapper, self).__init__(cmd_options=cmd_options)

        self.last_command = None

    def create_aux_files(self, ref):
        return True

    def make_sam(self, *args, **kwargs):
        ref = kwargs.get("ref")
        r1 = kwargs.get("R1")
        r2 = kwargs.get("R2")
        out_file = kwargs.get("out_file")
        sample_name = kwargs.get("sample_name", "test_sample")

#        make_aux = kwargs.get("make_aux", False)

        if ref is None or r1 is None or r2 is None or out_file is None:
            logging.error("One of the required parameters is not specified.")
            return False

        d = {"cmd": self._cmd,
             "ref": os.path.abspath(ref),
             "r1": os.path.abspath(r1),
             "r2": os.path.abspath(r2),
             "out_sam":out_file,
             "sample_name": sample_name,
             "extra_options": self.cmd_options
             }

#        if make_aux:
#            if not self.create_aux_files(ref):
#                logging.error("Computing index has failed. Abort")
#                return False

        cmd = r"%(cmd)s -x sr -a -R '@RG\tID:%(sample_name)s\tSM:%(sample_name)s' %(extra_options)s %(ref)s %(r1)s %(r2)s" % d
        logging.debug("CMD: %s", cmd)

        p = Popen(shlex.split(cmd), stdout=d["out_sam"], stderr=subprocess.PIPE)

        stderr = []
        for line in p.stderr:
            line = line.strip()
            logging.debug(line)
            stderr.append(line)

        p.wait()

        if p.returncode != 0:
            logging.error("Mapping reads has failed.")
            logging.error("\n".join(stderr))

            return False

        self.last_command = cmd
        return True

    def get_version(self):

        version = "n/a"

        try:
            p = subprocess.Popen(["minimap2", "--version"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            (output, _) = p.communicate()
        except OSError as e:
            logging.debug("Could not retrieve minimap2 version")
            logging.error(str(e))
            return "n/a"

        if p.returncode != 0:
                version = "n/a"
        else:
            try:
                version = output.rstrip()
            except Exception:
                version = "n/a"
        return version

    def get_info(self, plain=False):

        d = {"name": "minimap2", "version": self.get_version(), "command": self.last_command}

        if plain:
            result = "Minimap2(%(version)s): %(command)s" % d
        else:
            result = OrderedDict(d)

        return result
