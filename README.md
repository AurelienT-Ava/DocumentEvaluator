# Document Evaluator

A tool to evaluate Word documents for LLM compatibility using Azure OpenAI Service.

## Features

- **LLM Compatibility Scoring**: Evaluates documents on 7 criteria:
  - Relevance (0-5)
  - Factual Accuracy (0-5)
  - Clarity (0-5)
  - Hallucination Risk (0-5)
  - Style Match (0-5)
  - RAG Usability (0-5)
  - Citation Quality (0-5)

- **Smart Chunking**: Automatically chunks large documents (4000 tokens per chunk)
- **Flexible Scanning**: Process single files or entire directories (with optional recursion)
- **Multiple Output Formats**: CSV (default), JSON, or console output
- **Error Handling**: Continues processing on failures, logs errors for individual documents

## Installation

1. Install Python 3.10 or higher
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure Azure OpenAI credentials (choose one method):
   - **Environment variables** (recommended):
     ```bash
     $env:AZURE_OPENAI_API_KEY="your-api-key"
     $env:AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
     $env:AZURE_OPENAI_DEPLOYMENT="your-deployment-name"
     ```
   - **Config file**: Copy `.env.example` to `.env` and fill in your credentials
   - **Command-line arguments**: Pass credentials directly (see Usage)

## Usage

### Evaluate a single document

```bash
python main.py path/to/document.docx
```

### Evaluate all documents in a directory

```bash
python main.py path/to/directory
```

### Evaluate with recursive directory scanning

```bash
python main.py path/to/directory --recursive
```

### Output to JSON format

```bash
python main.py path/to/directory --format json --output results.json
```

### Output to CSV (default)

```bash
python main.py path/to/directory --format csv --output results.csv
```

### Provide credentials via CLI

```bash
python main.py document.docx --api-key "your-key" --endpoint "https://your-resource.openai.azure.com/" --deployment "gpt-4"
```

## Options

- `--recursive` / `-r`: Scan directories recursively
- `--format` / `-f`: Output format (csv, json, console) [default: csv]
- `--output` / `-o`: Output file path (for csv/json formats)
- `--api-key`: Azure OpenAI API key
- `--endpoint`: Azure OpenAI endpoint URL
- `--deployment`: Azure OpenAI deployment name
- `--api-version`: Azure OpenAI API version [default: 2024-02-15-preview]

## Output Format

### CSV
```csv
filename,relevance,factual_accuracy,clarity,hallucination,style_match,rag_usability,citation_quality,status,error_message
document1.docx,5,4,5,0,4,5,2,success,
document2.docx,0,0,0,0,0,0,0,error,Failed to parse document
```

### JSON
```json
[
  {
    "filename": "document1.docx",
    "evaluation": {
      "relevance": 5,
      "factual_accuracy": 4,
      "clarity": 5,
      "hallucination": 0,
      "style_match": 4,
      "rag_usability": 5,
      "citation_quality": 2
    },
    "status": "success"
  }
]
```

## License

MIT
