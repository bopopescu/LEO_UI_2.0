var pageLastLocation = "";
var pageTimeout;
var pageXHR = null;
var pageResize = null;
var pageClose = null;

var pageTimeDifferenceMs = 0;
var browserFromZuluMinutes = 0;

var gTimeRemainingSecs = 0;
var gSnoozeTimeoutTimer = 0;
var gPageInAlarm = false;

var touchScreenPresent = $('#touchScreenInfo').attr("touchScreenPresent");

// Global color settings for alarm entries
var retrycss = { backgroundColor: '#FFE4B5' };       // Light yellow/red
var alarmcss = { backgroundColor: '#f96e6e' };       // red
var warncss = { backgroundColor: '#F1F658' };       // Yellowish
var noalarmcss = { backgroundColor: '#ffffff' };  // White
var goodalarmcss = { backgroundColor: '#32C873' }; // Light green
var defrostOncss = { backgroundColor: '#FD9A37' };
var defrostOffcss = { backgroundColor: '#FFFFFF' };
var ackcss = { backgroundColor: '#EBBDF4' };       // Light purple

if (!Modernizr.sessionstorage) {
//  console.log("NEW SESSION")
  var sessionStorage = {}
}
else
{
//  console.log("existing session", sessionStorage )
  var dummy=1
}

function updateUnitGlyph() {
  var icon = 'icon-degreesC';
  switch(displayUnitSetting["temperature"]) {
    case "°F":
      icon = 'icon-degreesF';
      break;
    case "°K":
      icon = 'icon-degreesK';
      break;
  }
  if ( touchScreenPresent == "true" ) {
    $( "#nav_pageUnits" ).button( "option", "icons", {primary:'icon ' + icon + ' fs2x'} );
  } else {
    $( "#nav_pageUnits" ).button( "option", "icons", {primary:'icon ' + icon} );
  }
}

// function pageWaiting(option) { if (option == null) { dispOption="SPIN" } else { dispOption=option;} console.log('pageWaiting-', dispOption ); $('body').hlWaiting(option); }
function pageWaiting(option) {
  $('body').hlWaiting(option);
}

function pageSetTimeout(timeoutFunction, timeoutValue) {
    pageTimeout = setTimeout(timeoutFunction, timeoutValue);
}

function pageClearTimeout() {
    clearTimeout(pageTimeout);
}

function pageCheckLast(loc) {
  if (pageLastLocation === loc)
    return false;
  pageLastLocation = loc;
  return true;
}

// Not needed with touch screen
function pageArticleNoOverflow() {
  $("#article").css({overflowY: 'hidden'});
}

// Not needed with touch screen
function pageArticleOverflow() {
  $("#article").css({overflowY: 'auto'});
}

function pageLoadData(tag, loc) {
  pageWaiting();
  // console.log( "pageLoadData pageXHR = ", pageXHR);
  if ( (pageXHR !== null) && (pageXHR !== undefined) )
    pageXHR.abort();

  if ($.isFunction(pageClose))
    pageClose();

  pageXHR = null;
  pageClearTimeout();
  pageResize = null;
  pageClose = null;

  if ( touchScreenPresent === "true" ) {
    doNothing = 0;
  }
  else {
    pageArticleOverflow();
  }

  $(tag).load(loc, function(response, status, xhr) {
    // error handling
    if(status === "error") {
      $(tag).html("<p style='padding: 2px'>Could not load page.</p><p style='padding: 2px'>Verify the controller is still powered on and check network connections.</p>");
      $('#commError').show();
    }
    resizeArticle();
  })
}
function pageLoad(loc) {
  if (pageCheckLast(loc))
  {
    // Check for pages that we DO NOT want to return to on a page refresh.
    if ( ( loc !== "pageLogout" ) && ( loc !== "pageLogin" ) ) {
      // console.log(":) pageLoad->", loc);
      sessionStorage.lastPage = loc;
      deviceName = null;
    }
    pageLoadData("#content", loc );
  }
}

function pageLogout() { 

sessionStorage.clear();

pageLoad("pageLogout");
  }
