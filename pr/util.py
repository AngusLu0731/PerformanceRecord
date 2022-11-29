import requests
import json

from rest_framework import status
from rest_framework.response import Response
from pr.models import Order, Project, Employee, SupervisorInfo


def ValidToken(token):
    r = requests.post("https://soic.org.tw/v1/token/verify", headers=token)
    if r.status_code == 401:
        refreshDict = json.loads(r.text).get("data")
        token = refreshDict["refresh"]
        refresh = requests.post("https://soic.org.tw/v1/token/refresh", headers=token)
        refreshDict = json.loads(refresh.text).get("data")
        token = refreshDict["access"]
        r = requests.post("https://soic.org.tw/v1/token/verify", headers=token)
        rDict = json.loads(r.text).get("data")
        try:
            ret = rDict["username"]
            return ret
        except KeyError:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data="JWT認證錯誤")
    elif r.status_code == 400:
        return Response(status=status.HTTP_401_UNAUTHORIZED, data="JWT認證錯誤")
    elif r.status_code == 200:
        rDict = json.loads(r.text).get("data")
        try:
            ret = rDict["username"]
            return ret
        except KeyError:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data="JWT認證錯誤")
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED, data="JWT認證錯誤")


def msg(string):
    message = {"msg": string}
    return message


def orderData():
    r = requests.get("https://basic-service.sekixu.dev/api/v1/hr/department")
    if r.status_code == 200:
        rList = json.loads(r.text).get("data")
        orderList = list()
        print(rList)
        for rDict in rList:
            try:
                name = rDict["name"]
                dept = rDict["department_code"]
                parent = rDict["parent_code"]
                if name == "船舶產業處" or name == "海洋產業處":
                    parent = "viceCEO"
                data = {"name": name, "dept": dept, "parent": parent}
                orderList.append(data)
            except KeyError:
                print("error: ")
                print(rDict)
        orderList.append({"name": "副執行長室", "dept": "viceCEO", "parent": "執行長室"})
        print(orderList)
        Order.objects.bulk_create(orderList)
    else:
        print("get order api錯誤")


def projectData():
    r = requests.get("https://basic-service.sekixu.dev/api/v1/project")
    if r.status_code == 200:
        rList = json.loads(r.text).get("data")
        print(rList)
        projectList = list()
        for rDict in rList:
            try:
                pname = rDict["name"]
                pid = rDict["code"]
                for member in rDict["members"]:
                    if member["role"] == "admin":
                        pmid = member["username"]
                        break
                for member in rDict["members"]:
                    data = {"pname": pname, "pid": pid, "pmid": pmid,
                            "eid_id": member["username"]}
                    projectList.append(data)
                    print(data)
            except KeyError:
                print("error: ")
                print(rDict)
        print(projectList)
        Project.objects.bulk_create(projectList)
    else:
        print("get project api錯誤")


def userData():
    r = requests.get("https://basic-service.sekixu.dev/api/v1/hr/user")
    if r.status_code == 200:
        rList = json.loads(r.text).get("data")
        print(rList)
        userList = list()
        for rDict in rList:
            try:
                isSupervisor = SupervisorInfo.objects.filter(eid=rDict["username"])
                if len(isSupervisor) > 0:
                    try:
                        o = Order.objects.get(id=rDict["department_code"])
                        data = {"id": rDict["username"], "name": rDict["name"],
                                "dept": rDict["department_code"], "needPR": False,
                                "doneNormalPR": False, "creditStatus": o.parent}
                    except Order.DoesNotExist:
                        print("抓order錯誤"+rDict)
                    data = {"id": rDict["username"], "name": rDict["name"],
                            "dept": rDict["department"], "needPR": False,
                            "doneNormalPR": False, "creditStatus": rDict["department"]}
                userList.append(data)
            except KeyError:
                print("error: ")
                print(rDict)
        print(userList)
        Employee.objects.bulk_create(userList)
    else:
        print("get user api錯誤")
        print(r.status_code)


def supervisorData():
    r = requests.get("https://basic-service.sekixu.dev/api/v1/hr/department")
    if r.status_code == 200:
        rList = json.loads(r.text).get("data")
        supervisorList = list()
        for rDict in rList:
            try:
                eid = rDict["leader_username"]
                dept = rDict["department_code"]
                data = {"eid": eid, "dept": dept}
                supervisorList.append(data)
            except KeyError:
                print("error: ")
                print(rDict)
        supervisorList.append({"eid": "副執行長id", "dept": "viceCEO"})
        print(supervisorList)
        SupervisorInfo.objects.bulk_create(supervisorList)
    else:
        print("get order api錯誤")

