#!/bin/bash

# GPO Project Analysis Script
# This script runs AI analysis on a specific project

# Check if project ID was provided
if [ -z "$1" ]; then
    echo "Error: Project ID is required"
    echo "Usage: ./analyze_project.sh <project_id>"
    exit 1
fi

PROJECT_ID=$1

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🚀 Starting GPO AI Analysis for Project${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${YELLOW}Project ID: ${PROJECT_ID}${NC}"

# Run the AI analysis simulation
cd gpo_product
python simulate_ai_analysis.py $PROJECT_ID

echo -e "${GREEN}✅ Analysis complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${YELLOW}Refresh the project page in the browser to see the results${NC}"
echo -e "${BLUE}========================================${NC}" 