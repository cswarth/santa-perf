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

environ = os.environ.copy()

env = Environment(ENV=environ)
env.PrependENVPath('PATH', os.path.abspath('santa-sim/target'))
env.PrependENVPath('PATH', 'bin')
env['SANTAJAR']= os.path.abspath('santa-sim/dist/santa.jar')
env['SANTACONFIG']= 'santa_config.xml'

n = Nest(base_dict={})
w = SConsWrap(n, 'output', alias_environment=env)

n.add('population', [1000, 2000, 3000, 4000, 5000, 10000, 50000, 100000], label_func=lambda x: "pop"+str(x))

n.add('generations', [500, 700, 1000, 10000], label_func=lambda x: "gen"+str(x))

@w.add_target_with_env(env)
def config(env, outdir, c):
    return env.Command(os.path.join(outdir, "santa_config.xml"),
                        [ env['SANTACONFIG'] ],
                        Copy('${OUTDIR}/santa_config.xml', '${SOURCES[0]}'))

@w.add_target_with_env(env)
def logconfig(env, outdir, c):
    return env.Command(os.path.join(outdir, "logging.properties"),
                       'logging.properties',
                       Copy('${OUTDIR}/logging.properties', '${SOURCE}'))
                          

@w.add_target_with_env(env)
def santa_lineage(env, outdir, c):
    return env.Command(os.path.join(outdir, "santa.out"),
                       [ c['logconfig'], c['config'], env['SANTAJAR'] ],
                       [  # santa will produce output files in its current directory.
                          # so need to change to output directory before execution.
                          'java -mx512m -Djava.util.logging.config.file=${SOURCES[0].file} -jar ${SANTAJAR} -population=${population} -samplesize=10 -generations=${generations} -seed=1465407525161 ${SOURCES[1].file} >${TARGET.file} 2>&1'
                       ], chdir=1)[0]

#                          'java_args="-mx512m -Djava.util.logging.config.file=${SOURCES[0].file}" santa -population=${population} -samplesize=10 -generations=${generations} -seed=1465407525161 ${SOURCES[1].file} >${TARGET.file} 2>&1'


# @w.add_target_with_env(env)
# def santa_lineage(env, outdir, c):
#     return env.Command(os.path.join(outdir, "santa.out"),
#                        [ c['logconfig'], c['config'], env['SANTAJAR'] ],
#                        [  # santa will produce output files in its current directory.
#                           # so need to change to output directory before execution.
#                           'java -mx512m -Djava.util.logging.config.file=${SOURCES[0].file} -jar ${SANTAJAR} -population=${population} -samplesize=10 -generations=${generations} -seed=1465407525161 ${SOURCES[1].file} >${TARGET.file} 2>&1'
#                        ], chdir=1)[0]



