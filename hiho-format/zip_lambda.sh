#!/bin/sh

#Set path for AWS CLI
export PATH=/usr/local/bin:$PATH
source ~/.bash_profile

if [ "$1" == "update" ]
then
	# Update Zip dependencies
	pip install --target ./package oauth2client==1.5.2
	pip install --target ./package tempfile
	cd package
	zip -r ../format-deployment-package.zip .
	cd ..

else
	echo "Not updating dependencies"
fi

# Add handler to package
zip -g format-deployment-package.zip lambda_function.py

# Deploy to lambda
aws lambda update-function-code \
	--function-name HIHO-format \
	--zip-file fileb://format-deployment-package.zip \
