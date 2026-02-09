---
allowed-tools: Bash(python3 ./skills/ocr/scripts/ocr_skill.py:*)
description: 使用 PaddleOCR 识别图片中的文字
---

## Context

- 当前工作目录: `pwd`
- API Key: 已通过 SILICONFLOW_API_KEY 环境变量设置

## Your task

调用 OCR skill 识别指定图片中的文字内容。

调用格式：
```bash
export SILICONFLOW_API_KEY="sk-xxxxxxxxxxxxx"
python3 ./skills/ocr/scripts/ocr_skill.py [参数] 图片路径
```

常用参数：
- 图片路径（必选）
- `-j, --json`: 以 JSON 格式输出
- `-o, --output`: 保存到指定文件
- `-k, --api-key`: 指定 API Key
- `-m, --model`: 指定模型
- `--max-tokens`: 最大 token 数

示例：
```bash
# 单张图片
python3 ./skills/ocr/scripts/ocr_skill.py ./test.jpg

# JSON 输出
python3 ./skills/ocr/scripts/ocr_skill.py -j ./test.jpg

# 多张图片
python3 ./skills/ocr/scripts/ocr_skill.py ./*.png
```

执行后直接返回识别结果给用户。
