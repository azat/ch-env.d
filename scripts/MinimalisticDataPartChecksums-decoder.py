#!/usr/bin/env python3

# Example:
# $ zk-shell localhost --run-from-stdin <<<"add_auth digest $auth"$'\n'"get /ch/bl_links_v18/tables/1-1/rep_links/replicas/b1-1.ch.bl/parts/9_11889_323712_89_103346" | python3 /tmp/MinimalisticDataPartChecksums.py
# hex(columns_hash)='0xa87ff4e7ca465e40b277926738581fb7'
# num_compressed_files=41
# num_uncompressed_files=45
# hex(hash_of_all_files)='0xbc1bf40ebc3c5e33bff1bcc5b7c22352'
# hex(hash_of_uncompressed_files)='0x2072cca2c0df31c8d550a0bdaf51c36'
# hex(uncompressed_hash_of_compressed_files)='0xdd955e35caf59da9791cf4615ccbf6c7'

import sys
import io
from struct import Struct
from clickhouse_driver.varint import read_varint

class Stream(io.BytesIO):
    # compatiblity with clickhouse_driver.BufferedReader
    def read_one(self):
        return self.read(1)[0]

def read_binary_int(buf, fmt):
    """
    Reads int from buffer with provided format.
    """
    # Little endian.
    s = Struct('<' + fmt)
    return s.unpack(buf.read(s.size))[0]

def read_binary_uint128(buf):
    hi = read_binary_int(buf, 'Q')
    lo = read_binary_int(buf, 'Q')

    return (hi << 64) + lo

header = eval(sys.stdin.buffer.read().strip())
# drop "part header format version: 1\n"
header = b'\n'.join(header.split(b"\n")[1:])

b = Stream(header)

columns_hash = read_binary_uint128(b)
print(f'{hex(columns_hash)=}')

num_compressed_files = read_varint(b)
num_uncompressed_files = read_varint(b)
print(f'{num_compressed_files=}')
print(f'{num_uncompressed_files=}')

hash_of_all_files = read_binary_uint128(b)
print(f'{hex(hash_of_all_files)=}')

hash_of_uncompressed_files = read_binary_uint128(b)
print(f'{hex(hash_of_uncompressed_files)=}')

uncompressed_hash_of_compressed_files = read_binary_uint128(b)
print(f'{hex(uncompressed_hash_of_compressed_files)=}')

left = b.read()
assert len(left) == 0, f'{left=}, {len(left)=}'
