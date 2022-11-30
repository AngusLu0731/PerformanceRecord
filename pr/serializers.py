from rest_framework import serializers
from pr.models import Employee, ProjectPR, NormalPR, Project, Order, ProjectReviewRecord, NormalReviewRecord, \
    SupervisorInfo, CreditRecord, CreditDistribution, Annotation, AttendanceRecord
from django.core.exceptions import ObjectDoesNotExist


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ("id", "name", "dept", "needPR", "doneNormalPR", "creditStatus")


class ProjectPRSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPR
        fields = ("id", "eid", "belongProject", "workProject",
                  "workDirection", "proportion", "status", "score",
                  "done")


class NormalPRSerializer(serializers.ModelSerializer):
    class Meta:
        model = NormalPR
        fields = ("id", "eid", "workQuality", "workAmount",
                  "coordination", "learning", "status", "score", "done")


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("id", "eid", "done", "pname", "pid")


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("name", "id", "parent")


class ProjectReviewRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectReviewRecord
        fields = ("pid", "reviewer", "point", "content", "proportion", "id")


class NormalReviewRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = NormalReviewRecord
        fields = ("pid", "reviewer", "point", "content")


class SupervisorInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupervisorInfo
        fields = ("dept", "pid")


class CreditRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditRecord
        fields = ("giver", "receiver", "grade", "credit", "id")


class CreditDistributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditDistribution
        fields = ("giveDept", "receiveDept", "creditDept", "id")


class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotation
        fields = ("giveDept", "content", "status", "id")


class AnnotationGetSerializer(serializers.ModelSerializer):
    deptName = serializers.SerializerMethodField()
    supervisorName = serializers.SerializerMethodField()

    class Meta:
        model = Annotation
        fields = ("giveDept", "content", "status", "id", "deptName", "supervisorName")

    def get_deptName(self, obj):
        return obj.giveDept.name

    def get_supervisorName(self, obj):
        try:
            s = SupervisorInfo.objects.get(dept=obj.giveDept)
            return s.eid.name
        except ObjectDoesNotExist:
            return ""


class AttendanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = "__all__"


class CreditNeedRecordSerializer(serializers.ModelSerializer):
    deptName = serializers.SerializerMethodField()
    projectScore = serializers.SerializerMethodField()
    normalScore = serializers.SerializerMethodField()
    gl = serializers.SerializerMethodField()
    dl = serializers.SerializerMethodField()
    viceCEO = serializers.SerializerMethodField()
    ceo = serializers.SerializerMethodField()
    chairman = serializers.SerializerMethodField()
    isDL = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = (
            "id", "name", "deptName", "projectScore", "normalScore", "gl", "dl", "viceCEO", "ceo", "chairman", "isDL")

    def get_deptName(self, obj):
        return obj.dept.name

    def get_projectScore(self, obj):
        ceo = SupervisorInfo.objects.get(dept__id="S0A")
        prSet = ProjectPR.objects.filter(eid=obj.id)
        if len(prSet) > 0:
            pr = prSet[0]
            try:
                ceoPoint = ProjectReviewRecord.objects.get(reviewer=ceo.eid_id, pid=pr.id)
                return ceoPoint.point
            except ObjectDoesNotExist:
                return ""
        return ""

    def get_normalScore(self, obj):
        ceo = SupervisorInfo.objects.get(dept_id="S0A")
        prSet = ProjectPR.objects.filter(eid=obj.id)
        if len(prSet) > 0:
            pr = prSet[0]
            try:
                ceoPoint = NormalReviewRecord.objects.get(reviewer=ceo.eid_id, pid=pr.id)
                return ceoPoint.point
            except ObjectDoesNotExist:
                return ""
        return ""

    def get_gl(self, obj):
        data = {"credit": "", "id": ""}
        try:
            o = Order.objects.get(id=obj.dept.parent)
            AOX = ("A0S", "A0P", "A0M")
            if o.parent == "viceCEO" or obj.eid.dept_id in AOX:
                gl = SupervisorInfo.objects.get(dept=obj.dept)
                data = creditFind(gl.eid_id, obj.id, data)
        except ObjectDoesNotExist:
            pass
        return data

    def get_dl(self, obj):
        data = {"credit": "", "id": ""}
        d = ("S0X", "M0A", "Q0A", "O0X", "B0A", "A0X", "I0C")
        if obj.dept.parent in d:
            try:
                dl = SupervisorInfo.objects.get(dept=obj.dept.parent)
                data = creditFind(dl.eid_id, obj.id, data)
            except ObjectDoesNotExist:
                pass
        if obj.dept_id in d:
            try:
                dl = SupervisorInfo.objects.get(dept=obj.dept.parent)
                data = creditFind(dl.eid_id, obj.id, data)
            except ObjectDoesNotExist or KeyError:
                pass
        return data

    def get_viceCEO(self, obj):
        data = {"credit": "", "id": ""}
        viceCEO = SupervisorInfo.objects.get(dept_id="viceCEO")
        data = creditFind(viceCEO.eid_id, obj.id, data)
        return data

    def get_ceo(self, obj):
        data = {"credit": "", "id": ""}
        ceo = SupervisorInfo.objects.get(dept_id="S0A")
        data = creditFind(ceo.eid_id, obj.id, data)
        return data

    def get_chairman(self, obj):
        data = {"credit": "", "id": ""}
        chairman = SupervisorInfo.objects.get(dept_id="CM")
        data = creditFind(chairman.eid_id, obj.id, data)
        return data

    def get_isDL(self, obj):
        try:
            isSupervisor = SupervisorInfo.objects.get(id=obj.id)
            o = Order.objects.get(id=isSupervisor.dept_id)
            if o.parent == "viceCEO":
                return True
        except ObjectDoesNotExist:
            return False
        return False


