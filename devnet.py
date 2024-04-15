"""Helper functions for testing and development on the AVM"""

import os
import subprocess
from base64 import b64decode

import algosdk as sdk
from algosdk import atomic_transaction_composer, transaction
from algosdk.v2client.models import (
    simulate_request, SimulateRequestTransactionGroup
)


################ CONFIGURATION FOR DEVNET - EDIT AS NEEDED #################`
devnet_dir = os.path.expanduser("~/.algorand/devnet/MainNode")
kmd_dir = devnet_dir + "/kmd-v0.5"
kmd_port = 7833
############################################################################

print(f"\nStarting up the AVM test environment; "
      f"assuming local algorand node is running\n")
print(f"Configuring algod and kmd clients, using configuration parameters:\n"
      f"  * devnet directory: {devnet_dir}\n"
      f"  * kmd directory: {kmd_dir}\n"
      f"  * kmd port: {kmd_port}\n")
try:
    with open(devnet_dir + "/algod.token", "r") as f:
        devnet_token = f.read().strip()
    with open(devnet_dir + "/algod.net", "r") as f:
        devnet_address = f"http://{f.read().strip()}"
        kmd_address  = f"http://{f.read().strip().split(':')[0]}:{kmd_port}"
    with open(kmd_dir + "/kmd.token", "r") as f:
        kmd_token = f.read().strip()

    algod = sdk.v2client.algod.AlgodClient(devnet_token, devnet_address)
    kmd = sdk.kmd.KMDClient(kmd_token, kmd_address)

    subprocess.run(["goal", "kmd", "start", "-t", "5", "-d", devnet_dir],
                    check=True, capture_output=True)
    wallet = kmd.list_wallets()[0]["id"]
    wallet_handle = kmd.init_wallet_handle(wallet, "")
    pk = kmd.list_keys(wallet_handle)[0]
    sk = kmd.export_key(wallet_handle, "", pk)
    print(f"Using account {pk} as main account")
    print(f"Its balance is: {algod.account_info(pk)['amount'] // 10**6} algo\n")

except Exception as e:
    print(e)
    print("Error setting up clients, check configuration")
    exit()

def compile(filename):
    """compile a teal file and return the result"""
    with open (filename, "r") as f:
        teal = f.read()
    return b64decode(algod.compile(teal)['result'])

def send_txn(txn):
    """Sign a transaction, send it, and wait for confirmation.
       Return the transaction result"""
    signed_txn = txn.sign(sk)
    tx_id = algod.send_transaction(signed_txn)
    return transaction.wait_for_confirmation(algod, tx_id, 4)

def call_method(app_id, method_signature, args, simulate=False):
    sp = algod.suggested_params()
    atc = atomic_transaction_composer.AtomicTransactionComposer()
    atc.add_method_call(
        app_id=app_id,
        method=sdk.abi.Method.from_signature(method_signature),
        sender=pk,
        sp=sp,
        signer=atomic_transaction_composer.AccountTransactionSigner(sk),
        method_args=args,
    )
    if not simulate:
        resp = atc.execute(algod, 4)
        txn_id = resp.tx_ids[0]
        _ = transaction.wait_for_confirmation(algod, txn_id, 4)
        result = resp.abi_results[0]
        return result, resp.tx_info
    else:
        simreq = simulate_request.SimulateRequest(
            txn_groups = SimulateRequestTransactionGroup(txns = []),
            extra_opcode_budget= 320000
        )
        simres = atc.simulate(algod, simreq)
        return simres.abi_results[0], simres.simulate_response
