#!/bin/bash
# Relay Setup Script
# Automates the initial setup of Relay

set -e

echo "🚀 Relay Setup Script"
echo "===================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker"
    exit 1
fi

echo "✅ Docker found: $(docker --version)"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose"
    exit 1
fi

echo "✅ Docker Compose found"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip > /dev/null
pip install -r requirements.txt > /dev/null
echo "✅ Dependencies installed"
echo ""

# Generate Ed25519 keys
echo "🔐 Generating Ed25519 keypair..."
if [ ! -f ".env" ]; then
    python scripts/generate_keys.py --output .env
    echo "✅ Keys generated and saved to .env"
else
    echo "ℹ️  .env file already exists, skipping key generation"
    echo "   Delete .env and re-run if you want new keys"
fi
echo ""

# Start infrastructure
echo "🐳 Starting Docker infrastructure..."
cd infra
docker-compose up -d
cd ..
echo "✅ Infrastructure started"
echo ""

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if OPA is ready
until curl -s http://localhost:8181/health > /dev/null 2>&1; do
    echo "   Waiting for OPA..."
    sleep 2
done
echo "✅ OPA is ready"

# Check if PostgreSQL is ready
until docker exec relay-postgres pg_isready -U relay -d relay > /dev/null 2>&1; do
    echo "   Waiting for PostgreSQL..."
    sleep 2
done
echo "✅ PostgreSQL is ready"
echo ""

# Bootstrap policies
echo "📝 Compiling and loading policies..."
python scripts/bootstrap_policies.py
echo ""

# Success message
echo "✅ Relay setup complete!"
echo ""
echo "🎉 Next steps:"
echo "   1. Run the demo: python demo/agent.py"
echo "   2. View audit trail: python demo/visualize.py"
echo "   3. Check Gateway: curl http://localhost:8000/health"
echo ""
echo "📚 Documentation: See README.md for more information"
echo ""
