> 先贴一个官网的[开发者指南](https://developers.google.com/protocol-buffers/docs/overview)。里边介绍得挺详细的  

## 什么是 _protobuf_ ?
protobuf，全称为`Protocol Buffer`，是谷歌家出的一个"*跨平台、跨语言、可扩展* "的“__序列化、结构化数据的方式__”

## 跟我们有什么关系？
mavsdk(应该)是基于谷歌家gRPC框架实现对远程的飞控板的控制。其中数据和指令就是**以protobuf的_原型文件_ 指定的方式进行序列化**并传输的。  
以这层序列化作为中介，在地面使用python脚本发送出的指令与数据可以被gRPC的c++后端程序接收，并发送给飞控上的程序。
