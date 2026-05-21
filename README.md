# SWRT文档内容更新工具

一款基于Python开发的文档内容更新工具，根据SWRT输入文档自动更新SWRT平台文档中的相关内容。

## 功能特性

- 📄 支持导入.xlsx、.docx、.pdf、.txt格式文档
- 🔍 自动检查文档空值（输入文档E列、平台文档P列）
- ✨ 智能内容更新，精确ID匹配
- 📝 完整的变更预览和履历导出
- 💻 友好的图形用户界面

## 打点规则

1. SWRT输入文档E列="否"时提取C列ID
2. 在SWRT平台文档P列精确匹配ID
3. Q列设为NA，P列内容复制到R列
4. "实现状态"列设为"No"
5. "不能实现的原因"列设为P列内容

## 开发环境

- Python 3.8+
- PyQt5
- openpyxl
- python-docx
- pdfplumber
- pandas

## 快速开始

### 开发环境运行

```bash
cd doc_updater
python main.py
```

### 打包EXE

```bash
pyinstaller --clean package.spec
```

## 使用说明

详细使用说明请参考 `发布包_v1.5/使用说明.md`

## 项目结构

```
0503-test/
├── doc_updater/          # 主程序目录
│   ├── core/            # 核心逻辑
│   ├── formats/         # 格式处理
│   ├── ui/              # 用户界面
│   └── utils/           # 工具函数
├── 发布包_v1.5/         # 可执行文件发布包
└── README.md            # 项目说明
```

## 许可证

本项目仅供内部使用。