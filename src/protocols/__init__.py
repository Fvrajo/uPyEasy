#          
# Filename: __init__.py
# Version : 0.1
# Author  : Lisa Esselink
# Purpose : App to control and read SOC's
# Usage   : Runs the app
#
# Copyright (c) Lisa Esselink. All rights reserved.  
# Licensend under the Creative Commons Attribution-NonCommercial 4.0 International License.
# See LICENSE file in the project root for full license information.  
#

protocols = {}
protocols['domoticz_http'] = 'Domoticz HTTP;HTTP'
protocols['domoticz_mqtt'] = 'Domoticz MQTT;MQTT'
protocols['openhab_mqtt']  = 'OpenHab MQTT;MQTT'
protocols['aws_mqtt'] = 'Amazon AWS MQTT;MQTT'
