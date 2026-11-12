from pathlib import Path
import re,json
p=Path(__file__).parent
s=(p/'original/Movement-Library-ACE-IFT-v1.7.html').read_text()
seed=json.loads(re.search(r'const SEED = (.*?);\n',s).group(1))
(p/'original/ACE-IFT-original-records.json').write_text(json.dumps({'format':'MovementLibraryV1','records':seed},ensure_ascii=False,indent=2))
s=s.replace('V1.7 原型','V1.9 本地版').replace('<title>Movement Library · ACE IFT</title>','<title>Movement Library · 离线动作库</title>')
s=s.replace('☆　Favorites','☆　我的收藏').replace("?'Favorites':'全部动作'","?'我的收藏':'全部动作'")
s=s.replace('按部位 · BODY REGIONS','身体部位').replace('训练体系 · SYSTEMS','训练体系')
s=s.replace('<div class="toolbar">','<div class="toolbar">')
s=s.replace('<div class="chips" id="chips"></div>','<div class="viewbar"><div class="segments"><button id="gridView" aria-pressed="true">▦ 卡片</button><button id="listView" aria-pressed="false">☷ 列表</button></div><span class="hint">维度之间取交集 · 同维度多选取并集</span><select id="sortOrder" class="select" aria-label="排序"><option value="original">原始顺序</option><option value="name">名称排序</option><option value="recent">最近修改</option></select></div><div id="activeFilters" class="active-filters"></div><div class="chips" id="chips"></div>')
s=s.replace('<div class="meta"><span id="count"></span><span>点击动作可编辑 · 资料来源：ACE IFT 模型 · 肌群信息尚待补充</span></div>','<div class="meta"><span id="count" role="status"></span><span id="storageState">正在打开本地资料库…</span></div><div class="listhead"><span>动作名称</span><span>家族 / 模式</span><span>部位 / 体系</span></div>')
s=s.replace('<div class="cards" id="cards"></div>','<div class="cards" id="cards"></div>')
s=s.replace('<button class="clearSide"','<div class="sidehead">训练功能</div><div id="sideFunctions"></div><div class="sidehead">器械（可选）</div><div id="sideEquipment"></div><button class="clearSide"')
s=s.replace('<select class="select" id="family">','<select class="select" id="family" aria-label="动作家族">').replace('<select class="select" id="mode">','<select class="select" id="mode" aria-label="动作模式">')
s=s.replace('placeholder="搜索动作、别名、家族或标签…"','aria-label="搜索动作" placeholder="搜索动作、别名、笔记…"')
extra='<div class="field"><label for="editFunctions">训练功能（可选，逗号分隔）</label><input id="editFunctions" list="functionList" placeholder="例如：活动度、稳定性、力量"><datalist id="functionList"><option>活动度</option><option>稳定性</option><option>力量</option><option>爆发力</option><option>耐力</option></datalist></div><div class="field"><label for="editEquipment">器械（可选，逗号分隔）</label><input id="editEquipment" list="equipmentList" placeholder="例如：徒手、哑铃、弹力带"><datalist id="equipmentList"></datalist></div>'
s=s.replace('<details class="field">',extra+'<details class="field">',1)
relations='<details class="field" open><summary>动作关联 <span class="hint">可选</span></summary><label for="editParent" style="margin-top:12px">变式来源 / 基础动作</label><select id="editParent" class="select" style="width:100%"></select><label for="relationSearch" style="margin-top:14px">相关动作 · 保存后自动建立双向链接</label><input id="relationSearch" placeholder="搜索要关联的动作"><div id="relatedEditor" class="relation-options"></div><div id="recordConnections" class="connections"></div></details>'
s=s.replace('<div class="field"><label>动作笔记',relations+'<div class="field"><label>动作笔记')
s=s.replace('accept="image/*,video/*" multiple','multiple').replace('图片 / 视频（保存在浏览器本地）','图片、视频与附件（保存在浏览器本地）')
s=s.replace('<div class="bulkrow"><label>动作家族', ''.join(f'<div class="bulkrow"><label>{label}</label><div class="pair"><select id="bulk{field}Op"><option value="keep">不修改</option><option value="add">添加</option><option value="remove">移除</option><option value="replace">替换</option><option value="clear">清空</option></select><input id="bulk{field}" placeholder="多个用逗号分隔"></div></div>' for field,label in [('Functions','训练功能'),('Equipment','器械')])+'<div class="bulkrow"><label>动作家族',1)
s=s.replace('<option value="replace">替换</option>','<option value="replace">替换</option><option value="clear">清空</option>')
# Remove duplicated clear option on new rows.
s=s.replace('<option value="clear">清空</option><option value="clear">清空</option>','<option value="clear">清空</option>')
s=s.replace('Muscles:\'关联肌群\'',"Muscles:'关联肌群',Functions:'训练功能',Equipment:'器械'")
s=s.replace("['Parts','Systems','Tags','Family','Mode','Muscles']","['Parts','Systems','Tags','Family','Mode','Muscles','Functions','Equipment']")
s=s.replace("['Parts','Systems','Tags','Muscles']","['Parts','Systems','Tags','Muscles','Functions','Equipment']")
s=s.replace("['Systems','Tags','Family','Mode']","['Systems','Tags','Family','Mode','Functions','Equipment']")
s=s.replace("(f==='Systems'||f==='Tags')?", "(['Systems','Tags','Functions','Equipment'].includes(f))?")
s=s.replace("if(!vals.length){bulkMessage", "if(op!=='clear'&&!vals.length){bulkMessage")
s=s.replace("if(op==='keep')return prev;", "if(op==='keep')return prev;if(op==='clear')return [];")
s=s.replace("function closeBulk(){$('bulkMask')", "function closeBulk(){if(bulkSaving)return;$('bulkMask')")
s=s.replace("  closeBulk();\n  toggleBulk(false);", "  bulkSaving=false;\n  closeBulk();\n  toggleBulk(false);")
s=s.replace("  const y={...x};", "  const y={...x,updatedAt:new Date().toISOString()};")
s=s.replace("$('bulkMask').classList.add('show');updateBulkPreview()", "$('bulkPreview').className='bulk-preview';$('bulkMask').classList.add('show');updateBulkPreview();$('bulkClose').focus()")
s=s.replace("const request=(store,mode,callback)=>new Promise((resolve,reject)=>{const t=db.transaction(store,mode),s=t.objectStore(store);let result;t.oncomplete=()=>resolve(result);t.onerror=()=>reject(t.error);result=callback(s)});", "const request=(store,mode,callback)=>new Promise((resolve,reject)=>{let t;try{t=db.transaction(store,mode);t.oncomplete=()=>resolve();t.onerror=()=>reject(t.error||Error('数据库写入失败'));t.onabort=()=>reject(t.error||Error('写入已中止'));callback(t.objectStore(store))}catch(e){try{t?.abort()}catch{}reject(e)}});")
s=s.replace("r.onerror=()=>reject(r.error)});let stored=await allRecords();if(!stored.length)","r.onerror=()=>reject(r.error);r.onblocked=()=>{$('storageState').textContent='请关闭其他 Movement Library 标签页后重试'}});let stored=await allRecords();let initialized=false;try{initialized=localStorage.getItem(db.name+'-initialized')==='yes'}catch{}if(!stored.length&&!initialized)")
s=s.replace("items=stored;render()}","try{localStorage.setItem(db.name+'-initialized','yes')}catch{}items=stored;render()}",1)
s=s.replace("r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error)})}","r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);t.onabort=()=>reject(t.error||Error('数据库读取被中止'))})}",1)
start=s.index('function saveBatchRecords(records){')
end=s.index("$('bulkApply').onclick",start)
s=s[:start]+'''// One atomic transaction: reject aborts, synchronous clone failures and stalled writes.
function saveBatchRecords(records){return new Promise((resolve,reject)=>{
 let tx,finished=false;
 const finish=(err)=>{if(finished)return;finished=true;clearTimeout(timer);err?reject(err):resolve()};
 const timer=setTimeout(()=>{try{tx?.abort()}catch{}finish(Error('保存等待超过 15 秒，请重试；若仍失败，请先导出备份并重开页面'))},15000);
 try{if(!db)throw Error('本地数据库尚未就绪');tx=db.transaction('records','readwrite');
 tx.oncomplete=()=>finish();tx.onerror=()=>finish(tx.error||Error('数据库写入失败'));tx.onabort=()=>finish(tx.error||Error('写入已中止，本次修改未提交'));
 const store=tx.objectStore('records');for(const record of records)store.put(record);
 }catch(e){try{tx?.abort()}catch{}finish(e)}
})}
''' + s[end:]
# Hook extension rendering while preserving the existing cards and filters.
s=s.replace('function filters(){','function baseFilters(){',1).replace('function render(){','function baseRender(){',1).replace('function openRecord(id){','function baseOpenRecord(id){',1)
s=s.replace('function optionList(id,vals,placeholder){', 'function optionList(id,vals,placeholder){',1)
s=s.replace("el.value=v}\nfunction baseRender", "el.value=vals.includes(v)?v:''}\nfunction baseRender")
s=s.replace("parts:isScapularFocus({name,family:$('editFamily').value.trim()})?['肩胛骨']:checkedEditor('partEditor')", "parts:checkedEditor('partEditor')")
# Replace the record save, media and import handlers with guarded implementations in extension.
start=s.index("$('save').onclick=async()=>")
end=s.index("$('fav').onclick",start)
s=s[:start]+s[end:]
start=s.index('function drawMedia()')
end=s.index("$('fav').onclick",start)
s=s[:start]+s[end:]
s=s.replace("init().catch(err=>alert('无法打开本地数据库：'+err.message));",'')
start=s.index("$('importBtn').onclick")
s=s[:start]+s[s.index('</script>',start):]
s=s.replace('let selectedParts=new Set(),selectedSystems=new Set();','let selectedParts=new Set(),selectedSystems=new Set(),selectedFunctions=new Set(),selectedEquipment=new Set();')
s=s.replace("const set=k==='part'?selectedParts:selectedSystems;", "const set=({part:selectedParts,system:selectedSystems,function:selectedFunctions,equipment:selectedEquipment})[k];if(!set)return;")
s=s.replace("selectedParts.clear();selectedSystems.clear();selectedTag='';", "selectedParts.clear();selectedSystems.clear();selectedFunctions.clear();selectedEquipment.clear();selectedTag='';")
s=s.replace('return items.filter(x=>','return items.filter(x=>',1)
s=s.replace("...'", "...'")
s=s.replace("...(x.muscles||[])].join", "...(x.muscles||[]),...(x.functions||[]),...(x.equipment||[])].join")
s=s.replace("preview.data}", "safe(preview.data)}")
s=s.replace('<article class="card ', '<article tabindex="0" role="button" class="card ')
s=s.replace("<div class=\"cardphoto\">${preview?", "<div class=\"cardphoto ${preview?'has-media':''}\">${preview?")
s=s.replace("\" alt=\"\">`:'◇'", "\" alt=\"动作图片\">`:'↗'")
s=s.replace("$('bulkCount').textContent=`已选 ${bulkSelected.size} 个动作`", "$('bulkCount').textContent=`已选 ${bulkSelected.size} 个动作 · 当前结果中 ${filters().filter(x=>bulkSelected.has(x.id)).length} 个`")
s=s.replace('选中部位后默认「替换」','选中部位后默认「替换」')
css=(p/'ui.css').read_text()
css+='\n'+(p/'navigation.css').read_text()
extension=(p/'extension.js').read_text()+'\n'+(p/'navigation.js').read_text()
s=s.replace('</style>',css+'\n</style>',1).replace('</script>',extension+'\n</script>',1)
(p/'index.html').write_text(s)
qa=s.replace("indexedDB.open('MovementLibraryV1',1)","indexedDB.open('MovementLibraryV1-QA',1)")
qa=qa.replace('</body>','<script>'+(p/'qa.js').read_text()+'</script></body>')
(p/'qa.html').write_text(qa)
print('Built V1.9; original seed records:',len(seed))
