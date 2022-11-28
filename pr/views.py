from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


from pr.models import Employee, ProjectPR, NormalPR, Project, ProjectReviewRecord, NormalReviewRecord, SupervisorInfo, \
    Order, CreditRecord, CreditDistribution, Annotation, AttendanceRecord
from pr.serializers import EmployeeSerializer, ProjectPRSerializer, NormalPRSerializer, ProjectSerializer, \
    ProjectReviewRecordSerializer, NormalReviewRecordSerializer, ProjectNeedRecordSerializer, NormalNeedRecordSerializer, CreditRecordSerializer, CreditDistributionSerializer, AnnotationSerializer, AttendanceRecordSerializer, ProjectPRGetSerializer, CreditNeedRecordSerializer
from pr.util import msg, ValidToken


@swagger_auto_schema(
    method='GET',
    operation_summary="查看單一員工訊息",
    operation_description="GET /employee/",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        )
    ],
    responses={200: EmployeeSerializer()}
)
@api_view(['GET'])
def employee(request):
    # eid = ValidToken(request.headers.get("Authorization"))
    eid = 1
    if type(eid) == Response:
        return eid
    try:
        emp = Employee.objects.get(id=eid)
    except Employee.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND, data=msg("員工號不存在"))

    serializer = EmployeeSerializer(emp)
    return Response(status=status.HTTP_200_OK, data=serializer.data)


