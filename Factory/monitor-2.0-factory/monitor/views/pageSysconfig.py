from flask_restful import Resource
from flask import render_template, Response, session, current_app as app
import leoObject
import networkConstants
import LeoFlaskUtils
import os

class pageSysconfig(Resource):
    def __init__(self):
        self.gLeonardo = leoObject.getLeoObject()

    def get(self):

#      print "session = ", session

      ctx = LeoFlaskUtils.prepareContext("pageSysconfig")

      if 'can_edit_system' in session and session['can_edit_system'] == True:

        # Get Site Status
        sysObj = self.gLeonardo.directory.getSystemObject()
        dataSiteStatus = dict(sysObj.getSiteInfo().items() + self.gLeonardo.directory.getAlarmManager().getAlarmStatus().items())
        dataTimeInfo = dict( sysObj.getCurrentTime() )
        # Need to change data type from  datetime.datetime to string for html processing.
        dataTimeInfo['currentTime'] = str( dataTimeInfo['currentTime'] )

        # Get Version 2 of the email settings.
        dataEmailSettings = dict( self.gLeonardo.directory.getSystemObject().getEmailSettings( 2 ) )

        dataDeviceTypes = dict( self.gLeonardo.directory.getDeviceManager().getDeviceTypes() )

        dataDevices = dict( self.gLeonardo.directory.getDeviceManager().getDevices() )

        dataNetworkTypes = dict( self.gLeonardo.directory.getNetworkManager().getNetworkTypes() )

        dataNetworks = dict( self.gLeonardo.directory.getNetworkManager().getNetworks().items() )

        dataEthernet = dict( self.gLeonardo.directory.getSystemObject().getEthernetSettings() )

        dataSystemSettings = dict( self.gLeonardo.directory.getSystemObject().getSystemSettings() )

        dataEnunciatedAlarmFilters = dict( self.gLeonardo.directory.getAlarmManager().getEnunciatedAlarmFilters() )

        dataE2Settings = {}
        networkDict = self.gLeonardo.directory.getNetworkManager().getNetworks()
        if networkDict != None:
            # Since orderedDict, netrec will only be key into NetworkDict.
            for netrec in networkDict:
                if networkDict[netrec]['typeName'].find(networkConstants.networkE2NetText) == 0:
                    E2NetObject = self.gLeonardo.directory.getDeviceManager().getNetworkObjectByName(networkDict[netrec]['name'])
                    if E2NetObject != None :
                      dataE2Settings = dict( E2NetObject.getE2Settings() )

#        print "siteStatus =", dataSiteStatus, "type =", type(dataSiteStatus)
#        print "timeInfo = ", dataTimeInfo, "type = ", type(dataTimeInfo)
#        print "emailSettings = ", dataEmailSettings, "type = ", type(dataEmailSettings)
#        print "devicesTypes = ", dataDeviceTypes, "type = ", type(dataDeviceTypes)
#        print "networkTypes = ", dataNetworkTypes, "type = ", type(dataNetworkTypes)
#        print "ethernet = ", dataEthernet, "type = ", type(dataEthernet)
#        print "systemSettings = ", dataSystemSettings, "type = ", type(dataSystemSettings)
#        print "e2Settings = ", dataE2Settings, "type = ", type(dataE2Settings)
#        print "deviceList = ", dataDevices, "type = ", type(dataDevices)
#        print "networkList = ", dataNetworks, "type = ", type(dataNetworks)

        urlImagePath = '/static/uimg/devices'
        imgFilelist = os.listdir( app.root_path + urlImagePath )
    #        print "urlImage", urlImagePath
    #        print "Image Files = ", imgFilelist

        # If the ethernet is statically defined, the ethernet values will come from the database.
        # However, if we are using DHCP, we don't store the IP address in the database because it is
        # dynamic. So instead we will "plug" in the IP settings as determined at startup of the system.
        # through the ifconfig output capture and stored in the session.
        # Now, if we are running on the PC, the IpAddr will be 'Unknown', so just simply put
        # a little information to inform the UI of this case.
        if dataEthernet['dhcp'] > 0 :
          dataEthernet['address'] = app.dictIPInfo['IP_ADDR']
          dataEthernet['gateway'] = app.dictIPInfo['IP_GATEWAY']
          dataEthernet['netmask'] = app.dictIPInfo['IP_MASK']
          dataEthernet['dnsaddress'] = app.dictIPInfo['DNS_ADDRESS']

        template = 'pageSysconfig.html'

        return Response(render_template(ctx['clienttype']+'/'+template, ctx=ctx, mimetype='text/html',
                        siteStatus = dataSiteStatus, timeInfo = dataTimeInfo,
                        emailSettings = dataEmailSettings,
                        deviceTypes = dataDeviceTypes, devices = dataDevices,
                        networkTypes = dataNetworkTypes, networks = dataNetworks,
                        ethernet = dataEthernet,systemSettings = dataSystemSettings,
                        imageFiles = imgFilelist,
                        imagePath = urlImagePath,
                        e2Settings = dataE2Settings, showDevices = 1,
                        enunciatedAlarmFilters = dataEnunciatedAlarmFilters ) )
