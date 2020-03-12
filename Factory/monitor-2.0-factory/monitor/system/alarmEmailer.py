#!/usr/bin/python

import smtplib
import datetime
import requests
import logsystem
log = logsystem.getLogger()

import systemConstants

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], 'views')) # Need version.py
import version
import dbUtils
from datetime import timedelta
from pytz import timezone
from flask import json
import LeoFlaskUtils

alarmReportAPIData = {}
alarmEmailAPIData = {}
requestData = {}
hostName = "api.leocloud.us"
#hostName = "10.1.10.55"


def _getSubject(alarmRecsList, siteInfo, emailtype ):

  if emailtype == systemConstants.SEND_EMAIL_SEND_ALARM:
    subjectLine = siteInfo["name"] + " - "

    numberOfNewAlarms = 0
    
    for alarm in alarmRecsList:
      if alarm['EBrecId'] < 0 :
        # This is a new record.
        numberOfNewAlarms = numberOfNewAlarms + 1

    # Report number of NEW alarms as well as the number of "repeated/follow-up" alarms that are still active.
    subjectLine = subjectLine + str(numberOfNewAlarms) + " New Alarm"
    if numberOfNewAlarms > 1:
      subjectLine = subjectLine + "s"
      
    numberOfAlarms = len(alarmRecsList)
    if numberOfNewAlarms != numberOfAlarms :
      subjectLine = subjectLine + " - " + str(numberOfAlarms) + " active alarms total"

  elif emailtype == systemConstants.SEND_EMAIL_SEND_ALARM_REPORT :
    # Summary Email Report Subject Line
    subjectLine = "{} - Alarm Report - {} Active Alarms, {} Total Alarm Events".format(siteInfo["name"], alarmRecsList['totalActiveAlarms'], alarmRecsList['totalAlarmEvents'])

  elif emailtype == systemConstants.SEND_EMAIL_SEND_TEST_ALARM:
    subjectLine = siteInfo["name"] + " - Test Alarm"

  elif emailtype == systemConstants.SEND_EMAIL_SEND_TEST_ALARM_REPORT:
    # Summary Email Report Subject Line
    subjectLine = "{0} - TEST Alarm Report - {1} Active Alarms, {2} Total Alarm Events".format( siteInfo["name"], alarmRecsList['totalActiveAlarms'], alarmRecsList['totalAlarmEvents'] )

  return subjectLine


def _getBody(subjectLine, alarmRecsList, siteInfo, emailtype ):
  bodyheader = ('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
          '<html xmlns="http://www.w3.org/1999/xhtml">'
          '<head>'
          '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /></head>'
          '<body>')

  # Append "hidden" leo version at the end of each email.
  htmlLeoVersion = '<p><span style="color:white">LEO Version: {0} ({1})</span></p>'.format( version.versionInfo['LeoVersionNumber'], version.versionInfo['LeoVersionDate'] )
  LeoVersion = '{0} ({1})'.format( version.versionInfo['LeoVersionNumber'], version.versionInfo['LeoVersionDate'] )
  bodytail = ( htmlLeoVersion + '</body></html>')
  alarmReportInfo = alarmRecsList
  enableLeoCloudData = getEnableLeoCloudValue()

  body = []
  body.append ('<h2>' + subjectLine + '</h2>')
  body.append('<p>' + siteInfo["address"] + '</p>')

  # All times are UTC so we need to convert to localtime
  utcToLocalDiff = datetime.datetime.utcnow() - datetime.datetime.now()

    # SEND EMAIL - Real Alarm Email or follow-up
  if emailtype == systemConstants.SEND_EMAIL_SEND_ALARM :

    body.append('<p>All times are local to this site.</p>')
    if len( alarmRecsList ) > 0 :
      body.append('<table border="1px" cellpadding="4px" cellspacing="0px">')

      body.append('<tr>')

      body.append('<th>')
      body.append("date")
      body.append('</th>')

      body.append('<th>')
      body.append("name")
      body.append('</th>')

      body.append('<th>')
      body.append("alarm")
      body.append('</th>')

      body.append('<th>')
      body.append("description")
      body.append('</th>')

      body.append('</tr>')
      fmt = "%Y-%m-%d %H:%M:%S"
      now_time = datetime.datetime.now(timezone('US/Eastern'))
      emailDate = now_time.strftime(fmt)
      #alarmEmailAPIData["chainid"] = enableLeoCloudData["chainId"]
      #alarmEmailAPIData["storeMarkerId"] = enableLeoCloudData["storeMarkerId"]
      alarmEmailAPIData["MACAddress"] = getMACAddress()
      alarmEmailAPIData["alarmEmail"] = []
      alarmEmailSubjectAPIData = {}
      alarmEmailSubjectAPIData["strSubject"] = str(subjectLine)
      alarmEmailSubjectAPIData["strEmailDate"] = emailDate
      alarmEmailSubjectAPIData["strVersion"] = LeoVersion
      alarmEmailAPIData["alarmEmail"].append(alarmEmailSubjectAPIData)
      alarmEmailAPIData["alarmEmailRecord"] = []
      for alarm in alarmRecsList:
        alarmEmailRecordAPIData = {}
        if alarm['EBrecId'] < 0 :
          body.append('<tr style="font-weight: bold; background-color: yellow;">')
          alarmEmailRecordAPIData["alarmActive"] = 1
        else:
          body.append('<tr>')
          alarmEmailRecordAPIData["alarmActive"] = 0

        body.append('<td>')
        # print "alarm['date'] = ", alarm['date']
        # Strip milliseconds.
        periodLoc = alarm['date'].rfind(".")
        if periodLoc >= 0 :
          alarm['date'] = alarm['date'][0:periodLoc]
        # print "AFTER alarm['date'] = ", alarm['date']
        alarm_datetime = datetime.datetime.strptime( alarm['date'], '%Y-%m-%d %H:%M:%S')
        d = (alarm_datetime - utcToLocalDiff).strftime('%c').split()
        t = (alarm_datetime - utcToLocalDiff)

        tStr = t.strftime("%a %b %d %Y %H:%M")
        alarmDateAPI = t.strftime("%Y-%m-%d %H:%M:%S")
        alarmEmailRecordAPIData["LEOalmDate"] = alarmDateAPI
        alarmEmailRecordAPIData["emailDate"] = emailDate
        alarmEmailRecordAPIData["alarmApp"] = str(alarm["name"])
        alarmEmailRecordAPIData["alarmText"] = str(alarm["displayName"])
        alarmEmailRecordAPIData["alarmSource"] = str(alarm["description"])
        body.append(tStr)
        body.append('</td>')

        body.append('<td>')
        body.append(alarm["name"])
        body.append('</td>')

        body.append('<td>')
        body.append(alarm["displayName"])
        body.append('</td>')

        body.append('<td>')
        body.append(alarm["description"])
        body.append('</td>')

        body.append('</tr>')
        alarmEmailAPIData["alarmEmailRecord"].append(alarmEmailRecordAPIData)
      body.append('</table>')
    else:  # No alarms
      body.append('<tr style="font-weight: bold; ">No Alarms Since Last Report')
      body.append('</tr>')


      # SEND TEST EMAIL - Test Alarm Email
  elif emailtype == systemConstants.SEND_EMAIL_SEND_TEST_ALARM :
    body.append('<tr style="font-weight: bold; color:white; background-color: green;">TEST EMAIL ALARM MESSAGE SUCCESSFUL')
    body.append('</tr>')

    # SEND ALARM EMAIL REPORT
  elif emailtype == systemConstants.SEND_EMAIL_SEND_ALARM_REPORT or \
       emailtype == systemConstants.SEND_EMAIL_SEND_TEST_ALARM_REPORT:

    # We are majorly cheating. We are using the alarmRecsList parameter, but it is really self.alarmReportInfo...So rename it.
    body.append("<div>")
    body.append("<h2 align=center style='text-align:center'>" + siteInfo["name"] + "</h2>")
    