@swagger_auto_schema(
    method="POST",
    operation_summary="送出專案考核",
    operation_description="POST /projectPR/",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        )
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "belongProject": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="所屬專案ID"
            ),
            "workProject": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="工作項目"
            ),
            "workDirection": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="工作項目說明"
            ),
            "proportion": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="占比"
            ),
            "score": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="考勤分數"
            )

        }
    ),
    responses={201: ProjectPRSerializer()}
)
@swagger_auto_schema(
    method="GET",
    operation_summary="查看該員工所有專案考核",
    operation_description="GET /projectPR/",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        )
    ],
    responses={200: ProjectPRSerializer(many=True)}
)
@api_view(['POST', 'GET'])
def projectPR(request):
    # eid = ValidToken(request.headers.get("Authorization"))
    eid = 1
    if type(eid) == Response:
        return eid
    if request.method == 'POST':
        try:
            belongProject = request.data["belongProject"]
            emp = Employee.objects.get(id=eid)
            project = Project.objects.get(eid_id=eid, id=belongProject, done=False)
        except Employee.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data=msg("員工號不存在"))
        except Project.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=msg("無此專案或已送出考核"))
        if emp.needPR is False:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=msg("本年度不須考核"))
        workProject = request.data["workProject"]
        workDirection = request.data["workDirection"]
        proportion = request.data["proportion"]
        score = request.data["score"]
        data = {"eid": eid, "workProject": workProject, "workDirection": workDirection,
                "proportion": proportion, "belongProject": belongProject, "status": "pm", "score": score}
        serializer = ProjectPRSerializer(data=data)
        serializerPro = ProjectSerializer(project, data={"done": True}, partial=True)
        if serializer.is_valid() and serializerPro.is_valid():
            serializer.save()
            serializerPro.save()
            return Response(status=status.HTTP_201_CREATED, data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=msg(serializer.errors))

    if request.method == 'GET':
        project = ProjectPR.objects.filter(eid=eid)
        if len(project) == 0:
            return Response(status=status.HTTP_404_NOT_FOUND, data=msg("無專案考核或尚未完成專案考核"))
        serializer = ProjectPRGetSerializer(project, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


@swagger_auto_schema(
    method="GET",
    operation_summary="查看單一專案考核",
    operation_description="GET /projectPR/<int:pk>/",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        )
    ],
    responses={200: ProjectPRSerializer()}
)
@swagger_auto_schema(
    method="PATCH",
    operation_summary="修改已填寫過的一個專案考核",
    operation_description="PATCH /projectPR/<int:pk>/",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        )
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "workProject": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="工作項目"
            ),
            "workDirection": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="工作項目說明"
            ),
            "proportion": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="占比"
            ),
            "score": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="考勤分數"
            ),
        }),
    responses={200: ProjectPRSerializer()}
)
@api_view(['GET', 'PATCH'])
def projectPRRetrieve(request, pk):
    # eid = ValidToken(request.headers.get("Authorization"))
    eid = 1
    if type(eid) == Response:
        return eid
    try:
        project = ProjectPR.objects.get(id=pk)
    except ProjectPR.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND, data=msg("無此專案或尚未完成專案考核"))
    if request.method == 'GET':
        serializer = ProjectPRSerializer(project)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
    if request.method == 'PATCH':
        workProject = request.data["workProject"]
        workDirection = request.data["workDirection"]
        proportion = request.data["proportion"]
        score = request.data["score"]
        if project.eid_id != eid:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data=msg("非該考績所屬員工，無法修改"))
        serializer = ProjectPRSerializer(project,
                                         data={"workProject": workProject,
                                               "workDirection": workDirection,
                                               "proportion": proportion,
                                               "score": score},
                                         partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


@swagger_auto_schema(
    method="POST",
    operation_summary="送出一筆四大面向考核",
    operation_description="POST /normalPR/",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        )
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "workQuality": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="工作品質或客戶滿意度"
            ),
            "workAmount": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="工作業務量"
            ),
            "coordination": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="內部流程配合度"
            ),
            "learning": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="學習成長"
            ),
            "score": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="考勤分數"
            ),
        }
    ),
    responses={200: NormalPRSerializer()}
)
@swagger_auto_schema(
    method="GET",
    operation_summary="查看該員工所有四大面向考核",
    operation_description="GET /normalPR/",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        )],
    responses={200: NormalPRSerializer(many=True)}
)
@api_view(['POST', 'GET'])
def normalPR(request):
    # eid = ValidToken(request.headers.get("Authorization"))
    eid = 4
    if type(eid) == Response:
        return eid
    if request.method == 'POST':
        try:
            emp = Employee.objects.get(id=eid)
            nor = NormalPR.objects.filter(eid=eid)
        except Employee.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data=msg("員工號不存在"))
        if emp.doneNormalPR or len(nor) > 0:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=msg("已送出過四大面向考核"))
        elif emp.needPR is False:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=msg("本年度不須考核"))
        workQuality = request.data["workQuality"]
        workAmount = request.data["workAmount"]
        coordination = request.data["coordination"]
        learning = request.data["learning"]
        score = request.data["score"]
        isSupervisor = SupervisorInfo.objects.filter(eid=eid)
        if len(isSupervisor)>0:
            data = {"eid": eid, "workQuality": workQuality, "workAmount": workAmount,
                    "coordination": coordination, "learning": learning, "status": emp.dept.parent, "score": score}
        else:
            data = {"eid": eid, "workQuality": workQuality, "workAmount": workAmount,
                "coordination": coordination, "learning": learning, "status": emp.dept_id, "score": score}
        serializer = NormalPRSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            serializerEmp = EmployeeSerializer(emp, data={"doneNormalPR": True}, partial=True)
            if serializerEmp.is_valid():
                serializerEmp.save()
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=serializerEmp.errors)
            return Response(status=status.HTTP_201_CREATED, data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
    else:
        if request.method == 'GET':
            emp = NormalPR.objects.filter(eid=eid)
            if len(emp) == 0:
                return Response(status=status.HTTP_404_NOT_FOUND, data=msg("無四大面向考核"))
            serializer = NormalPRSerializer(emp, many=True)
            return Response(status=status.HTTP_200_OK, data=serializer.data)


@swagger_auto_schema(
    method="GET",
    operation_summary="查看一筆四大面向考核",
    operation_description="GET /normalPR/<int:pk>",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        )],
    responses={200: NormalPRSerializer()}
)
@swagger_auto_schema(
    method="PATCH",
    operation_summary="修改一筆四大面向考核",
    operation_description="PATCH /normalPR/<int:pk>",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        )],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "workQuality": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="工作品質或客戶滿意度"
            ),
            "workAmount": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="工作業務量"
            ),
            "coordination": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="內部流程配合度"
            ),
            "learning": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="學習成長"
            ),
            "score": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="考勤分數"
            ),
        }),
    responses=({200: NormalPRSerializer()})
)
@api_view(['GET', 'PATCH'])
def normalPRRetrieve(request, pk):
    # eid = ValidToken(request.headers.get("Authorization"))
    eid = 1
    if type(eid) == Response:
        return eid
    if pk == 1231253:
        return Response(status=status.HTTP_404_NOT_FOUND, data=msg("testing"))
    try:
        emp = NormalPR.objects.get(eid=eid)
    except NormalPR.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND, data=msg("尚未完成四大面向考核"))
    if request.method == 'GET':
        serializer = NormalPRSerializer(emp)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
    if request.method == 'PATCH':
        workQuality = request.data["workQuality"]
        workAmount = request.data["workAmount"]
        coordination = request.data["coordination"]
        learning = request.data["learning"]
        score = request.data["score"]
        if emp.eid_id != eid:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data=msg("非該考績所屬員工，無法修改"))
        serializer = NormalPRSerializer(emp,
                                        data={"workQuality": workQuality, "workAmount": workAmount,
                                              "coordination": coordination, "learning": learning, "score": score},
                                        partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=msg(serializer.data))


