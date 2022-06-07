#! /bin/bash

set -e

current_dir=$PWD
echo $current_dir

name=$1
config=$2

dir=`mktemp -d`

# Copy code
cp -r craigslist_rss.py $dir/
cp -r $config $dir/conf.yaml

# Copy dependencies
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
cp -r venv/lib/python3.[567]/site-packages/* $dir/

cd $dir
zip -r9 $current_dir/$name.zip .
cd $current_dir
rm -rf $dir
