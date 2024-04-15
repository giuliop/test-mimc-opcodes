#!/usr/bin/env python3
import algosdk as sdk

import devnet as dev


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
    print(f"Mimc contracrt created with app_id: {app_id}")

    # test the contract
    for curve in ["BN254", "BLS12_381"]:
        failed = False
        print()
        for i, test in enumerate(tests[curve]):
            hash_check, *inputs = [int.to_bytes(n, 32) for n in test]
            result, resp = dev.call_method(
                app_id,
                f"mimc_{curve}(byte[32][])byte[32]",
                [inputs],
                simulate=True
            )
            print(f"Test {i+1} for mimc_{curve} | # of 32-bytes inputs: "
                  f"{len(inputs)} | opcode consumed: "
                  f"{resp['txn-groups'][0]['app-budget-consumed']}")
            if result.raw_value != hash_check:
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

# each test is: hash_result (base 10), *inputs to mimc (base 16)
tests = {
    "BN254": [
        [12886436712380113721405259596386800092738845035233065858332878701083870690753,
        # one input: 32 bytes, less than modulus
        0x23a950068dd3d1e21cee48e7919be7ae32cdef70311fc486336ea9d4b5042535],

        [21488126545528900465245011371375368756899880390335832457798151394813541857337,
        # one input: 32 bytes, more than modulus
        0x30644e72e131a029b85045b68181585d2833e84879b9709143e1f593f000000b],

        [1037254799353855871006189384309576393135431139055333626960622147300727796413,
         # one input: less than 32 bytes
        0xdeadf00d],

        [11591811072896689251240213683306766706992046044563384371468671962583624497524,
        # two inputs: less than 32 bytes | 32 bytes, more than modulus |
        0x14,
        0x30644e72e131a029b85045b68181585d2833e84879b9709143e1f593f000000b],

        [18550063335027646392217389225443559231127180334580131721131519262234424458000,
         # three inputs: 32 bytes, less than modulus | 32 bytes, more than modulus | less than 32 byte
        0x83de351a72141d79c51a27d10405549c98302cb2536c5968deeb3cba6351217,
        0x30644e72e131a029b85045b68181585d2833e84879b9709143e1f5943d1e7358,
        0xabba],
    ],
    "BLS12_381": [
        [8791766422525455185980675814845076441443662947059416063736889106252015893524,
        # one input: 32 bytes, less than modulus
        0x23a950068dd3d1e21cee48e7919be7ae32cdef70311fc486336ea9d4b5042535],

        [49716029653782032528033446830605023465761129633657457825127154515040578106738,
        # one input: 32 bytes, more than modulus
        0xb97c3eeb75c8c873852959a675cfc00885fc399e6663c664ccccd111f82ac7a],

        [15039173432183897369859775531867817848264266283034981501223857291379142522368,
         # one input: less than 32 bytes
        0xdeadf00d],

        [41687140595726476439499037676493685597247699602720241103630673374487542475152,
        # two inputs: less than 32 bytes | 32 bytes, more than modulus |
        0x14,
        0xb97c3eeb75c8c873852959a675cfc00885fc399e6663e55261081f98171d5ea],

        [38215989719364062579714528971030347757178205832775123148034717181173932938622,
         # three inputs: 32 bytes, less than modulus | 32 bytes, more than modulus | less than 32 byte
        0x83de351a72141d79c51a27d10405549c98302cb2536c5968deeb3cba6351217,
        0xb97c3eeb75c8c873853899516e11290b0352633edd277b00296e3332945bb4d,
        0xabba],
    ]
}

if __name__ == "__main__":
    run_test()