@swagger_auto_schema(
    method="GET",
    operation_summary="查看單一員工所有專案",
    operation_description="GET /project/",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        )],
    responses={200: ProjectSerializer(many=True)}
)
@api_view(['GET'])
def projectEmp(request):
    # eid = ValidToken(request.headers.get("Authorization"))
    eid = 1
    if type(eid) == Response:
        return eid
    projects = Project.objects.filter(eid=eid)
    if len(projects) == 0:
        return Response(status=status.HTTP_200_OK, data=msg("此員工無專案"))
    serializer = ProjectSerializer(projects, many=True)
    return Response(status=status.HTTP_200_OK, data=serializer.data)


@swagger_auto_schema(
    method="GET",
    operation_summary="查看單一員工未完成的需考核專案",
    operation_description="GET /projectPRNotDone/",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        )],
    responses={200: ProjectSerializer(many=True)}
)
@api_view(['GET'])
def projectNotDone(request):
    # eid = ValidToken(request.headers.get("Authorization"))
    eid = 3
    if type(eid) == Response:
        return eid
    projects = Project.objects.filter(eid=eid, done=False)
    if len(projects) == 0:
        return Response(status=status.HTTP_200_OK, data=msg("此員工無專案或專案皆已完成考核"))
    serializer = ProjectSerializer(projects, many=True)
    return Response(status=status.HTTP_200_OK, data=serializer.data)


@swagger_auto_schema(
    method="GET",
    operation_summary="查看該員工當前所有需要評分的專案",
    operation_description="GET /needRecord/",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        )],
    responses={200: "{projectPR: list(ProjectNeedRecordSerializer), normalPR: list(NormalNeedRecordSerializer)}"}
)
@api_view(['GET'])
def needRecord(request):
    # eid = ValidToken(request.headers.get("Authorization"))
    eid = 5
    if type(eid) == Response:
        return eid
    pids = Project.objects.filter(pmid=eid)
    projectNeedRecordList = []
    for p in pids:
        try:
            proPR = ProjectPR.objects.get(belongProject=p.id, status="pm")
        except ProjectPR.DoesNotExist:
            continue
        serializer = ProjectNeedRecordSerializer(proPR)
        projectNeedRecordList.append(serializer.data)
    try:
        isSupervisor = SupervisorInfo.objects.get(eid=eid)
    except SupervisorInfo.DoesNotExist:
        if len(projectNeedRecordList) > 0:
            return Response(status=status.HTTP_200_OK, data={"projectNeedRecord": projectNeedRecordList})
        else:
            return Response(status=status.HTTP_200_OK, data=msg("無可評分考績"))
    proPRList = ProjectPR.objects.filter(status=isSupervisor.dept_id)
    for proPR in proPRList:
        serializer = ProjectNeedRecordSerializer(proPR)
        projectNeedRecordList.append(serializer.data)
    norPRList = NormalPR.objects.filter(status=isSupervisor.dept_id)
    normalNeedRecordList = []
    for norPR in norPRList:
        serializer = NormalNeedRecordSerializer(norPR)
        normalNeedRecordList.append(serializer.data)
    if len(projectNeedRecordList) == 0 and len(normalNeedRecordList) == 0:
        return Response(status=status.HTTP_200_OK, data=msg("無可評分考績"))
    return Response(status=status.HTTP_200_OK,
                    data={"projectPR": projectNeedRecordList,
                          "normalPR": normalNeedRecordList})


@swagger_auto_schema(
    method="GET",
    operation_summary="查看我評過的評分(單一)(專案面向)",
    operation_description="GET /projectReviewRecord/<int:pk>/",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        )],
    responses={200: ProjectReviewRecordSerializer()}
)
@swagger_auto_schema(
    method="PATCH",
    operation_summary="修改我評過的評分(專案面向)",
    operation_description="PATCH /projectReviewRecord/<int:pk>/",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        )],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "point": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="評點",
            ),
            "content": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="評語"
            ),
            "proportion": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="占比"
            ),
        }),
    responses={200: ProjectReviewRecordSerializer()}
)
@api_view(['GET', 'PATCH'])
def projectReviewRecord(request, pk):
    # eid = ValidToken(request.headers.get("Authorization"))
    eid = 3
    if type(eid) == Response:
        return eid
    try:
        prRR = ProjectReviewRecord.objects.get(id=pk)
    except ProjectReviewRecord.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND, data=msg("無此評分紀錄"))
    if request.method == 'GET':
        serializer = ProjectReviewRecordSerializer(prRR)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
    if request.method == 'PATCH':
        point = request.data["point"]
        content = request.data["content"]
        proportion = request.data["proportion"]
        if prRR.reviewer != eid:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data=msg("非評分者無法修改"))
        serializer = ProjectReviewRecordSerializer(prRR,
                                                   data={"point": point, "content": content, "proportion": proportion},
                                                   partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=msg(serializer.errors))