#    body.append('<td>')
#    body.append('</td>')

    # Determine current time from the currentReportTime
    currReportTime = alarmRecsList["currentReportTime"]
    dtCurrReportTimeUTC = datetime.datetime.strptime( currReportTime, "%Y-%m-%d %H:%M:%S" )
    currReportTimeLocal = (dtCurrReportTimeUTC- utcToLocalDiff)
    strCurrentReportHeaderTime = currReportTimeLocal.strftime("%b/%d/%Y %H:%M:%S") # Format into xx/xx/xx HH:MM:SS
    strCurrentReportTime = currReportTimeLocal.strftime("%a %b %d %Y %H:%M")       # Format into Month DD YYYY HH:MM

    strHtml = "<h2 align=center style='text-align:center'>{0}</h2>".format(strCurrentReportHeaderTime )
    body.append(strHtml)

    # All times are UTC so we need to convert to localtime
    utcToLocalDiff = datetime.datetime.utcnow() - datetime.datetime.now()
    strLastReportTime = alarmReportInfo['lastReportTime']
    dtLastReportTimeUTC= datetime.datetime.strptime( strLastReportTime, "%Y-%m-%d %H:%M:%S" )
    lastReportTimeLocal = (dtLastReportTimeUTC - utcToLocalDiff)
    strLastReportTime = lastReportTimeLocal.strftime("%a %b %d %Y %H:%M")
    fmt = "%Y-%m-%d %H:%M:%S"
    now_time = datetime.datetime.now(timezone('US/Eastern'))
    emailDate = now_time.strftime(fmt)
    #alarmReportAPIData["chainid"] = enableLeoCloudData["chainId"]
    #alarmReportAPIData["storeMarkerId"] = enableLeoCloudData["storeMarkerId"]
    alarmReportAPIData["MACAddress"] = getMACAddress()
    alarmReportAPIData["alarmReportEmail"] = []
    alarmReportAPIDataField={}
    alarmReportAPIDataField["LEOversion"] = LeoVersion
    alarmReportAPIDataField["subject"] = subjectLine
    alarmReportAPIDataField["emailDate"] = emailDate
    alarmReportAPIDataField["reportDate"] = currReportTimeLocal.strftime("%Y-%m-%d %H:%M:%S")
    alarmReportAPIDataField["numActiveAlarms"] = alarmReportInfo['totalActiveAlarms']
    alarmReportAPIDataField["numAlarmEvents"] = alarmReportInfo['totalAlarmEvents']
    alarmReportAPIDataField["createdDateTime"] = emailDate
    alarmReportAPIData["alarmReportEmail"].append(alarmReportAPIDataField)
    alarmReportAPIData["alarmReportRecord"] = []

    strHtml = "<h2 align=center style='text-align:center'>Reporting Alarm Events From {0} to {1}</h2>".format( strLastReportTime, strCurrentReportTime )
    body.append(strHtml)

    body.append("<div align=center>")
    body.append("<table border=0 cellspacing=0 cellpadding=0 style='border-collapse:collapse'>")
    body.append("<tr style='height:.5in'>")
    body.append("<td style='width=auto'>")
    body.append("<h2 align=center style='text-align:center'>Total # Alarm Events:</h2>")
    body.append("</td>")
    body.append("<td width=auto style='width:auto;padding:0in 2pt 0in 2pt;height:.5in'>")
    strHtml = "<h1 align=center style='text-align:center'>{0}</h1>".format( alarmReportInfo['totalAlarmEvents'] )
    body.append(strHtml)
    body.append("</td>")
    body.append("</tr>")
    body.append("<tr style='height:0in'>")
    body.append("<td width=auto style='width:auto;padding:0in 2pt 0in 2pt;height:.5in'>")
    body.append("<h2 align=center style='text-align:center'>Total # Active Alarms:</h2>")
    body.append("</td>")
    body.append("<td width=auto style='width:auto;padding:0in 2pt 0in 2pt;height:.5in'>")
    strHtml = "<h1 align=center style='text-align:center'>{0}</h1>".format( alarmReportInfo['totalActiveAlarms'] )
    body.append(strHtml)
    body.append("</td>")
    body.append("</tr>")
    body.append("</table>")
    body.append("</div>")

    # Only write out the table header and entries if there are actually entries
    if alarmReportInfo['totalAlarmEvents'] > 0 or alarmReportInfo['totalActiveAlarms'] > 0 :
      # Table Header Row
      
      body.append("<div align=center>")
      body.append("<table border=1 cellpadding=0 style='border:solid windowtext 1.0pt'>")
      body.append("<tr>")
      body.append("<td colspan=4 valign=top style='border:solid windowtext 1.0pt;background: seashell;padding:0in 6pt 0in 6pt'>")
      body.append("<h3 align=center style='margin-top:4pt;text-align:center'>Alarm Summary</h3>")
      body.append("<h5 align=right><span style='font-size:14.0pt;color:#F96E6E;'>&#9644;</span> &nbsp;: Annunciated&nbsp;")
      body.append("<span style='font-size:14.0pt;color:#f2ec48;'>&#9644; </span>&nbsp;: Filtered</h5>")
      body.append("</td>")
      body.append("</tr>")
      body.append("<tr>")
      body.append("<td valign=center style='border:solid windowtext 1.0pt;padding:0in 2pt 0in 2pt'>")
      body.append("<p align=center style='text-align:center'><b>Alarm Message</b></p>")
      body.append("</td>")
      body.append("<td valign=center style='border:solid windowtext 1.0pt;padding:0in 2pt 0in 2pt'>")
      body.append("<p align=center style='text-align:center'><b>Occurrences</b></p>")
      body.append("</td>")
      body.append("<td valign=center style='border:solid windowtext 1.0pt;padding:0in 2pt 0in 2pt'>")
      body.append("<p align=center style='text-align:center'><b>Active</b></p>")
      body.append("</td>")
      body.append("<td valign=center style='border:solid windowtext 1.0pt;padding:0in 2pt 0in 2pt'>")
      body.append("<p align=center style='text-align:center'><b>Active Duration (HH:MM:SS)</b></p>")
      body.append("</td>")
      body.append("</tr>")
      conn = dbUtils.getSystemDatabaseConnection()
      cur = conn.cursor()
      
      cur.execute("SELECT * FROM miscsettings where enunciatedAlarmFiltersActive = 1")
      systemEnableVal = cur.fetchall()
      val = []
      if(len(systemEnableVal) >0):
        cur.execute("SELECT alarm FROM enunciatedAlmFilters where enable = 1")
        systemAll = cur.fetchall()
        for i in systemAll:
          val.append(i[0])
      # Alarm Summary
        val.append("LEO Network Failure")
      conn.close()
      stringRed =""
      stringYellow = ""
      for summaryEntry in alarmReportInfo['alarmSummaryList'] :
        #body.append("<tr>")
        alarmReportAPIDataRecords = {}
        if(len(systemEnableVal) >0):

			if summaryEntry[1] in val or (any(value in summaryEntry[1] for value in val)):
			  alarmReportAPIDataRecords["alarmType"] =  "a"
			  stringRed = stringRed + "<tr>"
			  stringRed = stringRed + "<td valign=center style='border:solid windowtext 1.0pt;padding:0in 2pt 0in 2pt;font-weight: bold; background-color: #F96E6E;'>"
			  strHtml = "<p>{0} | {1}</p>".format( summaryEntry[0], summaryEntry[1] )
			  alarmReportAPIDataRecords["alarmApp"] = str(summaryEntry[0])
			  alarmReportAPIDataRecords["alarmText"] = str(summaryEntry[1])
			  stringRed = stringRed + strHtml
			  stringRed = stringRed +"</td>"
			  stringRed = stringRed +"<td valign=center style='border:solid windowtext 1.0pt;padding:0in 2pt 0in 2pt'>"
			  stringRed = stringRed +"<p align=center style='text-align:center'>" + str( summaryEntry[2] )  + "</p>"
			  alarmReportAPIDataRecords["alarmNumOccur"] = summaryEntry[2]
			  stringRed = stringRed +"</td>"
			  stringRed = stringRed +"<td align=center style='border:solid windowtext 1.0pt;padding:0in 2pt 0in 2pt'>"
			  if summaryEntry[3] is True :
				stringRed = stringRed +"<span style='font-size:16.0pt;color:red'>&#9679;</span></p>"
				alarmReportAPIDataRecords["alarmActive"] = "*"
			  else :
				stringRed = stringRed +"<p align=center style='text-align:center'>&nbsp;</p>"
				alarmReportAPIDataRecords["alarmActive"] = ""
			  stringRed = stringRed +"</td>"
			  stringRed = stringRed +"<td valign=center style='border:solid windowtext 1.0pt;padding:0in 2pt 0in 2pt'>"
			  stringRed = stringRed +"<p align=center style='text-align:center'>" + str( summaryEntry[4] )  + "</p>"
			  alarmReportAPIDataRecords["emailDate"] = emailDate
			  alarmReportAPIDataRecords["duration"] =  str( summaryEntry[4] )
			  stringRed = stringRed +"</td>"
			  stringRed = stringRed +"</tr>"
			else:
			  if (len(val)) == 0:
				backgroundColor = "#F96E6E;"
			  else:
				backgroundColor = "#f2ec48;"
			  alarmReportAPIDataRecords["alarmType"] =  "f"
			  stringYellow = stringYellow + "<tr>"
			  #stringYellow = stringYellow + "<td valign=center style='border:solid windowtext 1.0pt;padding:0in 2pt 0in 2pt;font-weight: bold; background-color: #f2ec48;'>"
			  strColor = "<td valign=center style='border:solid windowtext 1.0pt;padding:0in 2pt 0in 2pt;font-weight: bold; background-color: {0}'>".format(backgroundColor)
			  stringYellow = stringYellow + strColor
			  strHtml = "<p>{0} | {1}</p>".format( summaryEntry[0], summaryEntry[1] )
			  alarmReportAPIDataRecords["alarmApp"] = str(summaryEntry[0])
			  alarmReportAPIDataRecords["alarmText"] = str(summaryEntry[1])
			  stringYellow = stringYellow + strHtml
			  stringYellow = stringYellow +"</td>"
			  stringYellow = stringYellow +"<td valign=center style='border:solid windowtext 1.0pt;padding:0in 2pt 0in 2pt'>"
			  stringYellow = stringYellow +"<p align=center style='text-align:center'>" + str( summaryEntry[2] )  + "</p>"
			  alarmReportAPIDataRecords["alarmNumOccur"] = summaryEntry[2]
			  stringYellow = stringYellow +"</td>"
			  stringYellow = stringYellow +"<td align=center style='border:solid windowtext 1.0pt;padding:0in 2pt 0in 2pt'>"
			  if summaryEntry[3] is True :
				stringYellow = stringYellow +"<span style='font-size:16.0pt;color:red'>&#9679;</span></p>"
				alarmReportAPIDataRecords["alarmActive"] = "*"
			  else :
				stringYellow = stringYellow +"<p align=center style='text-align:center'>&nbsp;</p>"
				alarmReportAPIDataRecords["alarmActive"] = ""
			  stringYellow = stringYellow +"</td>"
			  stringYellow = stringYellow +"<td valign=center style='border:solid windowtext 1.0pt;padding:0in 2pt 0in 2pt'>"
			  stringYellow = stringYellow +"<p align=center style='text-align:center'>" + str( summaryEntry[4] )  + "</p>"
			  alarmReportAPIDataRecords["emailDate"] = emailDate
			  alarmReportAPIDataRecords["duration"] =  str( summaryEntry[4] )
			  stringYellow = stringYellow +"</td>"
			  stringYellow = stringYellow +"</tr>"
        else:
		  alarmReportAPIDataRecords["alarmType"] =  "a"
		  stringRed = stringRed + "<tr>"
		  stringRed = stringRed + "<td valign=center style='border:solid windowtext 1.0pt;padding:0in 2pt 0in 2pt;font-weight: bold; background-color: #F96E6E;'>"
		  strHtml = "<p>{0} | {1}</p>".format( summaryEntry[0], summaryEntry[1] )
		  alarmReportAPIDataRecords["alarmApp"] = str(summaryEntry[0])
		  alarmReportAPIDataRecords["alarmText"] = str(summaryEntry[1])
		  stringRed = stringRed + strHtml
		  stringRed = stringRed +"</td>"
		  stringRed = stringRed +"<td valign=center style='border:solid windowtext 1.0pt;padding:0in 2pt 0in 2pt'>"
		  stringRed = stringRed +"<p align=center style='text-align:center'>" + str( summaryEntry[2] )  + "</p>"
		  alarmReportAPIDataRecords["alarmNumOccur"] = summaryEntry[2]
		  stringRed = stringRed +"</td>"
		  stringRed = stringRed +"<td align=center style='border:solid windowtext 1.0pt;padding:0in 2pt 0in 2pt'>"
		  if summaryEntry[3] is True :
			stringRed = stringRed +"<span style='font-size:16.0pt;color:red'>&#9679;</span></p>"
			alarmReportAPIDataRecords["alarmActive"] = "*"
		  else :
			stringRed = stringRed +"<p align=center style='text-align:center'>&nbsp;</p>"
			alarmReportAPIDataRecords["alarmActive"] = ""
		  stringRed = stringRed +"</td>"
		  stringRed = stringRed +"<td valign=center style='border:solid windowtext 1.0pt;padding:0in 2pt 0in 2pt'>"
		  stringRed = stringRed +"<p align=center style='text-align:center'>" + str( summaryEntry[4] )  + "</p>"
		  alarmReportAPIDataRecords["emailDate"] = emailDate
		  alarmReportAPIDataRecords["duration"] =  str( summaryEntry[4] )
		  stringRed = stringRed +"</td>"
		  stringRed = stringRed +"</tr>"

        alarmReportAPIData["alarmReportRecord"].append(alarmReportAPIDataRecords)
      body.append(stringRed)
      body.append(stringYellow)
      body.append("</table>")
      body.append("</div>")
      body.append("<p align=center style='text-align:center'>&nbsp;</p>")
      body.append("</div>")
    #log.debug(alarmReportAPIData)
  return bodyheader + ''.join(body) + bodytail

