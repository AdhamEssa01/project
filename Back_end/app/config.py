"""
Centralized configuration for upload constraints and validation rules.
"""

# File upload constraints
SUPPORTED_EXTENSIONS: set[str] = {".pdf"}
MAX_FILES: int = 50

# Text quality thresholds
MIN_JOB_DESCRIPTION_LENGTH: int = 30
MIN_RESUME_TEXT_LENGTH: int = 30
