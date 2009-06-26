def pyprimes(n): # same as in main.py
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
   
def primes(n):
    cdef int i # the
    cdef int j # only
    cdef int f # difference!
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
   