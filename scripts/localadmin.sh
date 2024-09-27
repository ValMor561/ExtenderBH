#!/bin/bash
cat $2 | while read line
do
    echo "[+]" $line;
    net rpc group members Administrators -U $1 -I $line;
    echo ;
done