def returnRecipientList(recipients):
  recipientList = []
  addressSplit = recipients.split(";")
  for address in addressSplit:
    address = address.strip()
    if len(address) > 0:
      recipientList.append(address)
  return recipientList

def formatEmailSubject( alarmRecsList, siteInfo, emailtype ):
  return _getSubject(alarmRecsList, siteInfo, emailtype)

def formatEmailBody( subjectLine, alarmRecsList, siteInfo, emailtype ):
  return _getBody(subjectLine, alarmRecsList, siteInfo, emailtype)

def sendEmail(emailSettings, formattedSubjectLine, formattedBody ):

#  subjectLine = _getSubject(alarmRecsList, siteInfo, emailtype )

#  body = _getBody(subjectLine, alarmRecsList, siteInfo, emailtype )

  msg = MIMEMultipart('mixed')
  conn = dbUtils.getSystemDatabaseConnection()
  cur = conn.cursor()
  cur.execute("SELECT * FROM emailservers where defaultServer= 1")
  serverInfo = cur.fetchone()

  recipients = emailSettings["toaddress"]
  fromSender = serverInfo["fromaddress"]
  msg['Subject'] = formattedSubjectLine
  msg['From'] = serverInfo["fromaddress"] #fromSender
  msg['To'] = recipients
  conn.close()
  enableLeoCloud = getEnableLeoCloudValue()

  html_message = MIMEText(formattedBody, 'html')
