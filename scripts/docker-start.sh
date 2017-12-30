#!/usr/bin/env bash

docker build -t cryptoverse . && docker run -it --rm cryptoverse
