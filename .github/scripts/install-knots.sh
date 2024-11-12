#!/bin/sh

set -xeu

DIRNAME="bitcoin-${KNOTS_VERSION}"
FILENAME="${DIRNAME}-x86_64-linux-gnu.tar.gz"

cd "${HOME}"
wget -q "https://bitcoinknots.org/files/27.x/${KNOTS_VERSION}/bitcoin-${KNOTS_VERSION}-x86_64-linux-gnu.tar.gz"
tar -xf "${FILENAME}"
sudo mv "${DIRNAME}"/bin/* "/usr/local/bin"
rm -rf "${FILENAME}" "${DIRNAME}"
