var statusLayout = (function() {

  var siteMapImageDir = 'static/local/img/sitemap/';
  var leoWaitingGif = 'static/local/img/pleasewait.gif';
  var leoUserImageDir = 'static/uimg/devices/';
  var iWidgetCount = 0;          // Count of the number of objects/widgets and used as part of the div name.
  var slDeviceName = null;       // Stores device name for statuslayout - from deviceNameIn.

  var $sitemap = $("#sitemap");
  var $table = $("#inptbl");
  var $rows = "";
  var sitemapHeight = 0;
  var sitemapWidth = 0;
  var instruments = [];
  var sbIpTable ="";

  
  
  
  var zoominfo = { zoomlist: [], default: {h: 0, w: 0}, view: {h: 0, w: 0, m: 1},
    push: function(x, y, m) {
      this.zoomlist.push({x: x, y: y, m: m });
      return this.current();
    },
    pop: function() {
      if (this.zoomlist.length > 0) {
        this.zoomlist.pop();
      }
      return this.current();
    },
    current: function() {
      var cur;
      if (this.zoomlist.length > 0) {
        cur = this.zoomlist[this.zoomlist.length - 1];
      }
      else {
        cur = {x: 0, y: 0, m: 1 };
      }
      var view = this.view;
      var ret = {
              x: cur.x * view.w * cur.m,
              y: cur.y * view.h * cur.m,
              w: view.w * cur.m,
              h: view.h * cur.m,
              m: cur.m};
      return ret;
    },
    isfullzoom: function() { return this.zoomlist.length == 0; },
    getBestFitMultiplier: function(width, height, w, h) {
      var m = 1;
      var a = w / h;
      if ((width / a) < height) { m = width / w; } else { m = height / h; }
      return m;
    }
  };

  function getArticleHeight(articleHeight) {
    var $zoomwrapper = $("#zoomwrapper");
    return articleHeight - $zoomwrapper.height();
  }


//*************************************************************************

  var mode = 'view';
  var zoomMode = 'zoom';

  function selectEvent(x1, y1, x2, y2) {

  }

  function instrumentActivate(deviceName) {
    if (mode === "view")
      pageDeviceRedirect(deviceName);
  }

//*************************************************************************


  // $sitemap.selection({

  // Removed because of niceSelect seems to disable .selection...
  //  $sitemap.selection({
//    css: {border: '1px solid rgba(232, 207, 172, 0.8)', backgroundColor: 'rgba(232, 207, 172, 0.4)', zIndex: 1000       },
//  onSelect: function(x1, y1, x2, y2) {
//      if (zoomMode == 'zoom') {
//        zoomEvent(x1, y1, x2, y2);
//      }
//      else {
//          selectEvent(x1, y1, x2, y2);
//      }
//    },
//  });

  function zoomEvent(x1, y1, x2, y2) {
    $("#zoomoutbutton").enable();

    x1 = Math.max(x1, 0);
    y1 = Math.max(y1, 0);

    var current = zoominfo.current();
    var $article = $("#sitemap");

    var articleWidth = $article.width();
    var articleHeight = getArticleHeight($article.height());

    var m = zoominfo.getBestFitMultiplier(articleWidth, articleHeight, x2-x1, y2-y1) * current.m;
    var x = (current.x + x1) / current.w;
    var y = (current.y + y1) / current.h;

    current = zoominfo.push(x, y, m);
    for (var idx = 0; idx < instruments.length; idx++)
      instruments[idx].reposition(current.x, current.y, current.w, current.h, current.m);
  }


  function positionZoomWrapper() {
    var $article = $("#sitemap");
    var articleoffset = $article.offset();
    var articlebottom = articleoffset.top + $article.height() - 5;

    var $zoomwrapper = $("#zoomwrapper");
    $zoomwrapper.offset({ top: articlebottom - $zoomwrapper.height() - 5, left: articleoffset.left });
  }

  //
  // Common initialization and handling for all/most widgets.
  //
  // enumerate widget
  function gInitWidget ( widgetObj ) {
    widgetObj.eleNum = iWidgetCount;
    // If the json's device name is "*", we will replace this name with the current DeviceName.
    if (widgetObj.params.device === "*") {
      // console.log("Changing Name from:", widgetObj.params.device, " to:", deviceName )
      widgetObj.params.device = deviceName;
    }
    ++iWidgetCount;
  }

  // color based upon online status
  function gSetOnlineWidgetColor( widgetObj, online ) {
    if (online) {
      widgetObj.$el.css( { "background-color": "green" } );
    } else {
      widgetObj.$el.css( { "background-color": "gray" } ).fadeTo("slow", 0.1).fadeTo("slow", 1.0);
    }
  }

  // position function call
  function gReposition( wThisObj, x, y, w, h, m ) {
      // console.log( 'B4 wThisObj, x, y, w, h, m', wThisObj, x, y, w, h, m );
      //wThisObj.$el.width(Math.round(wThisObj.params.w / 100.0 * w));
      //wThisObj.$el.height(Math.round(wThisObj.params.h / 100.0 * h));
      var left = Math.round(w * wThisObj.params.x / 100.0 - x);
      var top = Math.round(h * wThisObj.params.y / 100.0 - y);
      // wThisObj.$el.css( { left: left.toString() + "px", top: top.toString() + "px" } );
      // console.log( 'top, left', top, left )
  }


  function GetMultiDeviceInfoJsonErr(a,b,c) {
    // console.log( "ERROR", b, "Details:", c );
    // console.log( 'Error in obtaining device values for ' + deviceName + '. Error:' + c );
    $sitemap.html('Error in obtaining device values for ' + deviceType + '. Error:' + c );
  }

  function statusLayoutJsonErr(a,b,c) {
    console.log( "ERROR", b, "Details:", c );
    $sitemap.html("Error in initialization file or file not found. File:" + siteMapImageDir + deviceType + ".json - Error:" + c );
  }

  pageResize = function($article, articleHeight, articleWidth) {
    positionZoomWrapper();

    if (zoominfo.default.w === 0 || zoominfo.default.h === 0) {
      return;
    }

    //$sitemap.width(articleWidth);
    $sitemap.height(articleHeight);

    articleHeight = getArticleHeight(articleHeight);

    var m = zoominfo.getBestFitMultiplier(articleWidth, articleHeight, zoominfo.default.w, zoominfo.default.h);

    zoominfo.view.w = zoominfo.default.w * m;
    zoominfo.view.h = zoominfo.default.h * m;
    zoominfo.view.m = m;

    var current = zoominfo.current();
    for (var idx = 0; idx < instruments.length; idx++)
      instruments[idx].reposition(current.x, current.y, current.w, current.h, current.m);
  };

  $("#zoomoutbutton").button({icons: { primary: "icon icon-search-minus"}}).disable();
  $("#zoomoutbutton").click(function(event) {
                    event.preventDefault();

    var current = zoominfo.pop();
    for (var idx = 0; idx < instruments.length; idx++)
      instruments[idx].reposition(current.x, current.y, current.w, current.h, current.m);

    if (zoominfo.isfullzoom()) {
      $(this).disable(); }
          });

  function startDataCollection() {
    var params = [];

     // console.log("startDataCollection- slDeviceName, deviceName->", slDeviceName, deviceName )

    // If the deviceName is still active, get the info
    if ( slDeviceName === deviceName ) {
      for (var idx = 0; idx < instruments.length; idx++) {
        valueList = instruments[idx].getValueList();
        if ( valueList !== null && valueList.device !== undefined ) {
          params.push(valueList);
        }
      }

      // console.log("getMultiDeviceInfo->", params )
      pageXHR = postJson({"jsonrpc":"2.0","id":"getMultiDeviceInfo","method":"getMultiDeviceInfo","params": params },
        function(data) {
          // console.log("getMultiDeviceInfo RESPONSE->", data );

          if (data === null) { return; }

          for (var idx = 0; idx < instruments.length; idx++) {
            instruments[idx].updateValues(data);
          }

          pageSetTimeout(function() { startDataCollection(); }, 3000);
        }, GetMultiDeviceInfoJsonErr );
    }
  }

  var init = function(data) {
	  

    Object.keys(data).forEach(function (key) {
      var val = data[key];

      if (key === "size") {
        zoominfo.default.w = val.w;
        zoominfo.default.h = val.h;
      } else if (key === "instruments") {
        for (var idx = 0; idx < val.length; idx++)
          instruments.push(instrumentFactory(val[idx]));
      }
		
    });
	
	//var url =  'static/devPluginUI/' +deviceType+'/'+ '__' +deviceType+'__'+ '.html';
	var uriSpaceDeviceType = encodeURIComponent(deviceType)
	var loc = '/static/devPluginUI/' + uriSpaceDeviceType + '/__' + uriSpaceDeviceType  + '__.html'
	//static/devPluginUI/__LAE BIT25B1S3WH-8TM-GDM-23__.html'
	$("#deviceName").html(deviceType);
  $("#caseName").html(deviceName)

	$('#sitemap').load(loc);

	
    for (var idx = 0; idx < instruments.length; idx++)
    {
      gInitWidget( instruments[idx] );
      instruments[idx].initialize($sitemap);
    }

    // This is a hack for IE 11
    setTimeout(function() { resizeArticle(); startDataCollection(); }, 1);
  };

//************************************************************************

  //
  // IMAGE
  //
  function instrImage(params) {
    this.params = params;
    this.$el = null;
    // console.log( "instr->", params )

    this.reposition = function(x, y, w, h, m) {
      gReposition( this, x, y, w, h, m);
    };

    this.initialize = function($parent) {

      // Need to dynamically update in the case that the image name is "*" (which means that we should use the image uploaded by the user through LEO).
      if ( this.params.device === undefined ) {
        this.params.device = deviceName; // Initialize the device name
      }
      if ( this.params.name === "*" ) {
        // We have problems renderring images on remote vs front display.
        if ( navigator.platform !== "Linux armv7l" ) {    // Need to add style for LEO hardware browser ...
          // Basic HTML...
          this.$el = $('<image id="hlslImg' + this.eleNum + '" src="' + leoWaitingGif + '" />');
        }
        else {
          // Running on 12.04 ubuntu - Linux browser ...Need to add style for the element...
          this.$el = $('<image id="hlslImg'+this.eleNum+'"style="left: calc(17% + 110px + 15px);" src="' + leoWaitingGif + '" />');
        }
        this.updateValues = function(result) {  // Need to make sure image name is up to date and changes as user changes in Leo
          var device = result[this.params.device];
          if ( ( device !== null ) && ( device !== undefined ) ) {// If we have a valid response, update the image URL.
            updateImgSrc = leoUserImageDir + device.deviceInfo.image;
            $("#hlslImg" + this.eleNum).attr("src", updateImgSrc);
          }
        };
      }
      else {
        this.$el = $('<image src="' + siteMapImageDir + this.params.name + '" style="position: absolute; z-index: -1;" />');
        this.updateValues = function(result) {}; // Nothing to do for image named in JSON.
      }

      if ( this.params.type === "*" ) {
        // Need initiatization for getting message to determine user selected image for the device.
        this.getValueList = function() {
          return { device: params.device, values : [this.params.property] };
        };
      }
      else {         // Standard image, no need to get values.
        this.getValueList = function(result) { return null; };
      }


      $parent.append(this.$el);
      this.$el.show();
    };
  }

  //
  // VALUE -- NOT DONE
  //
  function instrValue(params) {
    this.params = params;
    this.defaultFontSize = 14;

    // console.log( "instr->", params )

    this.reposition = function(x, y, w, h, m) {
      gReposition( this, x, y, w, h, m);
    };

    this.initialize = function($parent) {
      this.$el = $('<div id="sv-'+this.eleNum+'" style="position: absolute; text-align:center;z-index: 1;"></div>');
      this.$el.css(params.css);
      this.defaultFontSize = parseFloat(this.$el.css('font-size'));
      $parent.append(this.$el);
      this.$el.click(function() { instrumentActivate(deviceName); });
      this.$el.show();
    };

    this.getValueList = function() {
      return { device: params.device, values : [this.params.property] };
    };

    this.updateValues = function(result) {
//      console.log( "Value Update Values->", this )

      this.$el.fadeTo('slow', 1.0);

      var device = result[params.device];
      if (device !== null) {

        var online = true;
        if (device.deviceInfo.online !== "undefined") {
          online = device.deviceInfo.online;
        }

        propertyValue = statusLayoutFormatValue( device.values[params.property], device.valuesDescr[params.property] );
        $("#sv"+this.eleNum).html(propertyValue);

        measurements = "L:" + this.params.x + " T:" + this.params.y + " W:" + this.params.w + " H:" + this.params.h;
        this.$el.attr('title', this.params.device + '-' + this.params.property + ' : ' + propertyValue + '-->' + measurements );
      }
      this.$el.show();
    };
  }

  //
  // LABEL
  //
  function instrLabel(params) {
    this.params = params;
    this.defaultFontSize = 14;

    // console.log( "instr->", params )

    this.reposition = function(x, y, w, h, m) {
      gReposition( this, x, y, w, h, m);
    };

    this.initialize = function($parent) {
      this.$el = $('<div style="position: absolute; z-index: 1;" >' + params.text +  '</div>');
      this.$el.css(params.css);
      this.defaultFontSize = parseFloat(this.$el.css('font-size'));
      $parent.append(this.$el);
      this.$el.click(function() { instrumentActivate(deviceName); });
      this.$el.show();
    };

    this.getValueList = function(result) { return null; };
    this.updateValues = function(result) {};
  }

  //
  // LABEL VALUE -- NOT DONE
  //
  function instrLabelValue(params) {
    this.params = params;
    this.defaultWidth = 0;
    this.defaultHeight = 0;

    // console.log( "instr->", params )

    this.reposition = function(x, y, w, h, m) {
      gReposition( this, x, y, w, h, m);
    };

    this.initialize = function($parent) {
      // This will be a table with one row and two columns.
      tableStr = $('<table style="position: absolute; z-index: 1; cursor: pointer; border: 1px solid black;">');
      rowHtml = '<tr><td id="lvl'+this.eleNum+'"></td><td id="lvv'+this.eleNum+'"></td></tr></table>';
      this.$el = tableStr + rowHtml;
      this.$el.css(params.css);
      $parent.append(this.$el);

      this.defaultWidth = this.$el.width();
      this.defaultHeight = this.$el.height();
      this.$el.hide();
    };

    this.getValueList = function() {
      return { device: params.device, values : [this.params.property] };
    };

    this.updateValues = function(result) {
//      console.log( "LV Update Values->", this )

      this.$el.fadeTo("slow", 1.0);

      var device = result[params.device];
      if (device !== null) {

        var online = true;
        if (device.deviceInfo.online !== "undefined") {
          online = device.deviceInfo.online;
        }

        $("#lvl"+this.eleNum).html(this.params.label);
        propertyValue = statusLayoutFormatValue( device.values[params.property], device.valuesDescr[params.property] );
        $("#lvv"+this.eleNum).html(propertyValue);

        measurements = "L:" + this.params.x + " T:" + this.params.y + " W:" + this.params.w + " H:" + this.params.h;
        this.$el.attr('title', this.params.device + '-' + this.params.property + ' : ' + propertyValue + '-->' + measurements );
      }
      this.$el.show();
    };
  }

  //
  // STATUS BLOCK
  //
  // Properties required: { "type": "statusBlock", "x": 10, "y": 36.5, "device": "Desk BIT25", "property": "T1TEMP", "image":"<name only. Found in static/uimg/sitemap">, "css": {"color": "green"}  },

  function statusLayoutFormatValue( value, valueDescr )
  {
    returnValue = value;
    if ( ( value === undefined ) || ( value === null ) ) {
      returnValue = "---";
    }
    else if ( (value === "ERROR" ) ) {
      returnValue = "ERROR"
    }
    else {
      returnValue = getDisplayValueByType(valueDescr, value);
      unitType = getValueUnitByType( valueDescr );
      if (unitType !== null) {
        returnValue =  returnValue + '' + unitType;
      }
    }
    return( returnValue );
  }

  function instrStatusBlock(params, blStatusBlockShow) {
    this.params = params;
    this.defaultWidth = 0;
    this.defaultHeight = 0;
    this.blStatusBlockShow = blStatusBlockShow;

    // console.log( "instr->", params )

    this.reposition = function(x, y, w, h, m) {
      // console.log( "Reposition->", x, y, w, h, m )
      gReposition( this, x, y, w, h, m);
    };

    this.initialize = function($parent) {

     //var sbIpTable = sbIpTable + '<tr class="inptbl"><td class="inptbl"  border="1px" id="wPropName'+this.eleNum+'" style="text-align: center;" >&nbsp;</td><td class="inptbl" border="1px"  id="wDispName'+this.eleNum+'" style="text-align: center;">&nbsp;</td><td class="inptbl"  border="1px"  id="wValue'+this.eleNum+'" style="text-align: center;">&nbsp;</td></tr>';
		 var sbIpTable = '<tr><td border="1px"  align="center" id="wPropName'+this.eleNum+'"></td><td border="1px"  align="center" id="wDispName'+this.eleNum+'"></td><td border="1px"  align="center" id="wValue'+this.eleNum+'" ></td></tr>';
		//var sbHtml = $inptbl //.append(sbPropName);
//	 var sbHtml = sbPropName;
      // console.log( "sbHTML = ", sbHtml);

    this.$el = $(sbIpTable);
      //this.$el.css(.inptbl);
      // this.DisplayName = params.device
		//$rows.append(this.$el)
		//$parent.append(this.$el);

      this.defaultWidth = this.$el.width();
      this.defaultHeight = this.$el.height();

      this.$el.hide();

      var DisplayName = this.params.device;
      // On status screen, disable page transitions.
      // this.$el.click(function() { instrumentActivate(DisplayName); });
    };

    this.getValueList = function() {
      return { device: this.params.device, values : [ this.params.property ] };
    };

    this.updateValues = function(result) {
      // console.log( "Update Values->", this, "Num:", this.eleNum )

      this.$el.fadeTo('slow', 1.0);

      var device = result[params.device];
      if (device !== null) {

        var online = true;
        if (device.deviceInfo.online !== "undefined") {
          online = device.deviceInfo.online;
        }

        propertyValue = statusLayoutFormatValue( device.values[this.params.property], device.valuesDescr[this.params.property] );
		//console.log(params.property, propertyValue, typeof(propertyValue));
		$("#caseName").html(deviceName);
		if (this.params.property == "DEFROST")
		{
			//console.log(params.property, propertyValue, typeof(propertyValue));
			//console.log(abc)
			
			if (device.values[this.params.property] == true)
			{
				//console.log("Inside Defrost");
				var valID = "Defrost"
				$("#caseVal").html(valID);
			}
			else {
				var valID = "Refrigeration"
				$("#caseVal").html(valID);
			}
		}

		if (this.params.property == "STANDBY")
		{
		//console.log(params.property, propertyValue, typeof(propertyValue));
			if (device.values[this.params.property] == true)
			{
				var valID = "Manual Standby"
				$("#caseVal").html(valID);
			}
		}
		

        $("#wValue"+this.eleNum).html(propertyValue);

        measurements = "L:" + this.params.x + " T:" + this.params.y + " W:" + this.params.w + " H:" + this.params.h;
        this.$el.attr('title', this.params.device + '-' + this.params.property + ' : ' + propertyValue + '-->' + measurements );
        // this.$el.attr('title', this.params.device + '-' + this.params.property + ' : ' + propertyValue );
        console.log(this.params.property);
        console.log(device.valuesDescr[this.params.property]);

        displayName = device.valuesDescr[this.params.property].displayName;
        $("#wPropName"+this.eleNum).html(this.params.property);
		$("#wDispName"+this.eleNum).html(displayName);
		var row = 0;
		var Values = $("#configureDeviceTable").proptable('getData');

if (this.params.property == "AUX1 RLY" || this.params.property == "AUX RLY")
{
  for (var key in _configData) 
  {
	if (key == "OA1" ||key == "OAU" )
	{  var i=0;
		for( i in Values[row])
		{
			if ( i == 2)
			{
				if (Values[row][i] == "DEF")
				{
					$("#wDispName"+this.eleNum).html("Defrost");
				}
				else if (Values[row][i] == "FAN")
				{
					$("#wDispName"+this.eleNum).html("Fan");
				}
				else if (Values[row][i] == "NON")
				{
					$("#wDispName"+this.eleNum).html("None");
				}
				else if (Values[row][i] == "DEF")
				{
					$("#wDispName"+this.eleNum).html("Defrost");
				}
				else if (Values[row][i] == "LGT")
				{
					$("#wDispName"+this.eleNum).html("Light");
				}
				else if (Values[row][i] == "ALO" || Values[row][i] == "AL0" )  // 
				{
					$("#wDispName"+this.eleNum).html("Active Alarms Open");
				}
				else if (Values[row][i] == "ALC" || Values[row][i] == "AL1" || Values[row][i] == "ALR")  // 
				{
					$("#wDispName"+this.eleNum).html("Active Alarms Close");
				}
				else if (Values[row][i] == "0-1" || Values[row][i] == "O-I")
				{
					$("#wDispName"+this.eleNum).html("Controller State");
				}
				else if (Values[row][i] == "2CU")
				{
					$("#wDispName"+this.eleNum).html("Aux Compressor");
				}
				else if (Values[row][i] == "2EU")
				{
					$("#wDispName"+this.eleNum).html("ELE defrost 2nd Evap");
				}
				else
				{
					$("#wDispName"+this.eleNum).html(displayName);
				}
			}
		}
	}
		 row++;
  } 
}


if (this.params.property == "AUX2 RLY")
{
  for (var key in _configData) 
  {
	  
	if (key == "OA2")
	{  var i=0;
		for( i in Values[row])
		{
			if ( i == 2)
			{
				if (Values[row][i] == "DEF")
				{
					$("#wDispName"+this.eleNum).html("Defrost");
				}
				else if (Values[row][i] == "FAN")
				{
					$("#wDispName"+this.eleNum).html("Fan");
				}
				else if (Values[row][i] == "NON")
				{
					$("#wDispName"+this.eleNum).html("None");
				}
				else if (Values[row][i] == "LGT")
				{
					$("#wDispName"+this.eleNum).html("Light");
				}
				else if (Values[row][i] == "ALO")
				{
					$("#wDispName"+this.eleNum).html("Active Alarms Open");
				}
				else if (Values[row][i] == "ALC")
				{
					$("#wDispName"+this.eleNum).html("Active Alarms Close");
				}
				else if (Values[row][i] == "0-1")
				{
					$("#wDispName"+this.eleNum).html("Controller State");
				}
				else if (Values[row][i] == "2CU")
				{
					$("#wDispName"+this.eleNum).html("Aux Compressor");
				}
				else if (Values[row][i] == "2EU")
				{
					$("#wDispName"+this.eleNum).html("ELE defrost 2nd Evap");
				}
				else
				{
					$("#wDispName"+this.eleNum).html(displayName);
				}
			}
		}
	}
	row++;
  } 
}

if (this.params.property == "DIG Input 1")
{
  for (var key in _configData) 
  {

	if (key == "DI1" || key == "D1O")
	{  var i=0;
		for(  i in Values[row])
		{
			if ( i == 2)
			{
				if (Values[row][i] == "DOR")
				{
					$("#wDispName"+this.eleNum).html("Door");
				}
				else if (Values[row][i] == "ALR")
				{
					$("#wDispName"+this.eleNum).html("Alarm Condition");
				}
				else if (Values[row][i] == "NON")
				{
					$("#wDispName"+this.eleNum).html("None");
				}
				else if (Values[row][i] == "RDS")
				{
					$("#wDispName"+this.eleNum).html("Defrost Start");
				}
				else if (Values[row][i] == "TS1")
				{
					$("#wDispName"+this.eleNum).html("Test Bench Type1");
				}
				else if (Values[row][i] == "TS2")
				{
					$("#wDispName"+this.eleNum).html("Test Bench Type2");
				}
				else
				{
					$("#wDispName"+this.eleNum).html(displayName);
				}
			}
		}
	}
		 row++;
  } 
}


if (this.params.property == "DIG Input 2")
{
  for (var key in _configData) 
  {

	if (key == "DI2" || key == "D2O")
	{  var i=0;
		for(  i in Values[row])
		{
			if ( i == 2)
			{
				if (Values[row][i] == "DOR")
				{
					$("#wDispName"+this.eleNum).html("Door");
				}
				else if (Values[row][i] == "NON")
				{
					$("#wDispName"+this.eleNum).html("None");
				}
				else if (Values[row][i] == "ALR")
				{
					$("#wDispName"+this.eleNum).html("Alarm Condition");
				}
				else if (Values[row][i] == "RDS")
				{
					$("#wDispName"+this.eleNum).html("Defrost Start");
				}
				else if (Values[row][i] == "IISM")
				{
					$("#wDispName"+this.eleNum).html("Second Param Set");
				}
				else if (Values[row][i] == "T3")
				{
					$("#wDispName"+this.eleNum).html("T3 Probe");
				}
				else if (Values[row][i] == "PSP")
				{
					$("#wDispName"+this.eleNum).html("Potentiometer SP");
				}
				else if (Values[row][i] == "DSY")
				{
					$("#wDispName"+this.eleNum).html("Deforst Sync");
				}
				else if (Values[row][i] == "HPS")
				{
					$("#wDispName"+this.eleNum).html("High Press Switch");
				}
				else
				{
					$("#wDispName"+this.eleNum).html(displayName);
				}
			}
		}
	}
		 row++;
  } 
}

if (this.params.property == "DIG Input 3")
{
  for (var key in _configData) 
  {

	if (key == "DI3" || key == "D3O")
	{  var i=0;
		for(  i in Values[row])
		{
			if ( i == 2)
			{
				if (Values[row][i] == "DOR")
				{
					$("#wDispName"+this.eleNum).html("Door");
				}
				else if (Values[row][i] == "ALR")
				{
					$("#wDispName"+this.eleNum).html("Alarm Condition");
				}
				else if (Values[row][i] == "NON")
				{
					$("#wDispName"+this.eleNum).html("None");
				}
				else if (Values[row][i] == "RDS")
				{
					$("#wDispName"+this.eleNum).html("Defrost Start");
				}
				else if (Values[row][i] == "IISM")
				{
					$("#wDispName"+this.eleNum).html("Second Param Set");
				}
				else if (Values[row][i] == "DSY")
				{
					$("#wDispName"+this.eleNum).html("Deforst Sync");
				}
				else
				{
					$("#wDispName"+this.eleNum).html(displayName);
				}
			}
		}
	}
		 row++;
  } 
}

if (this.params.property == "T3 TEMP")
{
  for (var key in _configData) 
  {

	if (key == "T3M" || key == "T3")
	{  var i=0;
		for(  i in Values[row])
		{
			if ( i == 2)
			{
				if (Values[row][i] == "NON")
				{
					$("#wDispName"+this.eleNum).html("None");
				}
				else if (Values[row][i] == "DSP")
				{
					$("#wDispName"+this.eleNum).html("Display");
				}
				else if (Values[row][i] == "CND")
				{
					$("#wDispName"+this.eleNum).html("Condenser");
				}
				else if (Values[row][i] == "2EU")
				{
					$("#wDispName"+this.eleNum).html("2nd Evap Temp");
				}
				else if (Values[row][i] == "DTP")
				{
					$("#wDispName"+this.eleNum).html("DTP");
				}
				else
				{
					$("#wDispName"+this.eleNum).html(displayName);
				}
			}
		}
	}
		 row++;
  } 
}

        // See if there is a dynamicImage that needs to be displayed.
        if ( device.dynamicImages[this.params.property].length > 0 ) {
          $("#wImage" + this.eleNum).attr("src", "static/local/img/sitemap/" + device.dynamicImages[this.params.property] )
        }
        // console.log( 'We think the deviceName is:', deviceName, "Temperature Units = ", displayUnitSetting["temperature"] )
      }
      this.$el.show();
    };
  }


  instrumentFactory = function(params) {
    switch(params.type) {
      case 'statusBlock':
        return new instrStatusBlock(params,1);
      case 'statusBlockBlank':
        return new instrStatusBlock(params,0);
      case 'value':
        return new instrValue(params);
      case 'labelValue':
        return new instrLabelValue(params);
      case 'image':
        return new instrImage(params);
      case 'gridImage':
        return new instrImage(params);
      case 'label':
        return new instrLabel(params);
      case 'dynamicImgBlock':
        return new instrStatusBlock(params);
      case 'e2CaseState':
        return new instrE2CaseState(params);
    }
  };


  // These are publically exposed functions...
  return {
    initStatusLayout: function(deviceType, deviceNameIn) {
      // console.log("Getting json file...DevName:", deviceName, "DevType:", deviceType);
      // console.log("URL = ", siteMapImageDir + deviceType + ".json?nocache=" + (new Date()).getTime() )

      $("#sitemap").empty();   // Clear out any current widgets
      instruments.length = 0;  // Clear the instruments array
      slDeviceName = deviceNameIn;

      pageXHR = $.ajax({
          type: "GET",
          url: siteMapImageDir + deviceType + ".json?nocache=" + (new Date()).getTime(),
          contentType: "application/json; charset=utf-8",
          dataType: "json",
          success: init,
          error: statusLayoutJsonErr
      });
    },

    // This function simply erases all of the objects in the sitemap
    clearStatusLayout: function() {
      $("#sitemap").empty();  // Clear out any current widgets
      instruments.length = 0;  // Clear the instruments array
    }
  };

}());

//@ sourceURL=statusLayout.js
