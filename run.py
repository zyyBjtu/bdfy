import base64
import time

import ddddocr
import urllib3
from urllib3.exceptions import InsecureRequestWarning

from common.common import *

urllib3.disable_warnings(InsecureRequestWarning)

state = 'c6e2bd90-a6da-4c5f-b95c-859ed3bb2a40'

test_url = 'https://openapi.linkingcloud.cn/app/newLogin/index.html?state=d793a331-4cd8-4981-9090-0dad5080c15'

# https://fwcbj.linkingcloud.cn/app/unattended/



def getVerificationCode():
    url = 'https://openapi.linkingcloud.cn/oauth2/VerificationCode?state=' + state
    response = requests.get(url, headers=get_base_headers(), verify=False)
    data = json.loads(response.content)
    key = data.get('imgStr')
    img_value = key.split(',')[1]
    try:
        imgdata = base64.b64decode(img_value)
        with open('img.png', 'wb') as fp:
            fp.write(imgdata)
    except Exception as e:
        print('异常：', e)

    return key


def readImg():
    ocr = ddddocr.DdddOcr()
    with open('img.png', 'rb') as f:
        img_bytes = f.read()
    res = ocr.classification(img_bytes)
    return res


def get_base_headers(token=None):
    base_headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/6.8.0(0x16080000) MacWechat/3.8.6(0x13080610) XWEB/1156 Flue',
        'content-type': 'application/json; charset=utf-8',
        'accept': '*/*',
        'accept-language': 'zh'
    }
    if token is not None:
        base_headers['authorization'] = 'Bearer %s' % token
    return base_headers


def get_data():
    with open('doctor_list.json', 'r') as file:
        data = json.load(file)

    return data


def get_doc_resource():
    url = 'https://fwcbj.linkingcloud.cn/apiv3/GuaHao/OrderDocResources'
    cookies = read_cookies()
    token = cookies.pop('token')
    header = get_base_headers(token)
    # req = {"deptCode": "0002_3_643", "dataSource": "", "extInfo": "\"\""}
    req = {"deptCode": "0003_28_973", "dataSource": "", "extInfo": "\"\""}
    rep = requests.post(url, headers=header, json=req, verify=False, cookies=cookies)
    doc_list = json.loads(rep.text).get('deptResourceDocNoSourceList')

    doc_name = get_doc_name()
    doc_detail = list(
        filter(lambda x: x.get('resourceMemo') != '无排班',
               list(map(flap_doc_list, doc_list))))
    for d in doc_detail:
        d['docName'] = doc_name.get(d.get('docCode')).get('docName')
        d['codeList'] = doc_name.get(d.get('docCode')).get('codeList')
        d[
            'url'] = "https://fwcbj.linkingcloud.cn/app/unattended/index.html#/outpatientService/guahao/doctor?dataSource=&docCode=%s&hospitalID=0003" % d.get(
            'docCode'),
    return doc_detail


def get_doc_name():
    url = 'https://fwcbj.linkingcloud.cn/apiv3/GuaHao/OrderDeptResources'
    cookies = read_cookies()
    token = cookies.pop('token')
    header = get_base_headers(token)
    req = {
        "dataSource": ""
    }
    rep = requests.post(url, headers=header, json=req, verify=False, cookies=cookies)
    hospital = json.loads(rep.text).get('deptResourceDocList')

    return {h.get("docCode"): {
        "codeList": get_doc_detail(h.get("docCode")),
        "docName": h.get("docName")} for h in hospital if h.get('deptCode') == '0003_28_973'}


def get_doc_detail(docCode):
    url = 'https://fwcbj.linkingcloud.cn/apiv3/GuaHao/OrderDocNoSources'
    cookies = read_cookies()
    token = cookies.pop('token')
    header = get_base_headers(token)
    req = {
        "docCode": docCode,
        "extInfo": "\"\"",
        "dataSource": ""
    }
    rep = requests.post(url, headers=header, json=req, verify=False, cookies=cookies)
    detail = json.loads(rep.text)
    resource_list = detail.get('docResourceResourceList')

    docDuty = detail.get("doctorInfo").get("docDuty")
    return [{
        "day": d.get("day"),
        "registLevel1": d.get("registLevel1"),
        "resourceMemo": d.get("resourceMemo"),
        "timeEnd": d.get("timeEnd"),
        "resourceID": d.get("resourceID"),
        "docDuty": docDuty
    } for d in resource_list]


