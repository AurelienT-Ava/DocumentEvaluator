"""Output formatters for evaluation results."""

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, TextIO
import sys

from .evaluator import DocumentEvaluation


@dataclass
class EvaluationResult:
    """Result of evaluating a document."""
    
    filename: str
    evaluation: Optional[DocumentEvaluation]
    status: str  # 'success' or 'error'
    error_message: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        result = {
            'filename': self.filename,
            'status': self.status
        }
        
        if self.evaluation:
            result['evaluation'] = self.evaluation.to_dict()
        
        if self.error_message:
            result['error_message'] = self.error_message
        
        return result
    
    def to_flat_dict(self) -> dict:
        """Convert to flat dictionary for CSV."""
        result = {'filename': self.filename}
        
        if self.evaluation:
            result.update(self.evaluation.to_dict())
        else:
            # Add zeros for failed evaluations
            result.update({
                'relevance': 0,
                'factual_accuracy': 0,
                'clarity': 0,
                'hallucination': 0,
                'style_match': 0,
                'rag_usability': 0,
                'citation_quality': 0
            })
        
        result['status'] = self.status
        result['error_message'] = self.error_message or ''
        
        return result


class OutputFormatter:
    """Base class for output formatters."""
    
    def format(self, results: List[EvaluationResult]) -> str:
        """Format results to string."""
        raise NotImplementedError
    
    def write(self, results: List[EvaluationResult], output_path: Optional[Path] = None):
        """Write results to file or stdout."""
        formatted = self.format(results)
        
        if output_path:
            output_path.write_text(formatted, encoding='utf-8')
        else:
            print(formatted)


class ConsoleFormatter(OutputFormatter):
    """Format results for console output with colors."""
    
    # ANSI color codes
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    
    def format(self, results: List[EvaluationResult]) -> str:
        """Format results for console output."""
        lines = []
        lines.append(f"\n{self.BOLD}{self.HEADER}Document Evaluation Results{self.ENDC}\n")
        lines.append("=" * 80)
        
        for result in results:
            lines.append(f"\n{self.BOLD}File:{self.ENDC} {result.filename}")
            lines.append(f"{self.BOLD}Status:{self.ENDC} {self._format_status(result.status)}")
            
            if result.evaluation:
                eval_dict = result.evaluation.to_dict()
                lines.append(f"\n{self.BOLD}Scores:{self.ENDC}")
                for key, value in eval_dict.items():
                    formatted_key = key.replace('_', ' ').title()
                    score_color = self._get_score_color(value)
                    lines.append(f"  {formatted_key:.<30} {score_color}{value:.1f}/5{self.ENDC}")
            
            if result.error_message:
                lines.append(f"{self.FAIL}Error: {result.error_message}{self.ENDC}")
            
            lines.append("-" * 80)
        
        # Summary
        total = len(results)
        successful = sum(1 for r in results if r.status == 'success')
        failed = total - successful
        
        lines.append(f"\n{self.BOLD}Summary:{self.ENDC}")
        lines.append(f"  Total documents: {total}")
        lines.append(f"  {self.OKGREEN}Successful: {successful}{self.ENDC}")
        if failed > 0:
            lines.append(f"  {self.FAIL}Failed: {failed}{self.ENDC}")
        
        return '\n'.join(lines)
    
    def _format_status(self, status: str) -> str:
        """Format status with color."""
        if status == 'success':
            return f"{self.OKGREEN}✓ Success{self.ENDC}"
        else:
            return f"{self.FAIL}✗ Error{self.ENDC}"
    
    def _get_score_color(self, score: float) -> str:
        """Get color based on score."""
        if score >= 4.0:
            return self.OKGREEN
        elif score >= 3.0:
            return self.OKCYAN
        elif score >= 2.0:
            return self.WARNING
        else:
            return self.FAIL


class JSONFormatter(OutputFormatter):
    """Format results as JSON."""
    
    def format(self, results: List[EvaluationResult]) -> str:
        """Format results as JSON."""
        data = [result.to_dict() for result in results]
        return json.dumps(data, indent=2, ensure_ascii=False)


class CSVFormatter(OutputFormatter):
    """Format results as CSV."""
    
    FIELDNAMES = [
        'filename',
        'relevance',
        'factual_accuracy',
        'clarity',
        'hallucination',
        'style_match',
        'rag_usability',
        'citation_quality',
        'status',
        'error_message'
    ]
    
    def format(self, results: List[EvaluationResult]) -> str:
        """Format results as CSV."""
        from io import StringIO
        
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=self.FIELDNAMES)
        writer.writeheader()
        
        for result in results:
            writer.writerow(result.to_flat_dict())
        
        return output.getvalue()


def get_formatter(format_type: str) -> OutputFormatter:
    """
    Get formatter by type.
    
    Args:
        format_type: 'console', 'json', or 'csv'
    
    Returns:
        Appropriate OutputFormatter instance
    
    Raises:
        ValueError: If format_type is not recognized
    """
    formatters = {
        'console': ConsoleFormatter,
        'json': JSONFormatter,
        'csv': CSVFormatter
    }
    
    formatter_class = formatters.get(format_type.lower())
    if not formatter_class:
        raise ValueError(f"Unknown format type: {format_type}. Must be one of: {', '.join(formatters.keys())}")
    
    return formatter_class()