@swagger_auto_schema(
    method="GET",
    operation_summary="查看我評過的所有評分(專案面向)",
    operation_description="GET /projectReviewRecord/",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        )],
    responses={200: ProjectReviewRecordSerializer(many=True)}
)
@swagger_auto_schema(
    method="POST",
    operation_summary="送出一筆評分(專案面向)",
    operation_description="POST /projectReviewRecord/",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        )],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "projectPRID": openapi.Schema(
                type=openapi.TYPE_NUMBER,
                description="ProjectPRID",
            ),
            "point": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="評點",
            ),
            "content": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="評語"
            ),
            "proportion": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="占比"
            ),
        }),
    responses={201: ProjectReviewRecordSerializer()}
)
@api_view(['GET', 'POST'])
def projectReviewRecordList(request):
    # eid = ValidToken(request.headers.get("Authorization"))
    eid = 4
    if type(eid) == Response:
        return eid
    if request.method == 'POST':
        projectPRID = request.data["projectPRID"]
        point = request.data["point"]
        content = request.data["content"]
        proportion = request.data["proportion"]
        data = {"content": content, "pid": projectPRID,
                "point": point, "reviewer": eid, "proportion": proportion}
        serializer = ProjectReviewRecordSerializer(data=data)
        try:
            pPR = ProjectPR.objects.get(id=projectPRID)
        except ProjectPR.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data=msg("無此考績可評分"))
        if pPR.status == "pm":
            p = Project.objects.filter(eid=pPR.eid_id, id=pPR.belongProject_id, pmid=eid)
            if len(p) == 0:
                return Response(status=status.HTTP_401_UNAUTHORIZED, data=msg("非此專案PM無法評分"))
            try:
                isSupervisor = SupervisorInfo.objects.get(eid=pPR.eid_id)
                serializerPPR = ProjectPRSerializer(pPR, data={"status": pPR.eid.dept.parent}, partial=True)
            except SupervisorInfo.DoesNotExist:
                serializerPPR = ProjectPRSerializer(pPR, data={"status": pPR.eid.dept_id}, partial=True)
            if serializer.is_valid() and serializerPPR.is_valid():
                serializer.save()
                serializerPPR.save()
                return Response(status=status.HTTP_201_CREATED, data=serializer.data)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=msg("資料錯誤"))
        else:
            isSuperVisor = SupervisorInfo.objects.filter(dept_id=pPR.status, eid=eid)
            try:
                o = Order.objects.get(id=pPR.status)
            except Order.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND, data=msg("此考績狀態有誤，請聯絡管理員"))
            if len(isSuperVisor) == 0:
                return Response(status=status.HTTP_401_UNAUTHORIZED, data=msg("非目前可評分主管"))
            chairman = ("A3", "viceCEO")
            if pPR.status == "A3" and emp.dept_id in chairman:
                serializerPPR = ProjectPRSerializer(pPR, data={"status": "A4"}, partial=True)
            else:
                serializerPPR = ProjectPRSerializer(pPR, data={"status": o.parent}, partial=True)
            if serializer.is_valid() and serializerPPR.is_valid():
                serializer.save()
                serializerPPR.save()
                return Response(status=status.HTTP_201_CREATED, data=serializer.data)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=msg(serializer.errors + serializerPPR.errors))
    if request.method == 'GET':
        pRR = ProjectReviewRecord.objects.filter(reviewer=eid)
        if len(pRR) == 0:
            return Response(status=status.HTTP_404_NOT_FOUND, data=msg("無已評分過考績"))
        serializer = ProjectReviewRecordSerializer(pRR, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


@swagger_auto_schema(
    method="GET",
    operation_summary="查看我評過的評分(單一)(四大面向)",
    operation_description="GET /normalReviewRecord/<int:pk>/",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        )],
    responses={200: NormalReviewRecordSerializer()}
)
@swagger_auto_schema(
    method="PATCH",
    operation_summary="修改我評過的評分(四大面向)",
    operation_description="PATCH /normalReviewRecord/<int:pk>/",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        )],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "point": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="評點",
            ),
            "content": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="評語"
            )
        }),
    responses={200: NormalReviewRecordSerializer()}
)
@api_view(['GET', 'PATCH'])
def normalReviewRecord(request, pk):
    # eid = ValidToken(request.headers.get("Authorization"))
    eid = 3
    if type(eid) == Response:
        return eid
    try:
        nRR = NormalReviewRecord.objects.get(id=pk)
    except NormalReviewRecord.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND, data=msg("無此評分紀錄"))
    if request.method == 'GET':
        serializer = NormalReviewRecordSerializer(nRR)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
    if request.method == 'PATCH':
        point = request.data["point"]
        content = request.data["content"]
        if nRR.reviewer != eid:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data=msg("非評分者無法修改"))
        serializer = NormalReviewRecordSerializer(nRR,
                                                  data={"point": point, "content": content},
                                                  partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


@swagger_auto_schema(
    method="GET",
    operation_summary="查看我評過的所有評分(四大面向)",
    operation_description="GET /normalReviewRecord/",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        )],
    responses={200: NormalReviewRecordSerializer(many=True)}
)
@swagger_auto_schema(
    method="POST",
    operation_summary="修改我評過的評分(四大面向)",
    operation_description="POST /normalReviewRecord/",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        )],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "normalPRID": openapi.Schema(
                type=openapi.TYPE_NUMBER,
                description="NormalPRID",
            ),
            "point": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="評點",
            ),
            "content": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="評語"
            )
        }),
    responses={201: NormalReviewRecordSerializer()}
)
@api_view(['GET', 'POST'])
def normalReviewRecordList(request):
    # eid = ValidToken(request.headers.get("Authorization"))
    eid = 4
    if type(eid) == Response:
        return eid
    try:
        emp = Employee.objects.get(id=eid)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND,data=msg("找不到員工"))
    if request.method == 'POST':
        normalPRID = request.data["normalPRID"]
        point = request.data["point"]
        content = request.data["content"]
        data = {"content": content, "pid": normalPRID,
                "point": point, "reviewer": eid, }
        serializer = NormalReviewRecordSerializer(data=data)
        try:
            nPR = NormalPR.objects.get(id=normalPRID)
        except NormalPR.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data=msg("無此考績可評分"))
        isSuperVisor = SupervisorInfo.objects.filter(dept_id=nPR.status, eid=eid)
        try:
            o = Order.objects.get(id=nPR.status)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data=msg("此考績狀態有誤，請聯絡管理員"))
        if len(isSuperVisor) == 0:
            return Response(status=status.HTTP_401_UNAUTHORIZED, data=msg("非目前可評分主管"))
        chairman = ("A3", "viceCEO")
        if nPR.status == "A3" and emp.dept_id in chairman:
            serializerNPR = NormalPRSerializer(nPR, data={"status": "A4"}, partial=True)
        else:
            serializerNPR = NormalPRSerializer(nPR, data={"status": o.parent}, partial=True)
        if serializer.is_valid() and serializerNPR.is_valid():
            serializer.save()
            serializerNPR.save()
            return Response(status=status.HTTP_201_CREATED, data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=msg(serializer.errors + serializerNPR.errors))
    if request.method == 'GET':
        nRR = NormalReviewRecord.objects.filter(reviewer=eid)
        if len(nRR) == 0:
            return Response(status=status.HTTP_404_NOT_FOUND, data=msg("無已評分過考績"))
        serializer = NormalReviewRecordSerializer(nRR, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


@swagger_auto_schema(
    method="GET",
    operation_summary="查看我評過的所有評分(所有面相)",
    operation_description="GET /allReviewRecord/",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        )],
    responses={200: "{projectReviewRecord: list(projectReviewRecord), "
                    "normalReviewRecord: list(normalReviewRecord)}"}
)
@api_view(['GET'])
def ReviewRecordList(request):
    # eid = ValidToken(request.headers.get("Authorization"))
    eid = 2
    if type(eid) == Response:
        return eid
    nRR = NormalReviewRecord.objects.filter(reviewer=eid)
    pRR = ProjectReviewRecord.objects.filter(reviewer=eid)
    if len(nRR) == 0 and len(pRR) == 0:
        return Response(status=status.HTTP_404_NOT_FOUND, data=msg("無已評分過考績"))
    serializerNRR = NormalReviewRecordSerializer(nRR, many=True)
    serializerPRR = ProjectReviewRecordSerializer(pRR, many=True)
    return Response(status=status.HTTP_200_OK,
                    data={"projectReviewRecord": serializerPRR.data,
                          "normalReviewRecord": serializerNRR.data})

