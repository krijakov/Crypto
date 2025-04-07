import React, { useEffect, useState } from "react";
import { fetchNetworkInfo } from "../api/blockchain";
import { Block } from "../types/blockchain";

const BlockList = () => {
  const [blocks, setBlocks] = useState<Block[]>([]);

  useEffect(() => {
    fetchNetworkInfo()
      .then(data => setBlocks(data.pending_blocks))
      .catch(err => console.error("Failed to fetch blocks", err));
  }, []);

  return (
    <div>
      <h2>Pending Blocks</h2>
      <ul>
        {blocks.map((block) => (
          <li key={block.index}>
            <strong>Block #{block.index}</strong> | Transactions: {block.num_transactions} | Finalized: {String(block.finalized)}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default BlockList;
