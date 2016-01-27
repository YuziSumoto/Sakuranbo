# -*- coding: UTF-8 -*-
from google.appengine.ext import db
import datetime

class DatMain(db.Model):
#  author          = db.UserProperty()
  Hizuke          = db.DateTimeProperty(auto_now_add=False) # 年月
  Room            = db.IntegerProperty()                    # 居室番号
  KanzyaID        = db.IntegerProperty()                    # 患者ID
  KanzyaName      = db.StringProperty(multiline=False)      # 患者氏名(アクセス軽減のため非正規化）
  IOKubun         = db.IntegerProperty()                    # 入退院区分
  IONaiyo         = db.StringProperty(multiline=False)      # 内容(アクセス軽減のため非正規化）
  Zyokyo          = db.StringProperty(multiline=False)      # 状況
  Nissu           = db.IntegerProperty()                    # 入居日数
  GenkinFlg       = db.IntegerProperty()                    # 現金フラグ
  Biko            = db.StringProperty(multiline=False)      # 備考
  Kyoeki          = db.IntegerProperty()                    # 共益金（手入力 2015/10/05
  Kanri           = db.IntegerProperty()                    # 管理費（手入力 2015/10/05

  def GetKingaku(self,Nengetu,RecDat,RecMst): # 金額計算

    if RecMst == False: # マスタ無し？
      Yatin  = 0
      Kyoeki = 0
      Kanri  = 0
    elif RecDat.IOKubun == 1:  # 入院中
      if RecDat.KanzyaID == 6425:  # 新田登美子さんなら
        Yatin  = 30000                            # ３万円だそうな
      else:
        Yatin  = RecMst.Yatin                     # 全額
      Kyoeki = RecMst.KyoekiDay * RecDat.Nissu  # 共益、管理は日数分
      Kanri  = RecMst.KanriDay  * RecDat.Nissu  # 共益、管理は日数分
    elif RecDat.IOKubun == 2:  # 入退所
      Yatin  = RecMst.YatinDay  * RecDat.Nissu
      Kyoeki = RecMst.KyoekiDay * RecDat.Nissu
      Kanri  = RecMst.KanriDay  * RecDat.Nissu
    elif RecDat.IOKubun == 4:  # 入院中退所
      Yatin  = RecMst.YatinDay  * RecDat.Nissu
      Kyoeki = 0 # RecMst.KyoekiDay * RecDat.Nissu 2015/10/05 入院中退所は共益費０
      Kanri  = 0 # RecMst.KanriDay  * RecDat.Nissu 2015/10/05 入院中退所は共益費０
    elif RecDat.IOKubun == 3:  # 共益手入力
      Yatin  = RecMst.YatinDay  * RecDat.Nissu
      Kyoeki = RecDat.Kyoeki  # 2015/10/05 共益費手入力対応
      Kanri  = RecDat.Kanri   # 2015/10/05 共益費手入力対応
    else: # 入退所
      if RecDat.KanzyaID == 6425:  # 新田登美子さんなら
        Yatin  = 30000                            # ３万円だそうな
      else:
        Yatin  = RecMst.Yatin
      Kyoeki = RecMst.Kyoeki
      Kanri  = RecMst.Kanri

    return (Yatin,Kyoeki,Kanri)

class DatDenki(db.Model):
  Hizuke          = db.DateTimeProperty(auto_now_add=False) # 年月
  Room            = db.IntegerProperty()                    # 居室番号
  Meter           = db.FloatProperty()                      # メータ

  KeisanKubun     = db.IntegerProperty()                    # 計算区分 0:自動計算 1:手入力
  Comment         = db.StringProperty(multiline=False)      # コメント
  Kingaku         = db.IntegerProperty()                    # 手入力請求額

#  電気データ取得
  def GetRec(self,Nengetu,Room):

    Rec = ""

    Sql =  "SELECT * FROM DatDenki"
    Sql += " Where Hizuke = Date('" + Nengetu.replace("/","-") + "-01')"
    Sql += "  And  Room   = " + Room

    SnapMst = db.GqlQuery(Sql)
  
    if SnapMst.count() > 0:
      Rec = SnapMst.fetch(1)[0]

    return Rec

#  電気メータ取得
  def GetDenki(self,Nengetu,Room):

    Meter = 0

    Sql =  "SELECT * FROM DatDenki"
    Sql += " Where Hizuke = Date('" + Nengetu.replace("/","-") + "-01')"
    Sql += "  And  Room   = " + Room

    SnapMst = db.GqlQuery(Sql)
  
    if SnapMst.count() > 0:
      RecMst = SnapMst.fetch(1)
      Meter = RecMst[0].Meter

    return Meter

  def GetKingaku(self,Nengetu,Room,DenkiTanka):

    Sql =  "SELECT * FROM DatDenki"
    Sql += " Where Hizuke = Date('" + Nengetu.replace("/","-") + "-01')"
    Sql += "  And  Room  = " + str(Room)
    SnapDat = db.GqlQuery(Sql)
    if SnapDat.count() == 0:
      Tougetu  = 0
    else:
      RecDat = SnapDat.fetch(1)[0]
      if RecDat.KeisanKubun == 1:  # 手入力
        return  (RecDat.KeisanKubun,RecDat.Comment ,RecDat.Kingaku)
      elif RecDat.Meter == None:
        Tougetu  = 0
      else:
        Tougetu  = RecDat.Meter
        
    Zengetu = datetime.datetime.strptime(Nengetu + "/01", '%Y/%m/%d') # 当月１日
    Zengetu -= datetime.timedelta(days=1) # 前月末日

    Sql =  "SELECT * FROM DatDenki"
    Sql += " Where Hizuke = Date('" + Zengetu.strftime('%Y-%m') + "-01')"
    Sql += "  And  Room  = " + str(Room)
    SnapDat = db.GqlQuery(Sql)
    if SnapDat.count() == 0:
      KeisanKubun = 0
      Comment     = ""
      Zengetu  = 0
    else:
      RecDat = SnapDat.fetch(1)[0]
      if RecDat.Meter == None:
        KeisanKubun = 0
        Comment     = ""
        Zengetu  = 0
      else:
        KeisanKubun = RecDat.KeisanKubun
        Comment     = RecDat.Comment
        Zengetu     = RecDat.Meter

    Kingaku = (Tougetu - Zengetu) * DenkiTanka

    return (KeisanKubun,Comment,Kingaku)
