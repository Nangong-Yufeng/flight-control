工程文件在project里面  

目前成果:  
- 制作了简单但任务性强的地面站, 有以下作用:  
  - 监控飞机部分数据信息  
  - 武装(arm)飞机  
  - 控制飞机进行侦察任务  
  - 控制飞机飞向一个投弹点  
  - 控制飞机开启投弹模式(监听到投弹信号则进行投弹动作)  
- 完成了视觉部分的目标识别和目标追踪, 有以下作用:  
  - 显示图传画面, 人工看数字(人工更准确)  
  - 用yolo识别靶子(4个), 当目标靶(1个)移动到画面中投弹区时发出投弹消息  
  - 用camshift追踪目标靶(1个), 避免其余3个靶子对上述过程产生影响  

TODO: 

- [x] ~~通过键盘启动"前往给定数个侦察任务点"任务~~  
- [x] ~~通过键盘启动"前往指定投弹任务点"任务~~  
- [ ] 投弹  
- [x] 视觉(?)  
- [ ] (可选)通过图传画面修正无人机向目标靶飞行  
- [ ] (可选)增加数字识别, 自动框选目标把进行追踪(准确率不好说)  

## 做点笔记
- [PX4+ROS+Gazebo的安装教程](/PX4%E7%9B%B8%E5%85%B3/PX4%E5%AE%89%E8%A3%85%E6%95%99%E7%A8%8B%E4%B8%8E%E5%BC%80%E5%8F%91%E8%BF%9B%E5%BA%A6.md)  
- [PX4官网UserGuide](https://docs.px4.io/v1.12/en/)  
- [MAVSDK-python](https://github.com/mavlink/MAVSDK-Python)  
- [MAVSDK-Proto-mission-fixed-wing](https://github.com/iwishiwasaneagle/MAVSDK-Proto/tree/mission_fixed_wing)  
- [mavsdk-python-tutorials](https://github.com/maponarooo/mavsdk-python-tutorials)  
- [PX4与仿真入门教程](https://www.ncnynl.com/category/px4-sim/)   
- [MAVSDK-Python API reference](http://mavsdk-python-docs.s3-website.eu-central-1.amazonaws.com/)  
