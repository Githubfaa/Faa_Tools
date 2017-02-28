#!/usr/bin/env python
#
#################################################################################################
#
# Copy data from ESS Tools servers to performance web site data.
#
#################################################################################################
#
# 2017-02-07 gwn Based on copy_ess_web_data.ksh
#
#################################################################################################
import commands
import datetime
from datetime import date
import fcntl
import inspect
from optparse import OptionParser
import os
import sys
import time
import subprocess
#
# constants
CONVERT_THREAD_STAT     = "Convert_Thread_Stat"
CONVERT_WRE_STAT        = "Convert_WRE_Stat"
CONVERT_MIB_ERRORS      = "Convert_MIB_Errors"
CONVERT_MIB_OUT         = "Convert_MIB_Out"
LOCK_BASE               = "/user/home/_cat-global/logs"
PERFMON_SERVER          = "cmon.waas.lab"
PERFORMANCE_INDEX_DIR   = "/var/www/html/ess/performance/PERFMON/"
PID_TOOL_WRE_STATUS_FIX = "PID_Tool_WRE_Status_Fix.ksh"
PROD_WEB_SRVR           = "jactdwpnww500.act.faa.gov"
RSYNC_W_CMPR            = "-arvzO --timeout=30 --min-size=1"     # rsync common options with compression
# RSYNC_W_CMPR            = "-arvzO --timeout=30 --min-size=1 --dry-run"     # test only
RSYNC_WO_CMPR           = "-arvO --timeout=30 --min-size=1"      # rsync common options without compression
# RSYNC_WO_CMPR           = "-arvO --timeout=30 --min-size=1 --dry-run"      # test only
SPER_DAY                = 86400                              # seconds per day
STD_LOG_pre             = "/user/home/_cat-global/logs/"
STD_LOG_suf             = ".log"
SSH_CMD                 = "/bin/ssh"
SVM_HOME_HTDOCS         = "/rec_data/www/performance/SVM/raw/"
SVM_SERVER              = "csvm1.waas.lab"
TCS_SERVER              = "cutils1.waas.lab"
#TEST_WEB_SRVR           = "waas-test.amc.faa.gov"
TEST_WEB_SRVR           = "waas-test.faa.gov"
VERSION                 = "2.00"
LOCAL_DEST              = "/user/home/_cat-global/webfeeder"
#
# source destination pairs
LocDirList              = ["/rec_data/perfdata1/wre_status_archive/field",LOCAL_DEST + "/www/performance/WRESTATUS", \
                           "/rec_data/perfdata1/wre_status_archive/sl1",LOCAL_DEST + "/www/performance/WRESTATUS", \
                           "/rec_data/perfdata1/curr/",LOCAL_DEST + "/www/performance/PERFMON/curr", \
                           "/rec_data/perfdata1/html/",LOCAL_DEST + "/www/performance/PERFMON/html", \
                           "/rec_data/perfdatasl1/curr/",LOCAL_DEST + "/www/performance/PERFMON/curr/sl1", \
                           "/rec_data/perfdatasl1/html/",LOCAL_DEST + "/www/performance/PERFMON/html/sl1"]
#
# source destination pairs
LocMexicoList           = [LOCAL_DEST + "/www/performance/PERFMON/curr/wre/wre_graph_M*.png",LOCAL_DEST + "/www/mexico/PERFMON/curr/wre", \
                           LOCAL_DEST + "/www/performance/PERFMON/html/field/thread_status/thread_stat.html",LOCAL_DEST + "/www/mexico/PERFMON/html/field/thread_status", \
                           LOCAL_DEST + "/www/performance/PERFMON/html/wre/wre_stat_?_complete.html",LOCAL_DEST + "/www/mexico/PERFMON/html/wre"]
#
# source destination pairs
LocCanadaList           = [LOCAL_DEST + "/www/performance/PERFMON/curr/wre/wre_graph_Y*.png",LOCAL_DEST + "/www/canada/PERFMON/curr/wre", \
                           LOCAL_DEST + "/www/performance/PERFMON/html/field/thread_status/thread_stat.html",LOCAL_DEST + "/www/canada/PERFMON/html/field/thread_status", \
                           LOCAL_DEST + "/www/performance/PERFMON/html/wre/wre_stat_?_complete.html",LOCAL_DEST + "/www/canada/PERFMON/html/wre"]
