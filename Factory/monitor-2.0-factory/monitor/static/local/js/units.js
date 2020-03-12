/*
E2 has the following:
-------------------------
temp
temp rate change
big pressure
small pressure
air velocity
liquid velocity
liquid volume
volume flow
current
light
weight


My thoughts
--------------------------
°C - temp
pa - pressure
cd - light intensity
N - force (weight)
Hz - frequency
J - energy
m - length
kg - mass
V - voltage
A - amp
W - power
C - charge

need addition of small and big pressure, and absolute and delta temperatures

Current list
--------------------------
temperature
deltatemperature
pressure



NOTE: All controller data is stored in °C and pa

*/

function toDisplayTemperature(unitType, value) {
  switch(unitType) {
    case "°F":
      return (value * 1.8) + 32.0;
    case "°K":
      return value + 273.0;
  }
  return value;
}

function toValueTemperature(unitType, value) {
  switch(unitType) {
    case "°F":
      return (value - 32.0) / 1.8;
    case "°K":
      return value - 273.0;
  }
  return value;
}

function toDisplayDeltaTemperature(unitType, value) {
  if (unitType == (displayUnitsDelta + "°F"))
    return (value * 1.8);
  else
    return value;
}

function toValueDeltaTemperature(unitType, value) {
  if (unitType == (displayUnitsDelta + "°F"))
    return (value / 1.8);
  else
    return value;
}


function toDisplayPressure(unitType, value) {
  switch(unitType) {
    case "kPa":
      return value * 0.001;
    case "psi":
      return value * 0.000145037738007;
    case "inH2O":
      return value * 0.00401474213311;
  }
  return value;
}

function toValuePressure(unitType, value) {
  switch(unitType) {
    case "kPa":
      return value / 0.001;
    case "psi":
      return value / 0.000145037738007;
    case "inH2O":
      return value / 0.00401474213311;
  }
  return value;
}

//////////////////////////////////////////////////////////////////////////////
function getDisplayUnitText(unitType) { 

		return displayUnitSetting[unitType];

 }

function getDisplayUnitValue(unitType, value) {
  unit = displayUnitSetting[unitType];
  switch (unitType) {
    case "temperature":
      return toDisplayTemperature(unit, value);
    case "deltatemperature":
      return toDisplayDeltaTemperature(unit, value);
    case "pressure":
      return toDisplayPressure(unit, value);
  }
  return value;
}

function convertUnitStringToValue(unitType, strvalue) {
  var value = parseFloat(strvalue);
  unit = displayUnitSetting[unitType];
  switch (unitType) {
    case "temperature":
      return toValueTemperature(unit, value);
    case "deltatemperature":
      return toValueDeltaTemperature(unit, value);
    case "pressure":
      return toValuePressure(unit, value);
  }
  return value;
}

///////////////////////////////

var displayUnitsDelta = "Δ";

var displayUnitTypes = {
  "temperature" : ["°C", "°F", "°K"],
  "deltatemperature" : [displayUnitsDelta + "°C", displayUnitsDelta + "°F", displayUnitsDelta + "°K"],
  "pressure" : ["Pa", "kPa", "psi"]
}

var defaultDisplayUnitImperial = {  "temperature": "°F",
                                    "deltatemperature" : displayUnitsDelta + "°F",
                                    "pressure": "psi" ,
									 "OnOff":" ","Hert":" Hz"};
var defaultDisplayUnitSI = {        "temperature": "°C",
                                    "deltatemperature" : displayUnitsDelta + "°C",
                                    "pressure": "kPa"
									};


var displayUnitSetting = defaultDisplayUnitImperial;

if (navigator.language != "en-US")
  displayUnitSetting = defaultDisplayUnitSI;

// assigns if locally stored
if (Modernizr.localstorage) {
  for (idx in displayUnitSetting) {
    if (idx in localStorage)
      displayUnitSetting[idx] = localStorage[idx];
  }
}

function displayUnitStoreSettings() {
  if (Modernizr.localstorage) {
    for (idx in displayUnitSetting) {
      localStorage[idx] = displayUnitSetting[idx];
    }
  }
}

function displayUnitMatchDeltaToTemperature() {
  displayUnitSetting["deltatemperature"] = displayUnitsDelta + displayUnitSetting["temperature"];
}

