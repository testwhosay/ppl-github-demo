# coding:utf-8
import os, requests,datetime
from xlrd import open_workbook
from xlutils.copy import copy
from execl_demo.common.excel import Excel
from execl_demo.report.run_cases import token

filename = os.path.join(os.path.dirname(os.getcwd()), "cases", "api_excel.xls")
host_data = Excel(filename, '配置文件').dict_data()   # table name


def send_requests(excel_data,s=requests.session()):
    '''封装requests请求'''
    host = host_data[0]['host']
    excel_data = excel_data
    url = excel_data["url"]
    method = excel_data["method"]
    r_type = excel_data['type']
    try:                      # 请求头
        headers = eval(excel_data["headers"])
        print(headers)
    except:
        headers = None
    print("*******正在执行用例：-----  ID: %s" % int(excel_data['ID']))
    print("请求方式：%s, 请求url:%s" % (method, host+url))
    try:                      # post请求body内容
        bodydata = eval(excel_data["body"].replace('$token', token))
    except:
        bodydata = excel_data["body"].replace('$token', token)
    if r_type == "json":
        try:
            body = bodydata
        except:print('json格式有误！！！')
        r = s.request(method=method,
                      url=host + url,
                      json=body,
                      headers=headers,)
    else:
        body = bodydata
        r = s.request(method=method,
                      url=host + url,
                      headers=headers,
                      data=body,
                      params=body)
    if method == "post":
        print("请求类型为：%s ,body参数为：%s" % (r_type, body))
    res = {}   # 接受返回数据

    print("响应信息为：%s" % r.content.decode("utf-8"))
    res['ID'] = int(excel_data['ID'])
    res["statuscode"] = str(r.status_code)          # 状态码转成str
    res["text"] = str(r.content.decode("utf-8"))
    res["times"] = str(r.elapsed.total_seconds())   # 接口请求时间转str

    if res["statuscode"] != "200":
        res["error"] = res["text"]
    else:
        res["error"] = ""
    res["msg"] = ""
    if excel_data["checkpoint"] in res["text"]:
        res["result"] = "pass"
        print("用例测试结果:  ID: %s---->%s" % (int(excel_data['ID']), res["result"]))
    else:
        res["result"] = "fail"
        res["error"] = res["text"]
    res['time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    return res


def wirte_result(res, report_path, tablename):
    '''
    1.传需要写入的res
    2.report_path:写入的路径
    3.tablename
    '''

    excel = copy(open_workbook(report_path,
                               formatting_info=True))   # 将xlrd的对象转化为xlwt的对象
    row_nub = res['ID']                                 # 返回结果的行数row_nub
    table = excel.get_sheet(tablename)                   # 获取要操作的sheet
    table.write(row_nub, 8, res['statuscode'])          # 写入返回状态码statuscode,第8列
    table.write(row_nub, 9, res['result'])              # 测试结果 pass 还是fail
    table.write(row_nub, 10, res['times'])              # 耗时
    table.write(row_nub, 11, res['error'])              # 状态码非200时的返回信息
    table.write(row_nub, 12, res['msg'])                # 抛异常
    table.write(row_nub, 13, res['time'])               # 抛异常
    excel.save(report_path)                              # 保存并覆盖文件


if __name__ == '__main__':
    excel_data = Excel(filename, '登录模块').dict_data()
    r = send_requests(excel_data[0])
