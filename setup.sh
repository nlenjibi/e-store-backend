#!/bin/bash

# ========================================
# Django E-Commerce Quick Setup Script
# ========================================

set -e  # Exit on error

echo "🚀 Starting Django E-Commerce Backend Setup..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker and Docker Compose are installed${NC}"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ .env file created${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT: Please edit .env file with your actual values before continuing!${NC}"
    echo "   Required changes:"
    echo "   - SECRET_KEY"
    echo "   - POSTGRES_PASSWORD"
    echo "   - REDIS_PASSWORD"
    echo "   - ALLOWED_HOSTS"
    echo "   - Payment gateway credentials (if needed)"
    echo ""
    read -p "Press Enter after editing .env file to continue..."
fi

echo ""
echo "📦 Step 1: Building Docker images..."
docker-compose build

echo ""
echo "🚀 Step 2: Starting services..."
docker-compose up -d

echo ""
echo "⏳ Step 3: Waiting for services to be ready (30 seconds)..."
sleep 30

echo ""
echo "📊 Step 4: Checking service health..."
docker-compose ps

echo ""
echo "🗄️  Step 5: Running database migrations..."
docker-compose exec web python manage.py migrate

echo ""
echo "📁 Step 6: Collecting static files..."
docker-compose exec web python manage.py collectstatic --noinput

echo ""
echo "👤 Step 7: Creating superuser..."
echo "   You'll be prompted to create an admin account."
docker-compose exec web python manage.py createsuperuser

echo ""
echo "🧪 Step 8: Testing cache connection..."
docker-compose exec web python manage.py shell -c "
from django.core.cache import cache
cache.set('test_key', 'test_value', 60)
result = cache.get('test_key')
print('Cache test:', 'PASSED' if result == 'test_value' else 'FAILED')
"

echo ""
echo "✅ Step 9: Generating OpenAPI schema..."
docker-compose exec web python manage.py spectacular --file swagger.yaml
docker-compose exec web python manage.py spectacular --format openapi-json --file swagger.json

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    🎉 SETUP COMPLETE! 🎉                  ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "📍 Access your application at:"
echo ""
echo -e "   🌐 Swagger UI:    ${GREEN}http://localhost:8000/api/docs/${NC}"
echo -e "   📚 ReDoc:         ${GREEN}http://localhost:8000/api/redoc/${NC}"
echo -e "   ⚙️  Admin Panel:   ${GREEN}http://localhost:8000/admin/${NC}"
echo -e "   🔌 API Root:      ${GREEN}http://localhost:8000/api/${NC}"
echo ""
echo "📋 Useful commands:"
echo ""
echo "   View logs:        docker-compose logs -f"
echo "   Stop services:    docker-compose down"
echo "   Restart:          docker-compose restart"
echo "   Django shell:     docker-compose exec web python manage.py shell"
echo ""
echo "📖 For more information, see:"
echo "   - PRODUCTION_SETUP.md"
echo "   - API_DOCUMENTATION.md"
echo "   - DOCKER_DEPLOYMENT.md"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