@swagger_auto_schema(
    method="POST",
    operation_summary="送出一筆給點紀錄",
    operation_description="POST /creditRecord/",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        )],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "receiver": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="被給員工ID",
            ),
            "grade": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="評級"
            ),
            "credit": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="點數"
            ),
        }),
    responses={201: CreditRecordSerializer()}
)
@swagger_auto_schema(
    method="GET",
    operation_summary="查看給分紀錄",
    operation_description="GET /creditRecord/",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        )],
    responses={200: CreditNeedRecordSerializer()}
)
@api_view(['GET','POST'])
def creditRecord(request):
    # eid = ValidToken(request.headers.get("Authorization"))
    eid = 5
    if type(eid) == Response:
        return eid
    try:
        g = SupervisorInfo.objects.get(eid=eid)
    except SupervisorInfo.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST, data=msg("非主管"))
    if request.method == "POST":
        try:
            rec = Employee.objects.get(id=request.data["receiver"])
        except Employee.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST,data=msg("找不到接收者"))

        if rec.creditStatus != g.dept_id:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=msg("非當前給分者"))
        receiver = request.data["receiver"]
        grade = request.data["grade"]
        credit = request.data["credit"]
        data = {"giver": eid, "receiver": receiver, "grade": grade, "credit": credit}
        serializer = CreditRecordSerializer(data=data)
        try:
            o = Order.objects.get(id=rec.creditStatus)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=msg("找不到下一階段給分者"))
        chairman = ("A3", "viceCEO")
        if rec.creditStatus == "A3" and rec.dept_id in chairman:
            serializerEmp = EmployeeSerializer(rec, data={"creditStatus": "A4"}, partial=True)
        else:
            serializerEmp = EmployeeSerializer(rec, data={"creditStatus": o.parent}, partial=True)
        if serializer.is_valid() and serializerEmp.is_valid():
            serializer.save()
            serializerEmp.save()
            return Response(status=status.HTTP_201_CREATED, data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=msg("資料有誤"))
    if request.method == "GET":
        emp = Employee.objects.filter(creditStatus=g.dept_id)
        if len(emp) != 0:
            cre = CreditNeedRecordSerializer(emp,many=True)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND, data=msg("無資料"))
        return Response(status=status.HTTP_200_OK, data=cre.data)