#    msg.attach(text_message)
  msg.attach(html_message)

  result = {}

  try:

    #log.debug(os.path.dirname(os.path.abspath(__file__)))
    cwd = os.getcwd() + "/system"  # Get the current working directory (cwd)
    #files = os.listdir(cwd)  # Get all the files in that directory
    #print("Files in %r: %s" % (cwd, files))
    conn = dbUtils.getSystemDatabaseConnection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM emailaddresses")
    systemAll = cur.fetchall()
    val = 0
    systemInfo = {}
    systemInfoToAddress = ""
    for abc in systemAll:
      val = val + 1
      if val >6:
        systemInfoToAddress = abc["toaddress"]
        systemInfoEmailServer = abc["emailservername"]
    if (msg['Subject'].find("Alarm Report")>=0) and (msg['To'] == systemInfoToAddress) and (enableLeoCloud["enableLeoCloud"] == 2):
      data = sendAlarmAPICall("AlarmReport")
      filename = cwd+"/AlarmReport.txt"
      #log.debug(filename)
      result['strEmailStatus'] = 'Sent Alarm Report API Call Succesfully To LEO CLOUD'
      result['blSendSuccess'] = True
      if "results" in data:
        result['strEmailStatus'] = 'Sent Alarm Report API Call Succesfully To LEO CLOUD'
        result['blSendSuccess'] = True
        if data["results"]!="success":
          writeDataToFile("AlarmReport")
          result['strEmailStatus'] = 'Sent Alarm Report API Call Failed To Send Data To LEO CLOUD'
          result['blSendSuccess'] = True
        # elif data["results"]=="success":
          # dirname = os.path.dirname(filename)
          # #log.debug(dirname)
          # if not os.path.exists(filename):
            # createNewFile(filename)
          # with open(filename, 'w') as fp:
            # fp.close();
      else:
        result['strEmailStatus'] = 'Sent Alarm Report API Call Failed To Send Data To LEO CLOUD'
        result['blSendSuccess'] = True
        #if "Error" in data:
        writeDataToFile("AlarmReport")
    elif (msg['Subject'].find("New Alarm")>=0) and (msg['To'] == systemInfoToAddress) and (enableLeoCloud["enableLeoCloud"] == 2):
      data = sendAlarmAPICall("AlarmEmail")
      filename = cwd+"/AlarmEmail.txt"
      if "results" in data:
        result['strEmailStatus'] = 'Sent New Alarm Email API Call Succesfully To LEO CLOUD'
        result['blSendSuccess'] = True
        if data["results"]!="success":
          writeDataToFile("AlarmEmail")
          result['strEmailStatus'] = 'Sent New Alarm Email API Call Failed To Send Data To LEO CLOUD'
          result['blSendSuccess'] = True
        # elif data["results"]=="success":
          # dirname = os.path.dirname(filename)
          # if not os.path.exists(filename):
            # createNewFile(filename)
          # with open(filename, 'w') as fp:
            # fp.close();
      else:
        result['strEmailStatus'] = 'Sent New Alarm Email API Call Failed To Send Data To LEO CLOUD'
        result['blSendSuccess'] = True
        #if "Error" in data:
        writeDataToFile("AlarmEmail")

    else:
      if (msg['To'] == systemInfoToAddress) and (enableLeoCloud["enableLeoCloud"] == 0):
        doNothing = 0
        result['strEmailStatus'] = 'LEO Cloud Is Disabled'
        result['blSendSuccess'] = True
      else:
        mailServer = smtplib.SMTP("localhost",25)  # 8025, 587 and 25 can also be used. emailSettings["smtpserver"], int(emailSettings["smtpport"])
        mailServer.ehlo()
        if serverInfo["enabletls"] != 0:
          mailServer.starttls()
        mailServer.ehlo()
      # if emailSettings["enableauthentication"] != 0:    Authentication is not required as this will be handled by postfix to the external server.
        # mailServer.login(str(emailSettings["authaccount"]), str(emailSettings["authpassword"]))
        mailServer.sendmail(fromSender, recipients, msg.as_string())
        mailServer.close()
        result['strEmailStatus'] = 'Sent Email Succesfully To:{0} Using:{1}'.format( recipients, serverInfo["authaccount"])
        result['blSendSuccess'] = True
      log.debug( result['strEmailStatus'] )

  except Exception, e:
    result['strEmailStatus'] = 'Send Email ERROR = {0} {1} - To:{2} Using:{3}. NO email alarm was delivered.'.format( e, Exception, recipients, serverInfo["authaccount"] )
    result['blSendSuccess'] = False
    log.debug( result['strEmailStatus'] )

  return result

