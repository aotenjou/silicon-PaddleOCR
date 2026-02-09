import base64
import json
import re
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
from openai import OpenAI

"""用法: python ocr_test.py <图片路径>

输出格式（结构化 JSON）:
{
    "image_path": "图片路径",
    "image_size": [width, height],
    "texts": [
        {
            "text": "识别的文字",
            "confidence": 0.95,
            "box": [[x1, y1], [x2, y2], [x3, y3],
              [x4, y4]]
        }
    ],
    "full_text": "所有文本的组合"
}

LOC 坐标说明:
- LOC 数值是归一化坐标，需要转换成真实像素坐标
- 转换公式: pixel = LOC × (图片尺寸 / LOC最大值)
- LOC 最大值约为 972 (可能因模型/图片而有所变化)
"""


def image_to_base64(image_path: str) -> str:
    """将图片文件转换为 base64 字符串"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_image_size(image_path: str) -> Tuple[int, int]:
    """获取图片尺寸"""
    from PIL import Image
    with Image.open(image_path) as img:
        return img.size


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


def parse_loc_tags(content: str, image_size: Tuple[int, int]) -> List[Dict[str, Any]]:
    """
    解析 PaddleOCR-VL 模型返回的 <|LOC_xxx|> 标记
    返回带真实像素坐标的文字列表

    格式: 文本<|LOC_x1|><|LOC_y1|><|LOC_x2|><|LOC_y2|><|LOC_x3|><|LOC_y3|><|LOC_x4|><|LOC_y4|>文本...

    坐标转换: LOC 是归一化值，需要乘以缩放系数得到真实像素坐标
    """
    img_width, img_height = image_size

    text_coord_pairs = re.findall(r'([^\|<]+?)((?:<\|LOC_\d+\|\>)+)', content)

    # 先扫描所有 LOC 值，找到最大值用于计算缩放系数
    all_loc_values = []
    for _, loc_tags in text_coord_pairs:
        coords = [int(c) for c in re.findall(r'LOC_(\d+)', loc_tags)]
        all_loc_values.extend(coords)

    max_loc = max(all_loc_values) if all_loc_values else 972

    # 计算缩放系数
    x_scale = img_width / max_loc if max_loc > 0 else 1
    y_scale = img_height / max_loc if max_loc > 0 else 1

    texts = []

    for text_chunk, loc_tags in text_coord_pairs:
        text = text_chunk.strip()
        if not text:
            continue

        # 提取 LOC 数值
        coord_matches = re.findall(r'LOC_(\d+)', loc_tags)
        coords = [int(c) for c in coord_matches]

        # 转换为真实像素坐标
        if len(coords) >= 8:
            # 4个点(每个点2个坐标): x1,y1,x2,y2,x3,y3,x4,y4
            box = []
            for i in range(0, 8, 2):
                x = int(coords[i] * x_scale)
                y = int(coords[i+1] * y_scale)
                box.append([x, y])
        elif len(coords) >= 4:
            # 4个值: x1,y1,x2,y2 (边界框)
            x1 = int(coords[0] * x_scale)
            y1 = int(coords[1] * y_scale)
            x2 = int(coords[2] * x_scale)
            y2 = int(coords[3] * y_scale)
            box = [
                [x1, y1],
                [x2, y1],
                [x2, y2],
                [x1, y2]
            ]
        else:
            # 没有足够坐标
            box = [[0, 0], [0, 0], [0, 0], [0, 0]]

        texts.append({
            "text": text,
            "box": box,
        })

    return texts


def ocr_image(image_path: str, api_key: str, model: str = "PaddlePaddle/PaddleOCR-VL-1.5") -> Dict[str, Any]:
    """调用硅基流动平台的 OCR 模型识别图片中的文字，返回结构化数据

    Returns:
        Dict: {
            "image_path": str,
            "image_size": [width, height],
            "texts": List[Dict],  # 文本项列表
            "full_text": str,     # 所有文本的组合
        }
    """
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.siliconflow.cn/v1"
    )

    # 获取图片尺寸
    image_size = get_image_size(image_path)

    # 转换图片为 base64
    base64_image = image_to_base64(image_path)
    mime_type = get_mime_type(image_path)

    # 使用简单的提示词，让模型返回原生格式（包含 LOC 标记）
    prompt = "请识别这张图片中的所有文字。"

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
        max_tokens=2000
    )

    content = response.choices[0].message.content
    if not content:
        return {
            "image_path": image_path,
            "image_size": list(image_size),
            "texts": [],
            "full_text": ""
        }

    # 解析 LOC 标记，提取文本和位置信息（包含坐标转换）
    texts = parse_loc_tags(content, image_size)

    full_text = "\n".join([t.get("text", "") for t in texts])

    return {
        "image_path": image_path,
        "image_size": list(image_size),
        "texts": texts,
        "full_text": full_text
    }


def main():
    if len(sys.argv) < 2:
        print("用法: python ocr_test.py <图片路径>")
        sys.exit(1)

    # 配置你的 API Key
    api_key = "sk-slizahgqnoceguqzgxrdtjjoiddjezppwsglhzoypcehqylu"

    image_path = sys.argv[1]

    if not Path(image_path).exists():
        print(f"错误: 文件不存在: {image_path}")
        sys.exit(1)

    try:
        result = ocr_image(image_path, api_key)
        # 输出格式化的 JSON
        print(json.dumps(result, ensure_ascii=False, indent=2))

        # 可选：显示可读格式的总结
        # print(f"\n识别到 {len(result['texts'])} 处文字:")
        # print(f"图片尺寸: {result['image_size'][0]} x {result['image_size'][1]}")
        # for item in result['texts']:
        #     text = item.get('text', '')[:40]
        #     if len(item.get('text', '')) > 40:
        #         text += "..."
        #     box = item.get('box', [])
        #     conf = item.get('confidence', 0)
        #     print(f"  [{conf:.2f}] {text} @ {box}")

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
