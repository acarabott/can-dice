#!/bin/bash

# move old images to archive
COUNT=`ls incoming | wc -l`
if [ ! $COUNT -eq 0 ]
then
  NEW=data-set/`date +%Y%m%d-%H%M%S`
  echo "moving old images to $NEW"
  mkdir -p $NEW
  mv incoming/* $NEW
fi


# loop to get new images

while true; do
echo "syncing";
rsync -v -q --remove-source-files --exclude="*.jpg~" pi@pil:~/dev/can-dice/img-cap/output/*.jpg incoming 
sleep 10;
done