def _getDataBody( logCloudData, siteInfo, formattedSubjectLine):

  bodyheader = ('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
          '<html xmlns="http://www.w3.org/1999/xhtml">'
          '<head>'
          '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /></head>'
          '<body>')

  # Append "hidden" leo version at the end of each email.
  htmlLeoVersion = '<p><span style="color:white">LEO Version: {0} ({1})</span></p>'.format( version.versionInfo['LeoVersionNumber'], version.versionInfo['LeoVersionDate'] )
  bodytail = ( htmlLeoVersion + '</body></html>')

  body = []
  body.append ('<h2>' + formattedSubjectLine + '</h2>')
  body.append('<p>' + siteInfo + '</p>')

  # All times are UTC so we need to convert to localtime
  utcToLocalDiff = datetime.datetime.utcnow() - datetime.datetime.now()

  # We are majorly cheating. We are using the alarmRecsList parameter, but it is really self.alarmReportInfo...So rename it.
  logCloudData = logCloudData

  body.append("<div>")
  body.append("<h2 align=center style='text-align:center'>" + siteInfo + "</h2>")
    
#    body.append('<td>')
#    body.append('</td>')

    # # Determine current time from the currentReportTime
    # currReportTime = alarmRecsList["currentReportTime"]
    # dtCurrReportTimeUTC = datetime.datetime.strptime( currReportTime, "%Y-%m-%d %H:%M:%S" )
    # currReportTimeLocal = (dtCurrReportTimeUTC- utcToLocalDiff)
    # strCurrentReportHeaderTime = currReportTimeLocal.strftime("%b/%d/%Y %H:%M:%S") # Format into xx/xx/xx HH:MM:SS
    # strCurrentReportTime = currReportTimeLocal.strftime("%a %b %d %Y %H:%M")       # Format into Month DD YYYY HH:MM

    # strHtml = "<h2 align=center style='text-align:center'>{0}</h2>".format(strCurrentReportHeaderTime )
    # body.append(strHtml)

    # # All times are UTC so we need to convert to localtime
    # utcToLocalDiff = datetime.datetime.utcnow() - datetime.datetime.now()
    # strLastReportTime = alarmReportInfo['lastReportTime']
    # dtLastReportTimeUTC= datetime.datetime.strptime( strLastReportTime, "%Y-%m-%d %H:%M:%S" )
    # lastReportTimeLocal = (dtLastReportTimeUTC - utcToLocalDiff)
    # strLastReportTime = lastReportTimeLocal.strftime("%a %b %d %Y %H:%M")

    # strHtml = "<h2 align=center style='text-align:center'>Reporting Alarm Events From {0} to {1}</h2>".format( strLastReportTime, strCurrentReportTime )
    # body.append(strHtml)


    # Only write out the table header and entries if there are actually entries

      # Table Header Row
  body.append("<div align=center>")
  body.append("<table border=1 cellpadding=0 style='border:solid windowtext 1.0pt'>")
  body.append("<tr>")
  body.append("<td colspan=4 valign=top style='border:solid windowtext 1.0pt;background: #FFCC99;padding:0in 6pt 0in 6pt'>")
  body.append("<h3 align=center style='margin-top:4pt;text-align:center'>Data Logs</h3>")
  body.append("</td>")
  body.append("</tr>")
  body.append("<tr>")
  body.append("<td valign=center style='border:solid windowtext 1.0pt;padding:0in 2pt 0in 2pt'>")
  body.append("<p align=center style='text-align:center'><b>Controller Name</b></p>")
  body.append("</td>")
  body.append("<td valign=center style='border:solid windowtext 1.0pt;padding:0in 2pt 0in 2pt'>")
  body.append("<p align=center style='text-align:center'><b>Application Name</b></p>")
  body.append("</td>")
  body.append("<td valign=center style='border:solid windowtext 1.0pt;padding:0in 2pt 0in 2pt'>")
  body.append("<p align=center style='text-align:center'><b>Value</b></p>")
  body.append("</td>")
  body.append("<td valign=center style='border:solid windowtext 1.0pt;padding:0in 2pt 0in 2pt'>")
  body.append("<p align=center style='text-align:center'><b>Date Time</b></p>")
  body.append("</td>")
  body.append("</tr>")

      # Alarm Summary
  for summaryEntry in logCloudData :
    for x in logCloudData[summaryEntry]:
      body.append("<tr>")
      body.append("<td valign=center style='border:solid windowtext 1.0pt;padding:0in 2pt 0in 2pt'>")
      strHtml = "<p>{0}</p>".format( summaryEntry )
      body.append(strHtml)
      body.append("</td>")
      body.append("<td valign=center style='border:solid windowtext 1.0pt;padding:0in 2pt 0in 2pt'>")
      body.append("<p align=center style='text-align:center'>" + str( logCloudData[summaryEntry][x]['valueKey'] )  + "</p>")
      body.append("</td>")
      body.append("<td valign=center style='border:solid windowtext 1.0pt;padding:0in 2pt 0in 2pt'>")
      body.append("<p align=center style='text-align:center'>" + str( logCloudData[summaryEntry][x]['value'] )  + "</p>")
      body.append("</td>")
      body.append("<td valign=center style='border:solid windowtext 1.0pt;padding:0in 2pt 0in 2pt'>")
      body.append("<p align=center style='text-align:center'>" + str( logCloudData[summaryEntry][x]['date']  )  + "</p>")
      body.append("</td>")
      body.append("</tr>")
  body.append("</table>")
  body.append("</div>")
  body.append("<p align=center style='text-align:center'>&nbsp;</p>")
  body.append("</div>")

  return bodyheader + ''.join(body) + bodytail

