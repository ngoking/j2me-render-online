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

# Fetch the small emulator JAR once instead of issuing many remote range reads.
# /str is CheerpJ's transient, read-only Java filesystem.
library_loader = '''
async function loadEmulatorLibrary() {
    try {
    const response = await fetch("/freej2me-web.jar", {signal: AbortSignal.timeout(60000)});
    if (!response.ok) throw new Error("Could not download emulator: HTTP " + response.status);
    cheerpOSAddStringFile("/str/freej2me-web.jar", new Uint8Array(await response.arrayBuffer()));
    return cheerpjRunLibrary("/str/freej2me-web.jar");
    } catch (error) {
        console.warn("Direct emulator download failed; trying Java filesystem", error.message);
        return cheerpjRunLibrary(cheerpjWebRoot + "/freej2me-web.jar");
    }
}
'''
for name in ['launcher.js', 'main.js']:
    script = upstream/'web/src'/name
    text = script.read_text(encoding='utf-8')
    text = text.replace('cheerpjRunLibrary(cheerpjWebRoot+"/freej2me-web.jar")', 'loadEmulatorLibrary()')
    text += library_loader
    if name == 'launcher.js':
        text = text.replace('    lib = await loadEmulatorLibrary();', '    document.getElementById("loading").textContent = "Đang tải bộ giả lập...";\n    lib = await loadEmulatorLibrary();')
        text = text.replace('main();', '''main().catch(error => {
    console.error(error);
    document.getElementById("loading").textContent = "Không tải được giả lập: " + error.message;
});''')
    else:
        text = text.replace('function setListeners() {', '''function pointerPosition(point) {
    const bounds = display.getBoundingClientRect();
    return {
        x: ((point.clientX - bounds.left) * display.width / bounds.width) | 0,
        y: ((point.clientY - bounds.top) * display.height / bounds.height) | 0,
    };
}

function setListeners() {''')
        text = text.replace('''x: e.offsetX / display.currentCSSZoom | 0,
            y: e.offsetY / display.currentCSSZoom | 0,''', '...pointerPosition(e),')
        text = text.replace('''x: (e.pageX - display.offsetLeft) / display.currentCSSZoom | 0,
            y: (e.pageY - display.offsetTop) / display.currentCSSZoom | 0,''', '...pointerPosition(e),')
        text = text.replace('''x: (e.changedTouches[0].pageX - display.offsetLeft) / display.currentCSSZoom | 0,
            y: (e.changedTouches[0].pageY - display.offsetTop) / display.currentCSSZoom | 0,''', '...pointerPosition(e.changedTouches[0]),')
        assert 'display.currentCSSZoom' not in text
    script.write_text(text, encoding='utf-8')

(upstream/'web/diagnostics.html').write_text('''<!doctype html>
<html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kiểm tra kết nối J2ME</title>
<style>body{font:16px system-ui;max-width:600px;margin:32px auto;padding:16px}button{padding:12px;margin:8px}pre{white-space:pre-wrap;background:#eee;padding:16px}</style>
<h1>Kiểm tra kết nối</h1><p>Thử đường mạng tới web và máy chủ game. Không cần tài khoản.</p>
<label>Máy chủ: <select id="server" aria-label="Máy chủ"><option value="dragon1.teamobi.com">Vũ trụ 1</option><option value="dragon15.teamobi.com" selected>Vũ trụ 15</option></select></label>
<button id="http">Kiểm tra HTTP</button><button id="jar">Kiểm tra tải giả lập</button><button id="ws">Kiểm tra WebSocket</button>
<pre id="result" role="status">Chọn một phép kiểm tra.</pre><a href="/">Về trang game</a>
<script>
const result=document.getElementById('result');
for(const [id,url] of [['http','/healthz'],['jar','/freej2me-web.jar']]) document.getElementById(id).onclick=async()=>{
 result.textContent='Đang kiểm tra '+url;
 try{const r=await fetch(url,{signal:AbortSignal.timeout(20000)});const b=await r.arrayBuffer();result.textContent=url+': HTTP '+r.status+', nhận '+b.byteLength+' byte';}
 catch(e){result.textContent=url+': '+e.name+' - '+e.message;}
};
document.getElementById('ws').onclick=()=>{
 const gameHost=document.getElementById('server').value;
 result.textContent='Đang mở WebSocket tới '+gameHost+':14445';
 const w=new WebSocket((location.protocol==='https:'?'wss:':'ws:')+'//'+location.host+'/socket?host='+encodeURIComponent(gameHost)+'&port=14445&secure=0');
 const timer=setTimeout(()=>{result.textContent='WebSocket quá thời gian';w.close()},15000);
 w.onmessage=e=>{if(typeof e.data==='string'){clearTimeout(timer);result.textContent='WebSocket: '+e.data;w.close()}};
 w.onerror=()=>{clearTimeout(timer);result.textContent='WebSocket bị lỗi trong trình duyệt'};
};
</script></html>''',encoding='utf-8')