class ProjectPRGetSerializer(serializers.ModelSerializer):
    pName = serializers.SerializerMethodField()

    class Meta:
        model = ProjectPR
        fields = ("id", "eid", "belongProject", "workProject", "done",
                  "workDirection", "proportion", "status", "score",
                  "pName")

    def get_pName(self, obj):
        return obj.belongProject.pname


class ProjectNeedRecordSerializer(serializers.ModelSerializer):
    eName = serializers.SerializerMethodField()
    dept = serializers.SerializerMethodField()
    deptName = serializers.SerializerMethodField()
    pName = serializers.SerializerMethodField()
    pm = serializers.SerializerMethodField()
    gl = serializers.SerializerMethodField()
    dl = serializers.SerializerMethodField()
    viceCEO = serializers.SerializerMethodField()
    ceo = serializers.SerializerMethodField()
    chairman = serializers.SerializerMethodField()

    class Meta:
        model = ProjectPR
        fields = ("id", "eid", "belongProject", "workProject",
                  "workDirection", "proportion", "status", "score", "done",
                  "eName", "dept", "deptName", "pName", "pm",
                  "gl", "dl", "viceCEO", "ceo", "chairman")

    def get_eName(self, obj):
        return obj.eid.name

    def get_dept(self, obj):
        return obj.eid.dept_id

    def get_deptName(self, obj):
        return obj.eid.dept.name

    def get_pName(self, obj):
        return obj.belongProject.pname

    def get_pm(self, obj):
        con = {"point": "", "content": "", "proportion": "", "recordID": ""}
        rec = ProjectReviewRecord.objects.filter(pid=obj.id)
        try:
            pmRecord = rec.filter(reviewer=obj.belongProject.pmid)
            if len(pmRecord) != 0:
                con["point"] = pmRecord[0].point
                con["content"] = pmRecord[0].content
                con["recordID"] = pmRecord[0].id
        except ProjectReviewRecord.DoesNotExist:
            pass
        return con

    def get_gl(self, obj):
        con = {"point": "", "content": "", "proportion": "", "recordID": ""}
        rec = ProjectReviewRecord.objects.filter(pid=obj.id)
        data = glPoint(con, rec, obj)
        return data

    def get_dl(self, obj):
        con = {"point": "", "content": "", "proportion": "", "recordID": ""}
        rec = ProjectReviewRecord.objects.filter(pid=obj.id)
        data = dlPoint(con, rec, obj)
        return data

    def get_viceCEO(self, obj):
        con = {"point": "", "content": "", "proportion": "", "recordID": ""}
        rec = ProjectReviewRecord.objects.filter(pid=obj.id)
        data = viceCEOPoint(con, rec)
        return data

    def get_ceo(self, obj):
        con = {"point": "", "content": "", "proportion": "", "recordID": ""}
        rec = ProjectReviewRecord.objects.filter(pid=obj.id)
        data = cEOPoint(con, rec)
        return data

    def get_chairman(self, obj):
        con = {"point": "", "content": "", "proportion": "", "recordID": ""}
        rec = ProjectReviewRecord.objects.filter(pid=obj.id)
        data = chairmanPoint(con, rec)
        return data