function pageLogin() { pageLoad("pageLogin"); }
function pageSitemap() { pageLoad("pageSitemap"); }
function pageAlarms() { pageLoad("pageAlarms"); }
function pageDevices() { pageLoad("pageDevices"); }
function pageAnalysis() { pageLoad("pageAnalysis"); }
function pageExport() { pageLoad("pageExport"); }
function pageSystemConfig() { pageLoad("pageSysconfig"); }
function pageUsers() { pageLoad("pageUsers"); }
function pageUpload() { pageLoad("pageUpload"); }
function pageService() { pageLoad("pageService"); }
function pageE2AlarmLog() { pageLoad("pageE2alarms"); }
function pageAuditTrail() { pageLoad("pageAuditTrail"); }
function pageEmailHistory() { pageLoad("pageEmailHistory"); }
function pageNetworkStatus() { pageLoad("pageNetworkStatus"); }
function pageTestPage() { pageLoad("pageTestPage"); }
// function pageTestStatus() { pageLoad("pageTestStatus"); }

function pageDeviceRedirect(deviceName) {
  sessionStorage.devices_deviceName = deviceName;
  $("#nav_pageDevices").prop('checked', true).button("refresh");
  pageDevices();
}

function pageReload() {
  var loc = pageLastLocation;
  pageLastLocation = null;
  pageLoad(loc);
}

function resizeArticle() {
  var windowHeight = $(window).height();
  var articleHeight = windowHeight - $("#headertable").height();
  var $article = $("#article");
  $article.height(articleHeight);
  $("#nav").height(windowHeight);

  if (pageResize !== null)
    pageResize($article, articleHeight, $article.width());
}

// jquery plugin for vertical menus
(function( $ ){
//plugin buttonset vertical
$.fn.buttonsetv = function() {
  $(':radio, :checkbox', this).wrap('<div style="padding: 0px"/>');
  $(this).buttonset();
  $('label', this).removeClass('ui-corner-all ui-corner-right').addClass('ui-corner-left navbutton');
};
})( jQuery );

function getAction(alarmaction) {
  var action = '';
  if (alarmaction === 'RTN')
    action = 'Resolved';
  else if (alarmaction === 'NEW')
    action = 'New';
  else if (alarmaction === 'RST')
    action = 'Reset';
  else if (alarmaction === 'CLR')
    action = 'Cleared';
  else if (alarmaction === 'ACK')
    action = 'Acknowledged';
  return action;
}

function checkAlarm(alarm) {
  if (alarm === '_NETWORK_FAILURE_')
    alarm = 'LEO Network Failure'
  return alarm;
}

function str_pad_left(string,pad,length) {
    return (new Array(length+1).join(pad)+string).slice(-length);
}

var SNOOZE_TIMER_STARTED = 0;
var SNOOZE_ACTUAL_TIME = 1;
var SNOOZE_TIMER_UPDATE = 2;

function updateAlarmStatus(fadeEffect) {
  if (typeof(fadeEffect)==='undefined') fadeEffect = true;

  postJson({"jsonrpc":"2.0","id":"siteHeader","method":"getSiteStatus"},
    function(data) {
      var result = data;
      if ( (result != null) && (result.activeAlarms !== undefined ) ) {
        $('.sitename').html(result.name);
        document.title = result.name;
        gPageInAlarm = result.enunciatedAlarms;

        var selector = $("label[for='nav_pageAlarms']");
        if (fadeEffect) {
          if (gPageInAlarm)
            selector.removeClass('nav-alarm--active').addClass('nav-alarm--active');
          else
            selector.removeClass('nav-alarm--active');
        } else {
          if (gPageInAlarm)
            selector.addClass('nav-alarm--active');
          else
            selector.removeClass('nav-alarm--active');
        }

        if (result.strTestEmailMsg.length > 0) {
          $('#testEmailAlarmStatus').html(result.strTestEmailMsg);
          $('#testEmailAlarmStatus').show();
        }
        else {
          $('#testEmailAlarmStatus').hide();
        }

        if ( gPageInAlarm > 0 ) {
          // IF the alarm snooze feature is enabled
          if (result.alarmChimeSnoozeEnable > 0) {
            updateSnoozeButton(SNOOZE_ACTUAL_TIME, result.alarmChimeSnoozeTimeRemaining);
          }
          else {
            // Hide the snooze button and make sure timer is cleared.
            $('#snoozeInfoDiv').hide()
          }
        } else {
          // Hide the snooze button and make sure the timer is clered.
        }

        // minutes converted to ms
        var d = new Date();
        var pageTimeDifferenceMinutes = result.timeInfo.currentTimeZoneOffsetMinutes + d.getTimezoneOffset();
        pageTimeDifferenceMs = pageTimeDifferenceMinutes * 60 * 1000;
        browserFromZuluMinutes = result.timeInfo.currentTimeZoneOffsetMinutes + pageTimeDifferenceMinutes;
        d = utcToLocalDate(result.timeInfo.currentTime + "Z");
        var s = dateToString(d);
        $('#timeupdate').html(s);
      }
      $('#commError').hide();
      // Hide the comm error since we hit here.
      setTimeout(function() { updateAlarmStatus(fadeEffect) }, 10000);
    },
    function() {
      // No response from server.
      $('#testEmailAlarmStatus').hide();
      $('#commError').show();
      setTimeout(function() { updateAlarmStatus(fadeEffect) }, 20000); }
    );
}

