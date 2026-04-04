* ====================================================================
* MASTER MAPPING TABLE FOR SMF TYPE 80 (JSON CONVERSION)
* ====================================================================

* CONSTANTS FOR RS DATA TYPES : Relocate Section Variable Data
T_RS_1   EQU   1     Old resource name
T_RS_2   EQU   2     New data set name 
T_RS_8   EQU   8     NAME user-name
T_RS_9   EQU   9     Resource name 
T_RS_13  EQU   13    FROM resource name
T_RS_15  EQU   15    VOLSER volume serial  
T_RS_17  EQU   17    Class name 



         DS    0F                  

TABLE80  EQU   * 
         DC    AL4(SMF80RTY-SMF80LEN),AL4(0)
         DC    AL1(T_DEC1),AL3(0)
         DC    CL16'smf_record_type'

         DC    AL4(SMF80SID-SMF80LEN),AL4(0)
         DC    AL1(T_CHR4),AL3(0)
         DC    CL16'smf_system_id'

         DC    AL4(SMF80TME-SMF80LEN),AL4(0)
         DC    AL1(T_TME),AL3(0)
         DC    CL16'time'

         DC    AL4(SMF80DTE-SMF80LEN),AL4(0)
         DC    AL1(T_DTE),AL3(0)
         DC    CL16'date'

         DC    AL4(SMF80USR-SMF80LEN),AL4(0)
         DC    AL1(T_CHR8),AL3(0)
         DC    CL16'user_id'

         DC    AL4(SMF80GRP-SMF80LEN),AL4(0)
         DC    AL1(T_CHR8),AL3(0)
         DC    CL16'group_name'

         DC    AL4(SMF80REL-SMF80LEN),AL4(0)
         DC    AL1(T_RS_STR),AL1(T_RS_1),AL2(0)
         DC    CL16'old_resource'

         DC    AL4(SMF80REL-SMF80LEN),AL4(0)
         DC    AL1(T_RS_STR),AL1(T_RS_17),AL2(0)
         DC    CL16'class_name'

         DC    AL4(0)      * End of Table
