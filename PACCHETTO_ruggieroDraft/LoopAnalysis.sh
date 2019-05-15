for dir in ./SEW*?; do
    cd "./$dir"
    ./tutto_bcl.pl
    cd ..
done