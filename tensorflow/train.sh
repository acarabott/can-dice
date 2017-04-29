#!/bin/bash

echo "enter labelled dir";
read IN;
echo "enter training steps";
read STEPS;
echo "enter learning rate";
read RATE;

DST=dice-i`basename $IN`-s$STEPS-r$RATE

/Users/ac/src/tensorflow/bazel-bin/tensorflow/examples/image_retraining/retrain \
--image_dir $IN \
--how_many_training_steps $STEPS \
--output_graph=$DST/output_graph.pb \
--output_labels=$DST/output_labels.txt \
--summaries_dir=$DST/retrain_logs \
--bottleneck_dir=$DST/bottleneck