def sendDataEmail(logCloudData, siteName, len1 ):

#  subjectLine = _getSubject(alarmRecsList, siteInfo, emailtype )

  conn = dbUtils.getSystemDatabaseConnection()
  cur = conn.cursor()
  cur.execute("SELECT enableLeoCloud FROM system")
  systemAll = getEnableLeoCloudValue()
  #log.debug(systemAll)
  enableLeoCloud = systemAll["enableLeoCloud"]
  #log.debug(enableLeoCloud)
  #chainId = systemAll["chainId"]
  #storeMarkerId = systemAll["storeMarkerId"]
  if enableLeoCloud == 2:
    data = sendDataEmailAPICall(logCloudData, siteName, len1 )
    filename = "DataEmail.txt"
    if "results" in data:
      if data["results"]!="success":
        writeDataToFile("DataEmail")
        result = 'Send Data Email API Call Failed to send data'
      elif data["results"]=="success":
        # dirname = os.path.dirname(filename)
        # if not os.path.exists(filename):
          # createNewFile(filename)
        # with open(filename, 'w') as fp:
          # fp.close();
        result = 'Send Data Email API Call Succesfully Sent Data'
    else:
      writeDataToFile("DataEmail")
      result = 'Send Data Email API Call Failed to send data'
  else:
    formattedSubjectLine = "{} - Data Report - {} Total Devices".format(siteName, len1)
    formattedBody = _getDataBody(logCloudData, siteName, formattedSubjectLine)

    msg = MIMEMultipart('mixed')



    html_message = MIMEText(formattedBody, 'html')
