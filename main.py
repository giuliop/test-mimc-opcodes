#!/usr/bin/env python3
import math

import algosdk as sdk

import devnet as dev

# bn254 mod = 21888242871839275222246405745257275088548364400416034343698204186575808495617

# bls12_381 mod = 52435875175126190479447740508185965837690552500527637822603658699938581184513

def run_test():
    # create the contract
    app_create_txn = sdk.transaction.ApplicationCreateTxn(
        sender=dev.pk,
        sp = dev.algod.suggested_params(),
        approval_program=dev.compile("contract/mimc.approval.teal"),
        clear_program=dev.compile("contract/mimc.clear.teal"),
        on_complete=sdk.transaction.OnComplete.NoOpOC,
        global_schema=sdk.transaction.StateSchema(num_uints=0, num_byte_slices=0),
        local_schema=sdk.transaction.StateSchema(num_uints=0, num_byte_slices=0),
    )
    app_id = dev.send_txn(app_create_txn)['application-index']
    print(f"Mimc contract created with app_id: {app_id}")

    # test the contract
    for curve in ["BN254", "BLS12_381"]:
        failed = False
        print()
        for i, test in enumerate(tests[curve]):
            should_succeed = test[0]
            hash_check, *inputs = [int_to_bytes(x) for x in test[1:]]
            input = b''.join(inputs)
            result, resp = dev.call_method(
                app_id,
                f"mimc_{curve}(byte[])byte[32]",
                [input],
                simulate=True
            )
            print(f"Test {i+1} for mimc_{curve} | # of 32-bytes inputs: "
                  f"{math.ceil(len(input) / 32)} | opcode consumed: "
                  f"{resp['txn-groups'][0]['app-budget-consumed']}")
            if ((result.raw_value != hash_check) and should_succeed
                or (result.raw_value == hash_check) and not should_succeed):
                failed = True
                print(f"\nTest failed for mimc_{curve} !")
                print(f"Expected: {hash_check.hex()}"
                        f"\nGot raw:  {result.raw_value.hex()}"
                        f"\nError:    {result.decode_error}"
                        f"\n{'-'*10}\n")
        if not failed:
            print(f"\nAll MiMC tests for {curve} passed !")

    # delete the contract
    delete_txn = sdk.transaction.ApplicationDeleteTxn(
        sender=dev.pk,
        sp = dev.algod.suggested_params(),
        index=app_id,
    )
    dev.send_txn(delete_txn)
    print(f"\nMimc contract {app_id} deleted\n")

# each test is: bool (true for pass, false for fail), hash_result (base 10),
# *inputs to mimc (base 16)
tests = {
    "BN254": [
        [False,
        20104241803663641422577121134203490505137011783614913652735802145961801733870,
        # zero-length input
        ],

        [True,
        12886436712380113721405259596386800092738845035233065858332878701083870690753,
        # one input: 32 bytes, less than modulus
        0x23a950068dd3d1e21cee48e7919be7ae32cdef70311fc486336ea9d4b5042535],

        [False,
        19565877911319815535452130675266047290072088868113536892077808700068649624391,
        # one input: 32 bytes, more than modulus
        0x73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000002],

        [False,
        1037254799353855871006189384309576393135431139055333626960622147300727796413,
         # one input: less than 32 bytes
        0xdeadf00d],

        [True,
        6040222623731283351958201178122781676432899642144860863024149088913741383362,
        # thee inputs: all 32 bytes, less than modulus
        0x183de351a72141d79c51a27d10405549c98302cb2536c5968deeb3cba6351217,
        0x23a950068dd3d1e21cee48e7919be7ae32cdef70311fc486336ea9d4b5042535,
        0x30644e72e131a029b85045b68181585d2833e84879b9709143e1f593ef676981],

        [False,
        21691351735381703396517600859480938764038501053226864452091917666642352837076,
         # three inputs: 32 bytes, less than modulus | 32 bytes, less than
         # modulus | 32 bytes, more than modulus
        0x183de351a72141d79c51a27d10405549c98302cb2536c5968deeb3cba6351217,
        0x23a950068dd3d1e21cee48e7919be7ae32cdef70311fc486336ea9d4b5042535,
        0x30644e72e131a029b85045b68181585d2833e84879b9709143e1f593f000000b],

        [False,
        10501393540371963307040960561318023073151272109639330842515119353134949995409,
        # three inputs: 32 bytes, less than modulus | 32 bytes, more than
        # modulus | less than 32 byte
        0x183de351a72141d79c51a27d10405549c98302cb2536c5968deeb3cba6351217,
        0x23a950068dd3d1e21cee48e7919be7ae32cdef70311fc486336ea9d4b5042535,
        0xabba],
    ],
    "BLS12_381": [
        [False,
        17991912493598890696181760734961918471863781118188078948205844982816313445306,
        # zero-length input
        ],

        [True,
        8791766422525455185980675814845076441443662947059416063736889106252015893524,
        # one input: 32 bytes, less than modulus
        0x23a950068dd3d1e21cee48e7919be7ae32cdef70311fc486336ea9d4b5042535],

        [False,
        35137972692771717943992759113612269767581262500164574105059686144346651628747,
        # one input: 32 bytes, more than modulus
        0x73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000002],

        [False,
        15039173432183897369859775531867817848264266283034981501223857291379142522368,
         # one input: less than 32 bytes
        0xdeadf00d],

        [True,
        12964111614552580241101202600014316932811348627866250816177200046290462797607,
        # thee inputs: all 32 bytes, less than modulus
        0x183de351a72141d79c51a27d10405549c98302cb2536c5968deeb3cba6351217,
        0x23a950068dd3d1e21cee48e7919be7ae32cdef70311fc486336ea9d4b5042535,
        0x30644e72e131a029b85045b68181585d2833e84879b9709143e1f593ef676981],

        [False,
        21773894974440411325489312534417904228129169539217646609523079291104496302656,
         # three inputs: 32 bytes, less than modulus | 32 bytes, less than
         # modulus | 32 bytes, more than modulus
        0x183de351a72141d79c51a27d10405549c98302cb2536c5968deeb3cba6351217,
        0x23a950068dd3d1e21cee48e7919be7ae32cdef70311fc486336ea9d4b5042535,
        0x30644e72e131a029b85045b68181585d2833e84879b9709143e1f593f000000b],

        [False,
        9873666029497961930790892458408217321483390383568592297687427911011295910871,
        # three inputs: 32 bytes, less than modulus | 32 bytes, more than
        # modulus | less than 32 byte
        0x183de351a72141d79c51a27d10405549c98302cb2536c5968deeb3cba6351217,
        0x23a950068dd3d1e21cee48e7919be7ae32cdef70311fc486336ea9d4b5042535,
        0xabba],
    ],
}

def int_to_bytes(x):
    num_bytes = (x.bit_length() + 7) // 8
    return x.to_bytes(num_bytes, 'big')

if __name__ == "__main__":
    run_test()
