#!/bin/bash

# 强制清理旧文件
rm -rf build dist __pycache__

# 生成新的spec文件（包含所有依赖）
pyi-makespec --onefile --windowed \
--name CalcRaze \
--add-data "assets:Resources/assets" \
--add-data "config:Resources/config" \
--hidden-import pygame._macosx \
--hidden-import googletrans.models \
--osx-bundle-identifier "com.yourdomain.calcraze" \
calcraze.py

# 修改spec文件确保资源正确嵌入
sed -i '' 's/datas=\[\]/datas=[("assets", "Resources/assets"), ("config", "Resources/config")]/g' CalcRaze.spec

# 执行打包
pyinstaller --noconfirm CalcRaze.spec

# 强制签名（即使没有开发者证书）
codesign --force --deep --sign - dist/CalcRaze.app

# 生成用户友好的DMG
hdiutil create -volname CalcRaze \
-srcfolder dist/CalcRaze.app \
-ov -format UDZO \
-fs HFS+ \
-imagekey zlib-level=9 \
CalcRaze.dmg

echo "打包完成！请将 CalcRaze.dmg 发送给朋友。"