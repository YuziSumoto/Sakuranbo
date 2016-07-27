# -*- coding: UTF-8 -*-
from google.appengine.ext import db
import datetime

class DatMain(db.Model):
#  author          = db.UserProperty()
  Hizuke          = db.DateTimeProperty(auto_now_add=False) # 年月
  Room            = db.IntegerProperty()                    # 居室番号→番号
  KanzyaID        = db.IntegerProperty()                    # 患者ID
  KanzyaName      = db.StringProperty(multiline=False)      # 患者氏名(アクセス軽減のため非正規化）
  IOKubun         = db.IntegerProperty()                    # 入退院区分
  IONaiyo         = db.StringProperty(multiline=False)      # 内容(アクセス軽減のため非正規化）
  Zyokyo          = db.StringProperty(multiline=False)      # 状況
  Nissu           = db.IntegerProperty()                    # 入居日数
  NyuinNissu      = db.IntegerProperty()                    # 入院日数
  TaikenNissu     = db.IntegerProperty()                    # 体験日数
  GenkinFlg       = db.IntegerProperty()                    # 現金フラグ
  Hozyo           = db.IntegerProperty()                    # 家賃補助フラグ 20160510 0:無し 1:有り(規定値)
  Biko            = db.StringProperty(multiline=False)      # 備考
  Kyoeki          = db.IntegerProperty()                    # 共益金（手入力 2015/10/05
  Kanri           = db.IntegerProperty()                    # 管理費（手入力 2015/10/05

  def GetKingaku(self,Nengetu,RecDat,RecMst): # 金額計算

    if RecMst == False: # マスタ無し？
      Hozyo  = 0
      Yatin  = 0
      Kyoeki = 0
      Kanri  = 0
      return (Hozyo,Yatin,Kyoeki,Kanri) # ここで終わり

    if RecDat.IOKubun == 1:  # 入院中
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
      Yatin  = RecMst.Yatin                     # 全額
      Kyoeki = RecMst.Kyoeki
      Kanri  = RecMst.Kanri

    if RecDat.Hozyo == 0:  # 補助無し
      Hozyo = 0
    elif Yatin <= 10000:   # 1万以下なら全額補助 
      Hozyo = Yatin
      Yatin = 0
    else:
      Hozyo = 10000
      Yatin = Yatin - 10000 # 1万円引き

    return (Hozyo,Yatin,Kyoeki,Kanri)

class DatDenki(db.Model):
  Hizuke          = db.DateTimeProperty(auto_now_add=False) # 年月
  Room            = db.IntegerProperty()                    # 居室番号
  KanzyaID        = db.IntegerProperty()                    # 患者ID     20160510
  KanzyaName      = db.StringProperty(multiline=False)      # 患者氏名(アクセス軽減のため非正規化）20160510
  Meter           = db.FloatProperty()                      # メータ ～2016/05
  SMeter1         = db.FloatProperty()                      # 開始メータ１ 2016/05～
  EMeter1         = db.FloatProperty()                      # 終了メータ１ 2016/05～
  SMeter2         = db.FloatProperty()                      # 開始メータ２ 2016/05～
  EMeter2         = db.FloatProperty()                      # 終了メータ２ 2016/05～
  KeisanKubun     = db.IntegerProperty()                    # 計算区分 0:自動計算 1:手入力
  Comment         = db.StringProperty(multiline=False)      # コメント
  Kingaku         = db.IntegerProperty()                    # 手入力請求額

  def DelRec(self,Nengetu,Room):

    sql  = "SELECT * FROM DatDenki"
    sql += " where Hizuke = Date('" + Nengetu.replace("/","-") + "-01')" 
    sql += "  and  Room = " + Room

    Snap = db.GqlQuery(sql)
    for Rec in Snap.fetch(Snap.count()):
      Rec.delete()

    return
  
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

  def GetKingaku2(self,Nengetu,Room,DenkiTanka,Siyoryo): # 2016/06以降

    Sql =  "SELECT * FROM DatDenki"
    Sql += " Where Hizuke = Date('" + Nengetu.replace("/","-") + "-01')"
    Sql += "  And  Room  = " + str(Room)
    SnapDat = db.GqlQuery(Sql)

    Kingaku = 0

    if SnapDat.count() == 0:
      KeisanKubun = 0
      Comment     = ""
      Zengetu  = 0
      return (KeisanKubun,Comment,Kingaku)

    RecDat = SnapDat.fetch(1)[0]

    KeisanKubun = RecDat.KeisanKubun
    Comment     = RecDat.Comment
    if KeisanKubun == 1:
      Kingaku =  RecDat.Kingaku
    else:
      Kingaku = Siyoryo * DenkiTanka

    return (KeisanKubun,Comment,Kingaku)

  def GetSiyoryo(self,Rec): # 2016/06以降

    Siyoryo = 0
    for Ctr in range(1,3): # ２回ループ
      if getattr(Rec,"SMeter" + str(Ctr),None) == None: # 未指定？
        pass
      elif getattr(Rec,"EMeter" + str(Ctr),None) == None:
        pass
      else:
        Siyoryo += float(getattr(Rec,"EMeter" + str(Ctr))) - float(getattr(Rec,"SMeter" + str(Ctr)))

    return Siyoryo
