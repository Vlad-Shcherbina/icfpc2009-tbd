import time

import pyximport; pyximport.install()
import cy

def pyprimes(n):
    result = []
    for i in range(2,n):
        j = 2
        f = True
        while j*j <= i:
            if i%j == 0:
                f = False
                break
            j += 1
        if f:
            result.append(i)
    return result

if __name__ == '__main__':
    n = 100000

    start = time.clock()    
    print 'python',len(pyprimes(n))
    print time.clock()-start,'s'

    start = time.clock()    
    print 'python compiled by cython',len(cy.pyprimes(n))
    print time.clock()-start,'s'

    start = time.clock()    
    print 'cython',len(cy.primes(n))
    print time.clock()-start,'s'
    
    