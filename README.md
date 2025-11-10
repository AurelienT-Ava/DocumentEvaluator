# Document Evaluator for LLM Compatibility

Evaluate Word documents (.docx) for compatibility with Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) systems using Azure OpenAI Service.

## 📋 Overview

This tool automatically assesses Word documents on 7 key criteria to determine their suitability for use with LLMs like ChatGPT. It helps identify content quality issues that could impact LLM performance, particularly in RAG applications.

### Evaluation Criteria

Each document is scored 0-5 on:

| Criterion | Description |
|-----------|-------------|
| **Relevance** | How focused and on-topic the content is |
| **Factual Accuracy** | Quality of research and factual correctness |
| **Clarity** | Writing quality, structure, and understandability |
| **Hallucination Risk** | Likelihood of causing LLM hallucinations (0=high risk, 5=low risk) |
| **Style Match** | Consistency and professionalism of writing style |
| **RAG Usability** | Suitability as context for RAG systems |
| **Citation Quality** | Proper inclusion and formatting of sources/references |

### Key Features

✅ **Smart Chunking** - Automatically splits large documents into 4000-token chunks  
✅ **Batch Processing** - Scan entire directories with optional recursion  
✅ **Weighted Aggregation** - Combines chunk scores based on token count  
✅ **Multiple Output Formats** - CSV (default), JSON, or colored console output  
✅ **Robust Error Handling** - Retries on API failures, continues processing on errors  
✅ **Flexible Configuration** - Environment variables, config files, or CLI arguments  

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Azure OpenAI Service account with:
  - API Key
  - Endpoint URL
  - Deployed model (e.g., GPT-4, GPT-3.5-turbo)

### Installation

1. **Clone or download this repository**

2. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   This installs:
   - `python-docx` - Word document parsing
   - `openai` - Azure OpenAI API client
   - `tiktoken` - Token counting
   - `click` - CLI framework
   - `python-dotenv` - Environment configuration
   - `tqdm` - Progress bars

### Configuration

Choose **one** of these methods to configure Azure OpenAI credentials:

#### Option 1: Environment File (Recommended)

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```env
   AZURE_OPENAI_API_KEY=your-api-key-here
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT=your-deployment-name
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   ```

#### Option 2: Environment Variables

**Windows (PowerShell):**
```powershell
$env:AZURE_OPENAI_API_KEY="your-api-key"
$env:AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
$env:AZURE_OPENAI_DEPLOYMENT="gpt-4"
```

**Linux/macOS:**
```bash
export AZURE_OPENAI_API_KEY="your-api-key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT="gpt-4"
```

#### Option 3: Command-Line Arguments

Pass credentials directly when running (see Usage examples below).

## 📖 Usage

### Basic Examples

**Evaluate a single document:**
```bash
python main.py document.docx
```

**Evaluate all .docx files in a directory:**
```bash
python main.py ./documents
```

**Recursive directory scan:**
```bash
python main.py ./documents --recursive
```

### Output Formats

**CSV output (default):**
```bash
python main.py ./documents -r --output results.csv
```

**JSON output:**
```bash
python main.py ./documents -r --format json --output results.json
```

**Console output with colors:**
```bash
python main.py ./documents --format console
```

### Advanced Options

**Provide credentials via CLI:**
```bash
python main.py document.docx \
  --api-key "your-key" \
  --endpoint "https://your-resource.openai.azure.com/" \
  --deployment "gpt-4"
```

**Custom temperature and retries:**
```bash
python main.py ./documents \
  --temperature 0.0 \
  --max-retries 5
```

### Complete Command Reference

```
python main.py [OPTIONS] PATH

Arguments:
  PATH                    Path to .docx file or directory

Options:
  -r, --recursive        Scan directories recursively
  -f, --format TEXT      Output format: csv, json, or console [default: csv]
  -o, --output PATH      Output file path (for csv/json)
  --api-key TEXT         Azure OpenAI API key
  --endpoint TEXT        Azure OpenAI endpoint URL
  --deployment TEXT      Azure OpenAI deployment name
  --api-version TEXT     Azure OpenAI API version [default: 2024-02-15-preview]
  --temperature FLOAT    LLM temperature for consistency [default: 0.0]
  --max-retries INTEGER  Maximum API call retries [default: 3]
  --help                 Show this message and exit
```