def resource_to_int(str):
    try:
        return int(str.split(":")[1])
    except:
        return 0


def flap_doc_list(doc):
    return {
        "docCode": doc.get('docCode'),
        "day": doc.get('day'),
        "resourceMemo": doc.get('resourceMemo'),
        "isAvailable": doc.get('isAvailable'),
        "labelName": doc.get('labelName')
    }


def firstOk(docCode, day, docName, docDuty):
    cookies = read_cookies()
    token = cookies.pop('token')
    header = get_base_headers(token)

    url = 'https://fwcbj.linkingcloud.cn/app/unattended/'
    rep = requests.get(url, headers=header, verify=False, cookies=cookies)

    print(rep.text)

    url = 'https://fwcbj.linkingcloud.cn/public/DataFilterJs?time=%s' % (str(int(time.time() * 1000)))
    rep = requests.get(url, headers=header, verify=False, cookies=cookies)

    print(rep.text)

    url = 'https://fwcbj.linkingcloud.cn/Public/GetProfile'
    data = {
        "configList": [{"profileName": "FuWuChuang.Function.Show", "pageKay": [],
                        "funName": ["AppToastDuration", "customerTheme"]}],
        "customerID": "",
        "appToken": cookies.get("token")
    }
    rep = requests.post(url, headers=header, data=data, verify=False, cookies=cookies)

    print(rep.text)

    url = 'https://fwcbj.linkingcloud.cn/apiv3/cardv2/GetHospitalInfo'
    data = {
        "customerID": ""
    }
    rep = requests.post(url, headers=header, data=data, verify=False, cookies=cookies)

    print(rep.text)

    url = 'https://fwcbj.linkingcloud.cn/apiv3/Data/GetSysLanguage'
    rep = requests.post(url, headers=header, verify=False, cookies=cookies)

    print(rep.text)

    url = 'https://buriedpoint.linkingcloud.cn/bplog'
    rep = requests.options(url, verify=False, cookies=cookies)
    print(rep)

    url = 'https://fwcbj.linkingcloud.cn/Public/GetProfile'
    req = {
        "configList": "[{\"profileName\":\"FuWuChuang.Function.Show\",\"pageKay\":[],\"funName\":[\"customerTheme\",\"AppToastDuration\",\"isRarewords\"]}]",
        "customerID": "",
        "appToken": cookies.get('token')
    }
    rep = requests.post(url, headers=header, json=req, verify=False, cookies=cookies)

    print(rep.text)

    url = 'https://fwcbj.linkingcloud.cn/Public/GetProfile'
    req = {
        "configList": "[{\"profileName\":\"FuWuChuang.Function.Show\",\"pageKay\":[],\"funName\":[\"docIsShowNoResource.guahao\",\"resourceCondition.guahao\"]}]",
        "customerID": "",
        "appToken": cookies.get('token')
    }
    rep = requests.post(url, headers=header, json=req, verify=False, cookies=cookies)

    print(rep.text)

    url = 'https://fwcbj.linkingcloud.cn/Public/GetProfile'
    req = {
        "configList": "[{\"profileName\":\"FuWuChuang.Function.Show\",\"pageKay\":[],\"funName\":[\"guahaoDocDateCancel\",\"guahao.calendarShowDay\",\"doctorIsAvailable\",\"guahaoIsAvailableOpen.doctor\",\"guahaoIsAvailableOpen\",\"guahaoShowTimeHorizon\",\"guahao.confirm.dept\",\"guahao.doctorResourceOpen\",\"guahao.pageSize\"]},{\"profileName\":\"Function.Doctor\",\"pageKay\":[],\"funName\":[]}]",
        "customerID": "",
        "appToken": cookies.get('token')
    }
    rep = requests.post(url, headers=header, json=req, verify=False, cookies=cookies)

    print(rep.text)

    url = 'https://fwcbj.linkingcloud.cn/Public/GetProfile'
    req = {
        "profileName": "Function.GlobalMenu",
        "pageKey": "index",
        "appToken": cookies.get('token')
    }
    rep = requests.post(url, headers=header, json=req, verify=False, cookies=cookies)

    print(rep.text)

    url = 'https://buriedpoint.linkingcloud.cn/bplog'
    req = {
        "projectName": "unattended",
        "routerInfo": {
            "routerPath": "/app/unattended/#/outpatientService/guahao/doctor",
            "routerParams": "hospitalID=0003&dataSource=&docCode=" + docCode + "&date=" + get_current_time() + "&curDeptName=JUU1JUE2JTg3JUU0JUJBJUE3JUU3JUE3JTkxKCVFNSVBNCVBNyVFNSU4NSVCNCk%3D&quguang=",
            "prevRouterPath": "/app/unattended/#/"
        },
        "eventType": "view",
        "regulatoryInfo": {
            "category": "performance",
            "logType": "Info",
            "logInfo": "{\"curTime\":\"%s\",\"performance\":{\"redirectTime\":\"0.00\",\"dnsTime\":\"0.00\",\"ttfbTime\":\"315.00\",\"appcacheTime\":\"0.00\",\"unloadTime\":\"0.00\",\"tcpTime\":\"0.00\",\"reqTime\":\"1.00\",\"analysisTime\":\"1.00\",\"blankTime\":\"322.00\",\"domReadyTime\":\"495.00\",\"loadPageTime\":\"495.00\"},\"resourceList\":[],\"markUser\":\"h267C2CJ5Y1704018533704\",\"markUv\":\"WaA175hKzY1715215457685\",\"deviceInfo\":\"{\\\"deviceType\\\":\\\"PC\\\",\\\"OS\\\":\\\"Mac OS\\\",\\\"OSVersion\\\":\\\"10.15.7\\\",\\\"screenHeight\\\":982,\\\"screenWidth\\\":1512,\\\"language\\\":\\\"zh_CN\\\",\\\"netWork\\\":\\\"4g\\\",\\\"orientation\\\":\\\"竖屏\\\",\\\"browserInfo\\\":\\\"Wechat（版本: 6.8.0&nbsp;&nbsp;内核: WebKit）\\\",\\\"fingerprint\\\":\\\"54128beb\\\",\\\"userAgent\\\":\\\"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/6.8.0(0x16080000) MacWechat/3.8.7(0x13080710) XWEB/1191 Flue\\\"}\"}" % get_current_time()
        }
    }
    rep = requests.post(url, headers=header, json=req, verify=False, cookies=cookies)
    print(rep)

    url = 'https://fwcbj.linkingcloud.cn/apiv3/GuaHao/OrderDocNoSources'
    req = {
        "docCode": docCode,
        "day": day,
        "extInfo": "\"\"",
        "dataSource": ""
    }
    rep = requests.post(url, headers=header, json=req, verify=False, cookies=cookies)

    print(rep.text)

    url = 'https://fwcbj.linkingcloud.cn/apiv3/GuaHao/CollectAndHistory'
    req = {
        "dataSource": "",
        "dataDiv": "guahao"
    }
    rep = requests.post(url, headers=header, json=req, verify=False, cookies=cookies)

    print(rep.text)

    url = 'https://buriedpoint.linkingcloud.cn/bplog'
    req = {
        "projectName": "unattended",
        "routerInfo": {
            "routerPath": "/app/unattended/#/",
            "routerParams": "",
            "prevRouterPath": "/app/unattended/#/outpatientService/guahao/doctor"
        },
        "eventType": "buryingpoint",
        "regulatoryInfo": {
            "category": "performance",
            "logType": "Info",
            "logInfo": "{\"curTime\":\"%s\",\"performance\":{\"redirectTime\":\"0.00\",\"dnsTime\":\"0.00\",\"ttfbTime\":\"315.00\",\"appcacheTime\":\"0.00\",\"unloadTime\":\"0.00\",\"tcpTime\":\"0.00\",\"reqTime\":\"1.00\",\"analysisTime\":\"1.00\",\"blankTime\":\"322.00\",\"domReadyTime\":\"495.00\",\"loadPageTime\":\"495.00\"},\"resourceList\":[],\"markUser\":\"h267C2CJ5Y1704018533704\",\"markUv\":\"WaA175hKzY1715215457685\",\"deviceInfo\":\"{\\\"deviceType\\\":\\\"PC\\\",\\\"OS\\\":\\\"Mac OS\\\",\\\"OSVersion\\\":\\\"10.15.7\\\",\\\"screenHeight\\\":982,\\\"screenWidth\\\":1512,\\\"language\\\":\\\"zh_CN\\\",\\\"netWork\\\":\\\"4g\\\",\\\"orientation\\\":\\\"竖屏\\\",\\\"browserInfo\\\":\\\"Wechat（版本: 6.8.0&nbsp;&nbsp;内核: WebKit）\\\",\\\"fingerprint\\\":\\\"54128beb\\\",\\\"userAgent\\\":\\\"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/6.8.0(0x16080000) MacWechat/3.8.7(0x13080710) XWEB/1191 Flue\\\"}\"}" % get_current_time()
        },
        "name": "yuyue",
        "key": "",
        "extendInfo": {
            "url": "https://fwcbj.linkingcloud.cn/app/unattended/#/outpatientService/guahao/doctor?hospitalID=0003&dataSource=&docCode=" + docCode + "&date=" + day + "&curDeptName=JUU1JUE2JTg3JUU0JUJBJUE3JUU3JUE3JTkxKCVFNSVBNCVBNyVFNSU4NSVCNCk%3D&quguang=",
            "docName": docName,
            "doctorTitle": docDuty,
            "docCode": docCode,
            "doctorAvatar": ""
        }
    }
    rep = requests.post(url, headers=header, json=req, verify=False, cookies=cookies)
    print(rep)

    url = 'https://fwcbj.linkingcloud.cn/Public/GetProfile'
    req = {
        "configList": "[{\"profileName\":\"FuWuChuang.Function.Show\",\"pageKay\":[],\"funName\":[\"doctor.calendar.slide\"]}]",
        "customerID": "",
        "appToken": cookies.get('token')
    }
    rep = requests.post(url, headers=header, json=req, verify=False, cookies=cookies)

    print(rep.text)

    url = 'https://fwcbj.linkingcloud.cn/Data/GetUfontInfo'
    req = {
        "appToken": cookies.get('token')
    }
    rep = requests.post(url, headers=header, json=req, verify=False, cookies=cookies)

    print(rep.text)

    url = 'https://buriedpoint.linkingcloud.cn/bplog'
    req = {
        "projectName": "unattended",
        "routerInfo": {
            "routerPath": "/app/unattended/#/outpatientService/guahao/confirm",
            "routerParams": "hospitalID=0003&dataSource=&quguang=&isLimit=",
            "prevRouterPath": "/app/unattended/#/outpatientService/guahao/doctor"
        },
        "regulatoryInfo": {
            "category": "performance",
            "logType": "Info",
            "logInfo": "{\"curTime\":\"%s\",\"performance\":{\"redirectTime\":\"0.00\",\"dnsTime\":\"0.00\",\"ttfbTime\":\"315.00\",\"appcacheTime\":\"0.00\",\"unloadTime\":\"0.00\",\"tcpTime\":\"0.00\",\"reqTime\":\"1.00\",\"analysisTime\":\"1.00\",\"blankTime\":\"322.00\",\"domReadyTime\":\"495.00\",\"loadPageTime\":\"495.00\"},\"resourceList\":[],\"markUser\":\"h267C2CJ5Y1704018533704\",\"markUv\":\"WaA175hKzY1715215457685\",\"deviceInfo\":\"{\\\"deviceType\\\":\\\"PC\\\",\\\"OS\\\":\\\"Mac OS\\\",\\\"OSVersion\\\":\\\"10.15.7\\\",\\\"screenHeight\\\":982,\\\"screenWidth\\\":1512,\\\"language\\\":\\\"zh_CN\\\",\\\"netWork\\\":\\\"4g\\\",\\\"orientation\\\":\\\"竖屏\\\",\\\"browserInfo\\\":\\\"Wechat（版本: 6.8.0&nbsp;&nbsp;内核: WebKit）\\\",\\\"fingerprint\\\":\\\"54128beb\\\",\\\"userAgent\\\":\\\"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/6.8.0(0x16080000) MacWechat/3.8.7(0x13080710) XWEB/1191 Flue\\\"}\"}" % get_current_time()
        },
        "extendInfo": {
            "uniEventType": "navigateTo"
        }
    }
    rep = requests.post(url, headers=header, json=req, verify=False, cookies=cookies)
    print(rep)


