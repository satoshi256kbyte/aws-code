#!/bin/bash

cd `dirname $0`

# catchとthrowの数が一致していないコードの内、すでに把握しているものの数
known=1
catch=$(find ./app -name "*.php" | xargs pcre2grep -Mrh 'catch.*{[\s\S]*?'} | grep -v "//" | grep "catch" | wc -l)
throw=$(find ./app -name "*.php" | xargs pcre2grep -Mrh 'catch.*{[\s\S]*?'} | grep -v "//" | grep "throw" | wc -l)

echo "catch statements found : $catch"
echo "throw statements found : $throw"

if [ $((catch)) -ne $((throw)) ]; then
  echo "Number of catch and throw statements do not match"
  if [ $((known)) -ne $(($catch - $throw)) ]; then
    echo "Number of known exceptions do not match"
    exit 1
  else
    echo "Number of known exceptions match"
  fi
fi

echo "No problem found"
exit 0