class NormalNeedRecordSerializer(serializers.ModelSerializer):
    eName = serializers.SerializerMethodField()
    dept = serializers.SerializerMethodField()
    deptName = serializers.SerializerMethodField()
    gl = serializers.SerializerMethodField()
    dl = serializers.SerializerMethodField()
    viceCEO = serializers.SerializerMethodField()
    ceo = serializers.SerializerMethodField()
    chairman = serializers.SerializerMethodField()

    class Meta:
        model = NormalPR
        fields = ("id", "eid", "workQuality", "workAmount",
                  "coordination", "learning", "status", "score", "eName", "done",
                  "dept", "deptName", "gl", "dl", "viceCEO", "ceo", "chairman")

    def get_eName(self, obj):
        return obj.eid.name

    def get_dept(self, obj):
        return obj.eid.dept_id

    def get_deptName(self, obj):
        return obj.eid.dept.name

    def get_gl(self, obj):
        con = {"point": "", "content": "", "recordID": ""}
        rec = NormalReviewRecord.objects.filter(pid=obj.id)
        data = glPoint(con, rec, obj)
        return data

    def get_dl(self, obj):
        con = {"point": "", "content": "", "recordID": ""}
        rec = NormalReviewRecord.objects.filter(pid=obj.id)
        data = dlPoint(con, rec, obj)
        return data

    def get_viceCEO(self, obj):
        con = {"point": "", "content": "", "recordID": ""}
        rec = NormalReviewRecord.objects.filter(pid=obj.id)
        data = viceCEOPoint(con, rec)
        return data

    def get_ceo(self, obj):
        con = {"point": "", "content": "", "recordID": ""}
        rec = NormalReviewRecord.objects.filter(pid=obj.id)
        data = cEOPoint(con, rec)
        return data

    def get_chairman(self, obj):
        con = {"point": "", "content": "", "recordID": ""}
        rec = NormalReviewRecord.objects.filter(pid=obj.id)
        data = chairmanPoint(con, rec)
        return data


def glPoint(data, rec, obj):
    try:
        o = Order.objects.get(id=obj.eid.dept.parent)
        AOX = ("A0S", "A0P", "A0M")
        if o.parent == "viceCEO" or obj.eid.dept_id in AOX:
            gl = SupervisorInfo.objects.get(dept__id=obj.eid.dept_id)
            glRecord = rec.filter(reviewer=gl.eid_id)
            if len(glRecord) != 0:
                data["point"] = glRecord[len(glRecord) - 1].point
                data["content"] = glRecord[len(glRecord) - 1].content
                data["recordID"] = glRecord[len(glRecord) - 1].id
            if type(obj) == ProjectPR:
                data["proportion"] = glRecord.proportion
    except ObjectDoesNotExist:
        pass
    return data


def dlPoint(data, rec, obj):
    d = ("S0X", "M0A", "Q0A", "O0X", "B0A", "A0X", "I0C")
    if obj.eid.dept.parent in d:
        try:
            dl = SupervisorInfo.objects.get(dept__id=obj.eid.dept.parent)
            dlRecord = rec.filter(reviewer=dl.eid_id)
            if len(dlRecord) != 0:
                data["point"] = dlRecord[len(dlRecord) - 1].point
                data["content"] = dlRecord[len(dlRecord) - 1].content
                data["recordID"] = dlRecord[len(dlRecord) - 1].id
        except ObjectDoesNotExist:
            pass
    if obj.eid.dept_id in d:
        try:
            dl = SupervisorInfo.objects.get(dept__id=obj.eid.dept_id)
            dlRecord = rec.filter(reviewer=dl.eid_id)
            if len(dlRecord) != 0:
                data["point"] = dlRecord[len(dlRecord) - 1].point
                data["content"] = dlRecord[len(dlRecord) - 1].content
                data["recordID"] = dlRecord[len(dlRecord) - 1].id
        except ObjectDoesNotExist or KeyError:
            pass
    return data


def viceCEOPoint(data, rec):
    try:
        viceCEO = SupervisorInfo.objects.get(dept__id="viceCEO")
        viceCEORecord = rec.get(reviewer=viceCEO.eid_id)
        data["point"] = viceCEORecord.point
        data["content"] = viceCEORecord.content
        data["recordID"] = viceCEORecord.id
    except ObjectDoesNotExist:
        pass
    return data


def cEOPoint(data, rec):
    try:
        ceo = SupervisorInfo.objects.get(dept__id="S0A")
        ceoRecord = rec.get(reviewer=ceo.eid_id)
        data["point"] = ceoRecord.point
        data["content"] = ceoRecord.content
        data["recordID"] = ceoRecord.id
    except ObjectDoesNotExist:
        pass
    return data


def chairmanPoint(data, rec):
    try:
        chairman = SupervisorInfo.objects.get(dept__id="CM")
        chairmanRecord = rec.get(reviewer=chairman.eid_id)
        data["point"] = chairmanRecord.point
        data["content"] = chairmanRecord.content
        data["recordID"] = chairmanRecord.id
    except ObjectDoesNotExist:
        pass
    return data


def creditFind(giver, receiver, data):
    try:
        c = CreditRecord.objects.get(giver=giver, receiver=receiver)
        data["credit"] = c.credit
        data["id"] = c.id
    except ObjectDoesNotExist:
        pass
    return data