def secondOk(resourceID, deptCode):
    url = 'https://fwcbj.linkingcloud.cn/public/GetTip'
    cookies = read_cookies()
    token = cookies.pop('token')
    header = get_base_headers(token)
    req = {
        "tipCode": "[\"tip001\"]",
        "appToken": cookies.get('token')
    }
    rep = requests.post(url, headers=header, json=req, verify=False, cookies=cookies)

    print(rep.text)

    url = 'https://fwcbj.linkingcloud.cn/Public/GetProfile'
    req = {
        "configList": "[{\"profileName\":\"FuWuChuang.Function.Show\",\"pageKey\":[],\"funName\":[\"MedicalPay.CertificationValid\",\"yuyueguahao.position\",\"newYuYuePay\",\"payWayOther\",\"guahao.confirm.dept\",\"isEnergy@alipayMini\",\"payTypeCheck\"]},{\"profileName\":\"Function.GuaHao\",\"pageKey\":[],\"funName\":[\"guahaoConfirmFieldList\",\"vercodeType\",\"vercodeShowType\"]},{\"profileName\":\"FieldShow\",\"pageKey\":[],\"funName\":[\"guahaoConfirm\"]}]",
        "customerID": "",
        "appToken": cookies.get('token')}
    rep = requests.post(url, headers=header, json=req, verify=False, cookies=cookies)
    print(rep.text)

    url = 'https://fwcbj.linkingcloud.cn/Public/GetJsCode'
    req = {
        "pageUrl": "https%3A%2F%2Ffwcbj.linkingcloud.cn%2Fapp%2Funattended%2F",
        "appToken": cookies.get('token')
    }
    rep = requests.post(url, headers=header, json=req, verify=False, cookies=cookies)
    print(rep.text)

    url = 'https://fwcbj.linkingcloud.cn/apiv3/Card/GetDefaultCard'
    req = {
        "dataSource": "guahao",
        "pageKey": "unattended/outpatientService/guahao/confirm"
    }
    rep = requests.post(url, headers=header, json=req, verify=False, cookies=cookies)
    print(rep.text)

    url = 'https://fwcbj.linkingcloud.cn/apiv3/card/GetBindLst'
    req = {"dataSource": "guahao", "pageKey": "unattended/outpatientService/guahao/confirm"}
    rep = requests.post(url, headers=header, json=req, verify=False, cookies=cookies)
    print(rep.text)

    url = 'https://fwcbj.linkingcloud.cn/apiv3/Data/GetMedicalType'
    req = {
        "hospitalUserID": "xxxxxxx",
        "dataDiv": "大病医保类型查询",
        "dataSource": "guahao",
        "token": "",
        "extInfo": "{\"resourceID\":\"%s\"}" % resourceID
    }
    rep = requests.post(url, headers=header, json=req, verify=False, cookies=cookies)
    print(rep.text)

    url = 'https://fwcbj.linkingcloud.cn/apiv3/Data/CommonInterfase'
    req = {
        "extInfo": "{\"hospitalUserID\":\"xxxxxx\"}",
        "dataSource": "大病医保查询"
    }
    rep = requests.post(url, headers=header, json=req, verify=False, cookies=cookies)
    print(rep.text)

    url = 'https://fwcbj.linkingcloud.cn/apiv3/Data/GetMedicalType'
    req = {
        "feeType": "1",
        "extInfo": "{\"dataSource\":\"guahao\",\"resourceID\":\"%s\","
                   "\"hospitalUserID\":\"xxxxxxx\",\"deptCode\":\"%s\"}" % (
                       resourceID, deptCode),
        "appToken": cookies.get('token')
    }
    rep = requests.post(url, headers=header, json=req, verify=False, cookies=cookies)
    print(rep.text)

    url = 'https://fwcbj.linkingcloud.cn/Public/GetProfile'
    req = {
        "profileName": "LumbarPeakMessageConfig",
        "pageKey": "",
        "appToken": cookies.get('token')

    }
    rep = requests.post(url, headers=header, json=req, verify=False, cookies=cookies)
    print(rep.text)

    url = 'https://fwcbj.linkingcloud.cn/apiv3/Data/CommonInterfase'
    req = {
        "extInfo": "{\"resourceID\":\"%s\",\"deptCode\":\"%s\"}" % (resourceID, deptCode),
        "dataSource": "当日挂号二次确认"
    }
    rep = requests.post(url, headers=header, json=req, verify=False, cookies=cookies)
    print(rep.text)

    url = 'https://fwcbj.linkingcloud.cn/public/GetTip'
    cookies = read_cookies()
    token = cookies.pop('token')
    header = get_base_headers(token)
    req = {
        "tipCode": "[\"tip001.002\"]",
        "appToken": cookies.get('token')
    }
    rep = requests.post(url, headers=header, json=req, verify=False, cookies=cookies)

    print(rep.text)

    url = 'https://fwcbj.linkingcloud.cn/public/GetTip'
    cookies = read_cookies()
    token = cookies.pop('token')
    header = get_base_headers(token)
    req = {
        "tipCode": "[\"tipfee\"]",
        "appToken": cookies.get('token')
    }
    rep = requests.post(url, headers=header, json=req, verify=False, cookies=cookies)

    print(rep.text)


