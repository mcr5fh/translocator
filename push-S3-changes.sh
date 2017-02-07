echo "Make sure you are uploading from the proper virtual enviroment!!!"
echo "Bundling code..."
./bundle.sh > /dev/null 2>&1
echo "Bundled."
#send to S3
aws s3 cp ~/translocbundle.zip s3://mcr5fh-transloc/
aws lambda update-function-code --function-name Translocate --s3-bucket mcr5fh-transloc --s3-key translocbundle.zip 
