#!/bin/bash
FILENAME="$1"
echo $FILENAME
if [ ! -d "temp" ] 
then
    mkdir temp
fi
FILESIZE=$(wc -c < "$FILENAME")
echo $FILESIZE
for ((i = 1 ; i <= ("$FILESIZE"-600) ; i+=50));
do
    head -c $((i+300)) "$FILENAME" | tail -c 300 >> temp/file1
    head -c $((i+600)) "$FILENAME" | tail -c 300 >> temp/file2
    ./bcl2pezza
    rm temp/file1 temp/file2 temp/ris_bcl+300-300/Contig.file1
    cat temp/ris_bcl+300-300/Contig.file2 | grep file1 >> ContigSliding.csv
done
echo "\n endoffile"  >> ContigSliding.csv
#