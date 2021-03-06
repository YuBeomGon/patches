#!/bin/bash
# this is for makeing patches for wsi, using multi thread

#default src, des path
src_dir='/data/beomgon/Dataset/paps/20220405/HS6'
dst_dir='/data/beomgon/Dataset/paps/patch_images1/2022.04.07'
num_process=2
files_threshold=600

# ./make_patch src_dir des_dir
if [ $# -eq 2 ] ; then
    src_dir=$1
    dst_dir=$2
fi

# get src file list 
src_files=($src_dir/* )
src_files_len=${#src_files[*]}
split=$(($src_files_len / $num_process))

# split file list for multi processing
filesOne=${src_files[@]:0:$split}
filesTwo=${src_files[@]:$split:$src_files_len}

# echo ${filesOne[@]}
# echo '******************************'
# echo ${filesTwo[@]}

# if there is no des dir, make dst dir
[ -d $dst_dir ] || mkdir -p $dst_dir

make_patch() {
    for file in $@ ; do
        echo $file
        # use *.bif file only
        if [[ $file == *bif ]] ; then
        
            # get current file name only
            arr=(`echo $file | tr '/' ' '`)
            num=$((${#myarray[@]}-1))
            file=${arr[$num]}
            
            # wsi_name, use this as folder
            wsi_name=${file:0:-4}
            echo $wsi_name

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
}

# check file numbers of each wsi
check_files() {
    file_list=(`ls $src_dir`)
    for file in $file_list ; do
        # use *.bif file only
        if [[ $file == *bif ]] ; then
            wsi_name=${file:0:-4}
            echo $wsi_name `ls $dst_dir'/'$wsi_name | wc -l`
        fi
    done
}

# run patching wsi
( make_patch ${filesOne[@]} & make_patch ${filesTwo[@]} ) && check_files
