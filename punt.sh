TAR_FILE=/tmp/formby`date '+%H%M'`.tar.bz2
echo "Creating" $TAR_FILE
tar -cj --exclude ../formby/.git -f $TAR_FILE ../formby
echo "Copying" $TAR_FILE "to Dropbox"
cp $TAR_FILE ~/Dropbox/Formby
