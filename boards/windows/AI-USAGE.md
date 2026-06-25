# Windows AI Usage

分析 Windows PE/二进制时的 AI 工作约定。

## 默认工具路径

- Ghidra: `tools/common/ghidra_*/`
- Cutter: `tools/windows/Cutter/`
- PE-bear: `tools/windows/PE-bear/`
- DiE: `tools/windows/die/`
- HxD: `tools/windows/HxD/`
- Procmon: `tools/windows/ProcessMonitor/`

## 分析流程

1. 先做文件识别 (DiE/PE-bear)
2. Ghidra 静态分析，命名函数，标注关键逻辑
3. 需要动态验证时用 x64dbg 或 Frida
4. Procmon 采集行为日志 → `exports/windows/procmon/`
5. IOC 提取 → `exports/windows/iocs/`
6. YARA/Sigma 规则 → `exports/windows/yara/` / `exports/windows/sigma/`
