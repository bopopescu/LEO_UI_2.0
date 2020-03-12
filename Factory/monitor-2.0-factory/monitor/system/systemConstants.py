#! /usr/bin/python

# This module is so constants cam be shared between py modules in the system folder.
from collections import OrderedDict

# Settings for sendEmail emailtype
SEND_EMAIL_NONE                     = 0
SEND_EMAIL_SEND_ALARM               = 1
SEND_EMAIL_SEND_TEST_ALARM          = 2
SEND_EMAIL_SEND_ALARM_REPORT        = 3
SEND_EMAIL_SEND_TEST_ALARM_REPORT   = 4

# FUTURE EMAIL TYPES
SEND_EMAIL_SEND_DEBUG_FILE          = 50
SEND_EMAIL_SEND_HEARTBEAT           = 51
SEND_EMAIL_SEND_DAILY_LOG_INFO      = 52
SEND_EMAIL_SEND_BACKUP_FILE         = 53
SEND_EMAIL_SEND_SETPTS              = 54
SEND_EMAIL_SEND_ALARM_LOGS          = 55

# transstatus - Transaction status
# "Conclusion" status
SEND_SUCCESS  = 0
SEND_FAIL     = 1
SEND_TRY1_FAIL = 2
SEND_TRY2_FAIL = 3
# Third try fail goes to SEND_FAIL

# "In progress" status
SEND_REQUEST  = 20
QUEUE_TRY2    = 21
QUEUE_TRY3    = 22

# transcmd - Transaction commands
# Command Results
TRANS_DONE        = 0
TRANS_SEND_FAIL   = 1
TRANS_TERMINATE   = 2 # Should not see, but just in case we have a malformed email transaction, we need to "complete" it
# Active Command Actions
TRANS_SEND_START_ACTIVE_CMDS  = 20
TRANS_SEND_TRY1               = 20
TRANS_SEND_TRY2               = 21
TRANS_SEND_TRY3               = 22
TRANS_SEND_END_ACTIVE_CMDS    = 40

#This variable saves the current logging values of all the devices
LOGGING_VALUES = OrderedDict()
SITENAME = ""
DEVICE_LEN = 0

OLD_DEVICES = []

DATA_LOG_SUB_STRINGS = ["DEFROST",
"CONTROL TEMP",
"ACTIVE SETPT",
"FILTERED PRES",
"SUCT PRES OUT",
"SUCT PRES SETPT",
"CUR PRES SETPT",
"CUR PRESS SETPT",
"SPACE HUMID",
"SPACE TEMP OUT",
"ACT CTRL TEMP",
"ACT DEHUM SETPT",
"COOL STAGE1",
"HEAT STAGE1",
"FREON_LEVEL",
"PERCENT USED",
"SUCT PRES OUT",
"LIQUID LEVEL",
"CTRL VAL OUT",
"CTRL VAL STPT",
"ZONE TEMP OUT",
"ZONE HUM OUT",
"ACTIVE CL STPT",
"ACTIVE HT STPT",
"LIGHTS OUTPUT",
"T1 TEMP",
"T2 TEMP",
"T3 TEMP",
"DIG Input 1",
"DIG Input 2",
"DEFROST",
"COMP RLY",
"AUX1 RLY",
"AUX2 RLY",
"DOOR",
"AUX RLY",
"DEF RLY",
"FAN RLY",
"DIG Input 3",
"Hz"]





