import axios from "axios";
import { Block } from "../types/blockchain";

const BASE = "http://localhost:8000";

export async function fetchNetworkInfo(): Promise<{ pending_blocks: Block[] }> {
  const response = await axios.get(`${BASE}/info`);
  return response.data;
}
