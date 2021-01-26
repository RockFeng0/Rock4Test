#! python3
# -*- encoding: utf-8 -*-

import os
import time
import types
import shutil
import unittest

from rtsf import p_compat
from rtsf.p_common import CommonUtils
from rtsf.p_common import FileSystemUtils
from rtsf.p_common import FileUtils
from rtsf.p_common import IntelligentWaitUtils
from rtsf.p_common import DateTimeUtils
from rtsf.p_common import ZipUtils
from rtsf.p_common import ModuleUtils
from rtsf.p_common import SetupUtils
from rtsf.p_common import ProgressBarUtils


class TestCommonUtils(unittest.TestCase):
    
    def test_gen_random_string(self):
        result = CommonUtils.gen_random_string(5)
        self.assertEqual(isinstance(result, str) and len(result) == 5, True)
    
    def test_gen_cartesian_product(self):
        a = [{"a": 1}, {"a": 2}]
        b = [
                {"x": 111, "y": 112},
                {"x": 121, "y": 122}
            ]
        expect_result = [
                {'a': 1, 'x': 111, 'y': 112},
                {'a': 1, 'x': 121, 'y': 122},
                {'a': 2, 'x': 111, 'y': 112},
                {'a': 2, 'x': 121, 'y': 122}
            ]
        
        self.assertEqual(CommonUtils.gen_cartesian_product(a, b), expect_result)        
        
    def test_convert_to_order_dict(self):
                
        dict1 = dict(zip(("a", "b", "c"), ("A", "B", "C")))
        dict2 = dict(zip(("a", "c", "b"), ("A", "C", "B")))        
        self.assertEqual(dict1 == dict2, True)
        
        dict3 = CommonUtils.convert_to_order_dict([dict1])
        dict4 = CommonUtils.convert_to_order_dict([dict2])
        self.assertEqual(dict3 == dict4, False)        
        
    def test_get_value_from_cfg(self):
        results_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_tmp")
        fn = os.path.join(results_path, "test.conf")        
        with open(fn, 'w') as f:
            f.write("""
[device-1]
dut_ip = 192.168.1.1
user = admin
passwd = 123456

[device-2]
dut_ip = 192.168.1.2
user = admin
passwd = 123456
 
            """)
            
        conf = CommonUtils.get_value_from_cfg(fn)
        self.assertEqual(conf["device-1"]["dut_ip"], "192.168.1.1")
        self.assertEqual(conf["device-2"]["passwd"], "123456")
        FileSystemUtils.force_delete_file(fn)
    

class TestFileUtils(unittest.TestCase):
    
    def setUp(self):
        self.case = r'data\testcases\case_model.yaml' 
        self.csv = r'data\testcases\username_password.csv'
        
    def test_load_folder_files(self):        
        
        cases_path = r'test_tmp\testcases'
        p1 = os.path.join(cases_path, "t1")
        p2 = os.path.join(cases_path, "t2")
         
        FileSystemUtils.mkdirs(p1)
        FileSystemUtils.mkdirs(p2)
        shutil.copyfile(self.case, os.path.join(cases_path, "t.yaml"))
        shutil.copyfile(self.case, os.path.join(p1, "t1.yaml"))
        shutil.copyfile(self.case, os.path.join(p2, "t2.yaml"))
                
        result1 = FileUtils.load_folder_files(p1, recursive=False)        
        self.assertEqual(len(result1), 1)
        
        result2 = FileUtils.load_folder_files(cases_path, recursive=True)
        self.assertEqual(len(result2), 3)
        
        result3 = FileUtils.load_file(self.csv)
        self.assertIsInstance(result3, list)
        self.assertIsInstance(result3[0], dict)        
        
        
