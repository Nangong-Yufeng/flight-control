import os
init_mavsdk_server = r'"project\demo\cmd\mavsdk-windows-x64-release\bin\mavsdk_server_bin.exe"' # 你要运行的exe文件

server = os.system(init_mavsdk_server)
print (server)
