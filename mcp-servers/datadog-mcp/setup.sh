#!/bin/bash
# Setup script for Datadog MCP Server

set -e

echo "🚀 Setting up Datadog MCP Server for IaC Guardian"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Make server executable
echo "🔧 Making server executable..."
chmod +x server.py

# Test server
echo "🧪 Testing server..."
python3 -c "from mcp.server import Server; print('✅ MCP SDK installed correctly')"

echo ""
echo "✅ Datadog MCP Server setup complete!"
echo ""
echo "Next steps:"
echo "1. Add to Claude Code config:"
echo ""
echo "   File: ~/.config/Claude/claude_desktop_config.json"
echo ""
echo '   {
     "mcpServers": {
       "datadog": {
         "command": "/Users/ananth.vaidyanathan/iac-guardian/mcp-servers/datadog-mcp/venv/bin/python",
         "args": ["/Users/ananth.vaidyanathan/iac-guardian/mcp-servers/datadog-mcp/server.py"],
         "env": {
           "DATADOG_API_KEY": "'"${DATADOG_API_KEY}"'",
           "DATADOG_APP_KEY": "'"${DATADOG_APP_KEY}"'"
         }
       }
     }
   }'
echo ""
echo "2. Restart Claude Code"
echo "3. Test with: Ask Claude to 'query datadog metrics for payment-api'"
