/*! 
=======================================================================
* Web Worker for the miner component.
=======================================================================

* This worker handles the mining process in a separate thread to avoid blocking the UI.

*/

/// <reference lib="webworker" />
import { Block } from "../crypto/Block";

let isMining = false;

self.onmessage = (e: MessageEvent) => {
    const { blockData } = e.data as { blockData: any };

    console.log("⛏️ Received block data:", blockData);
    const block = Block.deserialize(blockData);
    isMining = true;

    let nonce = 0;
    const start = performance.now();

    while (isMining) {
        block.nonce = nonce.toString();
        const hash = block.computeHash();

        if (block.criterion.check(hash)) {
            const time = ((performance.now() - start) / 1000).toFixed(2);
            self.postMessage({ type: "solved", nonce, hash, time });
            break;
        }

        // Every 10000 attempts, report progress
        if (nonce % 10000 === 0) {
            self.postMessage({ type: "progress", nonce });
        }

        nonce += 1;
    }


}