class TestFileSystemUtils(unittest.TestCase):
    
    def setUp(self):
        self.results_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_tmp")
        
    def test_mkdirs(self):
        p = os.path.join(self.results_path, 't1', 't2', 't3')
        FileSystemUtils.mkdirs(p)
        self.assertEqual(os.path.isdir(p), True)
        shutil.rmtree(p)
        
    def test_get_file_md5(self):
        f = os.path.join(self.results_path, 'md5test.txt')
        with open(f, 'w') as fn:
            fn.write(u"千山鸟飞绝，万径人踪灭")
        
        self.assertEqual(FileSystemUtils.get_file_md5(f), "92e5a625b232d4c52ceb9d9330e02e44")
        FileSystemUtils.force_delete_file(f)
    
    def test_get_file_size(self):
        f = os.path.join(self.results_path, 'md5test.txt')
        with open(f, 'w') as fn:
            fn.write(u"千山鸟飞绝，万径人踪灭")
        
        self.assertEqual(FileSystemUtils.get_file_size(f), 22)
        FileSystemUtils.force_delete_file(f)
        
    def test_get_legal_filename(self):
        self.assertEqual(FileSystemUtils.get_legal_filename("你好&-|他*"), '你好&-他')
        self.assertEqual(FileSystemUtils.get_legal_filename("\n你好&-|他*"), '你好&-他')
    
    def test_add_unique_postfix(self):
        f = os.path.join(self.results_path, 'md5test.txt')
        with open(f, 'w') as fn:
            fn.write(u"千山鸟飞绝，万径人踪灭")
            
        self.assertNotEqual(FileSystemUtils.add_unique_postfix(f), 'md5test_2.txt')
        FileSystemUtils.force_delete_file(f)
    
    def test_force_delete_file(self):
        f = os.path.join(self.results_path, 'md5test.txt')
        with open(f, 'w') as fn:
            fn.write(u"千山鸟飞绝，万径人踪灭")
        
        FileSystemUtils.force_delete_file(f)
        
        self.assertEqual(os.path.isfile(f), False)


class TestIntelligentWaitUtils(unittest.TestCase):
    
    def setUp(self):
        self.results_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_tmp")
        
    def test_until_cmd(self):
        cmd = ["ping", "127.0.0.1", "-n", "2"]
        f = os.path.join(self.results_path, 'IntelligentWaitUtils.log')
        start = time.time()
        IntelligentWaitUtils.until_cmd(cmd)
        end = time.time()
        IntelligentWaitUtils.until_cmd(cmd, save2logfile=f)
        IntelligentWaitUtils.until_cmd(cmd, end_expects=u"平均 = 0ms", save2logfile=f)
        
        self.assertGreater(end - start, 1)
        self.assertEqual(os.path.isfile(f), True)
        
    def test_until(self):
        f = lambda: None if time.sleep(2) else True
        start = time.time()
        IntelligentWaitUtils.until(f)
        end = time.time()
        self.assertEqual(int(end - start), 2)
        
    def test_until_not(self):
        f = lambda: True if time.sleep(2) else None
        start = time.time()
        IntelligentWaitUtils.until_not(f)
        end = time.time()
        self.assertEqual(int(end - start), 2)
            
    def test_wait_for_connection(self):
        start = time.time()
        result = IntelligentWaitUtils.wait_for_connection("localhost", 4444, 2)
        end = time.time()
        if result in [True, False]:
            self.assertEqual(int(end - start), 2)
        else:
            self.assertEqual(result, None)


class TestDateTimeUtils(unittest.TestCase):
    
    def test_get_stamp_date(self):
        """ return data formate-> 2018-07-04 """
        self.assertEqual(DateTimeUtils.get_stamp_date(), time.strftime("%Y-%m-%d"))        
    
    def test_get_stamp_datetime(self):
        """ return data formate-> 2018-07-04 19:26:22 """
        self.assertEqual(DateTimeUtils.get_stamp_datetime(), time.strftime("%Y-%m-%d %H:%M:%S"))
    
    def test_get_stamp_datetime_coherent(self):
        """ return data formate-> 2018-07-04_19_27_04 """
        self.assertEqual(DateTimeUtils.get_stamp_datetime_coherent(), time.strftime("%Y-%m-%d_%H_%M_%S"))


class TestZipUtils(unittest.TestCase):
    
    def setUp(self):
        self.results_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_tmp")
        
    def test_mkzip(self):
        p = os.path.join(self.results_path, "testcase")
        t = os.path.join(self.results_path, "testcase.zip")                
        ZipUtils.mkzip(p, t)       
        
        self.assertEqual(os.path.isfile(t), True)
        FileSystemUtils.force_delete_file(t)
    
    def test_unzip(self):
        p = os.path.join(self.results_path, "testcase")
        fzip = os.path.join(self.results_path, "testcase.zip")                
        ZipUtils.mkzip(p, fzip)        
        
        t = os.path.join(self.results_path, "test-unzip")                                
        ZipUtils.unzip(fzip, t)
        
        self.assertEqual(os.path.isfile(fzip), True)        
        self.assertEqual(os.path.isdir(t), True)
        
        FileSystemUtils.force_delete_file(fzip)
        shutil.rmtree(t)


