#!/usr/bin/env bash
# GEO Optimizer — Installation Script
# https://github.com/auriti-web-design/geo-optimizer-skill
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/auriti-web-design/geo-optimizer-skill/main/install.sh | bash
#   OR: bash install.sh [--openclaw] [--dir /custom/path]

set -e

REPO_URL="https://github.com/auriti-web-design/geo-optimizer-skill.git"
DEFAULT_DIR="$HOME/geo-optimizer-skill"
OPENCLAW_SKILLS_DIR="$HOME/.openclaw/workspace/skills"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✅ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
err()  { echo -e "${RED}❌ $1${NC}"; exit 1; }
info() { echo -e "   $1"; }

INSTALL_DIR="$DEFAULT_DIR"
OPENCLAW_MODE=false

# Parse args
for arg in "$@"; do
  case $arg in
    --openclaw) OPENCLAW_MODE=true ;;
    --dir=*)    INSTALL_DIR="${arg#*=}" ;;
    --dir)      shift; INSTALL_DIR="$1" ;;
  esac
done

echo ""
echo "🤖 GEO Optimizer — Installation"
echo "================================"
echo ""

# Check git
command -v git >/dev/null 2>&1 || err "git is required. Install it first: https://git-scm.com"
ok "git found"

# Check Python
command -v python3 >/dev/null 2>&1 || err "Python 3 is required. Install it first: https://python.org"
PYTHON_VER=$(python3 --version 2>&1)
ok "Python found: $PYTHON_VER"

# Check pip
command -v pip3 >/dev/null 2>&1 || command -v pip >/dev/null 2>&1 || warn "pip not found — you'll need to install dependencies manually"

# Clone or update
if [ -d "$INSTALL_DIR/.git" ]; then
  echo ""
  echo "📂 Existing installation found at: $INSTALL_DIR"
  echo "   Running update instead..."
  cd "$INSTALL_DIR"
  git pull origin main
  ok "Updated to latest version"
else
  echo ""
  echo "📥 Cloning repository to: $INSTALL_DIR"
  git clone "$REPO_URL" "$INSTALL_DIR"
  ok "Repository cloned"
fi

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
if command -v pip3 >/dev/null 2>&1; then
  pip3 install -r "$INSTALL_DIR/requirements.txt" -q
  ok "Dependencies installed (requests, beautifulsoup4, lxml)"
elif command -v pip >/dev/null 2>&1; then
  pip install -r "$INSTALL_DIR/requirements.txt" -q
  ok "Dependencies installed (requests, beautifulsoup4, lxml)"
else
  warn "pip not found. Install manually: pip install requests beautifulsoup4 lxml"
fi

# OpenClaw skill symlink (optional)
if [ "$OPENCLAW_MODE" = true ]; then
  echo ""
  echo "🔗 Setting up OpenClaw skill symlink..."
  SKILL_LINK="$OPENCLAW_SKILLS_DIR/geo-optimizer"

  if [ -L "$SKILL_LINK" ]; then
    rm "$SKILL_LINK"
    info "Removed old symlink"
  fi

  if [ -d "$OPENCLAW_SKILLS_DIR" ]; then
    ln -s "$INSTALL_DIR" "$SKILL_LINK"
    ok "Symlink created: $SKILL_LINK → $INSTALL_DIR"
    info "OpenClaw will now detect the skill automatically."
  else
    warn "OpenClaw skills directory not found at: $OPENCLAW_SKILLS_DIR"
    info "Is OpenClaw installed? Skipping symlink."
  fi
fi

# Done
echo ""
echo "================================"
ok "Installation complete!"
echo ""
echo "🚀 Quick start:"
echo "   cd $INSTALL_DIR"
echo "   python3 scripts/geo_audit.py --url https://yoursite.com"
echo ""
echo "🔄 To update in the future:"
echo "   cd $INSTALL_DIR && git pull origin main"
echo "   OR just run: bash $INSTALL_DIR/update.sh"
echo ""
echo "📖 Full docs: https://github.com/auriti-web-design/geo-optimizer-skill"
echo ""
