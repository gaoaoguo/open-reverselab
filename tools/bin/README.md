# Tool Binaries / Wrappers

工具启动脚本。此目录存放指向 `tools/` 下各工具可执行文件的 `.bat` 快捷方式或符号链接。

## 建议创建

```powershell
# 示例：创建工具的 bat wrapper
@echo off
java -jar "%~dp0..\android\apktool\apktool.jar" %*
```
