#!/bin/bash

find ./ -type f -name "*.docx" -not -name "~*" -exec pandoc -s {} -o {}.pdf \;
find ./ -type f -name "*.docx" -not -name "~*" -exec pandoc {} -t html -o {}.html \;