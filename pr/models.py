from django.db import models


# Create your models here.


class Employee(models.Model):
    id = models.IntegerField(primary_key=True, null=False, unique=True)
    name = models.TextField(null=False)
    dept = models.ForeignKey("Order", on_delete=models.RESTRICT)
    needPR = models.BooleanField()
    doneNormalPR = models.BooleanField()
    creditStatus = models.TextField()

    class Meta:
        db_table = "employee"


class ProjectPR(models.Model):
    id = models.BigAutoField(primary_key=True)
    eid = models.ForeignKey("Employee", on_delete=models.RESTRICT)
    belongProject = models.ForeignKey('Project', on_delete=models.RESTRICT)
    workProject = models.TextField(blank=True)
    workDirection = models.TextField(blank=True)
    proportion = models.TextField(blank=True)
    status = models.TextField()  # pm-> 待PM審核
    score = models.TextField()

    class Meta:
        db_table = "projectPR"


class NormalPR(models.Model):
    id = models.BigAutoField(primary_key=True)
    eid = models.ForeignKey("Employee", on_delete=models.RESTRICT)
    workQuality = models.TextField(blank=True)
    workAmount = models.TextField(blank=True)
    coordination = models.TextField(blank=True)
    learning = models.TextField(blank=True)
    status = models.TextField()
    score = models.TextField()

    class Meta:
        db_table = "normalPR"


class Project(models.Model):
    eid = models.ForeignKey('Employee', on_delete=models.RESTRICT)
    pmid = models.TextField()
    done = models.BooleanField()
    pname = models.TextField(blank=True)
    pid = models.TextField()

    class Meta:
        db_table = "project"


class Order(models.Model):
    name = models.TextField()
    id = models.TextField(primary_key=True)
    parent = models.TextField()

    class Meta:
        db_table = "order"


class ProjectReviewRecord(models.Model):
    pid = models.ForeignKey("ProjectPR", on_delete=models.RESTRICT)
    reviewer = models.IntegerField(null=False)
    point = models.TextField(blank=True)
    content = models.TextField(blank=True)
    proportion = models.TextField(blank=True)

    class Meta:
        db_table = "projectReviewRecord"


class NormalReviewRecord(models.Model):
    pid = models.ForeignKey("NormalPR", on_delete=models.RESTRICT)
    reviewer = models.IntegerField(null=False)
    point = models.TextField(blank=True)
    content = models.TextField(blank=True)

    class Meta:
        db_table = "normalReviewRecord"


class SupervisorInfo(models.Model):
    dept = models.OneToOneField("Order", on_delete=models.RESTRICT)
    eid = models.OneToOneField('Employee', on_delete=models.RESTRICT)

    class Meta:
        db_table = "supervisorInfo"


class CreditRecord(models.Model):
    giver = models.ForeignKey("Employee", on_delete=models.RESTRICT)
    receiver = models.TextField()
    grade = models.TextField()
    credit = models.TextField()

    class Meta:
        db_table = "creditRecord"


class CreditDistribution(models.Model):
    giveDept = models.ForeignKey("Order", on_delete=models.RESTRICT)
    receiveDept = models.TextField()
    creditDept = models.TextField()

    class Meta:
        db_table = "creditDistribution"


class Annotation(models.Model):
    giveDept = models.ForeignKey("Order", on_delete=models.RESTRICT)
    content = models.TextField(blank=True)
    status = models.TextField()

    class Meta:
        db_table = "annotation"


class AttendanceRecord(models.Model):
    eid = models.OneToOneField("Employee", on_delete=models.RESTRICT)
    specialLeave = models.TextField(blank=True)
    sickLeave = models.TextField(blank=True)
    sickLeavePercentage = models.TextField(blank=True)
    personalLeave = models.TextField(blank=True)
    personalLeavePercentage = models.TextField(blank=True)
    marriageLeave = models.TextField(blank=True)
    bereavementLeave = models.TextField(blank=True)
    maternityLeave = models.TextField(blank=True)
    publicLeave = models.TextField(blank=True)
    absenteeism = models.TextField(blank=True)
    absenteeismPercentage = models.TextField(blank=True)
    commendation = models.TextField(blank=True)
    commendationPercentage = models.TextField(blank=True)
    minorMerit = models.TextField(blank=True)
    minorMeritPercentage = models.TextField(blank=True)
    majorMerit = models.TextField(blank=True)
    majorMeritPercentage = models.TextField(blank=True)
    petition = models.TextField(blank=True)
    petitionPercentage = models.TextField(blank=True)
    minorDemerit = models.TextField(blank=True)
    minorDemeritPercentage = models.TextField(blank=True)
    majorDemerit = models.TextField(blank=True)
    majorDemeritPercentage = models.TextField(blank=True)
    attendanceScore = models.TextField(blank=True)

    class Meta:
        db_table = "attendanceRecord"