class TestModuleUtils(unittest.TestCase):
    
    def setUp(self):
        self.results_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_tmp")
        
        def test1(self):
            pass
        
        def test2(self):
            pass
        
        def _test3(self):
            pass
        
        self.MyTest = type("MyTest", (), {'var1': "value1",
                                        "_var2": "_value2",
                                         "func1": test1,
                                         "_func2": test2,
                                         "func3": _test3,
                                        }
                            )
        
        self.file_module = f = os.path.join(self.results_path, "preference.py")        
        with open(f, 'w') as f:
            f.write("""
# encoding:utf-8
 
var1 = 'value1'
_var2 = 'value2'
 
def test1():
    return "call test1 ok."
 
def test2():
    pass
 
def _test3():
    pass
            """)
        
    def test_get_callable_class_method_names(self):
        funcs = ModuleUtils.get_callable_class_method_names(self.MyTest)
        
        self.assertIn("func1", funcs)
        self.assertNotIn("_func2", funcs)
        self.assertIn("func3", funcs)
        
    def test_is_function(self):
        funcs = ModuleUtils.get_callable_class_method_names(self.MyTest)
        
        for k,v in funcs.items():
            self.assertEqual(ModuleUtils.is_function((k, v)), True)
            
    def test_is_variable(self):
        is_vars = {"username": "test", "password":123456}
        not_vars = {"_unknow": "", "object": self.MyTest, "module": os}
        
        for k,v in is_vars.items():
            self.assertEqual(ModuleUtils.is_variable((k,v)), True)

        for k,v in not_vars.items():
            self.assertEqual(ModuleUtils.is_variable((k,v)), False)
    
    def test_get_imported_module(self):
        module = ModuleUtils.get_imported_module("logging")
        
        self.assertEqual(isinstance(module, types.ModuleType), True)
        
    def test_get_imported_module_from_file(self):
        
        module = ModuleUtils.get_imported_module_from_file(self.file_module)
        self.assertEqual(isinstance(module, types.ModuleType), True)
    
    def test_filter_module(self):
        result = ModuleUtils.filter_module(self.MyTest, "function")        
        self.assertIn("func1", result)
        self.assertIn("_func2", result)
        self.assertIn("func3", result)
          
        result = ModuleUtils.filter_module(self.MyTest, "variable")
        self.assertIn("var1", result)
        self.assertNotIn("_var2", result)
          
    def test_filter_module_from_file(self):     
        module = ModuleUtils.get_imported_module_from_file(self.file_module)
          
        result = ModuleUtils.filter_module(module, "function")
        self.assertIn("test1", result)
        self.assertIn("test2", result)
        self.assertIn("_test3", result)
          
        result = ModuleUtils.filter_module(module, "variable")
        self.assertIn("var1", result)
        self.assertNotIn("_var2", result)        
    
    def test_search_conf_item(self):
        func_obj = ModuleUtils.search_conf_item(self.file_module, "function", "test1")
        self.assertEqual(func_obj(), "call test1 ok.")
        
        var_value = ModuleUtils.search_conf_item(self.file_module, "variable", "var1")        
        self.assertEqual(var_value, "value1")
    
    def tearDown(self):
        FileSystemUtils.force_delete_file(self.file_module)


class TestSetupUtils(unittest.TestCase):
    
    def test_find_data_files(self):
        result = SetupUtils.find_data_files(r"C:\Python27\Lib\distutils\command", "distutils/command", ["*.exe", "*.dll", "*.pyd"])
        
        expected = [('distutils/command', ['C:\\Python27\\Lib\\distutils\\command\\wininst-6.0.exe', 
                                'C:\\Python27\\Lib\\distutils\\command\\wininst-7.1.exe', 
                                'C:\\Python27\\Lib\\distutils\\command\\wininst-8.0.exe', 
                                'C:\\Python27\\Lib\\distutils\\command\\wininst-9.0-amd64.exe', 
                                'C:\\Python27\\Lib\\distutils\\command\\wininst-9.0.exe'])
                                ]
        self.assertEqual(result, expected)


class TestProgressBarUtils(unittest.TestCase):
    
    def test_echo(self):
        for i in range(11):
            ProgressBarUtils.echo(i, 10)
            
    def test_echo_size(self):
        f = lambda x, y: x+y
        ldata = range(10)
        toBeTransferred = p_compat.reduce(f, range(10))
        
        progress = ProgressBarUtils("refresh", toBeTransferred=toBeTransferred, unit="KB", chunk_size=1.0, run_status="正在下载", fin_status="下载完成")        
        for i in ldata:
            time.sleep(0.2)
            progress.echo_size(transferred=i)
    
    def test_echo_percent(self):
        f=lambda x, y: x+y
        ldata = range(10)
        toBeTransferred = p_compat.reduce(f, range(10))
        
        progress = ProgressBarUtils("viewbar", toBeTransferred=toBeTransferred, run_status="正在下载", fin_status="下载完成")    
        for i in ldata:  
            time.sleep(0.1)  
            progress.echo_percent(i)
    
        
if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFileUtils))
#     suite.addTest(TestCommonUtils("test_gen_cartesian_product"))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
#     unittest.main(verbosity=2)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    