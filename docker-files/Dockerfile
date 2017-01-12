FROM ubuntu:16.04

MAINTAINER Andrey Zheregelya

# Currently this file contains the copy of validator node but without database config.
# It also starts CLI as entrypoint by default
# And also contains tester script

# Where install sovrin: still using old packages.
# TODO: move to sovrin-client when it will be ready
ARG install_sovrin="pip3 install --no-cache-dir sovrin"

RUN apt-get update \
    && apt-get install python3.5 libsodium18 libgmp3-dev flex bison libssl-dev bsdmainutils python3-pip -y \
    && apt-get install wget -y \
    && apt-get install git -y \
    && apt-get clean

# TODO: use native packages when they will be ready.
RUN wget https://crypto.stanford.edu/pbc/files/pbc-0.5.14.tar.gz \
    && tar xvf pbc-0.5.14.tar.gz \
    && cd pbc-0.5.14 \
    && ./configure && make && make install \
    && cd .. && rm -rf pbc-0.5.14 pbc-0.5.14.tar.gz

RUN pip3 install --upgrade pip wheel setuptools \
    && pip3.5 install Charm-Crypto==0.43 \
    && $install_sovrin

ENTRYPOINT ["sovrin"]
