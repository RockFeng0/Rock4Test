# rtsf(rock4 test service framework)

**[rock4automation项目](https://github.com/RockFeng0/rock4automation)痛点**
- 集成了 http测试,web UI测试，PC MFC UI测试，PC WPF UI测试，但实际上，QA或者测试人员，可能只需要http相关的api测试，却不得不将整个项目下载安装
- rock4automation项目,打包发布的程序，会将源码封装了exe或者加密为pyd；
- rock4automation项目,打包了相关工具，比如appium-server，java.exe 等等，大量冗余的，非项目源码的工具

**rtsf项目的目标**
- 可扩展，用于打造一个基本的测试服务框架,也许以后可以基于RPC，但是，目前，还只是一个可扩展的模块包
- 精简，拆分业务测试相关的功能、测试框架应有的基础功能、其他工具不再整合，rtsf项目，就是其中的基础功能
- 专注，rtsf已经完成了，自成一体的执行逻辑，测试开发人员，主要精力仅需要投入到，重写和设计测试用例执行过程的run_test函数
- 轻量，少造轮子，多复用标准库和优秀开源项目


## rtsf-测试用例模型

> 测试用例模型，计划扩展为, yaml, xml, excel三种，目前已扩展的只有yaml测试用例模型 

### Yaml测试用例模型介绍

- 用例模型，基本保持[rock4automation项目](https://github.com/RockFeng0/rock4automation)的case模型
- 其中的变量和函数的替换，参照了httprunner项目的格式  $VAR ${FUNC}, 该格式取代了我的[rock4automation项目](https://github.com/RockFeng0/rock4automation)中的， #var# 等替换规则
- 变量的引用: $VAR  其中，VAR为字母、数字、下划线组成的变量名.  正则表示为:  [a-zA-Z0-9_]
- 函数的引用: ${FUNC}    其中, FUNC为字母、数字、下划线、横线、点号、等号、逗号组成的函数. 示例:  /api/${add(1, 2)}?_t=${get_timestamp()}   正则表示为: [a-zA-Z0-9.-_=,]
- 如果函数引用的过程中，参数含有特殊字符，将不会被识别， 解决方法是，使用全局变量.   示例,如:  a='@#$%^&'; $print($a)   
- yaml测试用例，是一个testset(测试集)，可以引入api和suite

> 如果测试用例使用了api，则合并。  意思是，如果测试用例中（如下示例）使用了api关键字，那么api中定义的所有键值对，会和case中定义的键值对进行合并，形成一个完整的用例。**可以理解为并集的过程**

> 如果测试用例使用了suite，则扩展。 意思是，如果测试用例中（如下示例）使用了suite关键字,那么suite中定义的所有case，替换当前case。 可以理解为置当前case为空集，取suite中的所有case集合为当前测试用例。**所以在使用了suite的区域块case中，定义的键值对和关键字都无效**

> 执行顺序  pre_command(List) -> steps(List) -> post_command(List) -> verify(List)

```
# yaml基本测试模型
# 示例:
- project:
    name: xxx系统
    module: 登陆模块-功能测试

- case:
    id: ATP-1
    desc: 使用api示例
    
    # 用例分层-使用 api时，必填
    api: test_api()

- case:
    id: ATP-2
    desc: 使用suite示例, 当前case中的id 和desc 这些键值对，都无效
    
    # 用例分层-使用 suite时，必填
    suite: test_suite()
    
- case:
    # id 必填
    id: ATP-3
    # desc 必填
    desc: 测试用例-模板格式的设计-模板（全字段）
    
    # responsible 选填
    responsible: rockfeng0
    
    # tester 选填
    tester: rockfeng0
    
    # pre_command 选填
    pre_command:
        - Set(passwd = "123456")
    
    # steps 必填
    steps:
        # request 测试api或者 http /https 时使用
        - request:
            url: https://www.baidu.com
            method: GET
            headers:
            data:
        
        # webdriver 测试web ui 时使用
        - webdriver:
            by: css
            value: "#username"
            index: 0
            timeout: 10
            action: ${sendkey($username)}
        - webdriver:
            action: ${refresh}
        
        # appdriver 测试android UI 时使用
        - appdriver:
            action: ${refresh}
        
        # wpfdriver 测试pc wpf技术的客户端 ui 时使用    
        - wpfdriver:
            action: 
        
        # mfcdriver 测试pc mfc技术的客户端 ui 时使用    
        - mfcdriver:
            actiion:
    
    # post_command 选填
    post_command:
        - Set(passwd = "123456")
    
    # verify 选填
    verify:
        - VerifyCode("200")
```

模型解释:
- project: name->待测系统的名称; module->测试集名称
- case: 必填(id->测试用例id; desc->测试用例的描述;steps->测试步骤;verify->校验),选填(responsible->测试责任人;tester->测试执行人;pre_command->测试前置条件(前置钩子);post_command->测试后置条件(后置钩子))
- case-steps: request->http测试; webdriver->web UI测试; appdriver->移动端app测试;wpfdriver->使用wpf技术的pc客户端测试;mfcdriver->使用mfc技术的pc客户端测试)

## rtsf-测试用例分层(测试组件化)

- rtsf支持测试用例分层，允许测试用例的组件化
- 测试用例编写过程中，使用api关键字封装当前单个case，允许其他case进行调用,类似调用单个api一样
- 测试用例编写过程中，使用suite关键字，封装当前多个cases，允许其他case进行调用， 类似调用组件化模块一样
- api和suite的存放路径，在指定运行的测试用例同级目录的 dependencies/api和dependencies/suite中
- api用例的原理，两个字: 合并. 是指测试用例 合并 api用例的键值对。
- suite用例的原理，两个字: 扩展.，是指测试用例 扩展为suite中的用例。

> 注意: 其内在逻辑，其实是，先加载api和suite,以dict形式存储在内置变量中，然后，加载测试集的用例，如果测试用例使用了api则合并，如果测试用例使用了suite则扩展。

分层用例的示例，参见[rtsf-http项目的介绍](https://github.com/RockFeng0/rtsf-http)

### api用例介绍

- api测试用例，实际上是一个最小单元的测试，封装后，便于被suite和testset重复引入
- 应用测试用例的分层思想
- api测试用例中的def的解析，参照了httprunner项目
- 存放路径, 测试用例同级目录下:  dependencies/api/*。yaml, dependencies/api/*。yml, dependencies/api/*。json

```
# api测试用例的示例：
- api:
    # def 必填
    def: test_api()    
    
    # pre_command 选填
    pre_command:
        - Set(passwd = "123456")
    
    # steps 必填
    steps:
        # request 测试api或者 http /https 时使用
        - request:
            url: https://www.baidu.com
            method: GET
            headers:
            data:
        
        # webdriver 测试web ui 时使用
        - webdriver:
            by: css
            value: "#username"
            index: 0
            timeout: 10
            action: ${sendkey($username)}
        - webdriver:
            action: ${refresh}
        
        # appdriver 测试android UI 时使用
        - appdriver:
            action: ${refresh}
        
        # wpfdriver 测试pc wpf技术的客户端 ui 时使用    
        - wpfdriver:
            action: 
        
        # mfcdriver 测试pc mfc技术的客户端 ui 时使用    
        - mfcdriver:
            actiion:
    
    # post_command 选填
    post_command:
        - Set(passwd = "123456")
    
    # verify 选填
    verify:
        - VerifyCode("200")
```


### suite用例介绍

- suite测试用例，实际上是，由一些api或者一些case，封装后的，相对稳定的，测试用例
- 应用测试用例分层思想，suite也可以被testset引入
- 存放路径, 测试用例同级目录下:  dependencies/suite/*。yaml, dependencies/suite/*。yml, dependencies/suite/*。json

> suite的用例跟 testset差别不大，主要的是，在project中，添加def关键字，定义引入suite的函数入口

```
# suite测试套件的示例：
- project:
    def: test_suite()
            
- case:
    # id 必填
    id: ATP-2
    # desc 必填
    desc: suite测试用例-模板（字段与testset测试用例相同）
    
    # responsible 选填
    responsible: rockfeng0
    
    # tester 选填
    tester: rockfeng0
    
    # pre_command 选填
    pre_command:
        - Set(passwd = "123456")
    
    # steps 必填
    steps:
        # request 测试api或者 http /https 时使用
        - request:
            url: https://www.baidu.com
            method: GET
            headers:
            data:
        
        # webdriver 测试web ui 时使用
        - webdriver:
            by: css
            value: "#username"
            index: 0
            timeout: 10
            action: ${sendkey($username)}
        - webdriver:
            action: ${refresh}
        
        # appdriver 测试android UI 时使用
        - appdriver:
            action: ${refresh}
        
        # wpfdriver 测试pc wpf技术的客户端 ui 时使用    
        - wpfdriver:
            action: 
        
        # mfcdriver 测试pc mfc技术的客户端 ui 时使用    
        - mfcdriver:
            actiion:
    
    # post_command 选填
    post_command:
        - Set(passwd = "123456")
    
    # verify 选填
    verify:
        - VerifyCode("200")
        
```

## rtsf-使用方法

- rtsf提供入口，允许自定义执行模块的扩展，这个过程有点类似python中重写threading.Thread类.
- 不同的是，rtsf需要重写rtsf.p_executer.Runner.run_test方法

### Runner.run_test重写
自定义case运行过程，就是重写 Runner.run_test的过程，是使用rtsf的主要工作

```
# 示例:
from rtsf.p_executer import Runner
class SubRunner(Runner):      
    
    def __init__(self):
        super(SubRunner,self).__init__()        
        
    def run_test(self, testcase_dict, driver_map):
        fn, _ = driver_map
        tracer = self.tracers[fn]
        parser = self.parser
        
```
- run_test(testcase_dict, driver_map), rtsf在执行测试的时候，调用run_test方法，传入testcase_dict和driver_map
- testcase_dict参数，是当前要执行的测试用例，rtsf将会传入字典格式
- driver_map参数，是当前要执行的设备，rtsf将会传入一个列表，格式如:("192.168.0.1:5555":selenium_driver), 默认情况下，("",None)
- self.parser,Runner中继承的属性， 解析测试用例的实例，控制全局上下文和映射关键字与执行函数
- self.tracers,Runner中继承的属性, 跟踪设备执行日志的实例，详细记录每个用例的执行过程

> 注意: 重写的时候，第一个参数，是单个case，不是所有case，**只需要写一个case的执行逻辑**

另外，使用rtsf,我这里已经写了几个项目,供大家参考和使用:

- [http/https自动化测试](https://github.com/RockFeng0/rtsf-http)
- [web ui自动化测试](https://github.com/RockFeng0/rtsf-web)
- [android ui自动化测试](https://github.com/RockFeng0/rtsf-app)
- 桌面客户端(WPF技术)自动化测试-敬请期待
- 桌面客户端(MFC技术)自动化测试-敬请期待


### TestRunner执行测试

- TestRunner(runner = Runner),runner参数用于指定重写了Runner.run_test的Runner子类,用于运行case,默认值为Runner
- TestRunner.run, 该方法用于运行指定yaml的case文件，或者运行指定文件夹路径中的yaml和json,如c:\case目录下*.yaml和*.json
- TestRunner。gen_html_report,方法用于生成测试报告，报告路径是yaml文件所在路径

```
# 示例:
# test.py
# coding:utf-8
from rtsf.p_executer import TestRunner,Runner

# 执行测试, 指定测试文件test.yaml
runner = TestRunner(runner = Runner).run('test.yaml')
# runner = TestRunner(runner = Runner).run(r'c:\case')

# 生成测试报告
html_report = runner.gen_html_report()

# 打印测试报告路径
print(html_report)

```


