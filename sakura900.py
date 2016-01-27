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

class MainHandler(webapp2.RequestHandler):

  @login_required

  def get(self):

    user = users.get_current_user() # ログオン確認
    if MstUser().ChkUser(user.email()) == False:
      self.redirect(users.create_logout_url(self.request.uri))
      return

    if self.request.get('BtnSAKURA000')  != '':
      self.redirect("/sakura000/")
      return

    if self.request.get('BtnSAKURA905')  != '': # 追加
      self.redirect("/sakura905/" + "?Hizuke=" + datetime.datetime.now().strftime('%Y/%m'))
      return

    LblMsg = ""

    for param in self.request.arguments():
      if "BtnSAKURA905" in param:
        self.redirect("/sakura905/" + "?Hizuke=" + param.replace("BtnSAKURA905",""))
        return

      if "BtnDel" in param:
        self.DataDel(param.replace("BtnDel",""))

    strTable  =  self.tableSet()

    template_values = {'strTable':strTable,
                       'LblMsg':LblMsg}
    path = os.path.join(os.path.dirname(__file__), 'sakura900.html')
    self.response.out.write(template.render(path, template_values))

  def DataDel(self,Hizuke):
    SnapData = db.GqlQuery("SELECT * FROM MstYatin where Hizuke = Date('" + Hizuke.replace("/","-") + "-01')")
    results = SnapData.fetch(1)
    for result in results:
      result.delete()


#  テーブルセット
  def tableSet(self):
    retStr = ""
    SnapMst = db.GqlQuery("SELECT * FROM MstYatin Order by Hizuke")
    for RecMst in SnapMst.fetch(100):
      retStr += "<TR>"
      retStr += "<TD>"    # 更新ボタン
      retStr += "<input type='submit' value = '"
      retStr += RecMst.Hizuke.strftime("%Y/%m")
      retStr += "' name='BtnSAKURA905"
      retStr += RecMst.Hizuke.strftime("%Y/%m")
      retStr += "'>"
      retStr += "</TD>"
      retStr += "<TD>" + str(RecMst.Yatin) + "</TD>" # 家賃
      retStr += "<TD>" + str(RecMst.Kyoeki) + "</TD>" # 共益費
      retStr += "<TD>" + str(RecMst.Kanri) + "</TD>" # 管理費
      retStr += "<TD>" + str(RecMst.YatinDay) + "</TD>" # 家賃（日)
      retStr += "<TD>" + str(RecMst.KyoekiDay) + "</TD>" # 共益（日）
      retStr += "<TD>" + str(RecMst.KanriDay) + "</TD>" # 管理（日)
      retStr += "<TD>" + str(RecMst.DenkiTanka) + "</TD>" # 電気代単価
      retStr += "<TD>"    # 削除ボタン
      retStr += "<input type='submit' value = '削除'"
      retStr += " name='BtnDel"
      retStr += RecMst.Hizuke.strftime("%Y/%m")
      retStr += "'>"
      retStr += "</TD>"
      retStr += "</TR>"
    return retStr

app = webapp2.WSGIApplication([
    ('/sakura900/', MainHandler)
], debug=True)
