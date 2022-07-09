# 用于记录PX4学习的笔记
## 一. Ubuntu, PX4, Gazebo的安装
2022.7.5: protoc实在识别不到，所幸重装个系统，顺便写个ubuntu18.04安装PX4+ROS+Gazebo的教程.
- 本教程在装完系统, 换完镜像源, 打完显卡驱动, 安装完clash后开始记录, 基本与大多数人进程同步. 
- ！！！建议挂个梯子做以下内容！！！
- ！！！**以下的教程面对的是Ubuntu18.04**，对于Ubuntu20.04，
    - 要把每一个ros-melodic（melodic）改成ros-noetic(noetic)
    - 要把每一个python换成python3
- 强烈建议不要用20.04，不然你就会像我一样大晚上的还在整这玩意。

### ROS及PX4环境搭建
1. 加入ROS安装源
    ```sh
    sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
    ```
2. 加入密钥
    ```sh
    sudo apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
    ```
3. 更新
    ```sh
    sudo apt-get update
    ```
4. 安装ros
    ```sh
    sudo apt-get install ros-melodic-desktop
    ```
5. Source ROS\
    (此处注意，使用不是bash的shell的，**要切回bash而不是将命令改掉**)。
    ```sh
    echo "source /opt/ros/melodic/setup.bash" >> ~/.bashrc
    source ~/.bashrc
    ```
6. 安装Gazebo
    ```sh
    sudo apt install ros-melodic-gazebo9*
    ```
