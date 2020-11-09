

if [ ! -d ges71_env ]; then
    python3 -m venv ges71_env
fi
source "ges71_env/bin/activate"
which python
pip3 install --upgrade pip
pip3 install numpy
