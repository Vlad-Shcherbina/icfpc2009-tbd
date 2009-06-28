from __future__ import with_statement

import sys
import time
import os
import re

import solvers
import solvers.hohmann
import solvers.meetgreet

import vm
from vm import VM                


configs = [vm.Hohmann, vm.MeetGreet, vm.Eccentric, vm.ClearSkies]

solvers = [solvers.hohmann.HohmannController,
           solvers.meetgreet.MeetGreetController,
           solvers.meetgreet.MeetGreetController,
           None]

binaries = []
for n in range(4):
	binaries.append("../../task/bin%d.obf"%(n+1))

folder = 'solutions-x'

if __name__ == '__main__':

    try:
    	os.mkdir (folder)
    except:
    	pass

    i = -1
    for set in configs:
        i = i+1
        for config in set:
            
            print "run %d"%config

            with open(binaries[i],"rb") as fin:
                data = fin.read()
            vm = VM(data)
            vm.setScenario(config)
            solver = solvers[i](vm)
            
            while vm.state.score == 0.0:
                vm.execute()
                if solver:
                    solver.step()

            solution = vm.getSolution()
            score = vm.state.score
            fname = "%s/sol_%04d_%06d_%s.osf"%(folder, config, score,
                        re.sub(r'[\s:]', "_", time.ctime()))
            with open(fname,'wb') as fout:
                fout.write(solution)
            print "stored into "+ fname
        
