#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import webapp2

import os
from google.appengine.ext.webapp import template

from google.appengine.ext.webapp.util import login_required
from google.appengine.api import users
from MstUser   import *   # 使用者マスタ

import datetime

from Mst import *
from Dat import *

class MainHandler(webapp2.RequestHandler):

  @login_required

  def get(self):

    user = users.get_current_user() # ログオン確認
    if MstUser().ChkUser(user.email()) == False:
      self.redirect(users.create_logout_url(self.request.uri))
      return

    Nengetu = self.request.get('Nengetu')
    cookieStr = 'Nengetu=' + Nengetu + ';' 
    self.response.headers.add_header('Set-Cookie', cookieStr.encode('shift-jis'))

    Room = self.request.get('Room')
    cookieStr = 'Room=' + Room + ';' 
    self.response.headers.add_header('Set-Cookie', cookieStr.encode('shift-jis'))

    Return = self.request.get('Return')
    cookieStr = 'Return=' + Return + ';' 
    self.response.headers.add_header('Set-Cookie', cookieStr.encode('shift-jis'))

    LblMsg = ""

    Rec = {}
    Rec = self.DataGet(Rec,Nengetu,Room)

    template_values = { 'LblRoom'     :Room,
                        'Rec'         : Rec,
                        'StrKanzya'   : self.SetKanzya(Rec['CmbKanzya']),
                        'StrNyutaiin' : self.SetNyutaiin(Rec['CmbNyutaiin']),
                        'Nissu'    : self.SetNissu(),
                        'StrGenkin'    : self.SetGenkin(Rec['CmbGenkin']),
                        'LblMsg' : LblMsg #""
                      }
    path = os.path.join(os.path.dirname(__file__), 'sakura015.html')
    self.response.out.write(template.render(path, template_values))

  def post(self):

    user = users.get_current_user() # ログオン確認
    if MstUser().ChkUser(user.email()) == False:
      self.redirect(users.create_logout_url(self.request.uri))
      return

    Nengetu = self.request.cookies.get('Nengetu', '')
    Room    = self.request.cookies.get('Room', '')
    Return  = self.request.cookies.get('Return', '')

    if self.request.get('BtnSAKURA010')  != '': # 中止
      self.redirect("/" + Return + "/?Nengetu=" + Nengetu )
      return

    LblMsg = ""

    if self.request.get('BtnKettei')  != '':  # 決定

      ErrFlg,LblMsg = self.ErrCheck()
      if ErrFlg == False:
        self.DataDel(Nengetu,Room)
        self.DataAdd(Nengetu,Room)
        self.redirect("/" + Return + "/?Nengetu=" + Nengetu )
        return

    Rec = {}
    ParaNames = self.request.arguments()
    for ParaName in ParaNames:
      Rec[ParaName]    = self.request.get(ParaName)

    template_values = { 'LblRoom'     :Room,
                        'Rec'         : Rec,
                        'StrKanzya'   : self.SetKanzya(Rec['CmbKanzya']),
                        'StrNyutaiin' : self.SetNyutaiin(Rec['CmbNyutaiin']),
                        'Nissu'    : self.SetNissu(),
                        'StrGenkin'    : self.SetGenkin(Rec['CmbGenkin']),
                        'LblMsg' : LblMsg #""
                      }
    path = os.path.join(os.path.dirname(__file__), 'sakura015.html')
    self.response.out.write(template.render(path, template_values))

  def ErrCheck(self): # 入力エラーチェック

    if self.request.get('TxtKanri') != "" and self.request.get('TxtKanri').replace(".","").isdigit() == False:
      return (True,u"入力された管理費が数値ではありません")

    if self.request.get('TxtKyoeki') != ""  and self.request.get('TxtKyoeki').replace(".","").isdigit() == False:
      return (True,u"入力された共益費が数値ではありません")

    return (False," ")

  def SetKanzya(self,KanzyaID):

    retStr = ""

    retStr += "<option value=0"
    retStr += ">&nbsp</option>"

    SnapMst = db.GqlQuery("SELECT * FROM MstKanzya Order by Kana")
    for RecMst in SnapMst.fetch(100):
      retStr += "<option value='"
      retStr += str(RecMst.KanzyaID)
      retStr += "'"
      if KanzyaID == RecMst.KanzyaID:  # 選択判定
        retStr += " selected "
        Flg = False
      retStr += ">"
      retStr += RecMst.Name
      retStr += "</option>"

    return retStr

  def SetNyutaiin(self,SyoKubun):

    retStr = ""

    Sql =  "SELECT * FROM MstKoumoku"
    Sql += " Where DaiKubun = 1 "
    Sql += "  And  SyoKubun > 0 "
    Sql += " Order by SyoKubun"

    SnapMst = db.GqlQuery(Sql)
    for RecMst in SnapMst.fetch(100):
      retStr += "<option value='"
      retStr += str(RecMst.SyoKubun)
      retStr += "'"
      if int(SyoKubun) == RecMst.SyoKubun:  # 選択判定
        retStr += " selected "
        Flg = False
      retStr += ">"
      retStr += RecMst.Naiyo
      retStr += "</option>"

    return retStr

  def SetNissu(self):
    Nissu = []
    for Ctr in range(0,32):
      Nissu.append(Ctr)
    return Nissu

  def SetGenkin(self,Genkin):

    retStr = ""
    retStr += "<option value='0'"
    if Genkin == 0:  # 選択判定
      retStr += " selected "
    retStr += ">"
    retStr += "</option>"

    retStr += "<option value='1'"
    if Genkin == 1:  # 選択判定
      retStr += " selected "
    retStr += ">○"
    retStr += "</option>"

    return retStr

  def DataGet(self,Rec,Nengetu,Room):

    sql  = "SELECT * FROM DatMain"
    sql += " where Hizuke = Date('" + Nengetu.replace("/","-") + "-01')" 
    sql += "  and  Room = " + Room

    Rec['CmbKanzya']    = ""
    Rec['CmbNyutaiin']  = "0"
    Rec['TxtZyokyo']    = ""
    Rec['TxtYatin']     = 0
    Rec['TxtKyoeki']    = 0
    Rec['TxtKanri']     = 0
    Rec['Nissu']        = 0
    Rec['NyuinNissu']   = 0
    Rec['TaikenNissu']  = 0
    Rec['TxtBiko']      = ""
    Rec['CmbGenkin']    = 0
    Rec['Hozyo']        = 1 # 2016/05/13

    SnapData = db.GqlQuery(sql)
    results = SnapData.fetch(1)

    for result in results:
      Rec['CmbKanzya']    = result.KanzyaID
      Rec['CmbNyutaiin']  = result.IOKubun
      Rec['TxtZyokyo']    = result.Zyokyo
      Rec['TxtYatin']     = 0
      Rec['Nissu']        = result.Nissu
      Rec['NyuinNissu']   = result.NyuinNissu
      Rec['TaikenNissu']  = result.TaikenNissu
      Rec['TxtBiko']      = result.Biko
      Rec['CmbGenkin']    = result.GenkinFlg

      Rec['Hozyo']        = result.Hozyo # 2016/05/13

      if result.Kyoeki != None:
        Rec['TxtKyoeki']    = result.Kyoeki # 0  20151005
      if result.Kanri != None:
        Rec['TxtKanri']     = result.Kanri  # 0  20151005

    return Rec

  def DataDel(self,Nengetu,Room):

    sql  = "SELECT * FROM DatMain"
    sql += " where Hizuke = Date('" + Nengetu.replace("/","-") + "-01')" 
    sql += "  and  Room = " + Room

    Snap = db.GqlQuery(sql)
    for Rec in Snap.fetch(Snap.count()):
      Rec.delete()

  def DataAdd(self,Hizuke,Room):

    DynaData = DatMain()
    DynaData.Hizuke = datetime.datetime.strptime(Hizuke + "/01", '%Y/%m/%d')
    DynaData.Room = int(Room)

    DynaData.KanzyaID    = int(self.request.get('CmbKanzya'))
    DynaData.KanzyaName  = MstKanzya().GetKanzyaName(DynaData.KanzyaID)
    DynaData.IOKubun     = int(self.request.get('CmbNyutaiin'))
    DynaData.IONaiyo     = MstKoumoku().GetIOKubun(DynaData.IOKubun)
    DynaData.Zyokyo      = self.request.get('TxtZyokyo')

    DynaData.Nissu       = int(self.request.get('Nissu'))
    DynaData.NyuinNissu  = int(self.request.get('NyuinNissu'))
    DynaData.TaikenNissu = int(self.request.get('TaikenNissu'))

    DynaData.GenkinFlg   = int(self.request.get('CmbGenkin'))
    DynaData.Biko        = self.request.get('TxtBiko')

    if  self.request.get('Hozyo') == "1":
      DynaData.Hozyo     = 1
    else:
      DynaData.Hozyo     = 0
 
    DynaData.Kyoeki   = int(self.request.get('TxtKyoeki'))    # 2015/10/05
    DynaData.Kanri        = int(self.request.get('TxtKanri')) # 2015/10/05

    DynaData.put()

    return

app = webapp2.WSGIApplication([
    ('/sakura015/', MainHandler)
], debug=True)
