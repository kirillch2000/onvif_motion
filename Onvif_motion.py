from onvif import ONVIFCamera
import sys
from datetime import timedelta
import time
from lxml import objectify
from lxml import etree

#--Logging
#sys.stdout = open('out_log.txt', 'w')
sys.stderr = open('err_log.txt','w')


mycam = ONVIFCamera('192.168.1.240', 80, 'admin', 'admin')  # , no_cache=True)

#--Get Device Information
resp = mycam.devicemgmt.GetDeviceInformation()
print(resp)

#--Media Profiles
#media_service = mycam.create_media_service()
#profiles = media_service.GetProfiles()
#print('----------MEDIA PROFILE----------------------')
#print(profiles)

#--Event subscription
print('\n --------- Trying to subscribe to motion events...')

event_service = mycam.create_events_service()
print('------------- GetEventProperties --------------')
print(event_service.GetEventProperties())
print('------------------------------------------------------------------------------')

#-- 1.Create PullPointSubscription
pullpoint = event_service.CreatePullPointSubscription() #InitialTerminationTime='PT600S')
print(pullpoint)
print(pullpoint.SubscriptionReference.Address)
print('Current time:\t\t' + str(pullpoint.CurrentTime))
print('Termination time:\t' + str(pullpoint.TerminationTime))
print('--------------------------------------------------')

#-- 2.Create Pullpoint Serice
mycam.create_pullpoint_service()

#-- 3. Link 
plp = mycam.pullpoint.zeep_client.create_service('{http://www.onvif.org/ver10/events/wsdl}PullPointSubscriptionBinding', pullpoint.SubscriptionReference.Address._value_1)

print ('-------Pull----------------')

while True:
   time.sleep(1)
   # 4. PullMessage - get event messages   
   pullmess=plp.PullMessages(Timeout=timedelta(seconds=2), MessageLimit=50)
   cmess = len(pullmess.NotificationMessage)  #Count of messages
   print('====PullMessage Result:==count:  '+str(cmess) )
   for cur_message in pullmess.NotificationMessage:
     mess_tree = cur_message.Message._value_1 
     md_ell=mess_tree.xpath(".//*[@Name='IsMotion']/@Value")
     if len(md_ell):
          md_el=md_ell[0]
          print ('!!Motion:'+md_el)
          if md_el != 'false':
            #--  motion flag=TRUE
            for part in mess_tree:
              print( 'TAG=' + part.tag)
              print( part.attrib)
#       print(objectify.dump(part))
#       for subpart in part:
#          print(subpart.tag, subpart.attrib)
#     b = objectify.SubElement(mess_tree, "Source")
#     print(objectify.dump(b))
#     print(mess_tree)
              print('----------------')
              print(objectify.dump(mess_tree)) 
              print(etree.tostring(mess_tree,method="xml"))
          else:
            #--  motion flag = FALSE
            print(objectify.dump(mess_tree))
          print('----------------------------------------------------------------------------------------')
# except BaseException as e:
#   print(e.__class__)
#   break

