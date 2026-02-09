# silicon-PaddleOCR

A Claude Code plugin that provides OCR (Optical Character Recognition) capabilities using PaddleOCR via the SiliconFlow API.

## Features

- Extract text from images (JPG, PNG, WebP, BMP, GIF)
- Batch processing with glob patterns
- JSON output format for programmatic use
- Customizable recognition prompts
- Support for custom models and parameters

## Installation

1. Clone this repository to your local Claude Code plugins directory:
```bash
git clone https://github.com/aotenjou/silicon-PaddleOCR.git ~/.claude/plugins/silicon-PaddleOCR
```

2. Set up your SiliconFlow API key as an environment variable:
```bash
export SILICONFLOW_API_KEY="your_api_key_here"
```

3. Install required Python dependencies:
```bash
pip install openai
```

## Usage

### Via Claude Code Command

After installing the plugin, use the `/ocr` command in Claude Code:

```
/ocr /path/to/image.jpg
```

### Direct Script Usage

You can also run the OCR script directly:

```bash
# Single image
python3 skills/ocr/scripts/ocr_skill.py /path/to/image.jpg

# Multiple images with glob pattern
python3 skills/ocr/scripts/ocr_skill.py /path/to/images/*.png

# JSON output
python3 skills/ocr/scripts/ocr_skill.py --json /path/to/image.jpg

# Custom prompt
python3 skills/ocr/scripts/ocr_skill.py -p "Extract as Markdown table" /path/to/table.jpg

# Save results to file
python3 skills/ocr/scripts/ocr_skill.py --json --output results.json /path/to/images/*.jpg
```

## Script Arguments

| Argument | Description |
|----------|-------------|
| `images` | Image file path(s) or glob pattern (required) |
| `-k, --api-key` | API key (default: SILICONFLOW_API_KEY env) |
| `-m, --model` | OCR model (default: PaddlePaddle/PaddleOCR-VL-1.5) |
| `-p, --prompt` | Custom recognition prompt |
| `-j, --json` | Output in JSON format |
| `-o, --output` | Save results to file |
| `--max-tokens` | Max tokens in response (default: 300) |

## Configuration

Get your API key from [SiliconFlow](https://siliconflow.cn).

## Supported Image Formats

- JPG/JPEG
- PNG
- WebP
- BMP
- GIF

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Project Structure

```
silicon-PaddleOCR/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── commands/
│   └── ocr.md                   # /ocr command definition
└── skills/
    └── ocr/
        ├── SKILL.md             # Skill documentation
        ├── scripts/
        │   └── ocr_skill.py     # Main implementation
        ├── references/
        │   └── api-configuration.md
        └── examples/
            └── sample-usage.sh
```