#    msg.attach(text_message)
    msg.attach(html_message)

    conn = dbUtils.getSystemDatabaseConnection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM emailaddresses")
    systemAll = cur.fetchall()
    val = 0
    systemInfo = {}
    for abc in systemAll:
      val = val + 1
      if val >6:
        systemInfoToAddress = abc["toaddress"]
        systemInfoEmailServer = abc["emailservername"]
    #log.debug(systemInfoToAddress)
    #log.debug(systemInfoEmailServer)
    cur.execute("SELECT * FROM emailservers where defaultServer= 1")
    serverInfo = cur.fetchone()
    serverSmtp = "localhost" #serverInfo["smtpserver"] This is the hard coded values for implementing local postfix email server inside the LEO itself
    serverPort = 25 #serverInfo["smtpport"]
    authAccount = serverInfo["authaccount"]
    authPassword = serverInfo["authpassword"]
    recipients = systemInfoToAddress #"leoalarmstatus@gmail.com"
    fromSender = serverInfo["fromaddress"] #"hltechmember2@gmail.com"
    msg['Subject'] = formattedSubjectLine
    msg['From'] = fromSender
    msg['To'] = recipients
    conn.close()

    if recipients:

      try:
        #log.debug(bool(recipients))
        mailServer = smtplib.SMTP(serverSmtp, int(serverPort))  # 8025, 587 and 25 can also be used.
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        #mailServer.login(str(authAccount), str(authPassword))
        mailServer.sendmail(str(fromSender), str(recipients), msg.as_string())
        mailServer.close()
        result = 'Sent Data Log Email Succesfully To:{0} Using:{1}'.format( recipients, authAccount )
        log.debug( result )

      except Exception, e:
        result = 'Send Data Log Email ERROR = {0} {1} - To:{2} Using:{3}. NO email alarm was delivered.'.format( e, Exception, recipients, fromSender )

        log.debug( result )
    else:
      result = 'Send Data Log Email ERROR - No EMAIL Was Assigned to send data logs'

  return result

def sendDataEmailAPICall(logCloudData, siteName, len1 ):

  #log.debug("inside data email api call")
  cwd = os.getcwd() + "/system"
  url = "https://api.leocloud.us/app/DataEmailRecord"
  #requestData["chainid"] = chainId
  #requestData["storeMarkerId"] = storeMarkerId
  requestData["devicesLength"] = len1
  requestData["MACAddress"] = getMACAddress()
  requestData["data"] = []
  dataValues = {}
  # filename = cwd+"/DataEmail.txt"
  # dirname = os.path.dirname(filename)
  #log.debug(dirname)
  # if not os.path.exists(filename):
    # createNewFile(filename)
  # with open(filename) as json_file:
    # data = json_file.read()
    # if len(data) >0:
      # data = json.loads(data)
      # requestData["data"].extend(data)
  fmt = "%Y-%m-%d %H:%M:%S"
  now_time = datetime.datetime.now(timezone('US/Eastern'))
  emailDate = now_time.strftime(fmt)
  for summaryEntry in logCloudData :

    for x in logCloudData[summaryEntry]:
      dataValues = {}
      dataValues["emailDate"] = str(emailDate)
      dataValues["controllerName"] = str(summaryEntry)
      dataValues["applicationName"] = str( logCloudData[summaryEntry][x]['valueKey'] )
      dataValues["dataVal"] = str(logCloudData[summaryEntry][x]['value']) 
      dataValues["dataLogDate"] = str( logCloudData[summaryEntry][x]['date'] )
      requestData["data"].append(dataValues)
  #log.debug(requestData)
  responseData = sendAlarmAPICall("DataEmail")
  return responseData
  
