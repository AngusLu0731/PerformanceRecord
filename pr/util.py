import requests
import json

from rest_framework import status
from rest_framework.response import Response
from pr.models import Order, Project, Employee, SupervisorInfo


def ValidToken(token):
    r = requests.post("https://soic.org.tw/v1/token/verify", headers=token)
    if r.status_code == 401:
        refresh = requests.post("https://soic.org.tw/v1/token/refresh", headers=token)
        refreshDict = json.loads(refresh.text)
        token = refreshDict["token"]
        r = requests.post("https://soic.org.tw/v1/token/verify", headers=token)
        rDict = json.loads(r)
        try:
            ret = rDict["username"]
            return ret
        except KeyError:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data="JWT認證錯誤")
    elif r.status_code == 400:
        return Response(status=status.HTTP_401_UNAUTHORIZED, data="JWT認證錯誤")
    elif r.status_code == 200:
        rDict = json.loads(r)
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
    r = requests.get("https://soic.org.tw/v1/department")
    if r.status_code == 200:
        rList = json.loads(r)
        orderList = list()
        for rDict in rList:
            try:
                name = rDict["name"]
                dept = rDict["department_code"]
                parent = rDict["parent"]
                if name == "船舶產業處" or name == "海洋產業處":
                    parent = "viceCEO"
                data = {"name": name, "dept": dept, "parent": parent}
                orderList.append(data)
                print(data)
            except KeyError:
                print("error: " + rDict)
        print(orderList)
        Order.objects.bulk_create(orderList)
    else:
        print("get order api錯誤")


def projectData():
    r = requests.get("https://soic.org.tw/v1/project")
    if r.status_code == 200:
        rList = json.loads(r)
        projectList = list()
        for rDict in rList:
            try:
                pname = rDict["name"]
                pid = rDict["prj_code"]
                for member in rDict["members"]:
                    if member["role"] == "admin":
                        pmid = member["user"]["username"]
                        break
                for member in rDict["members"]:
                    data = {"pname": pname, "pid": pid, "pmid": pmid,
                            "eid_id": member["user"]["username"]}
                    projectList.append(data)
                    print(data)
            except KeyError:
                print("error: " + rDict)
        print(projectList)
        Project.objects.bulk_create(projectList)
    else:
        print("get project api錯誤")


def userData():
    r = requests.get("https://soic.org.tw/v1/user")
    if r.status_code == 200:
        rList = json.loads(r)
        userList = list()
        for rDict in rList:
            try:
                isSupervisor = SupervisorInfo.objects.filter(eid=rDict["username"])
                if len(isSupervisor) > 0:
                    try:
                        o = Order.objects.get(id=rDict["department"])
                        data = {"id": rDict["username"], "name": rDict["name"],
                                "dept": rDict["department"], "needPR": False,
                                "doneNormalPR": False, "creditStatus": o.parent}
                    except Order.DoesNotExist:
                        print("抓order錯誤"+rDict)
                    data = {"id": rDict["username"], "name": rDict["name"],
                            "dept": rDict["department"], "needPR": False,
                            "doneNormalPR": False, "creditStatus": rDict["department"]}
                userList.append(data)
            except KeyError:
                print("error: " + rDict)
        print(userList)
        Employee.objects.bulk_create(userList)
    else:
        print("get user api錯誤")


def supervisorData():
    pass
