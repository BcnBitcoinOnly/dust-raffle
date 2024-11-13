# Dust Raffle prototype

[![continuous integration](https://github.com/BcnBitcoinOnly/dust-raffle/actions/workflows/test.yml/badge.svg)](https://github.com/BcnBitcoinOnly/dust-raffle/actions/workflows/test.yml)

## Protocol

Revision v0

The Dust Raffle protocol is based on bidirectional JSON-RPC 2.0 messages over a TCP connection
between clients who want to participate in the raffle and a server that coordinates them.

### Phases

#### 1. Registration

Clients connect to the server and send soft-commitments to participate in the raffle.

A soft commitment consists of a message and a signature.
The message MUST be an outpoint in `txid:vout` format, like `4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b:0`
The signature MUST be a valid ECDSA signature made with the private key that unlocks the scriptPubKey at that outpoint.
The outpoint MUST NOT be spent at the time of making the soft commitment. Attempting to double-spend a committed outpoint
results in a ban from the service.

A client might send as many soft-commitments as it wants during the registration phase.

After making a soft commitment the client must keep the connection alive.

The server will send regular keepalive messages, which the client must acknowledge.
If the client closes the connection it will be excluded from the round.


#### 2. Signing

After a certain time has passed the server sends a message to all the clients that submitted at least one
soft commitment and are still connected.

The message includes a Bitcoin blockheight which hasn't been reached yet, the total amount of sats in the current raffle,
a merkle root hash and the payout addresses of all the participants.

Each client MUST return a signed transaction for each payout address.
These transactions spend its own soft-committed UTXO and send the total amount of sats to each one of the payout addresses.

The SIGHASH of the signatures MUST be ALL|ANYONECANPAY.
Individually these transactions are invalid because they spend more sats than they have in their inputs.
But due to the non-standard SIGHASH they can be joined together, and the combined transaction is valid.

The transactions MUST include an OP_RETURN with the blockheight the server committed to.

Clients SHOULD validate the Merkle Root according to the Raffle Rules before making any hard commitment.


#### 3. Raffle

The server waits until blockheight is reached and confirmed under 6 blocks.

Then uses the block hash to compute the final winner, constructs the correct transaction
and publishes the transaction.

### Raffle Rules

1. Participant outpoints are lexicographically sorted, and the Merkle root of them all
   is calculated using SHA256. If the number of outpoints is odd and greater than 1, the last outpoint is duplicated.
2. A second Merkle Root is computed from the Outputs Merkle Root and the Block hash. These are also
   lexicographically sorted.
3. The final Merkle Root hash is treated as a natural integer. Then hash % num_participants selects the winning input,
   which receives all the sats.

The server reveals the Outpoint Merkle Root to the clients before the block hash is known, therefore it cannot cheat
by trying a collection of its own inputs until one is the winner.

Once the block hash is known, anyone can verify that the transaction encodes a fair raffle.


### Claiming the prize

This proposal depends on package relay. The winner is supposed to make a CPFP transaction that
spends the raffle transaction (at 0 s/vB) paying as many fees from the prize as he wants.


### Bans

In the period between the server receiving all the hard commitments and the winner getting the raffle transaction mined, any of the
participants can double spend one of their inputs, and if their transaction gets mined first it will invalidate
the raffle transaction.

The server must scan the blockchain for any participant outpoint being spent before the raffle transaction.
When it detects such a case it bans that output AND the ones in the transaction that double spent it from
participating in the raffle again for at least 3 months. Any other UTXOs will the same scriptPubKey are also banned.


### Weaknesses

The current design trusts that the server will construct the correct transaction, but is actually capable of building
and broadcasting a transaction to any of the participants. However, it cannot cheat without everyone noticing it.

However, the clients are required to sign a large number of transactions. This design is only practical for
UTXOs held in a hot wallet able to keep connected to the server for a long period of time and sign a large
number of transactions quickly (so hardware wallets would not be able to use the service).

An improved version of the protocol would have the server construct the final TX right after he collects the soft
commitments and send the blinded final transaction to the clients for signing, but without requiring to trust the server.

### Privacy

Raffle transactions are not private by design, since it's plain to see which input won the raffle and which ones didn't.

Regarding client-server privacy, it should be studied if offering the service over Tor is performant enough.
