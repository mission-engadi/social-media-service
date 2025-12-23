# Social Media Service

## Overview
The Social Media Service is a comprehensive microservice for managing social media posts, campaigns, and analytics through Buffer integration. Part of the Mission Engadi platform.

## Features
- ✅ **Social Account Management** - Connect and manage multiple social media accounts
- ✅ **Post Scheduling** - Schedule posts across platforms via Buffer
- ✅ **Campaign Management** - Organize posts into campaigns
- ✅ **Analytics Tracking** - Track post performance and engagement
- ✅ **Buffer Integration** - Full Buffer API integration for seamless posting
- ✅ **Content Calendar** - Visual calendar view of scheduled posts

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 13+
- Buffer API access token

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd social_media_service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your settings (DATABASE_URL, BUFFER_ACCESS_TOKEN, etc.)

# Run database migrations
alembic upgrade head

# Start the service
./start.sh
```

### Access the Service
- **API**: http://localhost:8007
- **Documentation**: http://localhost:8007/docs
- **Health Check**: http://localhost:8007/api/v1/health

## Buffer Setup

See [BUFFER_INTEGRATION_GUIDE.md](BUFFER_INTEGRATION_GUIDE.md) for detailed Buffer setup instructions.

## API Documentation

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete endpoint documentation.

### Key Endpoints
- `POST /api/v1/social-accounts` - Create social account
- `POST /api/v1/posts` - Create scheduled post
- `POST /api/v1/posts/{id}/schedule` - Schedule post via Buffer
- `GET /api/v1/posts/calendar` - View content calendar
- `POST /api/v1/campaigns` - Create campaign
- `GET /api/v1/analytics/{id}` - Get post analytics

## Architecture

### Services (6 total)
1. **BufferService** - Buffer API integration
2. **SocialAccountService** - Account management
3. **ScheduledPostService** - Post scheduling
4. **PostAnalyticsService** - Analytics tracking
5. **CampaignService** - Campaign management
6. **BufferConfigService** - Buffer configuration

### Database Models
- `SocialAccount` - Social media account connections
- `ScheduledPost` - Scheduled posts
- `PostAnalytics` - Post performance data
- `Campaign` - Marketing campaigns
- `BufferConfig` - Buffer API configuration

## Development

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_social_accounts.py -v
```

### Management Scripts
```bash
./start.sh      # Start the service
./stop.sh       # Stop the service
./restart.sh    # Restart the service
./status.sh     # Check service status
```

### Environment Variables
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/social_media_db
SECRET_KEY=your-secret-key
BUFFER_API_URL=https://api.bufferapp.com/1
BUFFER_ACCESS_TOKEN=your-buffer-token
API_V1_PREFIX=/api/v1
PORT=8007
```

## Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for deployment instructions.

## Tech Stack
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy (async)
- **Authentication**: JWT
- **External API**: Buffer API
- **Testing**: Pytest with async support

## Project Structure
```
social_media_service/
├── app/
│   ├── api/v1/endpoints/     # API endpoints (35 total)
│   ├── models/               # Database models (5 models)
│   ├── schemas/              # Pydantic schemas
│   ├── services/             # Business logic (6 services)
│   ├── core/                 # Config, security, logging
│   └── main.py               # FastAPI application
├── tests/                    # Test suite (70%+ coverage)
├── migrations/               # Alembic migrations
├── start.sh, stop.sh, etc.   # Management scripts
└── requirements.txt          # Dependencies
```

## Contributing
1. Follow the existing code patterns
2. Write tests for new features
3. Update documentation
4. Run tests before committing

## License
Proprietary - Mission Engadi

## Support
For issues or questions, contact the development team.
