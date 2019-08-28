#!/bin/bash
FILENAME="$1"
echo $FILENAME
if [ ! -d "temp" ] 
then
    mkdir temp
fi
FILESIZE=$(wc -c < "$FILENAME")
echo $FILESIZE
endofile=$((FILESIZE/100))
echo $endofile
for ((i = 1 ; i <= $endofile ; i++));
do
    head -c $((i*100)) $FILENAME | tail -c 100 >> temp/file1
    head -c $(((i+1)*100)) $FILENAME | tail -c 100 >> temp/file2
    ./bcl2pezza
    rm temp/file1 temp/file2 temp/ris_bcl+100-100/Contig.file1
    cat temp/ris_bcl+100-100/Contig.file2 | grep file1 >> ContigSliding
done