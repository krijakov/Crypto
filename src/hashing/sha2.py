#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Manual implementation of the SHA-256 hashing algorithm, for educational purposes.

"""

class SHA256:
    @staticmethod
    def convert_to_binary_string(message: str) -> str:
        return ''.join(format(ord(char), '08b') for char in message ) # ensure 8-bit encoding

    @staticmethod
    def add_padding(binary_string: str) -> str:
        length = len(binary_string)
        binary_string += '1' # to uniquely identify the end of the message
        # Pad with zeros to reach 448 bits (mod 512), 448 to be able to append the length of the message as a 64-bit integer:
        binary_string += '0' * ((448 - (length + 1) % 512) % 512) 
        binary_string += format(length, '064b')
        return binary_string
    
    @staticmethod
    def split_to_blocks(binary_string: str) -> list:
        """Split to fixed size (length 512) blocks"""
        return [binary_string[i:i+512] for i in range(0, len(binary_string), 512)]