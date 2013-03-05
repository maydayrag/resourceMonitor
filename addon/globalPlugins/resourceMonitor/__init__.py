#Resource Monitor for NvDA
#Presents basic info on CPU load, memory and disk usage, as well as battery information.
#Authors: Alex Hall (core mechanics and messages), Joseph Lee (internationalization), Beqa Gozalishvili (updated psutil to 0.6.1, and made needed changes to make code run).

import globalPluginHandler, ui
import psutil, battery
import addonHandler
addonHandler.initTranslation()


def toBiggestBytes(n, x=2, useLongNames=False):
 #returns a string where n, rounded to x, is in the largest logical measure possible
 i=0 #counter
 units=[" bytes","kb","mb","gb","tb"]
 longUnits=[" bytes","kilobytes","megabytes","gigabytes","terrabytes"]
 n=float(n)
 while(n>=1024):
  n=n/1024.0
  i=i+1
 res=(str(round(n, x)))
 if useLongNames: return res+" "+longUnits[i]
 else: return res+units[i]

def tryTrunk(n):
 #this method basically removes decimal zeros, so 5/0 will just be 5.
 #If the number ends in anything other than a 0, nothing happens (if the trunkated number is not equal to the decimal).
 if n==int(n): return int(n)
 return n

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

 def script_announceBatteryInfo(self, gesture):
  info=""
  #returns nothing, but sets vars we can now inspect
  battery.getInfo()
  if battery.noBattery:
   info=_("This computer does not have a battery connected.")
  elif not battery.onBattery: 
   # Translators: message presented when AC is connected and battery is charging, also show current battery percentage.
   info=_("{percent}%, battery charging.").format(percent=tryTrunk(battery.percentage))
  elif battery.onBattery: 
   # Translators: message presented when computer running on battery power, showing percentage remaining and estimated remaining time.
   info=_("{percent}% battery remaining, about {time}.").format(percent=tryTrunk(battery.percentage), time=battery.timeLeft)
   if battery.low:
    info+=_(" Warning: low battery.")
   elif battery.critical:
    info+=_(" Warning: battery is critically low.")
  ui.message(info)
 script_announceBatteryInfo.__doc__=_("Presents battery percentage, charging status, remaining time (if not charging), and a warning if the battery is low or critical.")

 def script_announceDriveInfo(self, gesture):
  #goes through all registered drives and gives info on each one
  info=""
  #get all registered drives
  for drive in psutil.disk_partitions():
   try:
    #get info on each one
    driveInfo=psutil.disk_usage(drive[0])
    # Translators: Shows drive letter, type of drive (fixed or removable), used capacity and total capacity of a drive (example: C drive, ntfs; 40 GB of 100 GB used (40%).
    info+=_("{driveName} ({driveType} drive): {usedSpace} of {totalSpace} used {percent}%. ").format(driveName=drive[0], driveType=drive[2], usedSpace=toBiggestBytes(tryTrunk(driveInfo[1])), totalSpace=toBiggestBytes(tryTrunk(driveInfo[0])), percent=tryTrunk(driveInfo[3]))
   except:
    pass
  ui.message(info)
 script_announceDriveInfo.__doc__=_("Presents the used and total space of the static and removable drives on this computer.")

 def script_announceProcessorInfo(self, gesture):
  cores=psutil.NUM_CPUS #number of cores
  averageLoad=psutil.cpu_percent()
  #lists load for each core
  perCpuLoad=psutil.cpu_percent(percpu=True)
  coreLoad=""
  # Translators: Shows average load of CPU cores (example: core 1, 50%).
  for i in range(len(perCpuLoad)):
   coreLoad+=_("Core {coreNumber}: {corePercent}%. ").format(coreNumber=str(i+1), corePercent=tryTrunk(perCpuLoad[i]))
  # Translators: Shows average load of the processor and the load for each core.
  info=_("Average CPU load {avgLoad}%, {cores}").format(avgLoad=tryTrunk(averageLoad), cores=coreLoad)
  ui.message(info)
 script_announceProcessorInfo.__doc__=_("Presents the average processor load and the load of each core.")

 def script_announceRamInfo(self, gesture):
  ram=psutil.phymem_usage()
  # Translators: Shows RAM (physical memory) usage.
  info=_("Physical: {physicalUsed} of {physicalTotal} used ({physicalPercent}%). ").format(physicalUsed=toBiggestBytes(tryTrunk(ram[1])), physicalTotal=toBiggestBytes(tryTrunk(ram[0])), physicalPercent=tryTrunk(ram[3]))
  virtualRam=psutil.virtmem_usage()
  # Translators: Shows virtual memory usage.
  info+=_("Virtual: {virtualUsed} of {virtualTotal} used ({virtualPercent}%).").format(virtualUsed=toBiggestBytes(tryTrunk(virtualRam[1])), virtualTotal=toBiggestBytes(tryTrunk(virtualRam[0])), virtualPercent=tryTrunk(virtualRam[3]))
  ui.message(info)
 script_announceRamInfo.__doc__=_("Presents the used and total space for both physical and virtual ram.")

 def script_announceResourceSummary(self, gesture):
  cpuLoad=psutil.cpu_percent()
  ram=psutil.phymem_usage()
  freeRam=ram[3]
  # Translators: presents the overall summary of resource usage, such as CPU load and RAM usage.
  info=(_("{ramPercent}% RAM used, CPU at {cpuPercent}%. ").format(ramPercent=tryTrunk(freeRam), cpuPercent=tryTrunk(cpuLoad)))
  battery.getInfo()
  if not battery.noBattery and not battery.batteryStatusUnknown and not battery.onBatteryUnknown:
   if not battery.onBattery: info+=_("{percent}%, battery charging.").format(percent=tryTrunk(battery.percentage))
   elif battery.onBattery:
    #discharging battery, so provide info on it
    info+=_("{percent}% battery remaining, about {time}.").format(percent=tryTrunk(battery.percentage), time=battery.timeLeft)
    if battery.low:
     info+=_(" Warning: low battery.")
    elif battery.critical:
     info+=_(" Warning: critically low battery.")
  ui.message(info)
 script_announceResourceSummary.__doc__=_("Presents used ram, average processor load, and battery info if available.")

 __gestures={
  "KB:NVDA+shift+e":"announceResourceSummary",
  "KB:NVDA+shift+1":"announceProcessorInfo",
  "KB:NVDA+shift+2":"announceRamInfo",
  "KB:NVDA+shift+3":"announceDriveInfo",
  "KB:NVDA+shift+4":"announceBatteryInfo",
  "KB:NVDA+shift+5":"announceRamInfo",
 }
