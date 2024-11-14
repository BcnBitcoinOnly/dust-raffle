from bitcoinutils.constants import SIGHASH_ALL, SIGHASH_ANYONECANPAY
from bitcoinutils.keys import PrivateKey
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.setup import setup

from utils import p2pkh_script, op_return_script, winner_outpoint

BLOCK_HASH = '0000030782b6630b6b19daf62660c6dc6a3e4bd76d8f1741cdf750224549521c'
BLOCK_HEIGHT = 16845

PARTICIPANTS = {
    ('a684e5b40c95b65513fe417af43660f28dcfce298cf10a6b7d4a4696f61bd609', 0): 'cVWZUGHnX8VTdCYb69G9SRoqo3Yokct6dB8mLesqWcMoCHDnW26Q',
    ('a684e5b40c95b65513fe417af43660f28dcfce298cf10a6b7d4a4696f61bd609', 1): 'cNMg9KruPGDfR3DwJhHHGkRrjrXvTqyJYDBhB6CuMVEvdbjtHf2S',
    ('a684e5b40c95b65513fe417af43660f28dcfce298cf10a6b7d4a4696f61bd609', 3): 'cN1sHqwhjAFmwCnjvNzVQWDe4hoxemsiXRUgeZGusx843u7Ny5U6',
    ('a684e5b40c95b65513fe417af43660f28dcfce298cf10a6b7d4a4696f61bd609', 4): 'cTWRGdTU7XxBGCTtea4XzDq5NGZWZNRbA7SLXFBW7Qjpzc1SzTyi',
}


def raffle_tx() -> Transaction:
    """
    Each participant UTXO comes from a different address. The raffle algorithm sends the funds to the scriptPubKey
    of the winner UTXO.

    https://sigpool.bitcoinbarcelona.xyz/signet/tx/ed59a63e33722baae0db0c266bce96e35b91654da843f0d24ac21a10685b4ef9
    """
    txins = [TxInput(outpoint[0], outpoint[1]) for outpoint in list(PARTICIPANTS.keys())]

    winner = winner_outpoint(list(PARTICIPANTS.keys()), bytes.fromhex(BLOCK_HASH))
    print(f"Winner outpoint: {winner[0]}:{winner[1]}\n")

    txouts = [
        TxOutput(4000, PrivateKey(PARTICIPANTS[winner]).get_public_key().get_segwit_address().to_script_pub_key()),
        TxOutput(0, op_return_script(BLOCK_HEIGHT))
    ]

    tx = Transaction(txins, txouts, has_segwit=True)

    i = 0
    for outpoint, key in PARTICIPANTS.items():
        private_key = PrivateKey(key)
        public_key = private_key.get_public_key()
        tx.witnesses.append(TxWitnessInput([
            private_key.sign_segwit_input(tx, i, p2pkh_script(public_key), 1000, SIGHASH_ALL | SIGHASH_ANYONECANPAY),
            public_key.to_hex()
        ]))
        i = i + 1

    return tx


if __name__ == '__main__':
    setup("testnet")
    tx = raffle_tx()
    print(tx.get_txid())
    print(tx.serialize())
