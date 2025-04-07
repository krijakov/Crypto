/*! 
=======================================================================
* Block component (from the blockchain)
=======================================================================

* Mirrors the Block class from the backend, with mining logic.

*/
import SHA256 from "crypto-js/sha256";

export class Transaction {
    constructor(
        public sender: string,
        public receiver: string,
        public amount: number,
        public signature: [string, string]
    ) { }

    public serialize(): string {
        const ordered = {
            amount: this.amount,
            receiver: this.receiver,
            sender: this.sender,
        };

        // Serialize canonically: sorted keys, no whitespace
        return JSON.stringify(ordered, Object.keys(ordered).sort(), 0);
    }

    hash(): string {
        const canonicalString = this.serialize();
        return SHA256(canonicalString).toString();
    }
}

export class MiningCriterion {
    constructor(
        public type: string,
        public difficulty: number
    ) { }

    check(hash: string): boolean {
        if (this.type === "leading_zeros") {
            return hash.startsWith("0".repeat(this.difficulty));
        } else {
            throw new Error("Unknown mining criterion type.");
        }
    }
}

export class Block {
    constructor(
        public index: string,
        public previousHash: string,
        public data: Transaction[],
        public criterion: MiningCriterion,
        public timestamp: string,
        public nonce: string,
    ) {
        // Required for proper serialization
        this.index = index;
        this.previousHash = previousHash;
        this.data = data;
        this.criterion = criterion;
        this.timestamp = timestamp;
        this.nonce = nonce;
    }

    computeHash(): string {
        const txHashes = this.data
            .map((tx) => BigInt("0x" + tx.hash()).toString(16)) // hex string
            .map((hex) => hex.replace(/^0x/, "")) // just in case
            .join("");

        const rawString = `${this.previousHash}${this.timestamp}${txHashes}${this.nonce}`;
        return SHA256(rawString).toString(); // hex string
    }

    checkPoW(): boolean {
        return this.criterion.check(this.computeHash());
    }

    // Deserialize a block from JSON format (e.g., from the backend):
    public static deserialize(blockJson: any): Block {
        const transactions = blockJson.data.map(
            (tx: any) =>
                new Transaction(
                    tx.sender,
                    tx.receiver,
                    parseInt(tx.amount), // Ensure numeric type
                    tx.signature
                )
        );
        const criterion = new MiningCriterion(
            blockJson.criterion.type,
            parseInt(blockJson.criterion.difficulty)
        );

        return new Block(
            blockJson.index,
            blockJson.previousHash,
            transactions,
            criterion,
            blockJson.timestamp,
            "0" // We'll update nonce when mining begins
        );
    }


}