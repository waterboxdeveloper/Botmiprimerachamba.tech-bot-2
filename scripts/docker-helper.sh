#!/bin/bash

# Docker Helper Script for bot2mvp
# Simplifies common Docker Compose operations

set -e

PROJECT_NAME="bot2mvp"
COMPOSE_FILE="docker-compose.yml"
DEV_COMPOSE_FILE="docker-compose.dev.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}==== $1 ====${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
}

check_env() {
    if [ ! -f .env ]; then
        print_warning ".env file not found"
        print_header "Creating .env from .env.example"
        cp .env.example .env
        print_warning "Please fill in .env with your credentials"
        exit 1
    fi
}

# Commands
cmd_build() {
    print_header "Building Docker images"
    docker-compose build
    print_success "Build complete"
}

cmd_build_no_cache() {
    print_header "Building Docker images (no cache)"
    docker-compose build --no-cache
    print_success "Build complete"
}

cmd_up() {
    print_header "Starting services"
    docker-compose up -d
    sleep 2
    docker-compose ps
    print_success "Services started"
}

cmd_up_fg() {
    print_header "Starting services (foreground)"
    docker-compose up
}

cmd_down() {
    print_header "Stopping services"
    docker-compose down
    print_success "Services stopped"
}

cmd_restart() {
    print_header "Restarting services"
    docker-compose restart
    sleep 2
    docker-compose ps
    print_success "Services restarted"
}

cmd_logs() {
    SERVICE=${1:-""}
    if [ -z "$SERVICE" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f "$SERVICE"
    fi
}

cmd_ps() {
    print_header "Service status"
    docker-compose ps
}

cmd_shell_bot() {
    print_header "Connecting to telegram-bot shell"
    docker-compose exec telegram-bot /bin/bash
}

cmd_shell_api() {
    print_header "Connecting to jobspy-api shell"
    docker-compose exec jobspy-api /bin/bash
}

cmd_test_health() {
    print_header "Testing service health"

    # Check telegram-bot
    echo -e "\n${BLUE}Testing telegram-bot...${NC}"
    if docker-compose exec -T telegram-bot python -c "print('OK')" &>/dev/null; then
        print_success "telegram-bot is responsive"
    else
        print_error "telegram-bot is not responsive"
    fi

    # Check jobspy-api
    echo -e "\n${BLUE}Testing jobspy-api...${NC}"
    if docker-compose exec -T jobspy-api curl -s http://localhost:8000/health > /dev/null; then
        print_success "jobspy-api is healthy"
    else
        print_error "jobspy-api health check failed"
    fi

    # Check connectivity between services
    echo -e "\n${BLUE}Testing service connectivity...${NC}"
    if docker-compose exec -T telegram-bot curl -s http://jobspy-api:8000/health > /dev/null; then
        print_success "telegram-bot can reach jobspy-api"
    else
        print_error "telegram-bot cannot reach jobspy-api"
    fi
}

cmd_dev() {
    print_header "Starting services in DEVELOPMENT mode"
    docker-compose -f "$COMPOSE_FILE" -f "$DEV_COMPOSE_FILE" up
}

cmd_logs_save() {
    FILE="logs_$(date +%Y%m%d_%H%M%S).txt"
    print_header "Saving logs to $FILE"
    docker-compose logs > "$FILE" 2>&1
    print_success "Logs saved to $FILE"
}

cmd_clean() {
    print_warning "This will stop and remove all containers/volumes"
    read -p "Are you sure? (yes/no): " -r
    if [[ $REPLY == "yes" ]]; then
        print_header "Cleaning up"
        docker-compose down -v
        docker system prune -f
        print_success "Cleanup complete"
    else
        print_warning "Cleanup cancelled"
    fi
}

cmd_help() {
    cat << EOF
${BLUE}Bot2MVP Docker Helper${NC}

Usage: ./scripts/docker-helper.sh [COMMAND] [OPTIONS]

Commands:
  ${GREEN}build${NC}              Build Docker images
  ${GREEN}build-nc${NC}            Build Docker images (no cache)
  ${GREEN}up${NC}                 Start services (background)
  ${GREEN}up-fg${NC}              Start services (foreground)
  ${GREEN}down${NC}               Stop services
  ${GREEN}restart${NC}            Restart services
  ${GREEN}logs${NC} [SERVICE]     View logs (SERVICE: telegram-bot, jobspy-api)
  ${GREEN}ps${NC}                 Show service status
  ${GREEN}shell-bot${NC}          Open shell in telegram-bot
  ${GREEN}shell-api${NC}          Open shell in jobspy-api
  ${GREEN}health${NC}             Test service health
  ${GREEN}dev${NC}                Start in development mode (with volume mounts)
  ${GREEN}logs-save${NC}          Save all logs to file
  ${GREEN}clean${NC}              Remove all containers and volumes
  ${GREEN}help${NC}               Show this help message

Examples:
  ./scripts/docker-helper.sh build
  ./scripts/docker-helper.sh up
  ./scripts/docker-helper.sh logs telegram-bot
  ./scripts/docker-helper.sh shell-bot
  ./scripts/docker-helper.sh health

EOF
}

# Main
main() {
    check_docker
    check_env

    COMMAND=${1:-"help"}

    case "$COMMAND" in
        build) cmd_build ;;
        build-nc) cmd_build_no_cache ;;
        up) cmd_up ;;
        up-fg) cmd_up_fg ;;
        down) cmd_down ;;
        restart) cmd_restart ;;
        logs) cmd_logs "$2" ;;
        ps) cmd_ps ;;
        shell-bot) cmd_shell_bot ;;
        shell-api) cmd_shell_api ;;
        health) cmd_test_health ;;
        dev) cmd_dev ;;
        logs-save) cmd_logs_save ;;
        clean) cmd_clean ;;
        help) cmd_help ;;
        *)
            print_error "Unknown command: $COMMAND"
            cmd_help
            exit 1
            ;;
    esac
}

main "$@"