@swagger_auto_schema(
    method="PATCH",
    operation_summary="修改一筆給點紀錄",
    operation_description="PATCH /creditRecord/<int:pk>",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        ),
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "grade": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="評級"
            ),
            "credit": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="點數"
            ),
        }),
    responses={200: CreditRecordSerializer()}
)
@api_view(['PATCH'])
def creditRecordRetrieve(request, pk):
    # eid = ValidToken(request.headers.get("Authorization"))
    eid = 2
    if type(eid) == Response:
        return eid
    try:
        c = CreditRecord.objects.get(id=pk, giver=eid)
    except CreditRecord.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST, data=msg("找不到此筆紀錄"))
    grade = request.data["grade"]
    credit = request.data["credit"]
    serializer = CreditRecordSerializer(c, {"grade": grade, "credit": credit}, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(status=status.HTTP_200_OK,data=serializer.data)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST,data=msg("更新失敗"))


@swagger_auto_schema(
    method="POST",
    operation_summary="送出一筆給點紀錄",
    operation_description="POST /creditDistribution",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        ),
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "creditDept": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="點數"
            ),
            "receiveDept": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="被給予部門"
            ),
        }),
    responses={200: CreditDistributionSerializer()}
)
@swagger_auto_schema(
    method="GET",
    operation_summary="查看我所有的給點紀錄",
    operation_description="GET /creditDistribution",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        ),
    ],
    responses={200: CreditDistributionSerializer()}
)
@api_view(['POST','GET'])
def creditDistribution(request):
    # eid = ValidToken(request.headers.get("Authorization"))
    eid = 3
    if type(eid) == Response:
        return eid
    try:
        isSupervisor = SupervisorInfo.objects.get(eid=eid)
    except SupervisorInfo.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND, data=msg("當前使用者非主管職"))
    if request.method == "POST":
        recDept = request.data["receiveDept"]
        try:
            o = Order.objects.get(id=recDept, parent=isSupervisor.dept_id)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST,data=msg("非可給點對象"))
        creDept = request.data["creditDept"]
        serializer = CreditDistributionSerializer(data={"receiveDept": recDept,
                                                        "creditDept": creDept,
                                                        "giveDept": isSupervisor.dept_id})
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK,data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST,data=msg("資料錯誤"))
    if request.method == "GET":
        creDistribution = CreditDistribution.objects.filter(giveDept=isSupervisor.dept_id)
        if len(creDistribution) == 0 :
            return Response(status=status.HTTP_404_NOT_FOUND,data=msg("當前使用者無給點紀錄"))
        serializer = CreditDistributionSerializer(creDistribution, many=True)
        return Response(status=status.HTTP_200_OK,data=serializer.data)