#
# source destination pairs
PorD_Pairs              = [LOCAL_DEST + "/www/canada/","/var/www/html/ess/canada", \
                           LOCAL_DEST + "/www/mexico/","/var/www/html/ess/mexico", \
                           LOCAL_DEST + "/www/performance/AOS/","/var/www/html/ess/performance/AOS", \
                           LOCAL_DEST + "/www/performance/WRESTATUS/","/var/www/html/ess/performance/WRESTATUS", \
                           LOCAL_DEST + "/www/performance/PERFMON/","/var/www/html/ess/performance/PERFMON", \
                           LOCAL_DEST + "/www/performance/TCS/","/var/www/html/ess/performance/TCS"]
#
# source destination pairs
SVM_Pairs               = [LOCAL_DEST + "/www/performance/SVM/","/var/www/html/ess/performance/SVM"]
#
Src_Dirs                = [LOCAL_DEST, LOCAL_DEST + "/www", \
                           LOCAL_DEST + "/www/performance", \
                           LOCAL_DEST + "/www/performance/PERFMON", \
                           LOCAL_DEST + "/www/performance/PERFMON/curr", \
                           LOCAL_DEST + "/www/performance/PERFMON/curr/sl1", \
                           LOCAL_DEST + "/www/performance/PERFMON/history", \
                           LOCAL_DEST + "/www/performance/PERFMON/history/sl1", \
                           LOCAL_DEST + "/www/performance/PERFMON/html", \
                           LOCAL_DEST + "/www/performance/PERFMON/html/sl1", \
                           LOCAL_DEST + "/www/performance/AOS", \
                           LOCAL_DEST + "/www/performance/TCS", \
                           LOCAL_DEST + "/www/performance/TCS/Reports", \
                           LOCAL_DEST + "/www/performance/TCS/Logs", \
                           LOCAL_DEST + "/www/performance/WRESTATUS", \
                           LOCAL_DEST + "/www/canada", \
                           LOCAL_DEST + "/www/canada/PERFMON", \
                           LOCAL_DEST + "/www/canada/PERFMON/curr", \
                           LOCAL_DEST + "/www/canada/PERFMON/history", \
                           LOCAL_DEST + "/www/canada/PERFMON/history/wre", \
                           LOCAL_DEST + "/www/canada/PERFMON/html", \
                           LOCAL_DEST + "/www/canada/PERFMON/html/field", \
                           LOCAL_DEST + "/www/canada/PERFMON/html/field/thread_status", \
                           LOCAL_DEST + "/www/canada/PERFMON/html/wre", \
                           LOCAL_DEST + "/www/canada/TCS", \
                           LOCAL_DEST + "/www/canada/TCS/Reports", \
                           LOCAL_DEST + "/www/mexico", \
                           LOCAL_DEST + "/www/mexico/PERFMON", \
                           LOCAL_DEST + "/www/mexico/PERFMON/curr", \
                           LOCAL_DEST + "/www/mexico/PERFMON/history", \
                           LOCAL_DEST + "/www/mexico/PERFMON/history/wre", \
                           LOCAL_DEST + "/www/mexico/PERFMON/html", \
                           LOCAL_DEST + "/www/mexico/PERFMON/html/field", \
                           LOCAL_DEST + "/www/mexico/PERFMON/html/field/thread_status", \
                           LOCAL_DEST + "/www/mexico/PERFMON/html/wre", \
                           LOCAL_DEST + "/www/mexico/TCS", \
                           LOCAL_DEST + "/www/mexico/TCS/Reports"]
#
global AppliedUpdates
global DebugExt
global DebugMode
global LogFile
global LogFileName
#
#
def Call_Rsync (src,
                tgt,
                rcmd,
                ecmd = None,
                xtra = None):
#
   global DebugMode
   global LogFileName
