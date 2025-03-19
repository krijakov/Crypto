#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Basic Elliptic Curve Cryptography (ECC) implementation.

"""

class ECC:
    def __init__(self, a, b, p, G, n):
        self.a = a # Coefficient a
        self.b = b # Coefficient b
        self.p = p # Prime number modulo (field size)
        self.G = G # Generator point (G_x, G_y)
        self.n = n # Order of the curve

    def inverse_mod(self, k):
        """Calculate the modular inverse."""
        return pow(k, -1, self.p)

    def add_points(self, P, Q):
        """Point addition on the elliptic curve."""
        if P == (0, 0):
            return Q
        if Q == (0, 0):
            return P
        
        x1, y1 = P
        x2, y2 = Q
        
        if P == Q:
            # Point doubling
            l = (3 * x1 * x1 + self.a) * self.inverse_mod(2 * y1)
        else:
            # Point addition
            l = (y2 - y1) * self.inverse_mod(x2 - x1)
        
        x3 = (l * l - x1 - x2) % self.p
        y3 = (l * (x1 - x3) - y1) % self.p
        
        return (x3, y3)
    
    def double_point(self, P):
        """Double a point on the elliptic curve. NOTE: declared separately from add_points for efficiency."""
        x, y = P
        if y == 0:
            return (0, 0) # infinity point
        
        l = (3 * x * x + self.a) * self.inverse_mod(2 * y)
        x3 = (l * l - 2 * x) % self.p
        y3 = (l * (x - x3) - y) % self.p
        return (x3, y3)
        

    def scalar_multiply(self, k, P):
        """
            Scalar multiplication of a point, using Double-and-Add algorithm.

            The Logic is as follows:
            - Convert the scalar k to binary, this means k = k_0 + 2^1*k_1 + 2^2*k_2 + ... + 2^n*k_n
            - Initialize the result as the infinity point (0, 0)
            - If k_i is 0, then do nothing, just take a step, but that means we need to step in the magnitude as well, i.e. double the point
            - If k_i is 1, then add the point to the result and then take a step
        """
        result = (0, 0)
        current_magnitude = P # where we are in the binary representation

        while k: # Iterate over the bits of k
            if k & 1: # if at k we have a 1
                result = self.add_points(result, current_magnitude)
            current_magnitude = self.double_point(current_magnitude)

            k >>= 1 # Move to the next bit

        return result
    
# Initialize known curves:
secp256k1 = ECC(
    a=0,
    b=7,
    p=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F,
    G=(
        0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
        0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
    ),
    n=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
)

nist_p192 = ECC(
    a=-3,
    b=0x64210519E59C80E70FA7E9AB72243049FEB8DEECC146B9B1,
    p=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFFFFFFFFFFFF,
    G=(
        0x188DA80EB03090F67CBF20EB43A18800F4FF0AFD82FF1012,
        0x07192B95FFC8DA78631011ED6B24CDD573F977A11E794811,
    ),
    n=0xFFFFFFFFFFFFFFFFFFFFFFFF99DEF836146BC9B1B4D22831
)

toy_curve = ECC(
    a=2,
    b=3,
    p=97,
    G=(3, 6),
    n=5
)