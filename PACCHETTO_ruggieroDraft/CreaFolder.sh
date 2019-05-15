for file in ./SEW*?; do
    dir=${file##SEW}
    dir=${dir%_?}
    mkdir -p "./$dir/START" &&
    mv -iv "$file" "./$dir/START/"
    cp -v tutto_bcl.pl "./$dir/"
    cp -v 3provafinals_auto "./$dir/"
    cp -v bcl1pezza "./$dir/"
    cp -v script_diz "./$dir/"
    cp -v tridistanze_auto.pl "./$dir/"
done