def read_cookies():
    cookies = {}
    with open('cookies.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            str = line.split('	')
            key = str[0]
            value = str[1]
            cookies[key] = value

    return cookies


def filter_doc(doc):
    doc.get('resourceMemo')


def get_reports(begin_date=get_current_date(), end_date=get_current_date()):
    url = 'https://fwcbj.linkingcloud.cn/apiv3/Report/GetReportList'
    req = {
        "dataSource": "",
        "hospitalUserID": "xxxxxx",
        "cardNo": "xxxxxxx",
        "reportType": "",
        "pageNo": 1,
        "pageSize": 10,
        "keyword": "",
        "extInfo": "",
        "beginDate": begin_date,
        "endDate": end_date,
        "version": "4.0",
        "idCard": ""
    }
    cookies = read_cookies()
    token = cookies.pop('token')
    header = get_base_headers(token)
    rep = requests.post(url, headers=header, json=req, verify=False, cookies=cookies)
    data = json.loads(rep.text).get('reportsListv')
    if len(data) == 0:
        print('结果未出')
    for d in data:
        detail = d.get('reportDetail')
        title = detail.get('reportContent')
        time = detail.get('reportDateTime')
        print({
            'title': title,
            'time': time
        })


def send_message():
    doc_list = get_doc_resource()
    for doc in doc_list:
        if int(doc['isAvailable']) > 0:
            # send_dingtalk_message(doc)
            print('\n'.join(format_message(doc)))


def format_message(doc):
    msg = []
    name = doc.get('docName')
    day = doc.get('day')
    codeList = doc.get('codeList')
    for code in codeList:
        time = code.get('timeEnd')
        type = code.get('registLevel1')
        if code.get('day') == '2024-03-13' or type.startswith('特需'):
            continue
        resourceMemo = code.get('resourceMemo')

        res = str.format("{} ===> 姓名: {}, 日期: {}, 时间: {}, 类型: {}, 余号: {}", get_current_time(), name, day,
                         time, type, resourceMemo)
        msg.append(res)
    return msg


def generator_doc_list_json():
    doc_list = []
    hospitalUserID = "xxxxxx"
    deptCode = "0003_28_973"
    deptName = "产科门诊(大兴)"
    hospitalName = "北京大学第一医院(大兴院区)"
    docPhotoPath = ""
    extInfo = "{\"continueSubmit\":true}",
    feeType = "0"
    latLongitude = ""
    itemCode = ""
    isMedicalInsurance = ""
    docker_list = get_doc_resource()
    print(docker_list)
    for doc in docker_list:
        print(doc)
        url = doc.get("url")
        docName = doc.get("docName")
        docCode = doc.get("docCode")
        for d in doc.get('codeList'):
            docDuty = d.get('docDuty')
            resourceID = d.get('resourceID')
            timeEnd = d.get('timeEnd')
            day = d.get('day')
            doc_list.append({
                "hospitalUserID": hospitalUserID,
                "resourceID": resourceID,
                "registDate": "%s %s" % (day, timeEnd),
                "url": str(url),
                "docCode": docCode,
                "docName": docName,
                "docDuty": docDuty,
                "deptCode": deptCode,
                "deptName": deptName,
                "docPhotoPath": docPhotoPath,
                "extInfo": str(extInfo),
                "feeType": feeType,
                "latLongitude": latLongitude,
                "itemCode": itemCode,
                "isMedicalInsurance": isMedicalInsurance,
                "hospitalName": hospitalName
            })
    return doc_list


def write_to_file():
    doc_list = generator_doc_list_json()
    json_str = json.dumps(doc_list, ensure_ascii=False)
    newstr = json_str.replace("('", "").replace("',)", "")
    with open('docList.json', 'w') as f:
        f.write(newstr)
        f.close()


def read_doc_list():
    with open('docList.json', 'r') as f:
        data = json.loads(f.read())
    d = list(filter(lambda x: str(x.get('registDate')).startswith('2024-05-13'), data))
    print(d)

