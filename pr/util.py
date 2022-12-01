import requests
import json
import openpyxl
import os

from rest_framework import status
from rest_framework.response import Response
from pr.models import Order, Project, Employee, SupervisorInfo, AttendanceRecord
from pr.serializers import EmployeeSerializer, ProjectSerializer


def ValidToken(token):
    r = requests.post("https://basic-service.sekixu.dev/api/v1/token/verify", data={"token": token["access"]})
    if r.status_code == 401:
        refresh = requests.post("https://soic.org.tw/v1/token/refresh", data=token["refresh"])
        refreshDict = json.loads(refresh.text).get("data")
        r = requests.post("https://basic-service.sekixu.dev/api/v1/token/verify", data={"token": refreshDict["access"]})
        rDict = json.loads(r.text).get("data").get("payload")
        try:
            ret = rDict["username"]
            return ret
        except KeyError:
            return Response(status=status.HTTP_200_OK, data="JWT認證錯誤")
    elif r.status_code == 400:
        return Response(status=status.HTTP_200_OK, data="JWT認證錯誤")
    elif r.status_code == 200:
        rDict = json.loads(r.text).get("data").get("payload")
        try:
            ret = rDict["username"]
            return ret
        except KeyError:
            return Response(status=status.HTTP_200_OK, data="JWT認證錯誤")
    else:
        return Response(status=status.HTTP_200_OK, data="JWT認證錯誤")


def msg(string):
    message = {"msg": string}
    return message


def orderData():
    print("-" * 20)
    print("順序資料匯入開始")
    print("-" * 20)
    r = requests.get("https://basic-service.sekixu.dev/api/v1/hr/department")
    if r.status_code == 200:
        rList = json.loads(r.text).get("data")
        orderList = list()
        for rDict in rList:
            try:
                name = rDict["name"]
                dept = rDict["department_code"]
                parent = rDict["parent_code"]
                if name == "船舶產業處" or name == "海洋產業處":
                    parent = "viceCEO"
                if parent is None:
                    parent = "done"
                data = {"name": name, "dept": dept, "parent": parent}
                orderList.append(data)
            except KeyError:
                print("error: ")
                print(rDict)
        orderList.append({"name": "副執行長室", "dept": "viceCEO", "parent": "S0A"})
        print(orderList)
        batch = [Order(name=row["name"], parent=row["parent"], id=row["dept"]) for row in orderList]
        Order.objects.bulk_create(batch)
        print("-" * 20)
        print("順序資料匯入結束")
        print("-" * 20)
        return True
    else:
        print("get order api錯誤")
        return False


def projectData():
    print("-" * 20)
    print("專案資料匯入開始")
    print("-" * 20)
    r = requests.get("https://basic-service.sekixu.dev/api/v1/project")
    if r.status_code == 200:
        rList = json.loads(r.text).get("data")
        projectList = list()
        pmid = ""
        for rDict in rList:
            try:
                pname = rDict["name"]
                pid = rDict["code"]
                for member in rDict["members"]:
                    if member["role"] == "admin":
                        pmid = member["username"]
                        break
                for member in rDict["members"]:
                    if member["role"] != "admin":
                        data = {"pname": pname, "pid": pid, "pmid": pmid,
                                "eid": member["username"], "done": False}
                        projectList.append(data)
                        serializer = ProjectSerializer(data=data)
                        if serializer.is_valid():
                            serializer.save()
                        else:
                            print(serializer.errors)
            except KeyError or Project.DoesNotExist:
                print("error: ")
                print(rDict)
        print("-" * 20)
        print("專案資料匯入結束")
        print("-" * 20)
        return True
    else:
        print("get project api錯誤")
        return False


def userData():
    print("-" * 20)
    print("員工資料匯入開始")
    print("-" * 20)
    r = requests.get("https://basic-service.sekixu.dev/api/v1/hr/user")
    if r.status_code == 200:
        rList = json.loads(r.text).get("data")
        userList = list()
        for i in rList:
            print(i)
        for rDict in rList:
            if rDict["status"] == "active":
                if rDict["is_leader"]:
                    try:
                        o = Order.objects.get(id=rDict["department_code"])
                        data = {"id": rDict["username"], "name": rDict["name"],
                                "dept": rDict["department_code"], "needPR": False,
                                "doneNormalPR": False, "creditStatus": o.parent}
                        if rDict["department_code"] in ("S0A","I0A"):
                            data["creditStatus"] = "CM"
                    except Order.DoesNotExist:
                        print("抓order錯誤" + rDict)
                else:
                    data = {"id": rDict["username"], "name": rDict["name"],
                            "dept": rDict["department_code"], "needPR": False,
                            "doneNormalPR": False, "creditStatus": rDict["department_code"]}
                userList.append(data)
        print(userList)
        batch = [Employee(id=row["id"], name=row["name"], dept_id=row["dept"],
                          needPR=row["needPR"], doneNormalPR=row["doneNormalPR"],
                          creditStatus=row["creditStatus"]) for row in userList]
        Employee.objects.bulk_create(batch)
        print("-" * 20)
        print("員工資料匯入結束")
        print("-" * 20)
        return True
    else:
        print(r.status_code)
        print("get user api錯誤")
        return False


