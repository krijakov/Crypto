/*! 
=======================================================================
* Digital Signature utilities, based on ECC (from the Elliptic library)
=======================================================================

*/

import SHA256 from "crypto-js/sha256";
import { ec as EC } from "elliptic";
import BN from "bn.js";

// secp256k1 curve:
const ec = new EC("secp256k1");

export type PublicKey = [string, string]; // [x, y] as strings
export type Signature = [string, string]; // [r, s] as strings

export const generateKeyPair = (): {
    privateKey: string;
    publicKey: PublicKey;
} => {
    const key = ec.genKeyPair();
    const pub = key.getPublic();
    return {
        privateKey: key.getPrivate().toString(10),
        publicKey: [pub.getX().toString(10), pub.getY().toString(10)],
    };
};

export const getPublicFromPrivate = (privateKey: string): PublicKey => {
    const key = ec.keyFromPrivate(BigInt(privateKey).toString(16), "hex"); // Get the private key
    const pub = key.getPublic(); // Get the public key
    return [pub.getX().toString(10), pub.getY().toString(10)];
}

export const signMessage = (message: string, privateKey: string): Signature => {
    const key = ec.keyFromPrivate(privateKey, "decimal"); // Get the private key
    const hash = SHA256(message).toString();
    const signature = key.sign(hash);
    return [
        signature.r.toString(10),
        signature.s.toString(10)
    ];
};

export const manualSign = (message: string, privateKey: string): [string, string] => {
    const n = ec.curve.n; // order of the curve

    const h = BigInt("0x" + SHA256(message).toString()) % BigInt(n.toString(10)); // // Python's `int(..., 16) % n`

    let r: bigint = 0n;
    let s: bigint = 0n;

    while (r === 0n || s === 0n) {
        const k = ec.genKeyPair(); // Random ephemeral key
        const R = k.getPublic(); // R = k * G

        r = BigInt(R.getX().toString(10)) % BigInt(n.toString(10));
        if (r === 0n) continue;

        const kInv = BigInt(k.getPrivate().invm(n).toString(10)); // modular inverse of k mod n
        const d = BigInt(privateKey); // private key as bigint
        s = (kInv * (h + d * r)) % BigInt(n.toString(10));
        if (s === 0n) continue;
    }

    return [r.toString(), s.toString()];
};

export const manualVerify = (
    message: string,
    signature: Signature,
    publicKey: PublicKey
): boolean => {
    const [rStr, sStr] = signature;
    const r = new BN(rStr, 10);
    const s = new BN(sStr, 10);
    const n = ec.curve.n;

    if (r.isZero() || r.gte(n) || s.isZero() || s.gte(n)) {
        return false;
    }

    const hashHex = SHA256(message).toString();
    const h = new BN(hashHex, 16).umod(n);

    const sInv = s.invm(n); // s^(-1) mod n
    const u1 = h.mul(sInv).umod(n);
    const u2 = r.mul(sInv).umod(n);

    // Reconstruct public key point
    const pub = ec.curve.point(
        new BN(publicKey[0], 10),
        new BN(publicKey[1], 10)
    );

    const point1 = ec.g.mul(u1); // u1 * G
    const point2 = pub.mul(u2); // u2 * Q

    const P = point1.add(point2);

    // Signature is valid if r === P.x mod n
    return P.getX().umod(n).eq(r);
};