#
   bldcmd = "rsync " + rcmd + " "
   if xtra is not None:
      bldcmd = bldcmd + xtra + " "
#
   if ecmd is not None:
      bldcmd = bldcmd + ecmd + " "
#
   bldcmd = bldcmd + src + " " + tgt + "/"
#
   if DebugMode:
      PrintIt ("%s >>%s 2>&1" %(bldcmd, LogFileName))
   os.system ("%s >>%s 2>&1" %(bldcmd, LogFileName))
#
#
def CopyCanadaLocal (rcmd):
#
   cnt = 0
   while cnt < len (LocCanadaList):
      src = LocCanadaList[cnt]
      cnt = cnt + 1
      tgt = LocCanadaList[cnt]
      cnt = cnt + 1
      Call_Rsync(src,
                 tgt,
                 rcmd)
#
#  process html files to eliminate non-Canada data
   os.chdir (LOCAL_DEST + "/www/canada/PERFMON/html/field/thread_status")
   DoExternalCmd (CONVERT_THREAD_STAT,
                  external_parm1="CANADA",
                  debug_parm=DebugExt)
   os.chdir (LOCAL_DEST + "/www/canada/PERFMON/html/wre")
   DoExternalCmd (CONVERT_WRE_STAT,
                  external_parm1="CANADA",
                  external_parm2="1",
                  debug_parm=DebugExt)
   DoExternalCmd (CONVERT_WRE_STAT,
                  external_parm1="CANADA",
                  external_parm2="2",
                  debug_parm=DebugExt)
   DoExternalCmd (CONVERT_WRE_STAT,
                  external_parm1="CANADA",
                  external_parm2="3",
                  debug_parm=DebugExt)
   os.chdir ("/")
#
#
def CopyMexicoLocal (rcmd):
#
   cnt = 0
   while cnt < len (LocMexicoList):
      src = LocMexicoList[cnt]
      cnt = cnt + 1
      tgt = LocMexicoList[cnt]
      cnt = cnt + 1
      Call_Rsync(src,
                 tgt,
                 rcmd)
#
#  process html files to eliminate non-Mexico data
   os.chdir (LOCAL_DEST + "/www/mexico/PERFMON/html/field/thread_status")
   DoExternalCmd (CONVERT_THREAD_STAT,
                  external_parm1="MEXICO",
                  debug_parm=DebugExt)
   os.chdir (LOCAL_DEST + "/www/mexico/PERFMON/html/wre")
   DoExternalCmd (CONVERT_WRE_STAT,
                  external_parm1="MEXICO",
                  external_parm2="1",
                  debug_parm=DebugExt)
   DoExternalCmd (CONVERT_WRE_STAT,
                  external_parm1="MEXICO",
                  external_parm2="2",
                  debug_parm=DebugExt)
   DoExternalCmd (CONVERT_WRE_STAT,
                  external_parm1="MEXICO",
                  external_parm2="3",
                  debug_parm=DebugExt)
   os.chdir ("/")
#
#
def DoExternalCmd (external_cmd,
                   external_parm1 = None,
                   external_parm2 = None,
                   debug_parm = None):
#
   if external_parm1 is None:
      parm1 = ""
   else:
      parm1 = external_parm1
   if external_parm2 is None:
      parm2 = ""
   else:
      parm2 = external_parm2
   if debug_parm is None:
      debug = ""
   else:
      debug = debug_parm
#
   cmd = "which " + external_cmd
   stdout_value, stderr_value = Generic_Popen (cmd)
   if ((len (stdout_value) == 0) or (len (stderr_value) > 0)):
      PrintIt ("which " + cmd + " returns " + stderr_value)
      cmd = "find ~/. -name " + external_cmd
      stdout_value, stderr_value = Generic_Popen (cmd)
      if ((len (stdout_value) == 0) or (len (stderr_value) > 0)):
         raise SystemExit ("ERROR - Unable to find " + cmd + "=" + stderr_value)
      else:
         external_cmd = stdout_value.strip()
   else:
      external_cmd = stdout_value.strip()
   cmd = ("%s %s %s %s" %(external_cmd, parm1, parm2, debug))
   if DebugMode:
      PrintIt (cmd)
   stdout_value, stderr_value = Generic_Popen (cmd)
   if len (stderr_value) > 0:
      PrintIt ("ERROR - " + cmd + " returns " + stderr_value)
      raise SystemExit ("ERROR - " + external_cmd + "=" + stderr_value)
