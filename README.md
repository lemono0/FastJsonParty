# FastJsonParty

FastJson全版本Docker漏洞环境(涵盖1.2.47/1.2.68/1.2.80等版本)，主要包括JNDI注入、waf绕过、文件读写、原生反序列化、利用链探测绕过、不出网利用等。设定场景为黑盒利用，从黑盒的角度覆盖FastJson深入利用全过程，部分环境需要给到jar包反编译分析。

Docker环境，开箱即用。

环境启动：`docker compose up -d` 

若docker拉取环境缓慢，请尝试使用国内镜像

https://www.runoob.com/docker/docker-mirror-acceleration.html

环境启动后，访问对应ip的80端口：

![image](images/1.png)

总结了一些关于FastJson全版本常用漏洞利用Poc,可搭配食用：[Fastjson全版本检测及利用-Poc](Fastjson全版本检测及利用-Poc.md) 

环境使用后请销毁,否则可能会冲突：`docker compose down` 

整理一下靶场顺序：(根据利用特点分成三个大类)

## FastJson 1.2.47

[1247-jndi](1247-jndi)

[1247-jndi-waf](1247-jndi-waf)

[1247-waf-c3p0](1247-waf-c3p0)

[1245-jdk8u342](1245-jdk8u342)



## FastJson 1.2.68

[1268-readfile](1268-readfile)

[1268-jkd11-writefile](1268-jkd11-writefile)

[1268-jdk8-writefile](1268-jdk8-writefile)

[1268-writefile-jsp](1268-writefile-jsp)

[1268-writefile-no-network](1268-writefile-no-network)

[1268-jdbc](1268-jdbc)



## FastJson 1.2.80

[1280-groovy](1280-groovy)

[1283-serialize](1283-serialize)



每个机器根目录下都藏有flag文件，去尝试获取吧！

部分环境wp目前还未给出,打算过段时间放出，也欢迎提交你的wp和建议。

:sparkling_heart: 如果感觉有用，不要忘记star :star: Orz

And Enjoy FastJson Party!

