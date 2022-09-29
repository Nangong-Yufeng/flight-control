import torch

# torch是否可以正常连接CUDA
print(torch.cuda.is_available())

# torch是否可以正常连接cuDNN
from torch.backends import cudnn
print(cudnn.is_available())

# 显示cuDNN版本
print(cudnn.version())
# 显示cuda版本
print(torch.version.cuda)