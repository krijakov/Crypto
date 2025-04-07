export interface Transaction {
    sender: string;
    receiver: string;
    amount: number;
  }
  
// might need some reshaping to match /info better
export interface Block {
    index: number;
    num_transactions: number;
    timestamp: string;
    finalized: boolean;
  }