#
#
def Force_Single_Instance(lockfile):
#
#  try to open and lock a file
#  if unable, this denotes an instance is already running so exit
   lock_response = open("%s"%lockfile, "w")
   try:
      fcntl.lockf(lock_response,
                  fcntl.LOCK_EX | fcntl.LOCK_NB)
   except IOError as exc:
      PrintIt (time.asctime(time.localtime(time.time())) + \
                   "New instance attempting to run with instance already running.  New instance exiting.\n")
      raise SystemExit
#
   return lock_response
#
#
def Generic_Popen (popen_cmd):
#
   popen_result = subprocess.Popen(popen_cmd,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
   popen_out, popen_err = popen_result.communicate()
#
   return popen_out, \
          popen_err
#
#
def Is_Host_Alive (hostnme):
#
#  "prime" the call for while statement
   (p0, p1) = commands.getstatusoutput('ping -c 1 %s' %hostnme)
#
   cnt = 0
   while True:
      if p0 == 0:
         PrintIt ("Host is alive " + hostnme)
         return 1
      else:
         (p0, p1) = commands.getstatusoutput('ping -c1 -t1 %s' %hostnme)
         if cnt == 0:
            PrintIt ("   Trying host " + hostnme + " for up to 30 seconds")
         cnt = cnt + 1
#
      if cnt > 30:
         PrintIt ("Host is NOT responding " + hostnme)
         return 0
#
#
def PrintIt (print_string):
#
   global LogFile
   LogFile.write(print_string + "\n")
#
#
def UpdateLocalDirs (web_srvr,
                     rcmd):
#
   cnt = 0
   while cnt < len (LocDirList):
      src = LocDirList[cnt]
      cnt = cnt + 1
      tgt = LocDirList[cnt]
      cnt = cnt + 1
      Call_Rsync("monitor@" + web_srvr + ":" + src,
                 tgt,
                 rcmd,
                 ecmd=SSH_CMD)
#
#  The html pages ".../ess/performance/PERFMON/html/sl1/wre/*.html" have at least two issues.
#  1.  References are made as offsets i.e. "../../whatever" so when we added a level for "sl1" this became a problem.
#  2.  Instead of using skeleton webpages, the html is generated by the C code itself compounding the problem of making changes.
#  For Shadow Lite, the decision was made to copy the web pages to the local (cwfeed) server, do mass changes (hundreds) and then
#  push it all out to the web servers.
#
   DoExternalCmd (PID_TOOL_WRE_STATUS_FIX)
#
#  copy Mexico specific files from local performance directories to Mexico local performance directories
   CopyMexicoLocal (rcmd)
#
#  copy Canada specific files from local performance directories to Canada local performance directories
   CopyCanadaLocal (rcmd)
#
   AppliedUpdates = True
#
# This function pushes the data to the specified Test or Production server
# along with any server specific changes (differences between Test and Prod)
#
def UpdatePorT (web_srvr,
                rcmd):
#
   host_alive = Is_Host_Alive (web_srvr)
#
   if host_alive:
      cnt = 0
      while cnt < len (PorD_Pairs):
         src = PorD_Pairs[cnt]
         cnt = cnt + 1
         tgt = PorD_Pairs[cnt]
         cnt = cnt + 1
         Call_Rsync(src,
                    web_srvr + ":" + tgt,
                    rcmd,
                    ecmd=SSH_CMD)
#
#     Before pushing SVM data to the Test server, change the soft link to htdocs
      if web_srvr == TEST_WEB_SRVR:
         cmd = "ls -l " + SVM_HOME_HTDOCS + "htdocs | awk '{print$11}'"
         stdout_value, stderr_value = Generic_Popen (cmd)
         prod_htdocs = stdout_value
         link_target = stdout_value

         PrintIt ("Original " + SVM_HOME_HTDOCS + "htdocs -> " + prod_htdocs)
         if len (stderr_value) > 0:
            PrintIt ("==>" + str(stderr_value) + "<==>" + str(len (stderr_value)) + "<==")
         else:
#           remove production link
            PrintIt ("1-Before the link is removed,  cmd = " + cmd)
            PrintIt ("1a-Before the link is removed, cmd = " + link_target)
            os.unlink(SVM_HOME_HTDOCS + "htdocs")
            cmd = "ls -l " + SVM_HOME_HTDOCS + "htdocs | awk '{print$11}'"
            stdout_value, stderr_value = Generic_Popen (cmd)
            test_htdocs = stdout_value
            No_link     = test_htdocs
            PrintIt ("2-After the link is removed,  cmd should be empty. " + cmd)
            PrintIt ("2a-After the link is removed, cmd should be empty. " + No_link)
#           create test link
#            os.symlink(SVM_HOME_HTDOCS + "htdocs_test htdocs")
#            Link_Target = 'htdocs_SVM_LITE-0039-NA-OKC_ENV-01'   
            os.symlink(prod_htdocs, SVM_HOME_HTDOCS + "htdocs")
            cmd = "ls -l " + SVM_HOME_HTDOCS + "htdocs | awk '{print$11}'"  
            stdout_value, stderr_value = Generic_Popen (cmd)
            test_htdocs = stdout_value
            PrintIt ("3-the link is re-created as, cmd = " + test_htdocs)

            PrintIt ("Test " + SVM_HOME_HTDOCS + "htdocs -> " + test_htdocs)
            if len (stderr_value) > 0:
               PrintIt ("==>" + str(stderr_value) + "<==>" + str(len (stderr_value)) + "<==")

#           remove and redefine the cgi-bin link
#           get the production cgi-bin link
            cmd = "ls -l " + SVM_HOME_HTDOCS + "cgi-bin | awk '{print$11}'"
            stdout_value, stderr_value = Generic_Popen (cmd)
            prod_cgi_bin = stdout_value
            PrintIt ("Original " + SVM_HOME_HTDOCS + "cgi-bin -> " + prod_cgi_bin)
            if len (stderr_value) > 0:
               PrintIt ("==>" + str(stderr_value) + "<==>" + str(len (stderr_value)) + "<==")
            os.unlink(SVM_HOME_HTDOCS + "cgi-bin")
            os.symlink(SVM_HOME_HTDOCS + "cgi-bin_test cgi-bin")
            cmd = "ls -l " + SVM_HOME_HTDOCS + "cgi-bin | awk '{print$11}'"
            stdout_value, stderr_value = Generic_Popen (cmd)
            test_cgi_bin = stdout_value
            PrintIt ("Original " + SVM_HOME_HTDOCS + "cgi-bin -> " + test_cgi_bin)
            if len (stderr_value) > 0:
               PrintIt ("==>" + str(stderr_value) + "<==>" + str(len (stderr_value)) + "<==")
#           Web Test Sync
            PrintIt ("===Syncing cwfeed to waas-test web server===")
            Call_Rsync(SVM_Pairs[0],
                       web_srvr + ":" + SVM_Pairs[1],
                       rcmd,
                       ecmd=SSH_CMD,
                       xtra="--exclude=FIELD --exclude=BSHADOW1 --exclude=ESHADOW1 --exclude=SL1 --exclude=cgi-bin_SVM_LITE-* --exclude=htdocs_SVM_LITE-*")
#           remove test htdocs link
            os.unlink(SVM_HOME_HTDOCS + "htdocs")
#           create production htdocs link
            os.symlink(SVM_HOME_HTDOCS + "prod_htdocs htdocs")
            cmd = "ls -l " + SVM_HOME_HTDOCS + "htdocs | awk '{print$11}'"
            stdout_value, stderr_value = Generic_Popen (cmd)
            prod_htdocs = stdout_value
            PrintIt ("Prod " + SVM_HOME_HTDOCS + "htdocs->" + prod_htdocs)
            if len (stderr_value) > 0:
               PrintIt ("==>" + str(stderr_value) + "<==>" + str(len (stderr_value)) + "<==")
#           remove test cgi-bin link
            os.unlink(SVM_HOME_HTDOCS + "cgi-bin")
#           create production htdocs link
            os.symlink(SVM_HOME_HTDOCS + "prod_htdocs cgi-bin")
            cmd = "ls -l " + SVM_HOME_HTDOCS + "cgi-bin | awk '{print$11}'"
            stdout_value, stderr_value = Generic_Popen (cmd)
            prod_cgi_bin = stdout_value
            PrintIt ("Prod " + SVM_HOME_HTDOCS + "cgi-bin -> " + prod_cgi-bin)
            if len (stderr_value) > 0:
               PrintIt ("==>" + str(stderr_value) + "<==>" + str(len (stderr_value)) + "<==")
      else:
            Call_Rsync(SVM_Pairs[0],
                       web_srvr + ":" + SVM_Pairs[1],
                       rcmd,
                       ecmd=SSH_CMD)
#
      if web_srvr == PROD_WEB_SRVR:
#        After pushing data to the production server,
#        mv the production index to the default index and delete the test index
         cmd = SSH_CMD + " " + web_srvr + " mv " + \
               PERFORMANCE_INDEX_DIR + "index_prod.html " + \
               PERFORMANCE_INDEX_DIR + "index.html"
         stdout_value, stderr_value = Generic_Popen (cmd)
         if len (stderr_value) > 0:
            PrintIt ("==>" + stderr_value + "<==>" + len (stderr_value) + "<==")
         cmd = SSH_CMD + " " + web_srvr + " rm " + \
               PERFORMANCE_INDEX_DIR + "index_test.html"
         stdout_value, stderr_value = Generic_Popen (cmd)
         if len (stderr_value) > 0:
            PrintIt ("==>" + stderr_value + "<==>" + len (stderr_value) + "<==")
      else:
#        After pushing data to the test server,
#        mv the test index to the default index and delete the prod index
         cmd = SSH_CMD + " " + web_srvr + " mv " + \
               PERFORMANCE_INDEX_DIR + "index_test.html " + \
               PERFORMANCE_INDEX_DIR + "index.html"
         stdout_value, stderr_value = Generic_Popen (cmd)
         if len (stderr_value) > 0:
            PrintIt ("==>" + str(stderr_value) + "<==>" + str(len (stderr_value)) + "<==")
         cmd = SSH_CMD + " " + web_srvr + " rm " + \
               PERFORMANCE_INDEX_DIR + "index_prod.html"
         stdout_value, stderr_value = Generic_Popen (cmd)
         if len (stderr_value) > 0:
            PrintIt ("==>" + str(stderr_value) + "<==>" + str(len (stderr_value)) + "<==")
#
#
def VerifyInputs ():
#
   global DebugMode
#
   cnt = 0
   while cnt < len (Src_Dirs):
      src = Src_Dirs[cnt]
      if DebugMode:
         PrintIt ("Checking " + src)
      if not os.path.exists(src):
         if DebugMode:
            PrintIt ("Creating " + src)
         os.makedirs(src)
      cnt = cnt + 1
#
#
#
def main():
#
   global DebugExt
   global DebugMode
   global LogFile
   global LogFileName
#
   ProgWithExt = os.path.basename(sys.argv[0])
   Prog = os.path.splitext(ProgWithExt)[0]
   DOW = time.strftime("%A")
   DOW = DOW[:3]
   STD_LOG = STD_LOG_pre + Prog + "_" + DOW + STD_LOG_suf
   if os.path.exists(STD_LOG):
      filedatesec = int(round(os.path.getmtime(STD_LOG)))
      if round((int(round(time.time())) - int(filedatesec))/SPER_DAY) > 1:
         os.remove(STD_LOG)
#
   usage = "Summary: This script updates performance website data.\n\n"
   short_usage = "%s [-l <log path>] [-r <rsync command(s)>] [-v]" %ProgWithExt
   usage = usage + short_usage
   usage = usage + '\n\nExample:\n  %s \n  updates the latest data using standard defaults. ' \
         '\n (log file = %s) ' \
         '\n (rsync command = "%s") ' \
         %(ProgWithExt, STD_LOG, RSYNC_W_CMPR)
#
   parser = OptionParser(usage=usage)
   parser.add_option("-?", "--usage",
                   action="store_true", dest="SayUsage", default=False,
                   help="Print usage information")
   parser.add_option("-v", "--verbose",
                   action="store_true", dest="RunVerbose", default=False,
                   help="Run in verbose mode")
   parser.add_option("--version",
                   action="store_true", dest="SayVersion", default=False,
                   help="Print version information")
   parser.add_option("-l", "--LogFileName",
                   action="store", type="string", dest="ParmLogFile", default="",
                   help="The output log file.")
   parser.add_option("-r", "--rsyncmd",
                   action="store", type="string", dest="RsyncCmd", default="",
                   help="The RSYNC parameters.")
   (options, args) = parser.parse_args()
#
#  request for version?
   if options.SayVersion:
      print (short_usage + "  Version " + VERSION)
      return
#
#  request for usage?
   if options.SayUsage:
      print (short_usage)
      return
#
   if options.ParmLogFile != "":
      LogFileName = options.ParmLogFile
   else:
      LogFileName = STD_LOG
#
   if options.RsyncCmd != "":
      rcmd = options.RsyncCmd
   else:
      rcmd = RSYNC_W_CMPR
#
#  create a new log file (over-writes any prexisting file)
   LogFile = open(LogFileName, "w")
   os.chmod(LogFileName, 0777)    # make the logfile whatever permissions you want
#
   PrintIt ('\n%s %s %s  start' %(ProgWithExt, VERSION, str(time.asctime(time.localtime(time.time())))))
   if options.RunVerbose:
      PrintIt ('\nRunning in verbose mode')
      DebugExt = "DBG"
      DebugMode = True
   else:
      DebugExt = ""
      DebugMode = False
#
#  print the parameters.
   PrintIt ('\n%s\nlog=%s\nrsync=%s' %(ProgWithExt, LogFileName, rcmd))
#
#  insure this script is not already running and exit if it is
   lock_file = LOCK_BASE + ProgWithExt + '.lck'
   lock_response = Force_Single_Instance (lock_file)
#
   AppliedUpdates = False
#
#  verify input directory structure exists
   VerifyInputs ()
#
   host_alive = Is_Host_Alive (PERFMON_SERVER)
#
   if host_alive:
#
#     update the local /rec_data...
      UpdateLocalDirs (PERFMON_SERVER,
                       rcmd)
#
#     copy remote directory history and all contents to local directory PERFMON
      src = "monitor@" + PERFMON_SERVER + ":/rec_data/perfdata1/history/"
      dst = LOCAL_DEST + "/www/performance/PERFMON/history"
      Call_Rsync (src,
                  dst,
                  RSYNC_W_CMPR,
                  ecmd=SSH_CMD)
#
#     copy remote directory history and all contents to local directory PERFMON for SL1
      src = "monitor@" + PERFMON_SERVER + ":/rec_data/perfdatasl1/history/"
      dst = LOCAL_DEST + "/www/performance/PERFMON/history/sl1"
      Call_Rsync (src,
                  dst,
                  RSYNC_W_CMPR,
                  ecmd=SSH_CMD)
#
#     copy Mexico specific files from local performance directories to Mexico local performance directories
      src = LOCAL_DEST + "/www/performance/PERFMON/history/wre/M*.txt"
      dst = LOCAL_DEST + "/www/mexico/PERFMON/history/wre"
      Call_Rsync (src,
                  dst,
                  RSYNC_WO_CMPR)
#
#     copy Canada specific files from local performance directories to Canada local performance directories
      src = LOCAL_DEST + "/www/performance/PERFMON/history/wre/Y*.txt"
      dst = LOCAL_DEST + "/www/canada/PERFMON/history/wre"
      Call_Rsync (src,
                  dst,
                  RSYNC_WO_CMPR)
#
#  copy SVM files
   Call_Rsync("/svmdata/",
              LOCAL_DEST + "/www/performance/SVM/raw",
              RSYNC_W_CMPR,
              xtra="--exclude=*.sto --exclude=*.error --exclude=*_rerun/ \
                    --exclude=Clients/ --exclude=hold/ --exclude=LOGS/ \
                    --exclude=prep/ --exclude=REMOTE*/ --exclude=RUNS/ \
                    --exclude=yuma/ --exclude=prep/ --del")
   AppliedUpdates = True
#
# copy WUPS summary files
   Call_Rsync("/wupsdata/FIELD/POST_PROCESS/RSAT/RSAT_Summary.txt",
              LOCAL_DEST + "/www/performance/AOS/",
              RSYNC_W_CMPR)
   AppliedUpdates = True
#
# TCS Data
   host_alive = Is_Host_Alive (TCS_SERVER)
   if host_alive:
#
#     copy TCS data
      src = TCS_SERVER + ":/cygdrive/c/WinNMS/Web/Internal_Web/Reports/"
      dst = LOCAL_DEST + "/www/performance/TCS/Reports"
      Call_Rsync (src,
                  dst,
                  RSYNC_W_CMPR,
                  ecmd=SSH_CMD)
#
#     copy TCS logs
      src = TCS_SERVER + ":/cygdrive/c/WinNMS/NMS/*.log"
      dst = LOCAL_DEST + "/www/performance/TCS/Logs"
      Call_Rsync (src,
                  dst,
                  RSYNC_W_CMPR,
                  ecmd=SSH_CMD)
#
#     copy Mexico specific files from local TCS directories to Mexico local TCS directories
      Call_Rsync (LOCAL_DEST + "/www/performance/TCS/Reports/*Mexico*.htm",
                  LOCAL_DEST + "/www/mexico/TCS/Reports",
                  RSYNC_WO_CMPR)
      Call_Rsync (LOCAL_DEST + "/www/performance/TCS/Reports/{mib_In_Errors.html,mib_Mpkts_Out.html}",
                  LOCAL_DEST + "/www/mexico/TCS/Reports",
                  RSYNC_WO_CMPR)
#
#     process html files to eliminate non-Mexico data
      os.chdir (LOCAL_DEST + "/www/mexico/TCS/Reports")
      DoExternalCmd (CONVERT_MIB_ERRORS,
                     external_parm1="MEXICO",
                     debug_parm=DebugExt)
      DoExternalCmd (CONVERT_MIB_OUT,
                     external_parm1="MEXICO",
                     debug_parm=DebugExt)
      os.chdir ("/")
#
#     copy Canada specific files from local TCS directories to Canada local TCS directories
      Call_Rsync (LOCAL_DEST + "/www/performance/TCS/Reports/*Canada*.htm",
                  LOCAL_DEST + "/www/canada/TCS/Reports",
                  RSYNC_WO_CMPR)
      Call_Rsync (LOCAL_DEST + "/www/performance/TCS/Reports/{mib_In_Errors.html,mib_Mpkts_Out.html}",
                  LOCAL_DEST + "/www/canada/TCS/Reports",
                  RSYNC_WO_CMPR)
#
#     process html files to eliminate non-Canada data
      os.chdir (LOCAL_DEST + "/www/canada/TCS/Reports")
      DoExternalCmd (CONVERT_MIB_ERRORS,
                     external_parm1="CANADA",
                     debug_parm=DebugExt)
      DoExternalCmd (CONVERT_MIB_OUT,
                     external_parm1="CANADA",
                     debug_parm=DebugExt)
      os.chdir ("/")
      AppliedUpdates = True
#
   if AppliedUpdates == True:
#
#     update the production server
#??    UpdatePorT (PROD_WEB_SRVR,
#??                rcmd)
#
#     update the test server
      UpdatePorT (TEST_WEB_SRVR,
                  rcmd)
#
#
   PrintIt ('\n%s %s %s  finish' %(ProgWithExt, VERSION, str(time.asctime(time.localtime(time.time())))))
   return
#
if __name__ == '__main__':
    sys.exit(main())
#
