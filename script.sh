rm ~/translocbundle.zip;
cd $VIRTUAL_ENV/lib/python2.7/site-packages;
zip -r9 ~/translocbundle.zip * ;
cd $VIRTUAL_ENV/lib64/python2.7/site-packages;
zip -r9 ~/translocbundle.zip * ;
cd ~/translocator;
zip -g ~/translocbundle.zip *.py;
