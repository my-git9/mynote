#!/bin/bash

datetime=`date +'%Y%m%d'`
git add .
git commit -m "$datetime"

git push

