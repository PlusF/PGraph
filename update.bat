git pull origin main
CALL venv\Scripts\activate
python -m pip uninstall -y dataloader
python -m pip install git+https://github.com/PlusF/DataLoader