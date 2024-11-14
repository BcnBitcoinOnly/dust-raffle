from bitcoinutils.constants import SIGHASH_ALL, SIGHASH_ANYONECANPAY
from bitcoinutils.keys import PrivateKey
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.setup import setup

from utils import p2pkh_script, op_return_script

RAFFLE_VERSION = b'\x00'
BLOCK_HEIGHT = 16837
PRIVATE_KEY = 'cPGGXY5KSwFnLfes38WdVbCW3mT8buDwy4nbX6hqm9DP2SdV8Aya'
ADDRESS = 'tb1qmxkjngwjfn64j8kdpzdmc4y5v24cxm2hdkqn5j'
OUTPOINTS = [
    ('f06623450749b9efcea14e24f682ffa7337a7b0023ec853226a491092ec09b52', 4),
    ('f06623450749b9efcea14e24f682ffa7337a7b0023ec853226a491092ec09b52', 5),
    ('f06623450749b9efcea14e24f682ffa7337a7b0023ec853226a491092ec09b52', 6),
    ('f06623450749b9efcea14e24f682ffa7337a7b0023ec853226a491092ec09b52', 7),
]


def raffle_tx() -> Transaction:
    """
    All participant UTXOs come from the same address, a degenerate case where the raffle algorithm does not matter.

    https://sigpool.bitcoinbarcelona.xyz/tx/8eab313ef47e9d1c070e87f2f911ee0449b2d91c1df6b5030ba627a1fd33a5f7
    """
    private_key = PrivateKey(PRIVATE_KEY)
    public_key = private_key.get_public_key()

    assert ADDRESS == public_key.get_segwit_address().to_string()

    txin0 = TxInput(OUTPOINTS[0][0], OUTPOINTS[0][1])
    txin1 = TxInput(OUTPOINTS[1][0], OUTPOINTS[1][1])
    txin2 = TxInput(OUTPOINTS[2][0], OUTPOINTS[2][1])
    txin3 = TxInput(OUTPOINTS[3][0], OUTPOINTS[3][1])

    txout0 = TxOutput(4000, public_key.get_segwit_address().to_script_pub_key())
    txout1 = TxOutput(0, op_return_script(BLOCK_HEIGHT))
    tx = Transaction([txin0, txin1, txin2, txin3], [txout0, txout1], has_segwit=True)

    script = p2pkh_script(public_key)
    sig0 = private_key.sign_segwit_input(tx, 0, script, 1000, SIGHASH_ALL | SIGHASH_ANYONECANPAY)
    sig1 = private_key.sign_segwit_input(tx, 1, script, 1000, SIGHASH_ALL | SIGHASH_ANYONECANPAY)
    sig2 = private_key.sign_segwit_input(tx, 2, script, 1000, SIGHASH_ALL | SIGHASH_ANYONECANPAY)
    sig3 = private_key.sign_segwit_input(tx, 3, script, 1000, SIGHASH_ALL | SIGHASH_ANYONECANPAY)

    tx.witnesses.append(TxWitnessInput([sig0, public_key.to_hex()]))
    tx.witnesses.append(TxWitnessInput([sig1, public_key.to_hex()]))
    tx.witnesses.append(TxWitnessInput([sig2, public_key.to_hex()]))
    tx.witnesses.append(TxWitnessInput([sig3, public_key.to_hex()]))

    return tx


if __name__ == '__main__':
    setup("testnet")
    tx = raffle_tx()
    print(tx.get_txid())
    print(tx.serialize())
