from pathlib import Path
import shutil, sys

upstream=Path(sys.argv[1])
files=Path(__file__).parent
connector=upstream/'src/javax/microedition/io/Connector.java'
text=connector.read_text(encoding='utf-8')
text=text.replace('if (name != null && name.startsWith("sms://")) {', '''if (name != null && (name.startsWith("socket://") || name.startsWith("ssl://"))) {
            return new SocketConnectionImpl(name);
        } else if (name != null && (name.startsWith("http://") || name.startsWith("https://"))) {
            return new HttpConnectionImpl(name);
        } else if (name != null && name.startsWith("sms://")) {''')
text=text.replace('public static InputStream openInputStream(String name)','public static InputStream openInputStream(String name) throws IOException')
text=text.replace('public static DataInputStream openDataInputStream(String name)','public static DataInputStream openDataInputStream(String name) throws IOException')
text=text.replace('//System.out.println("Connector: " + name);','if (name.startsWith("socket://") || name.startsWith("ssl://") || name.startsWith("http://") || name.startsWith("https://")) return ((InputConnection)open(name)).openInputStream();')
text=text.replace('System.out.println("Faked DataInputStream: "+name);','if (name.startsWith("socket://") || name.startsWith("ssl://") || name.startsWith("http://") || name.startsWith("https://")) return ((InputConnection)open(name)).openDataInputStream();\n        System.out.println("Faked DataInputStream: "+name);')
text=text.replace('public static DataOutputStream openDataOutputStream(String name) { return new DataOutputStream(new DummyOutputStream()); }','public static DataOutputStream openDataOutputStream(String name) throws IOException { return ((OutputConnection)open(name)).openDataOutputStream(); }')
text=text.replace('public static OutputStream openOutputStream(String name) { return new DummyOutputStream(); }','public static OutputStream openOutputStream(String name) throws IOException { return ((OutputConnection)open(name)).openOutputStream(); }')
assert 'new SocketConnectionImpl' in text
connector.write_text(text,encoding='utf-8')
for name in ['InputConnection.java','OutputConnection.java']:
    interface=connector.parent/name
    source=interface.read_text(encoding='utf-8')
    source=source.replace('();', '() throws java.io.IOException;')
    interface.write_text(source,encoding='utf-8')
for name in ['SocketConnectionImpl.java','HttpConnectionImpl.java']:
    shutil.copy(files/name,connector.parent/name)
bridge=upstream/'src/pl/zb3/freej2me/bridge/network'
bridge.mkdir(parents=True,exist_ok=True)
shutil.copy(files/'NetworkBridge.java',bridge/'NetworkBridge.java')
shutil.copy(files/'network.js',upstream/'web/libjs/network.js')
main=upstream/'web/src/main.js'
text=main.read_text(encoding='utf-8')
text='import networkNatives from "../libjs/network.js";\n'+text
text=text.replace('natives: {','natives: {\n            ...networkNatives,',1)
main.write_text(text,encoding='utf-8')
page=upstream/'web/index.html'
text=page.read_text(encoding='utf-8').replace('<title>freej2me-web</title>','<title>J2ME Online</title>')
text=text.replace('<h1>freej2me-web</h1>','<h1>J2ME Online</h1><p>Chọn file JAR trên điện thoại để chơi. File game và dữ liệu lưu trong trình duyệt của bạn.</p>')
page.write_text(text,encoding='utf-8')
