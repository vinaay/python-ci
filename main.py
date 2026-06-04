"""FastAPI microservice for serving JSON data."""

import json
import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, List, Optional

from fastapi import FastAPI, HTTPException, status

from config import get_settings, validate_data_file_path

# Configure logging, can be further enhanced to log to files or external systems if needed
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for FastAPI application.

    Handles startup and shutdown events.

    Args:
        app: FastAPI application instance

    Yields:
        None: Application runs during this time
    """
    # Startup
    logger.info("Starting application...")
    try:
        load_data()
        logger.info("Application started successfully")
    except DataLoadError as e:
        logger.error(f"Failed to load data on startup: {e}")
        # Don't raise - allow app to start but endpoints will fail gracefully

    yield  # Application runs here

    # Shutdown (if needed in the future)
    logger.info("Shutting down application...")


# Create FastAPI app with metadata and lifespan
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan,
)

# Cache for loaded data (lazy loading)
_data_cache: Optional[List[Dict[str, Any]]] = None
_cached_file_path: Optional[str] = None


class DataLoadError(Exception):
    """Custom exception for data loading errors."""

    pass


def load_data(file_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Load JSON data from file with caching and error handling.

    Args:
        file_path: Optional path to data file. If not provided, uses settings.

    Returns:
        List[Dict[str, Any]]: Loaded JSON data as a list of dictionaries

    Raises:
        DataLoadError: If data cannot be loaded or parsed
    """
    global _data_cache, _cached_file_path

    # Determine file path - re-read settings to pick up environment variable changes
    if file_path is None:
        current_settings = get_settings()
        data_file = current_settings.data_file_path
    else:
        data_file = file_path

    # Return cached data only if it's for the same file path
    if _data_cache is not None and _cached_file_path == data_file:
        return _data_cache

    try:
        # Validate and get file path
        validated_path = validate_data_file_path(data_file)
        logger.info(f"Loading data from: {validated_path}")

        # Load JSON data
        with open(validated_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Validate data structure
        if not isinstance(data, list):
            raise DataLoadError(f"Expected list, got {type(data).__name__}")

        if len(data) == 0:
            logger.warning("Data file is empty")

        # Cache the data and file path
        _data_cache = data
        _cached_file_path = data_file
        logger.info(f"Successfully loaded {len(data)} items")

        return _data_cache

    except FileNotFoundError as e:
        logger.error(f"Data file not found: {e}")
        raise DataLoadError(f"Data file not found: {data_file}") from e
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in data file: {e}")
        raise DataLoadError(f"Invalid JSON in data file: {data_file}") from e
    except ValueError as e:
        logger.error(f"Invalid file path: {e}")
        raise DataLoadError(f"Invalid file path: {data_file}") from e
    except Exception as e:
        logger.error(f"Unexpected error loading data: {e}")
        raise DataLoadError(f"Failed to load data: {e}") from e


def clear_data_cache() -> None:
    """Clear the data cache to force reload on next request."""
    global _data_cache, _cached_file_path
    _data_cache = None
    _cached_file_path = None
    logger.info("Data cache cleared")


def find_item_by_guid(
    guid: str, data: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """
    Find an item in the data list by GUID.

    Args:
        guid: The GUID to search for
        data: List of data items to search

    Returns:
        Optional[Dict[str, Any]]: Found item or None if not found
    """
    for item in data:
        if item.get("guid") == guid:
            return item
    return None


@app.get("/", response_model=List[Dict[str, Any]])
async def read_data() -> List[Dict[str, Any]]:
    """
    Get all data items.

    Returns:
        List[Dict[str, Any]]: List of all data items

    Raises:
        HTTPException: If data cannot be loaded
    """
    try:
        data = load_data()
        return data
    except DataLoadError as e:
        logger.error(f"Error loading data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load data: {str(e)}",
        ) from e


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.

    Returns:
        Dict[str, str]: Health status
    """
    try:
        data = load_data()
        return {
            "status": "healthy",
            "data_items": str(len(data)),
        }
    except DataLoadError:
        return {
            "status": "unhealthy",
            "error": "Data file cannot be loaded",
        }


@app.get("/{guid}", response_model=Dict[str, Any])
async def read_data_by_guid(guid: str) -> Dict[str, Any]:
    """
    Get a specific data item by GUID.

    Args:
        guid: The GUID of the item to retrieve

    Returns:
        Dict[str, Any]: The requested data item

    Raises:
        HTTPException: If item is not found or data cannot be loaded
    """
    # Validate GUID format (basic validation)
    if not guid or len(guid.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GUID cannot be empty",
        )

    try:
        data = load_data()
        item = find_item_by_guid(guid, data)

        if item is None:
            logger.warning(f"Item with GUID '{guid}' not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with GUID '{guid}' not found",
            )

        return item

    except DataLoadError as e:
        logger.error(f"Error loading data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load data: {str(e)}",
        ) from e
