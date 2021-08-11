# STARK
Zero-Knowledge Scalable Transparent ARguments of Knowledge (zk-STARK) prover in Python

My version of the STARK101 tutorial by STARKWARE <br />
https://starkware.co/developers-community/stark101-onlinecourse/

The FibonacciSq sequence is defined by the recurrence relation 
```math
a[n+2] = a[n+1]^2 + a[n]^2
```

what we will proof: 
```math
I know a field element X in F such as the 1023rd element 
of the FibonacciSq sequence starting with 1 and X (which is 2338775057)
We just proof the fact that we know such a X without revealing it
```
In the underlying finite field F every operation is done mudulo 3221225473
