import torch
import sys

if str(sys.version)[:4] == '3.10' :
    print(f"CHECK PYTHON VERSION: {str(sys.version)[:7]}")
else :
    print("CHECK PYTHON VERSION: SOMETHING DIFFERENT.")

if str(torch.__version__) == '2.2.2+cu121':
    print("CHECK TORCH  VERSION: 2.2.2+cu121")
else:
    print("CHECK TORCH  VERSION: SOMETHING DIFFERENT.")

if torch.cuda.is_available():
    device = torch.device('cuda:0')
    print(f"CHECK GPU  AVAILABLE: {torch.cuda.get_device_name(device = 0)}")
else:
    device = torch.device('cpu')
    print(f"CHECK GPU  AVAILABLE: CPU")