// This function will manage the displaying of the timeremaining on the snooze button
// This will get called by the "main" alarm check (based upon a 10 second update of get site status
// It will also get called through a timeout timer.
var SNOOZE_DIV_HIDE_ALL = 0;
var SNOOZE_DIV_SHOW_COUNTDOWN = 1;
var SNOOZE_DIV_SHOW_SNOOZE_BUTTON = 2;

function updateSnoozeButton( caller, inTimeRemainingSecs ) {

   // console.log("updateSnoozeButton - Caller:", caller, "inTimeRemaining:", inTimeRemainingSecs)
   // console.log("gtimeRemainingSecs:", gTimeRemainingSecs, "gSnoozeTimeoutTimer:", gSnoozeTimeoutTimer)

  if (caller === SNOOZE_TIMER_STARTED) {  // Called by interval timer. Just decrement timer.
      // Start the timer update.
      gSnoozeTimeoutTimer = setTimeout(function () { updateSnoozeButton(SNOOZE_TIMER_UPDATE, null); }, 1000);
      gTimeRemainingSecs = inTimeRemainingSecs;
      // console.log( "START", gTimeRemainingSecs, "InAlarm", gPageInAlarm  )
  }
  else if (caller === SNOOZE_TIMER_UPDATE) {  // Called by interval timer. Just decrement timer.
      // If there is still time remaining on the snooze AND the page is still in alarm, set a one second callback timer
      if ( ( gTimeRemainingSecs > 0 ) && ( gPageInAlarm > 0 ) ) {
        gSnoozeTimeoutTimer = setTimeout(function () { updateSnoozeButton(SNOOZE_TIMER_UPDATE, null); }, 1000);
        gTimeRemainingSecs = gTimeRemainingSecs - 1;
      }
      // console.log( "UPDATE", gTimeRemainingSecs, "PIA", gPageInAlarm  )
  }

  if (gPageInAlarm > 0) {
    // There is an active alarm. By hitting here, we know the user has enabled the alarm snooze button.
    if (caller === SNOOZE_ACTUAL_TIME) {
      gTimeRemainingSecs = inTimeRemainingSecs;
      // If we are snoozed and the 1 second timer is not started, start it.
      if ( ( gTimeRemainingSecs > 0 ) && ( gSnoozeTimeoutTimer === 0 ) ) {
        setTimeout(function () { updateSnoozeButton(SNOOZE_TIMER_UPDATE, gTimeRemainingSecs); }, 1000);
      }
    }

    // Display either a snooze button or countdown.
    if (gTimeRemainingSecs > 0) {
      var timeRemainingMins = Math.floor((gTimeRemainingSecs / 60));
      var timeRemainingSecs = Math.ceil((gTimeRemainingSecs % 60));
      var snoozeString;
      var snoozeDivState;

      if (timeRemainingMins >= 1) {
        snoozeString = "Alarm Bell Snoozed for " + str_pad_left(timeRemainingMins, '0', 2) + ":" + str_pad_left(timeRemainingSecs, '0', 2) + " mins"
      }
      else {
        snoozeString = "Alarm Bell Snoozed for " + str_pad_left(timeRemainingMins, '0', 2) + ":" + str_pad_left(timeRemainingSecs, '0', 2) + " seconds"
      }
      $('#snoozeCountDownDiv').html(snoozeString);
      snoozeDivState = SNOOZE_DIV_SHOW_COUNTDOWN;
    }
    else {
      snoozeDivState = SNOOZE_DIV_SHOW_SNOOZE_BUTTON;
    }
  }
  else {
    snoozeDivState = SNOOZE_DIV_HIDE_ALL;
  }

  if (snoozeDivState === SNOOZE_DIV_SHOW_COUNTDOWN) {
    $('#snoozeInfoDiv').show();
    $('#snoozeCountDownDiv').show();
    $('#snoozeInfoBtnDiv').hide();
  }
  else if (snoozeDivState === SNOOZE_DIV_SHOW_SNOOZE_BUTTON) {
    $('#snoozeInfoDiv').show();
    $('#snoozeCountDownDiv').hide();
    $('#snoozeInfoBtnDiv').show();
    gSnoozeTimeoutTimer = 0;
  }
  else if (snoozeDivState === SNOOZE_DIV_HIDE_ALL) {
    // Page is not in alarm. Hide everything
    $('#snoozeInfoDiv').hide();
    $('#snoozeCountDownDiv').hide();
    $('#snoozeInfoBtnDiv').hide();
    gSnoozeTimeoutTimer = 0;
    gTimeRemainingSecs = 0;
  }
}

