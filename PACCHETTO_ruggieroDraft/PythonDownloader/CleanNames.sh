for file in ./*; do
    printf file
    mv file $(echo file | sed -e 's/[^A-Za-z0-9._-]/_/g')
done