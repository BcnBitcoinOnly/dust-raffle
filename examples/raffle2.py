from bitcoinutils.setup import setup

BLOCK_HASH = '0000030782b6630b6b19daf62660c6dc6a3e4bd76d8f1741cdf750224549521c'
BLOCK_HEIGHT = 16845

PARTICIPANTS = {
    ('f06623450749b9efcea14e24f682ffa7337a7b0023ec853226a491092ec09b52', 8): 'cPGGXY5KSwFnLfes38WdVbCW3mT8buDwy4nbX6hqm9DP2SdV8Aya',
    ('f06623450749b9efcea14e24f682ffa7337a7b0023ec853226a491092ec09b52', 9): 'cPGGXY5KSwFnLfes38WdVbCW3mT8buDwy4nbX6hqm9DP2SdV8Aya',
    ('f06623450749b9efcea14e24f682ffa7337a7b0023ec853226a491092ec09b52', 10): 'cPGGXY5KSwFnLfes38WdVbCW3mT8buDwy4nbX6hqm9DP2SdV8Aya',
    ('f06623450749b9efcea14e24f682ffa7337a7b0023ec853226a491092ec09b52', 11): 'cPGGXY5KSwFnLfes38WdVbCW3mT8buDwy4nbX6hqm9DP2SdV8Aya',
    ('a684e5b40c95b65513fe417af43660f28dcfce298cf10a6b7d4a4696f61bd609', 5): 'cPLwU12JY2dDKegRYW7Fhr1yUNkwP81x6UJfr9Lo3emN2sSHes7J',
}


if __name__ == '__main__':
    """
    Simulate client-server communication.
    """
    # 1. each client sends a soft-commitment to the server
    # 2. the server validates each soft-commitment
    # 3. the server sends the challenge to each client for the hard commitments
    # 4. each client sends the hard-commitments to the server
    # 5. the server validates all hard commitments
    # 6. the server constructs the final raffle transaction
    setup("testnet")
