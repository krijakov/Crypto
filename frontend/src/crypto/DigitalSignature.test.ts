import { ec as EC } from "elliptic";
import SHA256 from "crypto-js/sha256";
import BN from "bn.js";

import { manualVerify, Signature, PublicKey } from "./DigitalSignatureElliptic";

const ec = new EC("secp256k1");

const message = '{"amount":10,"receiver":"Ubulka","sender":"Ubulka"}';

describe("Digital Signature (manualVerify) tests", () => {
  it("should verify a valid signature", () => {
    // Generate keys
    const keyPair = ec.genKeyPair();
    const privateKey = keyPair.getPrivate(); // BN
    const publicKey = keyPair.getPublic(); // Point

    // Sign message
    const hashHex = SHA256(message).toString();
    const signature = keyPair.sign(hashHex, { canonical: true }); // deterministic sig

    const sig: Signature = [
      signature.r.toString(10),
      signature.s.toString(10)
    ];

    const pub: PublicKey = [
      publicKey.getX().toString(10),
      publicKey.getY().toString(10)
    ];

    const isValid = manualVerify(message, sig, pub);
    expect(isValid).toBe(true);
  });

  it("should fail verification with altered message", () => {
    const keyPair = ec.genKeyPair();
    const publicKey = keyPair.getPublic();

    const hashHex = SHA256(message).toString();
    const signature = keyPair.sign(hashHex, { canonical: true });

    const sig: Signature = [
      signature.r.toString(10),
      signature.s.toString(10)
    ];

    const pub: PublicKey = [
      publicKey.getX().toString(10),
      publicKey.getY().toString(10)
    ];

    const tamperedMessage = '{"amount":10,"receiver":"Evil","sender":"Ubulka"}';
    const isValid = manualVerify(tamperedMessage, sig, pub);
    expect(isValid).toBe(false);
  });

  it("should fail with wrong public key", () => {
    const keyPair1 = ec.genKeyPair();
    const keyPair2 = ec.genKeyPair(); // wrong pubkey

    const hashHex = SHA256(message).toString();
    const signature = keyPair1.sign(hashHex);

    const sig: Signature = [
      signature.r.toString(10),
      signature.s.toString(10)
    ];

    const pubWrong: PublicKey = [
      keyPair2.getPublic().getX().toString(10),
      keyPair2.getPublic().getY().toString(10)
    ];

    const isValid = manualVerify(message, sig, pubWrong);
    expect(isValid).toBe(false);
  });
});
