import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
import json
spec=importlib.util.spec_from_file_location('converter',Path(__file__).with_name('convert-intake.py'))
converter=importlib.util.module_from_spec(spec);spec.loader.exec_module(converter)

class IntakeTests(unittest.TestCase):
    def fixture(self):
        options=json.loads(Path(__file__).with_name('options.json').read_text())
        labels=list(converter.LABELS)
        dictionary=[(4,dict(enumerate(labels)))]+[(5+i,{col:options[converter.LABELS[label]][i] for col,label in enumerate(labels) if len(options[converter.LABELS[label]])>i}) for i in range(max(map(len,options.values()))) ]
        headers=['录入状态','动作名称*','体系*','课程/来源','目录路径','区域','身体部位','关联肌肉','动作模式','动作家族','训练功能','器械','别名','辅助标签','技术笔记','页码/时间点','参考链接','基础动作ID','相关动作ID','现有动作ID']
        row=['可导入','保留原名','ACE IFT 模型','课程A','第二章','上肢','肩胛骨，肩','菱形肌','髋铰链','','稳定性','徒手','Alias1,Alias2','','原文笔记','00:30','','','','']
        return {'动作录入':[(4,dict(enumerate(headers))),(6,dict(enumerate(row)))],'选项字典':dictionary}
    def convert(self,data):
        with patch.object(converter,'read_workbook',return_value=data):return converter.convert('fixture.xlsx')
    def test_mapping_and_optional_ids(self):
        result=self.convert(self.fixture());record=result['records'][0]
        self.assertEqual(record['name'],'保留原名');self.assertEqual(record['mode'],'髋铰链');self.assertEqual(record['parts'],['肩胛骨','肩']);self.assertEqual(record['aliases'],['Alias1','Alias2']);self.assertEqual(record['catalog'],'第二章');self.assertTrue(record['id'].startswith('COURSE-'))
    def test_skips_non_ready(self):
        for status in ['示例','待整理','暂缓','']:
            data=self.fixture();data['动作录入'][1][1][0]=status;self.assertEqual(self.convert(data)['records'],[])
    def test_missing_required(self):
        data=self.fixture();data['动作录入'][1][1][1]=''
        with self.assertRaises(ValueError):self.convert(data)
    def test_new_dictionary_values_even_if_unused(self):
        data=self.fixture();data['选项字典'].append((50,{4:'新课程模式'}));self.assertIn('新课程模式',self.convert(data)['dictionary']['modes'])
    def test_unknown_option_not_silently_classified(self):
        data=self.fixture();data['动作录入'][1][1][8]='未知模式'
        with self.assertRaises(ValueError):self.convert(data)
    def test_synonyms_rejected(self):
        data=self.fixture();data['选项字典'].append((50,{4:'屈髋'}))
        with self.assertRaises(ValueError):self.convert(data)
    def test_duplicate_explicit_id(self):
        data=self.fixture();data['动作录入'][1][1][19]='same';data['动作录入'].append((7,data['动作录入'][1][1].copy()))
        with self.assertRaises(ValueError):self.convert(data)
    def test_original_mode_vocabulary(self):
        modes=json.loads(Path(__file__).with_name('options.json').read_text())['modes']
        self.assertEqual(set(modes),{'推','拉','蹲','髋铰链','负重行走','旋转','抗伸展','抗旋转','抗侧屈','爬行'})
    def test_primary_secondary_multiselect(self):
        data=self.fixture();header=data['动作录入'][0][1];header[7]='主要肌群';header[20]='次要肌群';data['动作录入'][1][1][7]='菱形肌, 斜方肌';data['动作录入'][1][1][20]='三角肌，背阔肌'
        record=self.convert(data)['records'][0]
        self.assertEqual(record['primaryMuscles'],['菱形肌','斜方肌']);self.assertEqual(record['secondaryMuscles'],['三角肌','背阔肌']);self.assertEqual(record['muscles'],['菱形肌','斜方肌','三角肌','背阔肌'])
    def test_legacy_muscles_are_not_promoted(self):
        record=self.convert(self.fixture())['records'][0];self.assertEqual(record['primaryMuscles'],[]);self.assertEqual(record['secondaryMuscles'],[]);self.assertEqual(record['muscles'],['菱形肌'])

if __name__=='__main__':unittest.main()