def getEnableLeoCloudValue():
  conn = dbUtils.getSystemDatabaseConnection()
  cur = conn.cursor()
  cur.execute("SELECT enableLeoCloud FROM system")
  systemAll = cur.fetchall()
  #log.debug(systemAll)
  result = {}
  result["enableLeoCloud"] = systemAll[0]["enableLeoCloud"]
  #result["chainId"] = systemAll[0]["chainId"]
  #result["storeMarkerId"] = systemAll[0]["storeMarkerId"]
  #log.debug(result)
  return result
  
def sendAlarmAPICall(emailType):
  #cwd = os.getcwd() + "/system"
  headers = {
	  'accept': "application/json",
	  'content-type': "application/json",
	  'authorization': "Basic TEVPQVBJOkcwUjNkVDNAbSE=",
	  'cache-control': "no-cache"
	  }

  if emailType == "AlarmReport":
    #log.debug("inside Alarm Report email api call")
    url = "https://api.leocloud.us/app/AlarmReports"
    payload = alarmReportAPIData
  elif emailType == "AlarmEmail":
    #log.debug("inside Alarm Email api call")
    url = "https://api.leocloud.us/app/AlarmEmails"
    payload = alarmEmailAPIData
  elif emailType == "DataEmail":
    #log.debug("inside Data Email api call")
    url = "https://api.leocloud.us/app/DataEmailRecord"
    payload = requestData
  response = pushOutAPICalls(emailType, url, headers, payload)
  #log.debug(json.dumps(payload))
  # pingResponse = os.system("ping -c 1 " + hostName)
  # if pingResponse == 0:
    # response = requests.post( url, data=json.dumps(payload), headers=headers)
    # log.debug(response.content)
    # return json.loads(response.content)
  # else:
    # string = '{"results": "failed"}'
    # return json.loads(string)
  return response
  

  

def writeDataToFile(emailType):
  strPrint = "Writing Data into text files for '{0}' API Call ".format(emailType)
  log.debug(strPrint)
  cwd = os.getcwd() + "/system"
  previousData = []
  fmt = "%Y-%m-%d %H:%M:%S"
  now_time = datetime.datetime.now(timezone('US/Eastern'))
  fileDate = now_time.strftime(fmt)
  if emailType == "AlarmReport":
    cwd = os.getcwd() + "/system/AlarmReportData"
    filename = cwd+"/AlarmReport" + str(fileDate) + ".txt"
    dirname = os.path.dirname(filename)
    #log.debug(dirname)
    if not os.path.exists(filename):
      createNewFile(filename)
    previousData=alarmReportAPIData["alarmReportRecord"]
    # with open(filename) as json_file:
      # data = json_file.read()
      # if len(data) >0:
        # data = json.loads(data)
        # previousData.extend(data)
    with open(filename, 'w') as outfile:
      json.dump(previousData, outfile)
  elif emailType == "AlarmEmail":
    cwd = os.getcwd() + "/system/AlarmEmailData"
    previousData=alarmEmailAPIData["alarmEmailRecord"]
    filename = cwd+"/AlarmEmail" + str(fileDate) + ".txt"
    dirname = os.path.dirname(filename)
    #log.debug(dirname)
    if not os.path.exists(filename):
      createNewFile(filename)
    # with open(filename) as json_file:
      # data = json_file.read()
      # if len(data) >0:
        # data = json.loads(data)
        # previousData.extend(data)
    with open(filename, 'w') as outfile:
      json.dump(previousData, outfile)
  elif emailType == "DataEmail":
    cwd = os.getcwd() + "/system/DataEmailData"
    filename = cwd+"/DataEmail" + str(fileDate) + ".txt"
    dirname = os.path.dirname(filename)
    #log.debug(dirname)
    if not os.path.exists(filename):
      createNewFile(filename)
    previousData=requestData["data"]
    # with open(filename) as json_file:
      # data = json_file.read()
      # if len(data) >0:
        # data = json.loads(data)
        # previousData.extend(data)
    with open(filename, 'w') as outfile:
      json.dump(previousData, outfile)
  return True
  
def createNewFile(file_path):
    strPrint = "Creating A New File - {0}".format(file_path)
    log.debug(strPrint)
    file_object = open(file_path, 'w')
    file_object.close()
    return True

def pushOutAPICalls(emailType, url, headers, payload):
  cwd = os.getcwd() + "/system/"+emailType+"Data"  # Get the current working directory (cwd)
  #log.debug(cwd)
  files = os.listdir(cwd)
  try:
    response = requests.post( url, data=json.dumps(payload), headers=headers)
    log.debug(str(response.content))
    responseValue = json.loads(response.content)
    if len(files)>0:
      for file in files:
        filePath = cwd+"/"+file
        #log.debug(filePath)
        with open(filePath) as json_file:
          data = json_file.read()
          data = json.loads(data)
        if emailType =="AlarmReport":
          payload["alarmReportRecord"] = []
          payload["alarmReportRecord"].extend(data)
        elif emailType =="AlarmEmail":
          payload["alarmEmailRecord"] = []
          payload["alarmEmailRecord"].extend(data)
        elif emailType =="DataEmail":
          payload["data"] = []
          payload["data"].extend(data)
        response = requests.post( url, data=json.dumps(payload), headers=headers)
        log.debug(str(response.content))
        responseValue = json.loads(response.content)
        if("results" in responseValue):
          if responseValue["results"] == "success":
            os.remove(filePath)
    return responseValue
  except Exception, e:
    result = 'Send {0} API Call ERROR {1} - {2}  inside pushOutAPICalls for Directory {3}'.format( emailType, e, Exception, cwd )
    log.debug(result)
    responseValue = json.loads('{"results":"failed"}')
    return responseValue
    
        

def getMACAddress():
  IPConfig = LeoFlaskUtils.getNetworkStackIPInfo()
  HWAddr = IPConfig['HW_ADDR']
  return HWAddr