def supervisorData():
    print("-" * 20)
    print("主管資料匯入開始")
    print("-" * 20)
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
        supervisorList.append({"eid": "107", "dept": "viceCEO"})
        print(supervisorList)
        batch = [SupervisorInfo(eid_id=row["eid"], dept_id=row["dept"]) for row in supervisorList]
        SupervisorInfo.objects.bulk_create(batch)
        print("-" * 20)
        print("主管資料匯入結束")
        print("-" * 20)
        return True
    else:
        print("get supervisor api錯誤")
        return False


def excel():
    print("-" * 20)
    print("判斷是否需要考績開始")
    print("-" * 20)
    pwd = os.path.dirname(__file__)
    wb = openpyxl.load_workbook(pwd + "/prsheet.xlsx")
    sheet = wb["list"]
    eidList = sheet["A"]
    prList = list()
    for v in eidList:
        try:
            if type(v.value) is str or type(v.value) is int:
                e = str(v.value)
                prList.append(e)
        except ValueError or TypeError:
            pass
    for e in prList:
        try:
            emp = Employee.objects.get(id=e)
            serializer = EmployeeSerializer(emp, data={"needPR": True}, partial=True)
            if serializer.is_valid():
                serializer.save()
            else:
                print("資料錯誤")
        except Employee.DoesNotExist:
            print("該員工不存在" + str(e))
    print("-" * 20)
    print("判斷是否需要考績結束")
    print("-" * 20)


def haveProject():
    print("-" * 20)
    print("判斷是否有專案開始")
    print("-" * 20)
    p = Project.objects.values("eid_id").distinct()
    for i in p:
        print(i["eid_id"])
        try:
            emp = Employee.objects.get(id=i["eid_id"])
            serializer = EmployeeSerializer(emp, data={"doneNormalPR": True}, partial=True)
            if serializer.is_valid():
                serializer.save()
            else:
                print("資料錯誤")
        except Employee.DoesNotExist:
            print("該員工不存在" + str(i["eid_id"]))
    print("-" * 20)
    print("判斷是否有專案結束")
    print("-" * 20)

def attendance():
    print("-" * 20)
    print("寫入考勤資料")
    print("-" * 20)
    pwd = os.path.dirname(__file__)
    wb = openpyxl.load_workbook(pwd + "/ar.xlsx")
    sheet = wb["list"]
    empList = []
    for k in range(1,230):
        tdList = sheet["A"+str(k) : "Z"+str(k)]
        cList = []
        for dList in tdList:
            for i in dList:
                if i.value is None:
                    cList.append("")
                else:
                    cList.append(i.value)
        data = {"eid_id": cList[0], "specialLeave": cList[2],
                "sickLeave": cList[3], "sickLeavePercentage": cList[4],
                "personalLeave": cList[5], "personalLeavePercentage": cList[6],
                "marriageLeave": cList[7], "bereavementLeave": cList[8],
                "maternityLeave": cList[9], "publicLeave": cList[10],
                "absenteeism": cList[11], "absenteeismPercentage": cList[12],
                "commendation": cList[13], "commendationPercentage": cList[14],
                "minorMerit": cList[15], "minorMeritPercentage": cList[16],
                "majorMerit": cList[17], "majorMeritPercentage": cList[18],
                "petition": cList[19], "petitionPercentage": cList[20],
                "minorDemerit": cList[21], "minorDemeritPercentage": cList[22],
                "majorDemerit": cList[23], "majorDemeritPercentage": cList[24],
                "attendanceScore": cList[25]}
        empList.append(data)
    batch = [AttendanceRecord(eid_id=row["eid_id"], specialLeave=row["specialLeave"],
                  sickLeave=row["sickLeave"], sickLeavePercentage=row["sickLeavePercentage"],
                  personalLeave=row["personalLeave"], personalLeavePercentage=row["personalLeavePercentage"],
                  marriageLeave=row["marriageLeave"], bereavementLeave=row["bereavementLeave"],
                  maternityLeave=row["maternityLeave"], publicLeave=row["publicLeave"],
                  absenteeism=row["absenteeism"], absenteeismPercentage=row["absenteeismPercentage"],
                  commendation=row["commendation"], commendationPercentage=row["commendationPercentage"],
                  minorMerit=row["minorMerit"], minorMeritPercentage=row["minorMeritPercentage"],
                  majorMerit=row["majorMerit"], majorMeritPercentage=row["majorMeritPercentage"],
                  petition=row["petition"], petitionPercentage=row["petitionPercentage"],
                  minorDemerit=row["minorDemerit"], minorDemeritPercentage=row["minorDemeritPercentage"],
                  majorDemerit=row["majorDemerit"], majorDemeritPercentage=row["majorDemeritPercentage"],
                  attendanceScore=row["attendanceScore"]) for row in empList]
    AttendanceRecord.objects.bulk_create(batch)
    print("-" * 20)
    print("寫入考勤資料結束")
    print("-" * 20)

