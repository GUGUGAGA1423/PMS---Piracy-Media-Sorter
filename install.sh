#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "============================================================"
echo "🚀 Installing PMS - Piracy Media Sorter"
echo "============================================================"

# 1. Request storage permissions if not granted
if [ ! -d "$HOME/storage" ]; then
    echo "📱 Requesting storage permission..."
    termux-setup-storage
fi

# 2. Update and upgrade dependencies silently without hanging on config prompts
echo "📦 Installing system dependencies..."
export DEBIAN_FRONTEND=noninteractive
pkg update -y && pkg upgrade -y -o Dpkg::Options::="--force-confold" && pkg install -y python curl git

# 3. Install Python dependencies
echo "🐍 Installing Python libraries..."
pip install requests guessit

# 4. Download Python script
mkdir -p ~/.pms
curl -sL https://raw.githubusercontent.com/GUGUGAGA1423/PMS---piracy-media-sorter/main/organize.py -o ~/.pms/organize.py

# 5. Create executable wrapper so typing 'sort' runs the script from anywhere
cat << 'EOF' > $PREFIX/bin/sort
#!/data/data/com.termux/files/usr/bin/bash
python3 ~/.pms/organize.py "$@"
EOF

chmod +x $PREFIX/bin/sort

echo "============================================================"
echo "✅ Installation complete! Type 'sort' anywhere to run."
echo "============================================================"
