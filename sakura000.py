#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import webapp2

import os

from google.appengine.ext.webapp import template

from google.appengine.ext.webapp.util import login_required
from google.appengine.api import users

import datetime
from MstUser   import *   # 使用者マスタ

class MainHandler(webapp2.RequestHandler):

  @login_required

  def get(self):

    user = users.get_current_user() # ログオン確認
    if MstUser().ChkUser(user.email()) == False:
      self.redirect(users.create_logout_url(self.request.uri))
      return

    if self.request.get('BtnLogout')  != '':
      self.redirect(users.create_logout_url(self.request.uri))
      return

    if self.request.get('BtnMENU000')  != '':
      self.redirect("/")
      return

# 家賃共益費入力
    if self.request.get('BtnSAKURA010')  != '': # (2016/04まで)
      self.redirect("/sakura010/?Nengetu=" + self.request.get('CmbNengetu') )
      return
    if self.request.get('BtnSAKURA011')  != '': # (2016/05から)
      self.redirect("/sakura011/?Nengetu=" + self.request.get('CmbNengetu') )
      return

# 電気代入力
    if self.request.get('BtnSAKURA020')  != '': # (2016/04まで)
      self.redirect("/sakura020/?Nengetu=" + self.request.get('CmbNengetu') )
      return
    if self.request.get('BtnSAKURA021')  != '': # (2016/05から)
      self.redirect("/sakura021/?Nengetu=" + self.request.get('CmbNengetu') )
      return

# 家賃・共益・電気代マスタ
    if self.request.get('BtnSAKURA900')  != '':
      self.redirect("/sakura900/")
      return

# 患者マスタ
    if self.request.get('BtnSAKURA910')  != '':
      self.redirect("/sakura910/")
      return

# 居室マスタ
    if self.request.get('BtnSAKURA920')  != '':
      self.redirect("/sakura920/")
      return

# 項目マスタ
    if self.request.get('BtnSAKURA930')  != '':
      self.redirect("/sakura930/")
      return

    PrintParam = "?LstDate="
    if self.request.get('CmbNengetu') == "":
      Zengetu = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y/%m') + "/01", '%Y/%m/%d') # 当月１日
      Zengetu -= datetime.timedelta(days=1) # 前月末日
      SelHizuke = Zengetu.strftime('%Y/%m') # 前月１日
      PrintParam += SelHizuke.replace("/","%2F")
    else:
      PrintParam += self.request.get('CmbNengetu').replace("/","%2F")

    template_values = {'PrintParam' : PrintParam,
                       'StrNengetu' : self.StrNengetuSet(),
                       'LblMsg': ""}
    path = os.path.join(os.path.dirname(__file__), 'sakura000.html')
    self.response.out.write(template.render(path, template_values))

  def StrNengetuSet(self):

    Hizuke = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y/%m') + "/01", '%Y/%m/%d') # 当月１日

    if self.request.get('CmbNengetu') == "":
      Zengetu = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y/%m') + "/01", '%Y/%m/%d') # 当月１日
      Zengetu -= datetime.timedelta(days=1) # 前月末日
#      SelHizuke = datetime.datetime.now().strftime('%Y/%m') # 当月１日
      SelHizuke = Zengetu.strftime('%Y/%m') # 当月１日
    else:
      SelHizuke = self.request.get('CmbNengetu')
    
    retStr = ""

    while  Hizuke > datetime.datetime.strptime('2014/01/01', '%Y/%m/%d'):
      retStr += "<option value='"
      retStr += Hizuke.strftime('%Y/%m')
      retStr += "'"
      if SelHizuke == Hizuke.strftime('%Y/%m'):  # 選択？
        retStr += " selected "
        Flg = False
      retStr += ">"
      retStr += Hizuke.strftime('%Y/%m')
      retStr += "</option>"
      Hizuke = datetime.datetime.strptime(Hizuke.strftime('%Y/%m') + "/01", '%Y/%m/%d') # 当月１日
      Hizuke -= datetime.timedelta(days=1) # 前月末日

    return retStr

app = webapp2.WSGIApplication([
    ('/sakura000/', MainHandler),
    ('/', MainHandler)
], debug=True)
