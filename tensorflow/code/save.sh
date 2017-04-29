#!/bin/bash

echo "enter image dimension"
read DIM;
echo "enter training steps";
read STEPS;
echo "enter accuracy";
read ACC;

DST=dice-$DIM-$STEPS-$ACC

mkdir -p $DST && \
cp /tmp/output_graph.pb $DST && \
cp /tmp/output_labels.txt $DST && \
cp -R /tmp/retrain_logs $DST

echo "created $DST"
