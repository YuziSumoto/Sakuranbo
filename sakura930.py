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

    if self.request.get('BtnSAKURA935')  != '': # 追加
      self.redirect("/sakura935/" + "?Code=0-0")
      return

    LblMsg = ""

    for param in self.request.arguments():
      if "BtnSAKURA935" in param:
        self.redirect("/sakura935/" + "?Code=" + param.replace("BtnSAKURA935",""))
        return

      if "BtnDel" in param:
        self.DataDel(param.replace("BtnDel",""))

    strTable  =  self.tableSet()

    template_values = {'strTable':strTable,
                       'LblMsg':LblMsg}
    path = os.path.join(os.path.dirname(__file__), 'sakura930.html')
    self.response.out.write(template.render(path, template_values))

  def DataDel(self,Kubun):
    DaiKubun,SyoKubun = Kubun.split("-")
    SnapData = db.GqlQuery("SELECT * FROM MstKoumoku where DaiKubun = " + DaiKubun + " and SyoKubun = " + SyoKubun)
    results = SnapData.fetch(1)
    for result in results:
      result.delete()

#  テーブルセット
  def tableSet(self):
    retStr = ""
    SnapMst = db.GqlQuery("SELECT * FROM MstKoumoku Order by DaiKubun,SyoKubun")
    for RecMst in SnapMst.fetch(100):
      retStr += "<TR>"
      retStr += "<TD>"    # 更新ボタン
      retStr += "<input type='submit' value = '"
      retStr += "{0:03d}".format(RecMst.DaiKubun)
      retStr += "' name='BtnSAKURA935"
      retStr += str(RecMst.DaiKubun) + "-" + str(RecMst.SyoKubun)
      retStr += "'>"
      retStr += "</TD>"
      retStr += "<TD>" + str(RecMst.SyoKubun) + "</TD>" # 小区分
      retStr += "<TD>" + RecMst.Naiyo + "</TD>"         # 内容
      retStr += "<TD>"    # 削除ボタン
      retStr += "<input type='submit' value = '" + u"削除" + "'"
      retStr += " name='BtnDel"
      retStr += str(RecMst.DaiKubun) + "-" + str(RecMst.SyoKubun)
      retStr += "'>"
      retStr += "</TD>"
      retStr += "</TR>"
    return retStr

app = webapp2.WSGIApplication([
    ('/sakura930/', MainHandler)
], debug=True)
