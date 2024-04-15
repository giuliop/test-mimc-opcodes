"""A script to generate some output needed to make test pass for our new mimc opcodes"""
from base64 import b64decode

import devnet as dev

mimc_BN254Nonsense = """
#pragma version 11
pushbytes 0x11223344556677889900aabbccddeeff11223344556677889900aabbccddeeff
mimc_BN254
"""

mimc_BLS12_381Nonsense = """
#pragma version 11
pushbytes 0x11223344556677889900aabbccddeeff11223344556677889900aabbccddeeff
mimc_BLS12_381
"""

compiled_mimc_BN254Nonsense = b64decode(
    dev.algod.compile(mimc_BN254Nonsense)['result']
).hex()
compiled_mimc_BLS12_381Nonsense = b64decode(
    dev.algod.compile(mimc_BLS12_381Nonsense)['result']
).hex()

print(f"compiled_mimc_BN254Nonsense:\n{compiled_mimc_BN254Nonsense}\n")
print(f"compiled_mimc_BLS12_381Nonsense\n{compiled_mimc_BLS12_381Nonsense}\n")

