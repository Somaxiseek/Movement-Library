import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const out=process.argv[2];
const options=JSON.parse(await fs.readFile(new URL('./options.json',import.meta.url),'utf8'));
const wb=Workbook.create();
const main=wb.worksheets.add('动作录入'),dict=wb.worksheets.add('选项字典'),guide=wb.worksheets.add('填写说明');
const headers=['录入状态','动作名称*','体系*','课程/来源','目录路径','区域','身体部位','主要肌群','次要肌群','动作模式','动作家族','训练功能','器械','别名','辅助标签','技术笔记','页码/时间点','参考链接','基础动作ID','相关动作ID','现有动作ID'];
const keys=['systems','regions','parts','muscles','modes','families','functions','equipment','statuses'];
const labels=['体系','区域','身体部位','关联肌肉','动作模式','动作家族','训练功能','器械','录入状态'];
for(const sheet of [main,dict,guide]){sheet.showGridLines=true;sheet.getRange('A1:U40').format.font={name:'Arial',size:11,color:'#202124'};sheet.getRange('A1:U40').format.verticalAlignment='center';}
main.getRange('A1').values=[['课程动作录入']];main.getRange('A1').format.font={size:15,bold:true};
main.getRange('A2').values=[['名称、体系必填']];main.getRange('C2').values=[['第5行为示例，从第6行开始。准备好后设为可导入。']];
main.getRange('A3').values=[['其他字段可留空']];main.getRange('C3').values=[['多值逗号分隔。新增选项请在“选项字典”对应列末尾追加。']];
main.getRange('A4:U4').values=[headers];
main.getRange('A5:U5').values=[['示例','墙面滑动','ACE IFT 模型','示例课程（请替换）','第2章 > 肩胛控制','上肢','肩胛骨','','','','wall slide','稳定性','徒手','Wall slide','','示例行用于演示，不作为课程原文或肌肉映射依据。','第12页','','','','']];
main.getRange('A4:U504').format.rowHeight=27;
main.getRange('A4:U4').format={fill:'#F1F3F4',font:{bold:true},wrapText:true,rowHeight:40};
main.getRange('A5:U5').format.font={color:'#777777'};
main.getRange('A5:U504').setNumberFormat('@');
const widths=[105,190,170,210,220,100,145,190,190,135,145,130,140,180,170,330,150,260,160,190,180];
widths.forEach((width,i)=>main.getRangeByIndexes(0,i,504,1).format.columnWidthPx=width);
main.freezePanes.freezeRows(4);main.freezePanes.freezeColumns(2);
// Native table intent is preserved on import. Dynamic dictionaries use range rules below.
main.tables.add('A4:U504',true,'MovementIntake').style='TableStyleLight1';
dict.getRange('A1').values=[['可扩充的选项字典']];dict.getRange('A1').format.font={size:15,bold:true};
dict.getRange('A2').values=[['对应列末尾逐行追加。下拉预留1000行，超出后扩展引用范围。']];
dict.getRange('A3').values=[['沿用现有动作库的模式和部位；屈髋、提起统一归入“髋铰链”，不设为独立选项。']];
dict.getRange('A4:I4').values=[labels];dict.getRange('A4:I4').format={fill:'#F1F3F4',font:{bold:true},rowHeight:34};
const length=Math.max(...keys.map(k=>options[k].length));
dict.getRangeByIndexes(4,0,length,9).values=Array.from({length},(_,i)=>keys.map(k=>options[k][i]??''));
dict.getRange('A4:I1004').format.rowHeight=26;dict.getRange('A4:I1004').format.columnWidthPx=155;dict.freezePanes.freezeRows(4);
const mappings=[[0,8],[2,0],[5,1],[6,2],[7,3],[8,3],[9,4],[10,5],[11,6],[12,7]];
for(const [col,dc]of mappings){const letter=String.fromCharCode(65+dc);main.getRangeByIndexes(4,col,500,1).dataValidation={rule:{type:'list',formula1:`'选项字典'!$${letter}$5:$${letter}$1004`}};}
main.getRange('B6:B504').conditionalFormats.addCustom('AND($A6="可导入",$B6="")',{fill:'#FCE8E6',font:{color:'#A50E0E'}});
main.getRange('C6:C504').conditionalFormats.addCustom('AND($A6="可导入",$C6="")',{fill:'#FCE8E6',font:{color:'#A50E0E'}});
const instructions=[
 ['填写与交接','规则'],
 ['最低必填','动作名称、体系。其余分类可留空，不确定时不猜。'],
 ['建议补充','课程/来源，以及页码或视频时间点，方便日后核对。'],
 ['目录路径','课程中的章节位置。例如：第2章 > 肩胛控制。与动作家族分开。'],
 ['区域与身体部位','区域是上肢/下肢/躯干/全身；身体部位沿用原库的胸、肩、肩胛骨等。'],
 ['肩胛骨','墙面滑动、墙天使、俯卧YTW等肩胛控制动作优先选择肩胛骨。'],
 ['动作模式','推、拉、蹲、髋铰链等沿用现有分类。屈髋和提起不单列。'],
 ['多个值','身体部位、主要肌群、次要肌群在Google Sheet中使用多选标签；其他多值列可用逗号分隔。'],
 ['下拉的使用','身体部位、主要肌群、次要肌群可在下拉中勾选多个。主、次肌群分别保存，不确定可留空。'],
 ['增加选项','到“选项字典”对应列最后一个选项下方追加，主表下拉会读取新值。不要只改主表的下拉规则。'],
 ['准备交接','把已整理好的行设为可导入，保留其余行为待整理或暂缓。示例行不会导入。'],
 ['交给助手','把这份Google Sheet链接发到项目聊天，注明本次课程/范围。助手读取动作与选项字典并提供离线导入包。'],
 ['离线同步','表格中新增选项会即时进入表格下拉；离线网站需要导入交接包后更新，不会联网实时同步。'],
 ['自行离线转换','Google Sheet下载为Microsoft Excel .xlsx；运行仓库中的表格转换器生成JSON，再在动作库导入。'],
 ['基础动作ID与相关动作ID','可留空。需要关联时使用动作库里的稳定ID，不用同名动作自动推断。'],
 ['现有动作ID','新增动作留空。已存在的ID会在添加课程动作时跳过，不自动覆盖现有笔记和附件。'],
 ['重名与重复导入','同名动作不会自动合并。重复导入同一个JSON包按ID跳过；重新转换同一表格会生成新ID，需避免重复添加。'],
 ['肌肉与附件','主要肌群与次要肌群分别多选，可留空。旧版未区分的肌群不自动升级为主要肌群。附件在动作库中添加。'],
 ['保留课程原文','名称保留课程原名。其他名称放别名列。不要为套分类擅自改名。'],
 ['当前分类来源','本项目Movement Library V1.9原始记录与现有编辑字段。https://github.com/Somaxiseek/Movement-Library'],
 ['范围下拉依据','https://support.google.com/docs/answer/186103?hl=zh-Hans'],
 ];
guide.getRange(`A1:B${instructions.length}`).values=instructions;guide.getRange('A1:B1').format={fill:'#F1F3F4',font:{bold:true},rowHeight:34};guide.getRange(`A2:B${instructions.length}`).format.wrapText=true;guide.getRange(`A1:A${instructions.length}`).format.columnWidthPx=170;guide.getRange(`B1:B${instructions.length}`).format.columnWidthPx=760;guide.getRange(`A2:B${instructions.length}`).format.rowHeight=45;
wb.recalculate();await fs.mkdir(out,{recursive:true});
for(const [sheet,range,name]of [[main,'A1:J10','intake'],[dict,'A1:I22','dictionary'],[guide,'A1:B15','guide']]){const image=await wb.render({sheetName:sheet.name,range,scale:1.5,format:'png'});await fs.writeFile(`${out}/${name}.png`,new Uint8Array(await image.arrayBuffer()));}
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!',options:{useRegex:true,maxResults:10},summary:'error scan'})).ndjson);
await (await SpreadsheetFile.exportXlsx(wb)).save(`${out}/Movement-Library-课程动作录入模板.xlsx`);
console.log('Workbook saved');
