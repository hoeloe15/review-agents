"""
Configuration module for loading environment variables and settings.
"""
import os
import logging
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class AzureSettings:
    """Settings for Azure OpenAI services."""
    api_version: str
    endpoint: str
    deployment: str
    api_key: str


# Load Azure settings from environment variables
azure_settings = AzureSettings(
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION", ""),
    endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", ""),
    deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT", ""),
    api_key=os.environ.get("AZURE_OPENAI_API_KEY", ""),
)

# Validate settings
if not azure_settings.endpoint or not azure_settings.deployment or not azure_settings.api_key:
    logger.error("Missing required Azure OpenAI settings in environment variables")
    raise ValueError("Azure OpenAI settings are required. Please check your .env file.")
