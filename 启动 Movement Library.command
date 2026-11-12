#!/bin/zsh
cd -- "${0:A:h}"
if ! command -v python3 >/dev/null 2>&1; then
  print '本机没有 Python 3。请直接双击同文件夹中的 index.html 打开离线版本。'
  read 'reply?按回车退出…'
  exit 1
fi
exec python3 serve.py
