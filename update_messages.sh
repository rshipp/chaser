#!/bin/bash
xgettext chaser/*.py -p po/ \
      --copyright-holder="Ryan Shipp" \
      --package-name="Chaser" \
      --package-version=$(head -1 chaser/__init__.py|cut -d\" -f2) \
      --msgid-bugs-address=chakra@rshipp.com
sed -i 's/^\(# Copyright (C) \)YEAR/\12015-2016/;
		s/\(as the \)PACKAGE\( package.\)$/\1Chaser\2/;
		1c# Chaser translation file.\n# Do not change variables between {brackets}.' \
    po/messages.po

