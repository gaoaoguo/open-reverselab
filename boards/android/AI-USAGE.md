# Android AI Usage

分析 Android 应用时的 AI 工作约定。

## 默认工具路径

- apktool: `tools/android/apktool/apktool.jar`
- jadx: `tools/android/jadx/`
- uber-apk-signer: `tools/android/uber-apk-signer/uber-apk-signer.jar`

## 分析流程

1. 先用 apktool 解包 APK
2. 用 jadx 打开 DEX 反编译
3. 关注 AndroidManifest.xml、入口 Activity、native 库
4. Frida 动态 hook 时脚本保存到 `scripts/android/`
5. 重打包产物放入 `patches/android/apk-builds/`
