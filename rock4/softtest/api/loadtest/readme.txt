ʾ����Ŀ��
�μ����� loperf

1.ִ��
    ������->D:\auto\python\loperf\httpload.py 200 10 100
    ���ʼ��������ĿĿ¼�ṹ����ִ�����ܲ���(200�û�������ÿ�����ɲ���10���û�������100��)
2.�鿴����
    ������->D:\auto\python\loperf\httpload.py -h
3.����������д
    ����������ĿĿ¼�µ�config.ini�ļ�������
        [Xdata]
        name = test.xlsx        --> ���ò���Excel������test.xlsx������ļ�������ĿĿ¼��data����
        sheet = test            --> ���ò���Excel��sheetҳ�棬��ִ�����������
        
        [Linux]
        ip = 192.168.109.247        -->���ò��Ե�Linux������IP
        user = root                 -->ssh���ӷ��������û���
        passwd = TWSM@test247       -->ssh���ӷ�����������
        port = 22                   -->ssh���ӷ������Ķ˿�
    
    ��Σ�д������
        ָ����sheetҳ���У�����title��ID	Name	PreCommand	Transmission	Head	Data	Verify	Scene
            ID���ܲ�������Ψһ��ţ��� PTC-1,ATP-1��
            Name���ܲ������������ƣ��� ��ѯ��ҵ ��
            PreCommand���ڳ�ʼ���������������ؼ��֣����в�������
                1.sethost("http://192.168.109.247") --> ÿ�� Scene ʹ��һ�Σ�����ó�����host
                2.setvar(l_num="1") --> excel��ʹ�� #l_num#�û�������
                3.setfilevar('d:/auto/buffer/t.txt')
����t.txt����ôa��b����ȡֵ1��2 ...��ѭ��:
a   b
1   2
2   3
            Transmission���ڷ�������һ���ؼ���:
                send("/portal/ClientApi/getPublishResultList","post","json") -->����ָ��post����json��ʽ
                send("/portal/ClientApi/getPublishResultList") -->Ĭ�� get����,����ʽ
            
            Head��Data ��дjson����
            Verify һ���ؼ���:
                contain('resultCode\":0') -->������ܲ��ԣ�ÿ��vuser�Ľ��������resultCode\":0����ɹ�
            Scene������ţ����һ�µģ�����ID�������򳡾�����Ų�һ�£�ʶ��Ϊƽ�г���
4. д��������������֮ǰ��
    ʹ������--> D:\auto\python\loperf\httpload.py 200 10 100 -t 1 ���в��ԣ�������ﵽԤ�ڣ����в�����

5.���Խ�������Ŀ·���µ�resultĿ¼��result.html���ɱ��档ע�⣺��resource�У����bokeh�����������ļ�(js��css)