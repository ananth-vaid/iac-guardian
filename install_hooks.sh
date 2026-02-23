#!/bin/bash
# Install IaC Guardian git hooks

cd "$(dirname "$0")"

echo "🛡️  Installing IaC Guardian git hooks..."

# Check if we're in a git repo
if [ ! -d .git ]; then
    echo "❌ Not in a git repository"
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p .git/hooks

# Install pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# IaC Guardian pre-commit hook

# Get the project root
REPO_ROOT=$(git rev-parse --show-toplevel)

# Run IaC Guardian
cd "$REPO_ROOT"

# Load .env file if it exists
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

source venv/bin/activate 2>/dev/null || true
python iac-guardian-cli.py

# Capture exit code
EXIT_CODE=$?

# Exit with the same code
exit $EXIT_CODE
EOF

chmod +x .git/hooks/pre-commit

echo "✅ Pre-commit hook installed"
echo ""
echo "Test it with:"
echo "  1. Make a change to an IaC file"
echo "  2. git add <file>"
echo "  3. git commit -m 'test'"
echo ""
echo "IaC Guardian will analyze changes before committing!"