function postJson(requestObject, successFunc, errorFunc, downloadProgressFunc, uploadProgressFuncs) {
  $.ajax({
      type: "POST",
      url: requestObject.method,
      data: JSON.stringify(requestObject),
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: successFunc,
      error: errorFunc,
      xhr: function() {
        var xhr = new window.XMLHttpRequest();
        if (typeof(uploadProgressFuncs)!=='undefined')
          xhr.upload.addEventListener("progress", uploadProgressFunc, false);
        if (typeof(downloadProgressFunc)!=='undefined')
          xhr.addEventListener("progress", downloadProgressFunc, false);
        return xhr;
      }
  });
}

function getValueUnitByType(valueDescription) {
  if ("unitType" in valueDescription)
    return getDisplayUnitText(valueDescription.unitType);
  if ("unitText" in valueDescription)
    return valueDescription.unitText;
  return null;
}

function getDisplayValueByType(valueDescription, value) {
  if (value != null) {
    switch(valueDescription.dataType) {
      case "float":
        var newValue = getDisplayUnitValue(valueDescription.unitType, value);
        if ("significantDigits" in valueDescription)
          return newValue.toFixed(valueDescription.significantDigits);
        return newValue;
      case "list":
        return valueDescription.dataList[value.toString()];
      case "bool":
        if ("dataList" in valueDescription)
          return value ? valueDescription.dataList.true : valueDescription.dataList.false;
        else
          return value.toString();
	  case undefined:
			return value.toString();
      default :
          return value.toString();
    }
    return value.toString();
  }
  return value;
}

function convertStringToValueByType(valueDescription, strValue) {
  if (strValue != null) {
    switch(valueDescription.dataType) {
      case "float":
        return convertUnitStringToValue(valueDescription.unitType, strValue);
      case "list":
        var dataList = valueDescription.dataList;
        var firstprop = null;
        for (var prop in dataList) {
          if (dataList[prop] === strValue) return prop;
          if (firstprop === null) firstprop = prop;
        }
        return firstprop;
      case "bool":
        if (typeof strValue == 'boolean') return strValue;
        cmpValue = "true";
        if ("dataList" in valueDescription)
          cmpValue = valueDescription.dataList.true;
        return strValue == cmpValue ? true : false;
      case "int":
        return parseInt(strValue);
    }
  }
  return strValue;
}

// function jsonError(jqXHR, textStatus, errorThrown)  { $('#commError').show(); }
function jsonError(jqXHR, textStatus, errorThrown)  { console.log("*** jsonError *** Status:", textStatus, "Error", errorThrown ); $('#commError').show(); }

// time should be a time string from zulu - works in all browsers
function utcToLocalDate(time) { return new Date(new Date(Date.parse(time)).getTime() + pageTimeDifferenceMs); }
// local should be a date object
function localTimeToSystemLocalTime(local) { return new Date(local.getTime() - pageTimeDifferenceMs); }

function dateToString(d) { return d.toDateString() + ' ' + d.toTimeString().match( /^([0-9]{2}:[0-9]{2})/ )[0]; }
function MYdateToString(d) {
  return d.toDateString() + ' ' + d.toTimeString().match( /^([0-9]{2}:[0-9]{2})/ )[0];
}


