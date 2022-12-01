from pr.models import ProjectPR, NormalPR, AbleToCredit
from pr.serializers import ProjectPRSerializer, NormalPRSerializer, AbleToCreditSerializer


# function for schedule

def edit_status():
    pSet = ProjectPR.objects.all()
    nSet = NormalPR.objects.all()
    if len(pSet) > 0:
        for p in pSet:
            if p.done != "none":
                serializer = ProjectPRSerializer(p, data={"status": p.done, "done": "none"}, partial=True)
                if serializer.is_valid():
                    serializer.save()
                else:
                    print(serializer.errors)
    if len(nSet) > 0:
        for n in nSet:
            if n.done != "none":
                serializer = NormalPRSerializer(n, data={"status": n.done, "done": "none"}, partial=True)
                if serializer.is_valid():
                    serializer.save()
                else:
                    print(serializer.errors)
    print("修改結束")


def able_change(data):
    for deptName in data["data"]:
        try:
            a = AbleToCredit.objects.get(dept_id=deptName)
            if not a.able:
                serializer = AbleToCreditSerializer(a, data={"able": True})
            else:
                serializer = AbleToCreditSerializer(a, data={"able": False})
            if serializer.is_valid():
                serializer.save()
                print("修改結束")
            else:
                print(serializer.errors)
        except KeyError:
            print("Key Error")


def edit_status_retrieve(eid):
    try:
        p = ProjectPR.objects.get(eid=eid)
        if p.done != "none":
            serializer = ProjectPRSerializer(p, data={"status": p.done, "done": "none"}, partial=True)
            if serializer.is_valid():
                serializer.save()
            else:
                print(serializer.errors)
    except ProjectPR.DoesNotExist:
        print("無專案考核")
    try:
        n = NormalPR.objects.get(eid=eid)
        if n.done != "none":
            serializer = NormalPRSerializer(n, data={"status": n.done, "done": "none"}, partial=True)
            if serializer.is_valid():
                serializer.save()
            else:
                print(serializer.errors)
    except ProjectPR.DoesNotExist:
        print("無四大考核")
    print("修改結束")
