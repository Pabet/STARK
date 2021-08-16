# STARK
Zero-Knowledge Scalable Transparent ARguments of Knowledge (zk-STARK) prover in Python

What are zkSTARKs?
-> zkSTARK article series by Vitalik Buterin 
```math
https://vitalik.ca/general/2017/11/09/starks_part_1.html
https://vitalik.ca/general/2017/11/22/starks_part_2.html
https://vitalik.ca/general/2018/07/21/starks_part_3.html
```

My take on the STARK101 tutorial by STARKWARE <br />
https://starkware.co/developers-community/stark101-onlinecourse/

The FibonacciSq sequence is defined by the recurrence relation 
```math
a[n+2] = a[n+1]^2 + a[n]^2
```
over the underlying finite field F (every operation is done mudulo 3221225473).


what we will proof: 
```math
I know a field element X in F such that the 1023rd element 
of the FibonacciSq sequence starting with 1 and X (which is 3141592) is
2338775057 without revealing my X.
```
