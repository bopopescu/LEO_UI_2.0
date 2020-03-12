#! /usr/bin/python

valueTypeInput = "input"
valueTypeOutput = "output"
valueTypeConfig = "config"

dataTypeString = "string"
dataTypeFloat = "float"
dataTypeInt = "int"
dataTypeList = "list"
dataTypeBool = "bool"

unitTypeTemperature = "temperature"
unitTypeDeltaTemperature = "deltatemperature"
unitTypePressure = "pressure"
unitTypeHumidity = "humidity"
# Add Null unit type for unitless values
unitTypeNull = ""

networkFailureKey = "LEO Network Failure"   # alarm key

# These are device/virtual execution type constants
# Not to be confused with device types
# Each network object should include this and declare its type

deviceNetworkExecution = "networkDevice" # multiple devices communicating over the same port
deviceVirtualExecution = "virtualDevice"
deviceE2Execution = "e2Device" # multiple E2 devices communicating on their own, separate port
deviceAKSC255Execution = "AKSC255" # Danfoss AK-SC255 Device 
deviceSiteExecution = "SiteSupervisor"

# internationalization starts here
deviceNetworkExecutionText = "Network Device"
deviceVirtualExecutionText = "Virtual Device"
deviceE2ExecutionText = "E2 Device"
deviceAKSC255ExecutionText = "AKSC255"
deviceSiteExecutionText = "SiteSupervisor"

# Port numbers for IP Based devices
E2_JSON_INTERFACE_PORT = 14106
AKSC255_JSON_INTERFACE_PORT = 80
SITE_JSON_INTERFACE_PORT = 80