@swagger_auto_schema(
    method="PATCH",
    operation_summary="修改一筆給點紀錄",
    operation_description="PATCH /creditDistribution/<int:pk>",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        ),
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "creditDept": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="點數"
            ),
        }),
    responses={200: CreditDistributionSerializer()}
)
@swagger_auto_schema(
    method="GET",
    operation_summary="查看我被給予的點數",
    operation_description="GET /creditDistribution/<int:pk>",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        ),
    ],
    responses={200: CreditDistributionSerializer()}
)
@api_view(['PATCH','GET'])
def creditDistributionRetrieve(request, pk):
    # eid = ValidToken(request.headers.get("Authorization"))
    eid = 2
    if type(eid) == Response:
        return eid
    try:
        isSupervisor = SupervisorInfo.objects.get(eid=eid)
    except SupervisorInfo.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND, data=msg("當前使用者非主管職"))
    if request.method == "GET":
        try:
            creDistribution = CreditDistribution.objects.get(receiveDept=isSupervisor.dept_id)
        except CreditDistribution.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data=msg("當前使用者無被給點紀錄"))
        serializer = CreditDistributionSerializer(creDistribution)
        return Response(status=status.HTTP_200_OK,data=serializer.data)
    if request.method == "PATCH":
        try:
            creDistribution = CreditDistribution.objects.get(id=pk)
        except CreditDistribution.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data=msg("無此紀錄"))
        creDept = request.data["creditDept"]
        serializer = CreditDistributionSerializer(creDistribution,data={"creditDept":creDept},partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK,data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST,data=msg("資料錯誤"))


@swagger_auto_schema(
    method="POST",
    operation_summary="送出一筆備註",
    operation_description="POST /annotation",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        ),
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "content": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="內容"
            )
        }),
    responses={200: AnnotationSerializer()}
)
@swagger_auto_schema(
    method="GET",
    operation_summary="查看當前該看到的所有備註",
    operation_description="GET /annotation",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        ),
    ],
    responses={200: AnnotationSerializer()}
)
@api_view(["POST", "GET"])
def annotation(request):
    # eid = ValidToken(request.headers.get("Authorization"))
    eid = 3
    if type(eid) == Response:
        return eid
    try:
        isSupervisor = SupervisorInfo.objects.get(eid=eid)
    except SupervisorInfo.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND, data=msg("當前使用者非主管職"))
    if request.method == "POST":
        content = request.data["content"]
        viceCEOList = ("海洋產業處","船舶產業處") # test 待改成部門id
        if isSupervisor.dept_id in viceCEOList or isSupervisor.dept.parent in viceCEOList:
            serializer = AnnotationSerializer(data={"giveDept": isSupervisor.dept_id,
                                                "content": content,
                                                "status": "viceCEO"})
        else:
            serializer = AnnotationSerializer(data={"giveDept": isSupervisor.dept_id,
                                                    "content": content,
                                                    "status": "CEO"})
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK,data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST,data=msg("資料錯誤"))
    if request.method == "GET":
        if isSupervisor.dept_id == "viceCEO":
            anno = Annotation.objects.filter(status=isSupervisor.dept_id)
        else:
            anno = Annotation.objects.all()
        if len(anno) == 0:
            return Response(status=status.HTTP_404_NOT_FOUND, data=msg("無當前可查看備註"))
        serializer = AnnotationSerializer(anno, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


@swagger_auto_schema(
    method="PATCH",
    operation_summary="修改一筆備註",
    operation_description="PATCH /annotation/<int:pk>",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        ),
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "content": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="內容"
            )
        }),
    responses={200: AnnotationSerializer()}
)
@swagger_auto_schema(
    method="GET",
    operation_summary="查看我給出的備註",
    operation_description="GET /annotation/<int:pk>",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        ),
    ],
    responses={200: AnnotationSerializer()}
)
@api_view(["GET","PATCH"])
def annotationRetrieve(request, pk):
    # eid = ValidToken(request.headers.get("Authorization"))
    eid = 2
    if type(eid) == Response:
        return eid
    try:
        isSupervisor = SupervisorInfo.objects.get(eid=eid)
    except SupervisorInfo.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND, data=msg("當前使用者非主管職"))
    if request.method == "PATCH":
        try:
            anno = Annotation.objects.get(id=pk)
        except Annotation.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data=msg("找不到此筆資料"))
        content = request.data["content"]
        serializer = AnnotationSerializer(anno,data={"content": content},partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=msg("資料錯誤"))
    if request.method == "GET":
        try:
            anno = Annotation.objects.get(giveDept=isSupervisor.dept_id)
        except Annotation.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND,data=msg("尚未有備註"))
        serializer = AnnotationSerializer(anno)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


