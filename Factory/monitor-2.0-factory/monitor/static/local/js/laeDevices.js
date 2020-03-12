

	//var username = sessionStorage.getItem('username');
	//if (username== "huntlib")
	//{
			  	// $("#manualDefrostTbl").show();
	//}
	//else{
	 //$("#manualDefrostTbl").hide();
	
	//}
	
      var loginCounter = sessionStorage.getItem('loginCounter')
	  //if ( username == "undefined" || username == "null" || username== null)
	  if ( loginCounter == 1)
      { // Successful login loginCounter
	  	//console.log("username from device page inside doc fn = ", username);
		  	 $("#StatusTable").show();
        $("#InputOutputTable").show(); 

      }
	  else
	  {
	          $("#StatusTable").show();
		  $("#InputOutputTable").hide();
	  }

 var caseName = sessionStorage.devices_deviceName;
	var caseName = String(caseName)
	$("#CaseName").html(caseName)
	
	$("#manualDefrostOn").button({icons: { primary: "icon icon-toggle-on"}}).click(function( event ) {
  var configValues = {};

  sessionStorage.setItem("DefrostVal", true);
	configValues["MDEF"] = true;
	console.log(configValues);
    pageWaiting();
    pageXHR = postJson({"jsonrpc":"2.0","id":"setDeviceConfigValues","method":"setDeviceConfigValues",
      "params":[deviceName, configValues]},
      function(data) {setTimeout(function() { pageWaiting("done");}, 1000);}, jsonError);
    event.preventDefault();
});


$("#manualDefrostOff").button({icons: { primary: "icon icon-toggle-off"}}).click(function( event ) {
  var configValues = {};

  sessionStorage.setItem("DefrostVal", false);
	configValues["MDEF"] = false;
	console.log(configValues);
    pageWaiting();
    pageXHR = postJson({"jsonrpc":"2.0","id":"setDeviceConfigValues","method":"setDeviceConfigValues",
      "params":[deviceName, configValues]},
      function(data) {setTimeout(function() { pageWaiting("done");}, 1000);}, jsonError);
    event.preventDefault();
});