## 📊 Output Formats

### CSV Example

```csv
filename,relevance,factual_accuracy,clarity,hallucination,style_match,rag_usability,citation_quality,status,error_message
report.docx,4.5,4.2,4.8,4.0,4.3,4.6,3.5,success,
guide.docx,5.0,4.0,5.0,5.0,4.5,5.0,2.0,success,
broken.docx,0,0,0,0,0,0,0,error,Failed to parse document
```

### JSON Example

```json
[
  {
    "filename": "report.docx",
    "evaluation": {
      "relevance": 4.5,
      "factual_accuracy": 4.2,
      "clarity": 4.8,
      "hallucination": 4.0,
      "style_match": 4.3,
      "rag_usability": 4.6,
      "citation_quality": 3.5
    },
    "status": "success"
  },
  {
    "filename": "broken.docx",
    "status": "error",
    "error_message": "Failed to parse document"
  }
]
```

### Console Example

```
Document Evaluation Results
================================================================================

File: report.docx
Status: ✓ Success

Scores:
  Relevance...................... 4.5/5
  Factual Accuracy............... 4.2/5
  Clarity........................ 4.8/5
  Hallucination.................. 4.0/5
  Style Match.................... 4.3/5
  Rag Usability.................. 4.6/5
  Citation Quality............... 3.5/5
--------------------------------------------------------------------------------

Summary:
  Total documents: 2
  Successful: 2
```

## 🔧 How It Works

1. **Document Scanning** - Finds all `.docx` files in the specified path
2. **Text Extraction** - Reads document content using `python-docx`
3. **Smart Chunking** - Splits large documents at paragraph boundaries (max 4000 tokens)
4. **LLM Evaluation** - Sends each chunk to Azure OpenAI with structured evaluation prompt
5. **Score Aggregation** - Combines chunk scores using weighted average by token count
6. **Output Generation** - Formats results as CSV, JSON, or console display

### Chunking Strategy

- Maximum 4000 tokens per chunk (GPT-4 context window)
- Splits at paragraph boundaries when possible
- Falls back to sentence-level splitting for very long paragraphs
- Uses `tiktoken` with `cl100k_base` encoding

### Error Handling

- **API Failures**: Exponential backoff retry (configurable)
- **Document Errors**: Logs error, continues with remaining documents
- **Missing Config**: Clear error messages with suggested fixes

## 🛠️ Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### "Missing required configuration" errors
Verify your `.env` file or environment variables are set correctly:
```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('AZURE_OPENAI_API_KEY'))"
```

### API rate limit errors
- Reduce batch size by processing fewer documents at once
- Increase `--max-retries` value
- Add delays between runs

### No documents found
- Verify the path is correct
- Use `--recursive` flag for nested directories
- Ensure files have `.docx` extension (not `.doc`)

## 📁 Project Structure

```
DocumentEvaluator/
├── main.py                 # CLI entry point
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
├── .env.example           # Example environment config
├── README.md              # This file
└── src/
    ├── __init__.py
    ├── config.py          # Azure OpenAI configuration
    ├── document_parser.py # Word document parsing & chunking
    ├── evaluator.py       # LLM evaluation logic
    ├── scanner.py         # File/directory scanning
    └── output.py          # Output formatters (CSV/JSON/Console)
```

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Support for additional document formats (.pdf, .txt, .md)
- Custom evaluation criteria and prompts
- Parallel processing for faster batch evaluation
- Integration with other LLM providers (OpenAI, Anthropic, etc.)
- Web interface or GUI

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

Built with:
- [python-docx](https://python-docx.readthedocs.io/) - Word document processing
- [OpenAI Python SDK](https://github.com/openai/openai-python) - Azure OpenAI integration
- [tiktoken](https://github.com/openai/tiktoken) - Token counting
- [Click](https://click.palletsprojects.com/) - CLI framework
