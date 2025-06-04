#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Manual implementation of the SHA-256 hashing algorithm, for educational purposes.

"""
from typing import List, Any
import struct

class SHA256:
    # Constants, calculate them only once and store them as class variables:
    # Some explanation:
    #    - fixed "seed" to make the hash reproducable
    #    - square root of primes to increase "randomness" (prime distribution is already quite random and square roots are irrational adding to the unpredictability).
    #    - 32 bit, to have a uniform size
    # 32-bit representation of the fractional part of the square root of the first 8 primes:
    INITIAL_HASH_VALUES = [int(((prime ** 0.5) % 1) * 2**32) for prime in [
        2, 3, 5, 7, 11, 13, 17, 19
    ]]
    # 32-bit representation of the fractional part of the cube root of the first 64 primes:
    ROUND_CONSTANTS = [int(((prime ** (1/3)) % 1) * 2**32) for prime in [
        2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311
    ]]
    
    @staticmethod
    def convert_to_binary_string(message: str) -> str:
        """Convert a string to a binary string using UTF-8 encoding and struct."""
        #NOTE: using struct makes the conversion more efficient (C-style memory packing).
        return ''.join(f"{byte:08b}" for byte in struct.pack(f"{len(message.encode('utf-8'))}s", message.encode('utf-8'))) # ensure 8-bit encoding (and utf-8 support)

    @staticmethod
    def add_padding(binary_string: str) -> str:
        length = len(binary_string)
        binary_string += '1' # to uniquely identify the end of the message
        # Pad with zeros to reach 448 bits (mod 512), 448 to be able to append the length of the message as a 64-bit integer:
        binary_string += '0' * ((448 - (length + 1) % 512) % 512) 
        binary_string += format(length, '064b')
        return binary_string
    
    @staticmethod
    def split_to_blocks(binary_string: str) -> List[str]:
        """Split to fixed size (length 512) blocks"""
        return [binary_string[i:i+512] for i in range(0, len(binary_string), 512)]
    
    # Message schedule
    @staticmethod
    def circular_right_rotate(value: Any, bits: int) -> Any:
        """Circular right rotation (>>> in SHA-256 pseudocode)."""
        # NOTE: >> zeros out the bits it shifts from, so the steps are, with 32-bit binary example:
        # 1. Shift the value to the right (by 7 in the example): 11010010101011001111000010101011 -> 00000001101001010101100111100001, the first 7 bits become zeros
        # 2. Shift the value to the left (by 32-7 = 25 in the example): 11010010101011001111000010101011 -> 10100101010110011110000100000000, the last 7 bits become zeros
        # 3. OR the two values together: 00000001101001010101100111100001 | 10100101010110011110000100000000 = 10100101101011001111000110101011
        # 4. Make sure the result int is 32 bits, since python can handle arbitrary length integers: and with 0xFFFFFFFF (11111111111111111111111111111111 in binary, so "and"-ing with it only keeps the first 32 bits)
        return ((value >> bits) | (value << (32 - bits))) & 0xFFFFFFFF
        
    @staticmethod
    def message_schedule(block: str) -> List[int]:
        """Expands the 512-bit block to a 64-word message schedule"""
        W = []
        # The first 16 words are the block split into 32-bit words:
        for i in range(16):
            W.append(int(block[i*32:(i+1)*32], 2)) # Convert to int from binary string
            
        # The rest of the words are generated from the first 16 with nonlinear operations (rotations and XORs):
        for i in range(16, 64):
              sigma0 = SHA256.circular_right_rotate(W[i-15], 7) ^ SHA256.circular_right_rotate(W[i-15], 18) ^ (W[i-15] >> 3)
              sigma1 = SHA256.circular_right_rotate(W[i-2], 17) ^ SHA256.circular_right_rotate(W[i-2], 19) ^ (W[i-2] >> 10)
              W.append((W[i-16] + sigma0 + W[i-7] + sigma1) & 0xFFFFFFFF) # Ensure 32-bit int output
        return W
    
    # Compression:
    @staticmethod
    def compression_loop(words: List[int], current_hash: List[int] = None) -> str:
        """
            Main compression loop of the SHA-256 algorithm.
            
            This is where the 64 words are compressed into the 8 hash values.
        """
        if current_hash is None:
            a,b,c,d,e,f,g,h = SHA256.INITIAL_HASH_VALUES # Initialize hash values
        else:
            a,b,c,d,e,f,g,h = current_hash
        round_constants = SHA256.ROUND_CONSTANTS
        
        assert len(words) == 64, "Message schedule should be 64 words long."
        
        for i in range(64):
            Sigma1 = SHA256.circular_right_rotate(e, 6) ^ SHA256.circular_right_rotate(e, 11) ^ SHA256.circular_right_rotate(e, 25)
            ch = (e & f) ^ (~e & g)
            temp1 = (h + Sigma1 + ch + round_constants[i] + words[i]) & 0xFFFFFFFF # Ensure 32-bit int output
            
            Sigma0 = SHA256.circular_right_rotate(a, 2) ^ SHA256.circular_right_rotate(a, 13) ^ SHA256.circular_right_rotate(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (Sigma0 + maj) & 0xFFFFFFFF
            #NOTE: each variable is supposed to be 32 bits, which the the rotations and bitwise operations could change, so when calculating the hash values, we ensure 32 bit outputs
            
            # SHA-256 variable shifting:
            h = g
            g = f
            f = e
            e = (d + temp1) & 0xFFFFFFFF
            d = c
            c = b
            b = a
            a = (temp1 + temp2) & 0xFFFFFFFF
            
        return [(val + new_val) & 0xFFFFFFFF for val, new_val in zip(current_hash, [a,b,c,d,e,f,g,h])]
    
    # Complete hashing function:
    @staticmethod
    def digest(message: str) -> str:
        binary_message = SHA256.convert_to_binary_string(message)
        padded_message = SHA256.add_padding(binary_message)
        blocks = SHA256.split_to_blocks(padded_message)
        
        hash_values = SHA256.INITIAL_HASH_VALUES # Initialize hash values
        for block in blocks:
            message_schedule = SHA256.message_schedule(block)
            hash_values = SHA256.compression_loop(message_schedule, hash_values) # Update the hash values with the compression loop
        
        return ''.join(format(val, '08x') for val in hash_values) # Convert the hash values to hex  