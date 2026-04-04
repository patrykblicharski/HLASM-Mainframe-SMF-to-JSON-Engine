* ====================================================================
* MASTER MAPPING TABLE FOR SMF TYPE 30 (JSON CONVERSION)
* ====================================================================

* CONSTANTS FOR DATA TYPES
T_BIN1   EQU   0      Binary 1 Byte
T_CHR1   EQU   1      EBCDIC STRING 1 Bytes
T_CHR2   EQU   2      EBCDIC STRING 2 Bytes
T_CHR4   EQU   3      EBCDIC STRING 4 Bytes
T_CHR8   EQU   4      EBCDIC STRING 8 Bytes 
T_DEC1   EQU   5      Decimal 1 Byte
T_DEC2   EQU   6      Decimal 2 Bytes
T_DEC4   EQU   7      Decimal 4 Bytes   
T_DTE    EQU   8      SMF DATE (4 Bytes)
T_TME    EQU   9      SMF TIME (4 Bytes)
T_RS_STR EQU   10     RS Variable Length EBCDIC String (Tag-Len-Data)
            

TABLE30  SMF_START   

         SMF_FIELD SMF30RTY-SMF30LEN,TYPE=T_DEC1,JSON=smf_record_tpe


         SMF_FIELD SMF30SID-SMF30LEN,TYPE=T_CHR4,JSON=smf_system_id


         SMF_FIELD SMF30TME-SMF30LEN,TYPE=T_TME,JSON=time


         SMF_FIELD SMF30DTE-SMF30LEN,TYPE=T_DTE,JSON=date


         SMF_FIELD SMF30RVN-SMF30PSS,TRIPLET=SMF30SOF-SMF30LEN,        X
               TYPE=T_CHR2,JSON=rec_version


         SMF_FIELD SMF30PNM-SMF30PSS,TRIPLET=SMF30SOF-SMF30LEN,        X
               TYPE=T_CHR8,JSON=addr_space_ind


         SMF_FIELD SMF30PGM-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X
               TYPE=T_CHR8,JSON=program_name


         SMF_FIELD SMF30STM-SMF30JBN,TRIPLET=SMF30IOF-SMF30LEN,        X
               TYPE=T_CHR8,JSON=step_name


         SMF_FIELD SMF30CPT-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=cpu_step_time


         SMF_FIELD SMF30CPS-SMF30PTY,TRIPLET=SMF30COF-SMF30LEN,        X
               TYPE=T_DEC4,JSON=srb_time


         SMF_END
