# -*- coding: UTF-8 -*-
from google.appengine.ext import db

class MstYatin(db.Model):
  Hizuke            = db.DateTimeProperty(auto_now_add=False) # 開始年月日
  Yatin             = db.IntegerProperty()                    # 家賃
  Kyoeki            = db.IntegerProperty()                    # 共益費
  Kanri             = db.IntegerProperty()                    # 管理費
  YatinDay          = db.IntegerProperty()                    # 家賃(日割)
  KyoekiDay         = db.IntegerProperty()                    # 共益(日割)
  KanriDay          = db.IntegerProperty()                    # 管理(日割)
  DenkiTanka        = db.FloatProperty()                      # 電気代単価

  def GetRec(self,Nengetu):

    Sql =  "SELECT * FROM MstYatin"
    Sql += " Where Hizuke <= Date('" + Nengetu.replace("/","-") + "-01')"
    Sql += "  Order by Hizuke Desc"
    SnapDat = db.GqlQuery(Sql)
    if SnapDat.count() == 0:
      RecMst = False
    else:
      RecMst = SnapDat.fetch(1)[0]

    return RecMst

class MstKanzya(db.Model):
  KanzyaID          = db.IntegerProperty()                    # 患者ID
  Name              = db.StringProperty(multiline=False)      # 患者氏名
  Kana              = db.StringProperty(multiline=False)      # かな氏名
  Syozoku           = db.StringProperty(multiline=False)      # 所属
  Bikou             = db.StringProperty(multiline=False)      # 備考

#  患者名取得
  def GetKanzyaName(self,KanzyaID):

    KanzyaName = ""

    Sql =  "SELECT Name FROM MstKanzya"
    Sql += " Where KanzyaID = " + str(KanzyaID)

    SnapMst = db.GqlQuery(Sql)
  
    if SnapMst.count() > 0:
      RecMst = SnapMst.fetch(1)
      KanzyaName = RecMst[0].Name

    return KanzyaName

class MstRoom(db.Model):
  Room              = db.IntegerProperty()                    # 居室番号

class MstKoumoku(db.Model):
  DaiKubun          = db.IntegerProperty()                    # 大区分
  SyoKubun          = db.IntegerProperty()                    # 小区分
  Naiyo             = db.StringProperty(multiline=False)      # 内容

#  入退院区分取得
  def GetIOKubun(self,SyoKubun):

    Kubun = ""

    Sql =  "SELECT * FROM MstKoumoku"
    Sql += " Where DaiKubun = 1 "
    Sql += "  And  SyoKubun = " + str(SyoKubun)

    SnapMst = db.GqlQuery(Sql)
    if SnapMst.count() > 0:
      RecMst = SnapMst.fetch(1)
      Kubun = RecMst[0].Naiyo

    return Kubun

#  入退院区分取得
  def GetNyutai(self):

    Rec = {}

    Sql =  "SELECT * FROM MstKoumoku"
    Sql += " Where DaiKubun = 1 "

    SnapMst = db.GqlQuery(Sql)
    for RecMst in  SnapMst.fetch(SnapMst.count()):
      Rec[RecMst.SyoKubun] =  RecMst.Naiyo

    return Rec


