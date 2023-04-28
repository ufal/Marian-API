#!/usr/bin/python3
import sys, json, re

in_file = open(sys.argv[1], "r", encoding="utf-8")

in_lines = in_file.readlines()
for line in in_lines:
    print(json.dumps(line))
