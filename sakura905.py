#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import webapp2

import os
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import users
from MstUser   import *   # 使用者マスタ

from Mst import *
import datetime

#from dateutil import relativedelta

class MainHandler(webapp2.RequestHandler):

  @login_required

  def get(self):

    user = users.get_current_user() # ログオン確認
    if MstUser().ChkUser(user.email()) == False:
      self.redirect(users.create_logout_url(self.request.uri))
      return

    LblMsg = ""

    if self.request.get('BtnSAKURA900')  != '':
      self.redirect("/sakura900/")
      return

    if self.request.get('BtnKettei')  != '':
      ErrFlg,LblMsg = self.ChkInput() # 入力チェック
      if ErrFlg == False: # エラー無し
        self.DataDel()
        self.DataAdd()
        self.redirect("/sakura900/")
        return

    if self.request.get('Hizuke') != '': # 初期表示→パラメタ取得
      Hizuke = self.request.get('Hizuke')
      cookieStr = 'Hizuke=' + Hizuke + ';' # expires=Fri, 31-Dec-2020 23:59:59 GMT'
      self.response.headers.add_header('Set-Cookie', cookieStr.encode('shift-jis'))
    else:    # ２回目からはクッキー取得
      Hizuke = self.request.cookies.get('Hizuke', '')

    strNengetu = self.StrNengetuSet(Hizuke)

    if  self.request.get('CmbNengetu') == "": # 初回表示?
      Rec = self.DataGet(Hizuke)
    else:
      Rec = {}
      Rec['TxtYatin']      = self.request.get('TxtYatin')
      Rec['TxtKyoeki']     = self.request.get('TxtKyoeki')
      Rec['TxtKanri']      = self.request.get('TxtKanri')
      Rec['TxtYatinDay']   = self.request.get('TxtYatinDay')
      Rec['TxtKyoekiDay']  = self.request.get('TxtKyoekiDay')
      Rec['TxtKanriDay']   = self.request.get('TxtKanriDay')
      Rec['TxtDenkiTanka'] = self.request.get('TxtDenkiTanka')

    template_values = {'StrNengetu':strNengetu,
                      'Rec':Rec,
                      'LblMsg': LblMsg}
    path = os.path.join(os.path.dirname(__file__), 'sakura905.html')
    self.response.out.write(template.render(path, template_values))

  def StrNengetuSet(self,Nengetu):

    retStr = ""
    Hizuke = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y/%m') + "/01", '%Y/%m/%d') # 当月１日
    Hizuke += datetime.timedelta(days=62) # ２か月後まで

    while  Hizuke > datetime.datetime.strptime('2014/01/01', '%Y/%m/%d'):
      retStr += "<option value='"
      retStr += Hizuke.strftime('%Y/%m')
      retStr += "'"
      if Hizuke.strftime('%Y/%m') == Nengetu:
        retStr += " selected "
      retStr += ">"
      retStr += Hizuke.strftime('%Y/%m')
      retStr += "</option>"
      Hizuke = datetime.datetime.strptime(Hizuke.strftime('%Y/%m') + "/01", '%Y/%m/%d') # 当月１日
      Hizuke -= datetime.timedelta(days=1) # 前月末日

    return retStr

  def ChkInput(self):

    ErrFlg = True
    LblMsg = ""

    if   self.request.get('TxtYatin').isdigit() == False:
      LblMsg = "家賃が数値として認識できません。"
    elif self.request.get('TxtKyoeki').isnumeric() == False:
      LblMsg = "共益費が数値として認識できません。"
    elif self.request.get('TxtKanri').isnumeric() == False:
      LblMsg = u"管理費が数値として認識できません。"
    elif self.request.get('TxtYatinDay').isnumeric() == False:
      LblMsg = u"家賃（日別）が数値として認識できません。"
    elif self.request.get('TxtKyoekiDay').isnumeric() == False:
      LblMsg = u"共益（日別）が数値として認識できません。"
    elif self.request.get('TxtKanriDay').isnumeric() == False:
      LblMsg = u"管理（日別）が数値として認識できません。"
    elif self.request.get('TxtDenkiTanka').replace(".","").isdigit() == False:
      LblMsg = u"電気代が数値として認識できません。"
    else:
      ErrFlg = False

    return (ErrFlg,LblMsg)

  def DataGet(self,Hizuke):

    Rec = {}

    SnapData = db.GqlQuery("SELECT * FROM MstYatin where Hizuke = Date('" + Hizuke.replace("/","-") + "-01')")
    results = SnapData.fetch(1)
    for result in results:
      Rec['TxtYatin']      = result.Yatin
      Rec['TxtKyoeki']     = result.Kyoeki
      Rec['TxtKanri']      = result.Kanri
      Rec['TxtYatinDay']   = result.YatinDay
      Rec['TxtKyoekiDay']  = result.KyoekiDay
      Rec['TxtKanriDay']   = result.KanriDay
      Rec['TxtDenkiTanka'] = result.DenkiTanka

    return Rec

  def DataDel(self):
    Hizuke = self.request.get('CmbNengetu').replace("/","-") + "-01"
    SnapData = db.GqlQuery("SELECT * FROM MstYatin where Hizuke = Date('" + Hizuke + "')")
    results = SnapData.fetch(1)
    for result in results:
      result.delete()

  def DataAdd(self):

    DynaData = MstYatin()
    DynaData.Hizuke = datetime.datetime.strptime(self.request.get('CmbNengetu') + "/01", '%Y/%m/%d')
    DynaData.Yatin = int(self.request.get('TxtYatin'))
    DynaData.Kyoeki = int(self.request.get('TxtKyoeki'))
    DynaData.Kanri = int(self.request.get('TxtKanri'))
    DynaData.YatinDay = int(self.request.get('TxtYatinDay'))
    DynaData.KyoekiDay = int(self.request.get('TxtKyoekiDay'))
    DynaData.KanriDay = int(self.request.get('TxtKanriDay'))
    DynaData.DenkiTanka = float(self.request.get('TxtDenkiTanka'))
    DynaData.put()

app = webapp2.WSGIApplication([
    ('/sakura905/', MainHandler)
], debug=True)
