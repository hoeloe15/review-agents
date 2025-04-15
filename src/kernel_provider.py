"""
Kernel Provider - Centralized kernel management module

This module provides centralized creation and access to Semantic Kernel instances,
ensuring consistent configuration across the application.
"""

import logging
import os
from typing import Optional

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, OpenAIChatCompletion

from plugins.review_plugin import ReviewPlugin

from dotenv import load_dotenv

# Load environment variables if not already loaded
load_dotenv(override=True)

logger = logging.getLogger(__name__)

class KernelProvider:
    """
    Centralized provider for Semantic Kernel instances.
    
    This class handles the creation and configuration of kernel instances,
    ensuring they are properly configured with the necessary AI services.
    """
    
    _instance: Optional[Kernel] = None
    
    @classmethod
    def get_kernel(cls) -> Kernel:
        """
        Get a configured Semantic Kernel instance.
        
        If a kernel has already been created, returns the existing instance.
        Otherwise, creates a new kernel with the appropriate configuration.
        
        Returns:
            A configured Semantic Kernel instance
        """
        if cls._instance is None:
            cls._instance = cls._create_kernel()
            
        return cls._instance
    
    @classmethod
    def reset_kernel(cls) -> Kernel:
        """
        Reset the kernel instance and create a new one.
        
        This is useful when you need to start with a fresh kernel state.
        
        Returns:
            A fresh Semantic Kernel instance
        """
        cls._instance = None
        return cls.get_kernel()
    
    @staticmethod
    def _create_kernel() -> Kernel:
        """
        Create a new Semantic Kernel instance with appropriate configuration.
        
        First tries to use Azure OpenAI configuration, and if not available,
        falls back to regular OpenAI configuration. Also loads the ReviewPlugin.
        
        Returns:
            A newly configured Semantic Kernel instance
            
        Raises:
            ValueError: If required environment variables are missing
        """
        kernel = Kernel()
        
        # Load the ReviewPlugin
        kernel.add_plugin(ReviewPlugin(), plugin_name="Reviewer")
        logger.info("Loaded Reviewer plugin.")
        
        # First try to configure for Azure OpenAI
        if all(var in os.environ for var in ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY"]):
            try:
                deployment_name = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
                api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2023-05-15")
                
                logger.info(f"Configuring kernel with Azure OpenAI service (deployment: {deployment_name})")
                
                kernel.add_service(
                    service=AzureChatCompletion(
                        deployment_name=deployment_name,
                        endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
                        api_key=os.environ["AZURE_OPENAI_API_KEY"],
                        api_version=api_version
                    )
                )
                return kernel
            except Exception as e:
                logger.warning(f"Failed to configure Azure OpenAI: {e}. Trying standard OpenAI...")
        
       
        
        # If we get here, we couldn't configure any service
        error_msg = "Could not configure AI service. Please check your environment variables."
        logger.error(error_msg)
        raise ValueError(error_msg) 