@swagger_auto_schema(
    method="GET",
    operation_summary="查看我的考勤紀錄",
    operation_description="GET /attendanceRecord",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            description='token key',
            type=openapi.TYPE_STRING
        ),
    ],
    responses={200: AttendanceRecordSerializer()}
)
@api_view(["GET"])
def attendanceRecord(request):
    # eid = ValidToken(request.headers.get("Authorization"))
    eid = 1
    if type(eid) == Response:
        return eid
    try:
        ar = AttendanceRecord.objects.get(eid=eid)
    except AttendanceRecord.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND, data=msg("無考勤紀錄"))
    serializer = AttendanceRecordSerializer(ar)
    return Response(status=status.HTTP_200_OK, data=serializer.data)

def isPM(request):
    # eid = ValidToken(request.headers.get("Authorization"))
    eid = 2
    if type(eid) == Response:
        return eid
    pm = Project.objects.filter(pmid=eid)
    if len(pm) == 0:
        return Response(status=status.HTTP_200_OK, data={"isPM": False})
    else:
        return Response(status=status.HTTP_200_OK, data={"isPM": True})


@api_view(["GET"])
def isGL(request):
    # eid = ValidToken(request.headers.get("Authorization"))
    eid = 2
    if type(eid) == Response:
        return eid
    try:
        emp = Employee.objects.get(id=eid)
    except:
        return Response(status=status.HTTP_200_OK, data={"isGL": False})
    try:
        o = Order.objects.get(id=emp.dept.parent)
        if o.parent == "viceCEO":
            return Response(status=status.HTTP_200_OK, data={"isGL": True})
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_200_OK, data={"isGL": False})
    return Response(status=status.HTTP_200_OK, data={"isGL": False})

@api_view(["GET"])
def isDL(request):
    # eid = ValidToken(request.headers.get("Authorization"))
    eid = 2
    if type(eid) == Response:
        return eid
    try:
        emp = Employee.objects.get(id=eid)
    except:
        return Response(status=status.HTTP_200_OK, data={"isDL": False})
    try:
        o = Order.objects.get(id=emp.dept_id)
        if o.parent == "viceCEO":
            return Response(status=status.HTTP_200_OK, data={"isDL": True})
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_200_OK, data={"isDL": False})
    return Response(status=status.HTTP_200_OK, data={"isDL": False})


@api_view(["GET"])
def isViceCEO(request):
    # eid = ValidToken(request.headers.get("Authorization"))
    eid = 2
    if type(eid) == Response:
        return eid
    try:
        viceCEO = SupervisorInfo.objects.get(eid=eid,dept="viceCEO")
        return Response(status=status.HTTP_200_OK, data={"isViceCEO": True})
    except SupervisorInfo.DoesNotExist:
        return Response(status=status.HTTP_200_OK, data={"isViceCEO": False})
    return Response(status=status.HTTP_200_OK, data={"isViceCEO": False})

@api_view(["GET"])
def isCEO(request):
    # eid = ValidToken(request.headers.get("Authorization"))
    eid = 2
    if type(eid) == Response:
        return eid
    try:
        ceo = SupervisorInfo.objects.get(eid=eid,dept="A3") #test 待改
        return Response(status=status.HTTP_200_OK, data={"isCEO": True})
    except SupervisorInfo.DoesNotExist:
        return Response(status=status.HTTP_200_OK, data={"isCEO": False})
    return Response(status=status.HTTP_200_OK, data={"isCEO": False})

@api_view(["GET"])
def isChairman(request):
    # eid = ValidToken(request.headers.get("Authorization"))
    eid = 2
    if type(eid) == Response:
        return eid
    try:
        chairman = SupervisorInfo.objects.get(eid=eid,dept="A4") #test 待改
        return Response(status=status.HTTP_200_OK, data={"isChairman": True})
    except SupervisorInfo.DoesNotExist:
        return Response(status=status.HTTP_200_OK, data={"isChairman": False})
    return Response(status=status.HTTP_200_OK, data={"isChairman": False})


def apiData(request):
    pass
