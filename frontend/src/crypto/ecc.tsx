/*! 
=======================================================================
* Basic Elliptic Curve Cryptography (ECC) implementation
=======================================================================

* Elliptic Curve: y² = x³ + ax + b (mod p)
* Mirrors the ECC class from the backend.

*/

// A point on the curve:
export type ECPoint = [bigint, bigint];

export class ECC {
    // Declare attributes:
    a: bigint; // Coefficient a
    b: bigint; // Coefficient b
    p: bigint; // Prime number modulo (field size)
    G: ECPoint; // Generator point (G_x, G_y)
    n: bigint; // Order of the curve

    // Methods come here:
    constructor(a: bigint, b: bigint, p: bigint, G: ECPoint, n: bigint) {
        this.a = a;
        this.b = b;
        this.p = p;
        this.G = G;
        this.n = n;
    }

    // Modular inverse from Fermat's Little Theorem (Kis Fermat tétel):
    // since a^(p - 2) ≡ a^(-1) mod p from that
    inverseMod(k: bigint): bigint {
        return this.modPow(k, this.p - 2n, this.p);
    }

    // Compute base^exp % mod using fast modular exponentiation (square and multiply).
    private modPow(base: bigint, exp: bigint, mod: bigint): bigint {
        let result = 1n;
        base = base % mod;
        while (exp > 0n) {
            if (exp % 2n === 1n) result = (result * base) % mod;
            exp = exp / 2n;
            base = (base * base) % mod;
        }
        return result;
    }

    // Add points:
    addPoints(P: ECPoint, Q: ECPoint): ECPoint {
        const [x1, y1] = P;
        const [x2, y2] = Q;

        if (P[0] === 0n && P[1] === 0n) return Q;
        if (Q[0] === 0n && Q[1] === 0n) return P;

        // P + (-P) = O (point at infinity)
        if (x1 === x2 && y1 !== y2) return [0n, 0n];

        let lambda: bigint;

        // Point doubling:
        if (x1 == x2 && y1 == y2) {
            lambda = (3n * x1 * x1 + this.a) * this.inverseMod(2n * y1) % this.p
        } else { // Point addition:
            lambda = ((y2 - y1) * this.inverseMod(x2 - x1)) % this.p;
        }

        const x3 = (lambda * lambda - x1 - x2) % this.p;
        const y3 = (lambda * (x1 - x3) - y1) % this.p;

        return [(x3 + this.p) % this.p, (y3 + this.p) % this.p];
    }

    // Double the point (separate for efficiency):
    doublePoint(P: ECPoint): ECPoint {
        const [x, y] = P;
        if (y === 0n) return [0n, 0n];

        const lambda = ((3n * x * x + this.a) * this.inverseMod(2n * y)) % this.p;

        const x3 = (lambda * lambda - 2n * x) % this.p;
        const y3 = (lambda * (x - x3) - y) % this.p;

        return [(x3 + this.p) % this.p, (y3 + this.p) % this.p];
    }

    // Scalar multiplication of a point, using Double-and-Add algorithm.
    public scalarMultiply(k: bigint, P: ECPoint): ECPoint {
        let result: ECPoint = [0n, 0n]; // Identity (point at infinity)
        let addend: ECPoint = P;

        while (k > 0n) {
            if (k & 1n) {
                result = this.addPoints(result, addend);
            }
            addend = this.doublePoint(addend);
            k >>= 1n;
        }

        return result;
    }
}

export const secp256k1 = new ECC(
    0n,
    7n,
    BigInt('0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F'),
    [
        BigInt('0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798'),
        BigInt('0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8')
    ],
    BigInt('0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141')
);

// Random bigint generator:
export const randomBigInt = (max: bigint): bigint => {
    const maxBits = max.toString(2).length;
    let rand: bigint;
    do {
        const randBytes = new Uint8Array(Math.ceil(maxBits / 8));
        crypto.getRandomValues(randBytes);
        rand = BigInt('0x' + [...randBytes].map(b => b.toString(16).padStart(2, '0')).join(''));
    } while (rand >= max || rand === 0n);
    return rand;
};


export const generateKeys = () => {
    const d = randomBigInt(secp256k1.n);
    const Q = secp256k1.scalarMultiply(d, secp256k1.G);
    return {
        privateKey: d,
        publicKey: Q,
        publicKeySerializable: [
            Q[0].toString(), // or Q[0].toString(16) for hex
            Q[1].toString(),
        ],
    };
};