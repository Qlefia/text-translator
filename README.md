# Text Translator

A screen OCR translator powered by Large Language Models (LLMs). Captures text from the screen, translates it using providers such as DeepSeek, OpenAI, and others.

## Features

- 🖼️ Screen capture modes:
  - Full window capture
  - Area selection capture
  - File import support
- 📝 OCR capabilities:
  - Tesseract OCR integration
  - Support for multiple languages
  - High accuracy text recognition
- 🌐 Translation features:
  - Multiple LLM providers support (DeepSeek, OpenAI)
  - Real-time translation
  - History tracking
- 🎨 Modern UI:
  - Catppuccin theme support
  - Multiple color schemes
  - User-friendly interface

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Qlefia/text-translator.git
cd text-translator
```

2. Install dependencies:

```bash
pip install -r translator/requirements.txt
```

3. Install Tesseract OCR:

- Windows: Download and install from [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
- Linux: `sudo apt install tesseract-ocr`
- macOS: `brew install tesseract`

## Usage

1. Run the application:

```bash
python -m translator.main
```

2. Configure your API keys in the settings tab:

- OpenAI API key
- DeepSeek API key

3. Select your preferred capture mode:

- Window capture
- Area capture
- File import

4. Choose source and target languages

5. Start translating!

## Development

This project uses Poetry for dependency management and follows modern Python development practices.

1. Install Poetry:

```bash
pip install poetry
```

2. Install development dependencies:

```bash
poetry install
```

3. Run tests:

```bash
poetry run pytest
```

4. Format code:

```bash
poetry run black .
poetry run isort .
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [OpenAI API](https://openai.com/blog/openai-api)
- [DeepSeek](https://deepseek.com)
- [Catppuccin](https://github.com/catppuccin/catppuccin)
