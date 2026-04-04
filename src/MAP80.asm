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



TABLE80  SMF_START             

         SMF_FIELD SMF80RTY-SMF80LEN,TYPE=T_DEC1,JSON=smf_record_type


         SMF_FIELD SMF80SID-SMF80LEN,TYPE=T_CHR4,JSON=smf_system_id


         SMF_FIELD SMF80TME-SMF80LEN,TYPE=T_TME,JSON=time


         SMF_FIELD SMF80DTE-SMF80LEN,TYPE=T_DTE,JSON=date


         SMF_FIELD SMF80USR-SMF80LEN,TYPE=T_CHR8,JSON=user_id


         SMF_FIELD SMF80GRP-SMF80LEN,TYPE=T_CHR8,JSON=group_name


         SMF_FIELD SMF80REL-SMF80LEN,TYPE=T_RS_STR,TAG=T_RS_1,         X
               JSON=old_resource


         SMF_FIELD SMF80REL-SMF80LEN,TYPE=T_RS_STR,TAG=T_RS_17,        X
               JSON=class_name


         SMF_END

