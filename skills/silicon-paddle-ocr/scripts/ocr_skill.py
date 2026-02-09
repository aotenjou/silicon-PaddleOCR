#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR Skill - 使用 PaddleOCR 识别图片中的文字
"""

import base64
import json
import sys
from pathlib import Path
from typing import List, Optional

try:
    from openai import OpenAI
except ImportError:
    print("错误: 需要安装 openai 库")
    print("运行: pip install openai")
    sys.exit(1)


def image_to_base64(image_path: str) -> str:
    """将图片文件转换为 base64 字符串"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_mime_type(image_path: str) -> str:
    """根据文件扩展名获取 MIME 类型"""
    ext = Path(image_path).suffix.lower()
    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
        ".gif": "image/gif",
    }
    return mime_types.get(ext, "image/jpeg")


def ocr_image(
    image_path: str,
    api_key: str,
    model: str = "PaddlePaddle/PaddleOCR-VL-1.5",
    prompt: str = "请识别这张图片中的所有文字，只输出识别到的文字内容，不要添加任何解释。",
    max_tokens: int = 300
) -> str:
    """
    调用硅基流动平台的 OCR 模型识别图片中的文字

    Args:
        image_path: 图片文件路径
        api_key: API 密钥
        model: 使用的模型名称
        prompt: 识别提示词
        max_tokens: 最大返回 token 数

    Returns:
        识别到的文字内容
    """
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.siliconflow.cn/v1"
    )

    # 转换图片为 base64
    base64_image = image_to_base64(image_path)
    mime_type = get_mime_type(image_path)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=max_tokens
    )

    return response.choices[0].message.content


def resolve_glob_pattern(pattern: str) -> List[str]:
    """解析 glob 模式返回文件列表"""
    import glob
    return glob.glob(pattern)


def get_api_key() -> Optional[str]:
    """从环境变量获取 API Key"""
    import os
    return os.environ.get("SILICONFLOW_API_KEY")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="OCR - 使用 PaddleOCR 识别图片中的文字",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Use cases:
  - 单张图片识别:
      %(prog)s ./test.jpg

  - 多张图片批处理:
      %(prog)s ./images/*.png

  - 自定义模型:
      %(prog)s -m 模型名 ./test.jpg

  - 自定义提示词:
      %(prog)s -p "请识别并翻译成英文" ./test.jpg
        """
    )

    parser.add_argument(
        "images",
        nargs="+",
        help="图片路径或 glob 模式（支持 *.jpg, *.png 等）"
    )
    parser.add_argument(
        "-k", "--api-key",
        default=None,
        help="API 密钥（默认从 SILICONFLOW_API_KEY 环境变量读取）"
    )
    parser.add_argument(
        "-m", "--model",
        default="PaddlePaddle/PaddleOCR-VL-1.5",
        help="使用的模型名称（默认: PaddlePaddle/PaddleOCR-VL-1.5）"
    )
    parser.add_argument(
        "-p", "--prompt",
        default="请识别这张图片中的所有文字，只输出识别到的文字内容，不要添加任何解释。",
        help="识别提示词"
    )
    parser.add_argument(
        "-j", "--json",
        action="store_true",
        help="以 JSON 格式输出结果（便于程序解析）"
    )
    parser.add_argument(
        "-o", "--output",
        help="将结果保存到指定文件"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=300,
        help="最大返回 token 数（默认: 300）"
    )

    args = parser.parse_args()

    # 获取 API Key
    api_key = args.api_key or get_api_key()
    if not api_key:
        print("错误: 未提供 API Key", file=sys.stderr)
        print("请通过以下方式之一提供:", file=sys.stderr)
        print("  1. 设置环境变量: export SILICONFLOW_API_KEY=your_key", file=sys.stderr)
        print("  2. 使用 -k 参数: %(prog)s -k your_key image.png" % {"prog": parser.prog}, file=sys.stderr)
        sys.exit(1)

    # 解析图片列表
    image_files: List[str] = []
    for pattern in args.images:
        files = resolve_glob_pattern(pattern)
        if files:
            image_files.extend(files)
        else:
            # 如果 glob 没匹配到，可能是精确路径
            if Path(pattern).exists():
                image_files.append(pattern)
            else:
                print(f"警告: 未找到匹配的文件: {pattern}", file=sys.stderr)

    if not image_files:
        print("错误: 没有找到有效的图片文件", file=sys.stderr)
        sys.exit(1)

    # 处理每张图片
    results = {}
    for image_path in image_files:
        if not Path(image_path).exists():
            print(f"警告: 跳过不存在的文件: {image_path}", file=sys.stderr)
            continue

        try:
            result = ocr_image(
                image_path,
                api_key,
                model=args.model,
                prompt=args.prompt,
                max_tokens=args.max_tokens
            )

            file_name = Path(image_path).name
            results[file_name] = result

            # 输出结果
            if args.json:
                pass  # JSON 输出在最后统一处理
            else:
                print(f"--- {file_name} ---")
                print(result)
                print()

        except Exception as e:
            print(f"错误: 处理 {image_path} 时出错 - {e}", file=sys.stderr)
            results[Path(image_path).name] = {"error": str(e)}

    # JSON 输出或保存到文件
    if args.json or args.output:
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"结果已保存到: {args.output}", file=sys.stderr)
        else:
            print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
