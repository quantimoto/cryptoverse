#!/usr/bin/env bash

docker build -t cryptoverse . && docker run --rm -it cryptoverse
