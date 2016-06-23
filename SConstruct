#!/usr/bin/env scons
# -*- coding: utf-8 -*-

'''
Measure the performance of Santa over various configuration scenarios

We want to know how the performance of Santa scales with the number of sequence being simulated and the number of generations.

'''



# Simulations for lcfit
import os
import os.path
import glob
import tempfile

from nestly import Nest
from nestly.scons import SConsWrap
from SCons.Script import Environment
from SCons.Action import ActionFactory

environ = os.environ.copy()

env = Environment(ENV=environ)
env.PrependENVPath('PATH', 'bin')
env['SANTAJAR']= os.path.expanduser('~/Development/santa-sim/target/santa-sim-0.0.1-SNAPSHOT.jar')
env['SANTACONFIG']= os.path.expanduser('~/Development/santa-sim/examples/small-indel.xml')
with open(os.path.expanduser('~/Development/santa-sim/cp.txt'), 'r') as fh:
    env['CLASSPATH']= fh.next().strip()

n = Nest(base_dict={})
w = SConsWrap(n, 'output', alias_environment=env)

n.add('population', [1000, 2000, 3000, 4000, 5000, 6000])

n.add('generations', [500, 600, 700, 800, 1000])


@w.add_target_with_env(env)
def santa_lineage(env, outdir, c):
    return env.Command(os.path.join(outdir, "santa.out"),
                       [ env['SANTACONFIG'], env['SANTAJAR'] ],
                       [  # santa will produce output files in its current directory.
                          # so need to change to output directory before execution.
                          Copy('${OUTDIR}/santa_config.xml', '${SOURCES[0]}'),
                          'java -mx512m -Djava.util.logging.config.file="logging.properties" -jar ${SOURCES[1]} -population=${population} -samplesize=10 -generations=${generations} -seed=1465407525161 ${OUTDIR}/santa_config.xml >${TARGET} 2>&1'
                       ])[0]



