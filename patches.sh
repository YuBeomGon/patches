#!/bin/bash
# this is for makeing patches for wsi, using single thread

#default src, des path
src_dir='/data/beomgon/Dataset/paps/20220405/HS6'
dst_dir='/data/beomgon/Dataset/paps/patch_images1/2022.04.07'
files_threshold=600

# ./make_patch src_dir des_dir
if [ $# -eq 2 ] ; then
    src_dir=$1
    dst_dir=$2
fi

# wsi file list
file_list=`ls $src_dir`

# if there is no des dir, make dst dir
[ -d $dst_dir ] || mkdir -p $dst_dir

for file in $file_list ; do
    # use *.bif file only
    if [[ $file == *bif ]] ; then
        echo $file
        # wsi_name, use this as folder
        wsi_name=${file:0:-4}
        
        # make folder which name is wsi
        [ -d $dst_dir'/'$wsi_name ] || mkdir -p $dst_dir'/'$wsi_name
        
        # if file number is less than 800, remove and do paching again
        if [ `ls $dst_dir'/'$wsi_name | wc -l` -le $files_threshold ] ; then 
            
            # print folder and number of files in it
            echo '******remove folder******' $wsi_name 'num' `ls $dst_dir'/'$wsi_name | wc -l`
            
            # remove that folder and make folder again
            rm -rf $dst_dir'/'$wsi_name && mkdir -p $dst_dir'/'$wsi_name
            
            # do patching
            echo 'patching is going on'
            
            python main.py $src_dir'/'$file $dst_dir'/'$wsi_name
            # print number of files
            echo '******complete******' $wsi_name 'num' `ls $dst_dir'/'$wsi_name | wc -l`   
        
        else 
            echo $wsi_name 'is already done' 'num' `ls $dst_dir'/'$wsi_name | wc -l`
        fi
    fi
done

# check file numbers of each wsi
file_list=`ls $src_dir`
for file in $file_list ; do
    # use *.bif file only
    wsi_name=${file:0:-4}
    if [[ $file == *bif ]] ; then
        echo $wsi_name `ls $dst_dir'/'$wsi_name | wc -l`
    fi
done

