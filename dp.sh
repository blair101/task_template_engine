#!/bin/bash

echo "start commit..."
git add *
git status
git commit -m "add a article or modify article"
git push
echo "successful commit"
