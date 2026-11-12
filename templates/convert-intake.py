"""Convert the template's downloaded XLSX into an additive offline intake package.

Standard library only. Does not upload anything or modify the source workbook.
"""
import argparse
import json
from pathlib import Path
import posixpath
import re
import uuid
from zipfile import ZipFile
from xml.etree import ElementTree as ET

NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
LABELS={'体系':'systems','区域':'regions','身体部位':'parts','关联肌肉':'muscles','动作模式':'modes','动作家族':'families','训练功能':'functions','器械':'equipment','录入状态':'statuses'}
def multiple(text):
    return list(dict.fromkeys(v.strip() for v in re.split(r'[,，、\n]',text or '') if v.strip()))
def read_workbook(path):
    with ZipFile(path) as z:
        shared=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            shared=[''.join(si.itertext()) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',NS)]
        relationships={x.attrib['Id']:x.attrib['Target'] for x in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        result={}
        for sheet in ET.fromstring(z.read('xl/workbook.xml')).findall('s:sheets/s:sheet',NS):
            target=relationships[sheet.attrib['{'+NS['r']+'}id']]
            filename=target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target)
            rows=[]
            for row in ET.fromstring(z.read(filename)).findall('s:sheetData/s:row',NS):
                data={}
                for cell in row.findall('s:c',NS):
                    ref=cell.attrib['r'];letters=re.match('[A-Z]+',ref).group();index=0
                    for c in letters:index=index*26+ord(c)-64
                    value=cell.findtext('s:v','',NS)
                    if cell.attrib.get('t')=='s':value=shared[int(value)]
                    elif cell.attrib.get('t')=='inlineStr':value=''.join(cell.find('s:is',NS).itertext())
                    data[index-1]=value
                rows.append((int(row.attrib['r']),data))
            result[sheet.attrib['name']]=rows
        return result
def convert(path):
    sheets=read_workbook(path)
    if not all(k in sheets for k in ['动作录入','选项字典']):raise ValueError('缺少动作录入或选项字典工作表')
    dr=sheets['选项字典'];header=next((data for _,data in dr if '动作模式' in data.values() and '身体部位' in data.values()),None)
    if header is None:raise ValueError('选项字典表头不正确')
    dictionary={key:[] for key in LABELS.values()}
    for row,data in dr:
        if row<=4:continue
        for col,label in header.items():
            value=str(data.get(col,'')).strip()
            if value and label in LABELS and value not in dictionary[LABELS[label]]:dictionary[LABELS[label]].append(value)
    if any(v in dictionary['modes'] for v in ['屈髋','提起','屈髋提起','宽铰链']):raise ValueError('动作模式请统一使用髋铰链，不单列屈髋、提起或宽铰链')
    rows=sheets['动作录入'];cols=next((data for _,data in rows if '动作名称*' in data.values()),None)
    if cols is None:raise ValueError('动作录入表头不正确')
    records=[];ids=set()
    for number,data in rows:
        if number<=4:continue
        row={label:str(data.get(col,'')).strip() for col,label in cols.items()}
        if row.get('录入状态')!='可导入':continue
        if not row.get('动作名称*') or not row.get('体系*'):raise ValueError(f'第{number}行缺少名称或体系')
        primary=multiple(row.get('主要肌群'));secondary=multiple(row.get('次要肌群'))
        record={'id':row.get('现有动作ID') or 'COURSE-'+uuid.uuid4().hex,'name':row['动作名称*'],'source':row.get('课程/来源') or '课程摘录','course':row.get('课程/来源',''),'catalog':row.get('目录路径',''),'locator':row.get('页码/时间点',''),'regions':multiple(row.get('区域')),'systems':multiple(row['体系*']),'parts':multiple(row.get('身体部位')),'primaryMuscles':primary,'secondaryMuscles':secondary,'muscles':list(dict.fromkeys(multiple(row.get('关联肌肉'))+primary+secondary)),'mode':row.get('动作模式',''),'family':row.get('动作家族',''),'functions':multiple(row.get('训练功能')),'equipment':multiple(row.get('器械')),'aliases':multiple(row.get('别名')),'tags':multiple(row.get('辅助标签')),'notes':row.get('技术笔记',''),'links':[x.strip() for x in row.get('参考链接','').splitlines() if x.strip()],'parentId':row.get('基础动作ID',''),'relatedIds':multiple(row.get('相关动作ID')),'media':[],'favorite':False}
        if record['id'] in ids:raise ValueError(f'第{number}行动作ID重复，不会自动合并')
        ids.add(record['id'])
        for key,dkey in [('systems','systems'),('parts','parts'),('muscles','muscles'),('regions','regions'),('mode','modes'),('family','families'),('functions','functions'),('equipment','equipment')]:
            values=record[key] if isinstance(record[key],list) else [record[key]]
            for value in values:
                if value and value not in dictionary[dkey]:raise ValueError(f'第{number}行的{value}不在选项字典中，请先补入字典')
        records.append(record)
    return {'format':'MovementLibraryIntakeV1','records':records,'dictionary':dictionary,'sourceWorkbook':Path(path).name}
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('xlsx');parser.add_argument('-o','--output');args=parser.parse_args()
    try:
        data=convert(args.xlsx);output=Path(args.output) if args.output else Path(args.xlsx).with_suffix('.intake.json');output.write_text(json.dumps(data,ensure_ascii=False,indent=2));print(f'已生成 {output}，可导入动作 {len(data["records"])} 条。字典中的未使用选项也会同步。')
    except (ValueError,KeyError,ET.ParseError) as error:parser.exit(1,str(error)+'\n')
if __name__=='__main__':main()
