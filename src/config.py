"""Configuration module for Azure OpenAI credentials."""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv


@dataclass
class AzureOpenAIConfig:
    """Azure OpenAI configuration."""
    
    api_key: str
    endpoint: str
    deployment: str
    api_version: str = "2024-02-15-preview"
    
    @classmethod
    def from_env(cls) -> 'AzureOpenAIConfig':
        """Load configuration from environment variables."""
        # Load from .env file if it exists
        load_dotenv()
        
        api_key = os.getenv('AZURE_OPENAI_API_KEY')
        endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT')
        api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
        
        if not all([api_key, endpoint, deployment]):
            missing = []
            if not api_key:
                missing.append('AZURE_OPENAI_API_KEY')
            if not endpoint:
                missing.append('AZURE_OPENAI_ENDPOINT')
            if not deployment:
                missing.append('AZURE_OPENAI_DEPLOYMENT')
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}. "
                f"Set them in environment or create a .env file."
            )
        
        return cls(
            api_key=api_key,
            endpoint=endpoint,
            deployment=deployment,
            api_version=api_version
        )
    
    @classmethod
    def from_args(
        cls,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        deployment: Optional[str] = None,
        api_version: Optional[str] = None
    ) -> 'AzureOpenAIConfig':
        """
        Load configuration with fallback chain: CLI args → environment variables → .env file.
        
        Args:
            api_key: Azure OpenAI API key (optional, falls back to env)
            endpoint: Azure OpenAI endpoint (optional, falls back to env)
            deployment: Azure OpenAI deployment name (optional, falls back to env)
            api_version: Azure OpenAI API version (optional, falls back to env)
        
        Returns:
            AzureOpenAIConfig instance
        
        Raises:
            ValueError: If required configuration is missing
        """
        # Load from .env file if it exists
        load_dotenv()
        
        # Fallback chain: CLI args → environment variables
        final_api_key = api_key or os.getenv('AZURE_OPENAI_API_KEY')
        final_endpoint = endpoint or os.getenv('AZURE_OPENAI_ENDPOINT')
        final_deployment = deployment or os.getenv('AZURE_OPENAI_DEPLOYMENT')
        final_api_version = api_version or os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
        
        if not all([final_api_key, final_endpoint, final_deployment]):
            missing = []
            if not final_api_key:
                missing.append('api_key/AZURE_OPENAI_API_KEY')
            if not final_endpoint:
                missing.append('endpoint/AZURE_OPENAI_ENDPOINT')
            if not final_deployment:
                missing.append('deployment/AZURE_OPENAI_DEPLOYMENT')
            raise ValueError(
                f"Missing required configuration: {', '.join(missing)}. "
                f"Provide via CLI arguments, environment variables, or .env file."
            )
        
        return cls(
            api_key=final_api_key,
            endpoint=final_endpoint,
            deployment=final_deployment,
            api_version=final_api_version
        )
