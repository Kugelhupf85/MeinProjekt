#!/bin/bash

# ================================================================================================
# ARCANOVI ADMIN USER CREATION SCRIPT
# ================================================================================================
# 
# This script creates an admin user with DungeonMaster profile and superuser privileges.
# It uses the Django management command to ensure proper integration with the Arcanovi system.
#
# Usage:
#   ./create_admin.sh [username] [email] [password] [display_name]
#
# Examples:
#   ./create_admin.sh admin admin@arcanovi.com mypassword "System Administrator"
#   ./create_admin.sh gamemaster gm@arcanovi.com secretpass "Game Master"
#
# Environment Variables:
#   ADMIN_PASSWORD - If set, will be used as default password
#
# ================================================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DEFAULT_USERNAME="admin"
DEFAULT_EMAIL="admin@arcanovi.com"
DEFAULT_DISPLAY_NAME="System Administrator"

# Parse arguments
USERNAME=${1:-$DEFAULT_USERNAME}
EMAIL=${2:-$DEFAULT_EMAIL}
PASSWORD=${3:-$ADMIN_PASSWORD}
DISPLAY_NAME=${4:-$DEFAULT_DISPLAY_NAME}

echo -e "${BLUE}🎮 Arcanovi Admin User Creation${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# Check if password is provided
if [ -z "$PASSWORD" ]; then
    echo -e "${RED}❌ Error: Password is required!${NC}"
    echo ""
    echo "Please provide a password in one of these ways:"
    echo "  1. As third argument: ./create_admin.sh admin admin@arcanovi.com mypassword"
    echo "  2. Set ADMIN_PASSWORD environment variable: export ADMIN_PASSWORD=mypassword"
    echo ""
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo -e "${RED}❌ Error: This script must be run from the Django project root directory!${NC}"
    echo "Please navigate to the backend directory and run this script."
    exit 1
fi

echo -e "${YELLOW}📝 Creating admin user with following details:${NC}"
echo "   👤 Username: $USERNAME"
echo "   📧 Email: $EMAIL"
echo "   🎭 Display Name: $DISPLAY_NAME"
echo "   🔑 Superuser: Yes"
echo "   🛡️  Staff: Yes"
echo ""

# Ask for confirmation
read -p "Do you want to continue? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⚠️  Operation cancelled.${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}🚀 Creating admin user...${NC}"
echo ""

# Run the Django management command
python manage.py create_admin_user \
    --username "$USERNAME" \
    --email "$EMAIL" \
    --password "$PASSWORD" \
    --display-name "$DISPLAY_NAME" \
    --force

echo ""
echo -e "${GREEN}✅ Admin user creation completed!${NC}"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo "  1. Start the Django development server: python manage.py runserver"
echo "  2. Access the admin interface: http://localhost:8000/admin/"
echo "  3. Login with username: $USERNAME"
echo ""
echo -e "${YELLOW}🔒 Security reminder:${NC}"
echo "  - Change the default password after first login"
echo "  - Keep admin credentials secure"
echo "  - Use strong passwords in production"
echo "" 