#!/usr/bin/env python3
"""Document Evaluator - Assess Word documents for LLM compatibility."""

from pathlib import Path
from typing import Optional
import click
from tqdm import tqdm

from src.config import AzureOpenAIConfig
from src.scanner import DocumentScanner
from src.document_parser import DocumentParser
from src.evaluator import LLMEvaluator, DocumentEvaluation
from src.output import EvaluationResult, get_formatter


@click.command()
@click.argument('path', type=click.Path(exists=True, path_type=Path))
@click.option(
    '--recursive', '-r',
    is_flag=True,
    help='Scan directories recursively'
)
@click.option(
    '--format', '-f',
    type=click.Choice(['csv', 'json', 'console'], case_sensitive=False),
    default='csv',
    help='Output format (default: csv)'
)
@click.option(
    '--output', '-o',
    type=click.Path(path_type=Path),
    help='Output file path (for csv/json formats). If not specified, outputs to console.'
)
@click.option(
    '--api-key',
    envvar='AZURE_OPENAI_API_KEY',
    help='Azure OpenAI API key'
)
@click.option(
    '--endpoint',
    envvar='AZURE_OPENAI_ENDPOINT',
    help='Azure OpenAI endpoint URL'
)
@click.option(
    '--deployment',
    envvar='AZURE_OPENAI_DEPLOYMENT',
    help='Azure OpenAI deployment name'
)
@click.option(
    '--api-version',
    envvar='AZURE_OPENAI_API_VERSION',
    default='2024-02-15-preview',
    help='Azure OpenAI API version'
)
@click.option(
    '--temperature',
    type=float,
    default=0.0,
    help='Temperature for LLM evaluation (default: 0.0 for consistency)'
)
@click.option(
    '--max-retries',
    type=int,
    default=3,
    help='Maximum retries for API calls (default: 3)'
)
def main(
    path: Path,
    recursive: bool,
    format: str,
    output: Optional[Path],
    api_key: Optional[str],
    endpoint: Optional[str],
    deployment: Optional[str],
    api_version: str,
    temperature: float,
    max_retries: int
):
    """
    Evaluate Word documents for LLM compatibility.
    
    PATH can be a single .docx file or a directory containing Word documents.
    """
    try:
        # Load configuration
        click.echo("Loading Azure OpenAI configuration...")
        config = AzureOpenAIConfig.from_args(
            api_key=api_key,
            endpoint=endpoint,
            deployment=deployment,
            api_version=api_version
        )
        
        # Initialize components
        scanner = DocumentScanner()
        parser = DocumentParser()
        evaluator = LLMEvaluator(config, temperature=temperature, max_retries=max_retries)
        
        # Scan for documents
        click.echo(f"Scanning for documents in: {path}")
        documents = scanner.scan(path, recursive=recursive)
        
        if not documents:
            click.echo("No Word documents found.", err=True)
            return
        
        click.echo(f"Found {len(documents)} document(s)")
        
        # Process documents
        results = []
        
        with tqdm(total=len(documents), desc="Evaluating documents", unit="doc") as pbar:
            for doc_path in documents:
                result = evaluate_document(doc_path, parser, evaluator)
                results.append(result)
                pbar.update(1)
        
        # Output results
        formatter = get_formatter(format)
        
        if output:
            formatter.write(results, output)
            click.echo(f"\nResults written to: {output}")
        else:
            if format == 'console':
                formatter.write(results)
            else:
                # For csv/json without output file, print to console
                formatter.write(results)
        
        # Summary
        successful = sum(1 for r in results if r.status == 'success')
        failed = len(results) - successful
        
        if format != 'console':
            click.echo(f"\nProcessed {len(results)} document(s): {successful} successful, {failed} failed")
    
    except ValueError as e:
        click.echo(f"Configuration error: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


def evaluate_document(
    doc_path: Path,
    parser: DocumentParser,
    evaluator: LLMEvaluator
) -> EvaluationResult:
    """
    Evaluate a single document.
    
    Args:
        doc_path: Path to document
        parser: Document parser
        evaluator: LLM evaluator
    
    Returns:
        EvaluationResult
    """
    try:
        # Parse document into chunks
        chunks = parser.parse(doc_path)
        
        # Evaluate chunks
        evaluation = evaluator.evaluate_chunks(chunks)
        
        return EvaluationResult(
            filename=str(doc_path),
            evaluation=evaluation,
            status='success'
        )
    
    except Exception as e:
        return EvaluationResult(
            filename=str(doc_path),
            evaluation=None,
            status='error',
            error_message=str(e)
        )


if __name__ == '__main__':
    main()
