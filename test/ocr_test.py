import base64
import sys
from pathlib import Path
from openai import OpenAI

"""用法: python ocr_test.py <图片路径>"""

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


def ocr_image(image_path: str, api_key: str, model: str = "PaddlePaddle/PaddleOCR-VL-1.5") -> str:
    """调用硅基流动平台的 OCR 模型识别图片中的文字"""
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
                    {"type": "text", "text": "请识别这张图片中的所有文字，只输出识别到的文字内容，不要添加任何解释。"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=300
    )

    return response.choices[0].message.content


def main():
    if len(sys.argv) < 2:
        print("用法: python ocr_test.py <图片路径>")
        sys.exit(1)

    # 配置你的 API Key
    api_key = ""

    image_path = sys.argv[1]

    if not Path(image_path).exists():
        print(f"错误: 文件不存在: {image_path}")
        sys.exit(1)

    try:
        result = ocr_image(image_path, api_key)
        print(result)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