7. 初始化rosdep\
    先安装rosdep
    ```sh
    sudo apt-get install python-rosdep
    rosdep init
    rosdep update
    ```
    init这一步可能会报错,像这样
    ```
    ERROR: cannot download default sources list from:
    https://raw.githubusercontent.com/ros/rosdistro/master/rosdep/sources.list.d/20-default.list
    Website may be down.
    ```
    解决方法见[这个帖子](https://zskitecho.blog.csdn.net/article/details/107852051?spm=1001.2101.3001.6661.1&utm_medium=distribute.pc_relevant_t0.none-task-blog-2%7Edefault%7ECTRLIST%7Edefault-1-107852051-blog-105759665.pc_relevant_multi_platform_whitelistv2&depth_1-utm_source=distribute.pc_relevant_t0.none-task-blog-2%7Edefault%7ECTRLIST%7Edefault-1-107852051-blog-105759665.pc_relevant_multi_platform_whitelistv2&utm_relevant_index=1)
8. 安装catkin工具
    ```sh
    sudo apt-get install ros-melodic-catkin python-catkin-tools
    ```
9. 安装mavros
    ```sh
    sudo apt install ros-melodic-mavros ros-melodic-mavros-extras
    ```
10. 安装geographiclib dataset\
    下载脚本
    ```sh
    wget https://raw.githubusercontent.com/mavlink/mavros/master/mavros/scripts/install_geographiclib_datasets.sh
    ```
    为脚本添加权限
    ```sh
    chmod +x install_geographiclib_datasets.sh
    ```
    执行脚本
    ```sh
    sudo ./install_geographiclib_datasets.sh
    ```
    这一步**很慢而且没有任何提示**, 所以我去睡了一会()
### PX4仿真工具安装
11. 利用脚本安装必要的工具链
    ```sh
    wget https://raw.githubusercontent.com/PX4/Firmware/master/Tools/setup/ubuntu.sh
    wget https://raw.githubusercontent.com/PX4/Firmware/master/Tools/setup/requirements.txt
    bash ubuntu.sh
    ```
    不知道为什么这次装得好慢(可能是因为没报错?)\
    完成后重启
    > 但是我报错了:cry:（可能是因为我直接没装前面的直接装px4）。  
    > 报的错是：`由于没有公钥，无法验证下列签名 NO_PUBKEY 354e516d494ef95f`(这串数字是我网上找的)  
    > 解决方法[见这个帖子](https://blog.csdn.net/loovejava/article/details/21837935)。
    > 由于CSDN不登陆没法复制，我把命令**前半部分**贴在这里：  
    > `sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys`
    
12. 创建工作空间
    ```sh
    mkdir -p ~/catkin_ws/src
    cd ~/catkin_ws/src/
    catkin_init_workspace
    ```
11. 下载编译px4\
    下载代码
    ```sh
    cd ~/catkin_ws/
    git clone https://github.com/PX4/Firmware
    or
    git clone -b v1.12.3 https://github.com/PX4/Firmware.git
    注：当前默认下载PX4为1.13版本(git命令不带  -b v1.12.3),进行gazebo仿真时会出现问题，建议安装较低版本，例如v1.12.3
	注：这里会下载Gazebo，和JMAVSim两个虚拟仿真软件，可能会造成耗时较长
    ```
    然后更新submodule切换固件并编译(我直接在master编译的)
    ```sh
    cd Firmware
    git submodule update --init --recursive
    ```
    这一行反复运行直到没有报错
12. 在具体编译前还需要安装相关的工具
    ```sh
    sudo apt-get install python-jinja2
    sudo pip install numpy toml
    ```
    若提示 `sudo: pip：找不到命令 `的话先安装`python-pip`
13. 开始编译
    ```sh
    make px4_sitl gazebo_plane
    ```
    若出现以下错误\
    `gzclient: symbol lookup error: /usr/lib/x86_64-linux-gnu/libgazebo_common.so.9: undefined symbol: _ZN8ignition10fuel_tools12ClientConfig12SetUserAgentERKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE`\
    解决方法:
    ```sh
    sudo apt upgrade
    ```
    再次编译即可成功
    ```sh
    make clean
    make px4_sitl gazebo_plane
    ```
    至此, 启动成功, 教程结束



~~Ubuntu(一个操作系统): CSDN随便看~~\
~~PX4(飞控程序)+Gazebo(一个仿真环境): https://www.guyuehome.com/8983~~
## 二. 地面站
地面站在PC上获取飞控信息以及给PC发送指令等(通过数传或WIFI或数据线(?))
常用地面站软件有有两种: QGroundControl(QGC)和MissionPlanner(MP)\
PX4官方文档使用的QGC所以我们暂时使用QGC作为地面站. (不过好像MP功能更强大)\
*不过我们不打算使用地面站对飞机进行过多的控制, 考虑到可能会做视觉, 而且负责飞控部分的有计科人, 所以打算采用MAVSDK-python对飞控进行控制*
## TIPS  
- 在启动px4+gazebo仿真前执行下列指令, 可将飞机位置变为我们学校  
```sh
export PX4_HOME_LAT=22.58670
export PX4_HOME_LON=113.96434
export PX4_HOME_ALT=29
```


---
# 问题记录
- [ ] 2022.7.4前: MAVSDK控制固定翼时, 出现了一次起飞降落一次后模式改变拒绝起飞的问题. 
    - 通过重启飞控解决, 但显然有更好的通过切换模式解决的方法. 
       **TODO**: 寻找mavsdk切换模式的方法  
       20220707-1719: mavsdk中没找到, 但可以直接在qgc中切换模式或者绑定按键到遥控器上. 
- [x] 2022.7.4前: MAVSDK控制固定翼mission时, 因为mavsdk.mission中没有降落任务, mission upload被PX4拒绝, 原因是PX4之前的某次更新中新增了对固定翼mission的限制: 必须要有landing. 
    - ~~解决方法1: 在浏览github时注意到了一些mavsdk的插件, 这个问题好像很早就被发现, 有专门的插件做mission_fixed_wing\
      https://github.com/iwishiwasaneagle/MAVSDK-Proto/tree/mission_fixed_wing \
        **TODO**: 研究一下怎么使用~~
    - [x] **解决方法2: 二次开发飞控, 浏览过论坛和github后, 得知是参数RTL_TYPE在某次更新变为了1(对固定翼来说更安全的返航方式), 网传改成0就好了(?)**  
        **20220707-1718: 这个方法成功了, mission正常运行.**  
            - [ ] 如何将修改过的PX4刷入飞控?
    - ~~解决方法3: 使用旧版飞控, 但是也不知道是那个版本...\
        220704-1804: https://github.com/PX4/PX4-Autopilot/issues/13107~~
