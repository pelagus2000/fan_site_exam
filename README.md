Implement Blog Platform with User Management and Content Organization

This project represents a complete Django-based blogging platform with the following features:

- User management with verification and subscription system
- Content creation and publishing through Post model
- Categorization system for organizing content
- Response/comment functionality for user interaction
- Media handling for images and attachments
- User notification system
- Authorization and authentication controls
- Responsive front-end with templates

Core technology stack:
- Django 5.2 as the main web framework
- Celery 5.5.1 with Redis 6.0.0 for asynchronous task processing and notifications
- Pillow for image processing and media management
- FFmpeg for video content processing
- Python-magic for file type detection and validation
- Django-filter for advanced content filtering and search
- Django JS Asset for frontend asset management

Implementation notes:
- Purely web-based solution with no API endpoints
- Frontend implementation is functional but requires refinement
- Project is currently in development state and not production-ready
- Focus has been on backend functionality and data modeling

The platform includes full CRUD operations for all content types and 
supports user subscription management with verification codes.
Database optimizations implemented with appropriate indexes.
