# 用于记录PX4学习的笔记
## 一. Ubuntu, PX4, Gazebo的安装
2022.7.5: protoc实在识别不到，所幸重装个系统，顺便写个ubuntu18.04安装PX4+ROS+Gazebo的教程.
- 本教程在装完系统, 换完镜像源, 打完显卡驱动, 安装完clash后开始记录, 基本与大多数人进程同步. 
- ！！！建议挂个梯子做以下内容！！！  
### ROS及PX4环境搭建
1. 加入ROS安装源\
    `sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'`
2. 加入密钥\
    `sudo apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654`
3. 更新\
    `sudo apt-get update`
4. 安装ros\
    `sudo apt-get install ros-melodic-desktop`
5. Source ROS\
    `echo "source /opt/ros/melodic/setup.bash" >> ~/.bashrc`\
    `source ~/.bashrc`
6. 安装Gazebo\
    `sudo apt install ros-melodic-gazebo9*`
7. 初始化rosdep\
    先安装rosdep\
    `sudo apt-get install python-rosdep`\
    `rosdep init`\
    `rosdep update`\
    init这一步可能会报错,像这样
    ```
    ERROR: cannot download default sources list from:
    https://raw.githubusercontent.com/ros/rosdistro/master/rosdep/sources.list.d/20-default.list
    Website may be down.
     ```
     解决方法: https://zskitecho.blog.csdn.net/article/details/107852051?spm=1001.2101.3001.6661.1&utm_medium=distribute.pc_relevant_t0.none-task-blog-2%7Edefault%7ECTRLIST%7Edefault-1-107852051-blog-105759665.pc_relevant_multi_platform_whitelistv2&depth_1-utm_source=distribute.pc_relevant_t0.none-task-blog-2%7Edefault%7ECTRLIST%7Edefault-1-107852051-blog-105759665.pc_relevant_multi_platform_whitelistv2&utm_relevant_index=1
8. 安装catkin工具
    `sudo apt-get install ros-melodic-catkin python-catkin-tools`
9. 安装mavros
    `sudo apt install ros-melodic-mavros ros-melodic-mavros-extras`
10. 安装geographiclib dataset\
    下载脚本\
    `wget https://raw.githubusercontent.com/mavlink/mavros/master/mavros/scripts/install_geographiclib_datasets.sh`\
    为脚本添加权限\
    `chmod +x install_geographiclib_datasets.sh`\
    执行脚本\
    `sudo ./install_geographiclib_datasets.sh`\
    这一步很慢而且没有任何提示, 所以我去睡了一会()
### PX4仿真工具安装
11. 利用脚本安装必要的工具链\
    `wget https://raw.githubusercontent.com/PX4/Firmware/master/Tools/setup/ubuntu.sh`\
    `wget https://raw.githubusercontent.com/PX4/Firmware/master/Tools/setup/requirements.txt`\
    `bash ubuntu.sh`\
    不知道为什么这次装得好慢(可能是因为没报错?)\
    完成后重启
12. 创建工作空间\
    `mkdir -p ~/catkin_ws/src`\
    `cd ~/catkin_ws/src/`\
    `catkin_init_workspace`
11. 下载编译px4\
    下载代码\
    `cd ~/catkin_ws/`\
    `git clone https://github.com/PX4/Firmware`\
    然后更新submodule切换固件并编译(我直接在master编译的)\
    `cd Firmware`\
    `git submodule update --init --recursive`\
    这一行反复运行直到没有报错
12. 在具体编译前还需要安装相关的工具\
    `sudo apt-get install python-jinja2`\
    `sudo pip install numpy toml`\
    若提示 `sudo: pip：找不到命令 `的话先安装`python-pip`
13. 开始编译\
    `make px4_sitl gazebo_plane`\
    若出现以下错误\
    `gzclient: symbol lookup error: /usr/lib/x86_64-linux-gnu/libgazebo_common.so.9: undefined symbol: _ZN8ignition10fuel_tools12ClientConfig12SetUserAgentERKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE`\
    解决方法:\
    `sudo apt upgrade`\
    再次编译即可成功\
    `make clean`\
    `make px4_sitl gazebo_plane`\
    至此, 启动成功, 教程结束



~~Ubuntu(一个操作系统): CSDN随便看~~\
~~PX4(飞控程序)+Gazebo(一个仿真环境): https://www.guyuehome.com/8983~~
## 二. 地面站
地面站在PC上获取飞控信息以及给PC发送指令等(通过数传或WIFI或数据线(?))
常用地面站软件有有两种: QGroundControl(QGC)和MissionPlanner(MP)\
PX4官方文档使用的QGC所以我们暂时使用QGC作为地面站. (不过好像MP功能更强大)\
*不过我们不打算使用地面站对飞机进行过多的控制, 考虑到可能会做视觉, 而且负责飞控部分的有计科人, 所以打算采用MAVSDK-python对飞控进行控制*



---
# 问题记录
- [ ] 2022.7.4前: MAVSDK控制固定翼时, 出现了一次起飞降落一次后模式改变拒绝起飞的问题. 
    - 通过重启飞控解决, 但显然有更好的通过切换模式解决的方法. 
       **TODO**: 寻找mavsdk切换模式的方法
- [ ] 2022.7.4前: MAVSDK控制固定翼mission时, 因为mavsdk.mission中没有降落任务, mission upload被PX4拒绝, 原因是PX4之前的某次更新中新增了对固定翼mission的限制: 必须要有landing. 
    - 解决方法1: 在浏览github时注意到了一些mavsdk的插件, 这个问题好像很早就被发现, 有专门的插件做mission_fixed_wing\
    https://github.com/iwishiwasaneagle/MAVSDK-Proto/tree/mission_fixed_wing \
        **TODO**: 研究一下怎么使用
    - 解决方法2: 二次开发飞控, 浏览过论坛和github后, 得知是参数RTL_TYPE在某次更新变为了1(对固定翼来说更安全的返航方式), 网传改成0就好了(?)
    - 解决方法3: 使用旧版飞控, 但是也不知道是那个版本...\
        220704-1804: https://github.com/PX4/PX4-Autopilot/issues/13107
