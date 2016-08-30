#!/usr/bin/env scons
# -*- coding: utf-8 -*-

'''
Measure the performance of Santa over various configuration scenarios

We want to know how the performance of Santa scales with the number of sequence being simulated and the number of generations.

'''

import os
import os.path
import glob
import tempfile

from nestly import Nest
from nestly.scons import SConsWrap
from SCons.Script import Environment

from sconsutils import Wait
import sconsutils

environ = os.environ.copy()

env = Environment(ENV=environ)
env.PrependENVPath('PATH', os.path.abspath('santa-sim/target'))
env.PrependENVPath('PATH', 'bin')
env['SANTAJAR']= os.path.abspath('../santa-wercker/dist/santa.jar')
env['SANTACONFIG']= 'santa_config.xml'

n = Nest(base_dict={})
w = SConsWrap(n, 'output', alias_environment=env)

n.add('population', [1000, 3000, 5000, 7000, 10000, 15000, 20000, 50000], label_func=lambda x: "pop"+str(x))

n.add('length', [50, 100, 500, 1000, 1533], label_func=lambda x: "len"+str(x))

n.add('generations', [10000], label_func=lambda x: "gen"+str(x), create_dir=False)
                          
@w.add_target_with_env(env)
def sequence(env, outdir, c):
    return env.Command(
        os.path.join(outdir, "sequence.fa"),
		['templates/gp120.fa'],
		"seqmagick convert --cut :${length} ${SOURCE} ${TARGET}"
        )[0]

@w.add_target_with_env(env)
def config(env, outdir, c):
    return env.Command(
        os.path.join(outdir, "santa_config.xml"),
		['templates/santa_config.xml', '${sequence}'],
		"mksanta.py  -p patient1 ${SOURCES}   >${TARGET}"
        )[0]

@w.add_target_with_env(env)
def santa_lineage(env, outdir, c):
    return env.Command([
                            os.path.join(outdir, "santa.out"),
                            os.path.join(outdir, "logging.properties"),
                            os.path.join(outdir, "srun.log")
                        ],
                        [
                            c['config'],
                            env['SANTAJAR'],
                            'logging.properties'
                        ],
                        [  # santa will produce output files in its current directory.
                          # so need to change to output directory before execution.
                          Copy('${TARGETS[1]}', '${SOURCES[2]}'),
                          'srun --time=120 --chdir=${OUTDIR} --output=${TARGETS[0]} /usr/bin/time --verbose -o time.txt java -mx512m -Djava.util.logging.config.file=${TARGETS[1].file} -jar ${SOURCES[1]} -population=${population} -samplesize=10 -generations=${generations} -seed=1465407525161 ${SOURCES[0].file} 2>&1 | tee ${TARGETS[2]}' 
                        ])[0]



