/*! 
=======================================================================
* Basic Digital Signature utilities, based on ECC
=======================================================================

* Mirrors the ECC class from the backend.

*/
import SHA256 from "crypto-js/sha256";
import { ECC, secp256k1, randomBigInt, ECPoint } from "../ecc";

export const sha256 = (msg: string): string => {
    return SHA256(msg).toString();
  };

export const digitalSign = (data: string, privateKey: bigint, curve: ECC = secp256k1): [bigint, bigint] => {
    const h = BigInt("0x" + sha256(data));
    console.log("h (frontend, string):", h.toString());
    const k = randomBigInt(curve.n - 1n);
    const R = curve.scalarMultiply(k, curve.G);
    const r = R[0] % curve.n;

    if (r === 0n) throw new Error("Invalid r value, retry signing");

    const k_inv = curve.inverseMod(k);
    const s = (k_inv * (h + privateKey * r)) % curve.n;

    if (s === 0n) throw new Error("Invalid s value, retry signing");

    return [r, s];
};

export const verifySignature = (
    data: string,
    signature: [bigint, bigint],
    publicKey: ECPoint,
    curve: ECC = secp256k1
  ): boolean => {
    const [r, s] = signature;
    const h = BigInt("0x" + sha256(data)) % curve.n;
  
    if (!(1n <= r && r < curve.n) || !(1n <= s && s < curve.n)) {
      return false;
    }
  
    const s_inv = curve.inverseMod(s);
    const u1 = (h * s_inv) % curve.n;
    const u2 = (r * s_inv) % curve.n;
  
    const P = curve.addPoints(
      curve.scalarMultiply(u1, curve.G),
      curve.scalarMultiply(u2, publicKey)
    );
  
    return P[0] % curve.n === r;
  };