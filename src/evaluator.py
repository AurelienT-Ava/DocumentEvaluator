"""LLM evaluator for document compatibility assessment."""

import json
import time
from dataclasses import dataclass
from typing import List, Dict, Optional
from openai import AzureOpenAI
from openai import APIError, RateLimitError, APITimeoutError

from .config import AzureOpenAIConfig
from .document_parser import DocumentChunk


@dataclass
class DocumentEvaluation:
    """Evaluation scores for a document."""
    
    relevance: float
    factual_accuracy: float
    clarity: float
    hallucination: float
    style_match: float
    rag_usability: float
    citation_quality: float
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            'relevance': self.relevance,
            'factual_accuracy': self.factual_accuracy,
            'clarity': self.clarity,
            'hallucination': self.hallucination,
            'style_match': self.style_match,
            'rag_usability': self.rag_usability,
            'citation_quality': self.citation_quality
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'DocumentEvaluation':
        """Create from dictionary."""
        return cls(
            relevance=data.get('relevance', 0.0),
            factual_accuracy=data.get('factual_accuracy', 0.0),
            clarity=data.get('clarity', 0.0),
            hallucination=data.get('hallucination', 0.0),
            style_match=data.get('style_match', 0.0),
            rag_usability=data.get('rag_usability', 0.0),
            citation_quality=data.get('citation_quality', 0.0)
        )
    
    @classmethod
    def weighted_average(cls, evaluations: List[tuple['DocumentEvaluation', int]]) -> 'DocumentEvaluation':
        """
        Calculate weighted average of evaluations.
        
        Args:
            evaluations: List of (evaluation, weight) tuples
        
        Returns:
            Weighted average evaluation
        """
        if not evaluations:
            return cls(0, 0, 0, 0, 0, 0, 0)
        
        total_weight = sum(weight for _, weight in evaluations)
        if total_weight == 0:
            return cls(0, 0, 0, 0, 0, 0, 0)
        
        weighted_sums = {
            'relevance': 0.0,
            'factual_accuracy': 0.0,
            'clarity': 0.0,
            'hallucination': 0.0,
            'style_match': 0.0,
            'rag_usability': 0.0,
            'citation_quality': 0.0
        }
        
        for evaluation, weight in evaluations:
            for key in weighted_sums:
                weighted_sums[key] += getattr(evaluation, key) * weight
        
        return cls(
            relevance=weighted_sums['relevance'] / total_weight,
            factual_accuracy=weighted_sums['factual_accuracy'] / total_weight,
            clarity=weighted_sums['clarity'] / total_weight,
            hallucination=weighted_sums['hallucination'] / total_weight,
            style_match=weighted_sums['style_match'] / total_weight,
            rag_usability=weighted_sums['rag_usability'] / total_weight,
            citation_quality=weighted_sums['citation_quality'] / total_weight
        )


class LLMEvaluator:
    """Evaluator using Azure OpenAI to assess document quality."""
    
    EVALUATION_PROMPT = """You are an expert evaluator assessing document quality for use with Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) systems.

Evaluate the following document text on these criteria (score 0-5 for each):

1. **Relevance** (0-5): How relevant and focused is the content? Does it stay on topic?
2. **Factual Accuracy** (0-5): Does the content appear factually accurate and well-researched?
3. **Clarity** (0-5): Is the writing clear, well-structured, and easy to understand?
4. **Hallucination Risk** (0-5): How likely is this content to cause LLM hallucinations? (0=very likely, 5=very unlikely)
5. **Style Match** (0-5): Is the writing style consistent and professional?
6. **RAG Usability** (0-5): How useful would this be as context for a RAG system? Is it well-structured for retrieval?
7. **Citation Quality** (0-5): Are sources, references, and citations properly included and formatted?

Respond ONLY with a JSON object in this exact format:
{
  "relevance": <score>,
  "factual_accuracy": <score>,
  "clarity": <score>,
  "hallucination": <score>,
  "style_match": <score>,
  "rag_usability": <score>,
  "citation_quality": <score>
}

Document text to evaluate:

{text}"""
    
    def __init__(self, config: AzureOpenAIConfig, temperature: float = 0.0, max_retries: int = 3):
        """
        Initialize LLM evaluator.
        
        Args:
            config: Azure OpenAI configuration
            temperature: Temperature for LLM responses (0 for deterministic)
            max_retries: Maximum number of retries on API errors
        """
        self.config = config
        self.temperature = temperature
        self.max_retries = max_retries
        self.client = AzureOpenAI(
            api_key=config.api_key,
            api_version=config.api_version,
            azure_endpoint=config.endpoint
        )
    
    def evaluate_chunk(self, chunk: DocumentChunk) -> Optional[DocumentEvaluation]:
        """
        Evaluate a single document chunk.
        
        Args:
            chunk: Document chunk to evaluate
        
        Returns:
            DocumentEvaluation or None if evaluation fails
        """
        prompt = self.EVALUATION_PROMPT.format(text=chunk.text)
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.config.deployment,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert document quality evaluator. Respond only with valid JSON."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=self.temperature,
                    max_tokens=500,
                    response_format={"type": "json_object"}
                )
                
                # Parse response
                content = response.choices[0].message.content
                data = json.loads(content)
                
                return DocumentEvaluation.from_dict(data)
            
            except RateLimitError as e:
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"Rate limit exceeded after {self.max_retries} retries: {e}")
            
            except APITimeoutError as e:
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    raise Exception(f"API timeout after {self.max_retries} retries: {e}")
            
            except (APIError, json.JSONDecodeError) as e:
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    raise Exception(f"API error after {self.max_retries} retries: {e}")
            
            except Exception as e:
                raise Exception(f"Unexpected error during evaluation: {e}")
        
        return None
    
    def evaluate_chunks(self, chunks: List[DocumentChunk]) -> DocumentEvaluation:
        """
        Evaluate multiple chunks and aggregate results.
        
        Uses weighted average based on chunk token counts.
        
        Args:
            chunks: List of document chunks
        
        Returns:
            Aggregated DocumentEvaluation
        
        Raises:
            Exception: If all chunks fail to evaluate
        """
        evaluations_with_weights = []
        
        for chunk in chunks:
            try:
                evaluation = self.evaluate_chunk(chunk)
                if evaluation:
                    evaluations_with_weights.append((evaluation, chunk.token_count))
            except Exception as e:
                # Log but continue with other chunks
                print(f"Warning: Failed to evaluate chunk {chunk.chunk_index + 1}/{chunk.total_chunks}: {e}")
        
        if not evaluations_with_weights:
            raise Exception("Failed to evaluate any chunks in the document")
        
        # Calculate weighted average
        return DocumentEvaluation.weighted_average(evaluations_with_weights)
