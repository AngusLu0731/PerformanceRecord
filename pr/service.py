from pr.models import ProjectPR, NormalPR
from pr.serializers import ProjectPRSerializer, NormalPRSerializer


# function for schedule

def editStatus():
    pSet = ProjectPR.objects.all()
    nSet = NormalPR.objects.all()
    for p in pSet:
        if p.done != "none":
            serializer = ProjectPRSerializer(p, data={"status": p.done, "done": "none"}, partial=True)
            if serializer.is_valid():
                serializer.save()
            else:
                print(serializer.errors)
    for n in nSet:
        if n.done != "none":
            serializer = NormalPRSerializer(n, data={"status": n.done, "done": "none"}, partial=True)
            if serializer.is_valid():
                serializer.save()
            else:
                print(serializer.errors)
    print("修改結束")
