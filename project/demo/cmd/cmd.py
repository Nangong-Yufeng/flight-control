import os
init_mavsdk_server = r'"project\demo\cmd\mavsdk-windows-x64-release\bin\mavsdk_server_bin.exe -p 50051 serial://COM6:57600"' # 你要运行的exe文件

server = os.system(init_mavsdk_server)
print (server)
