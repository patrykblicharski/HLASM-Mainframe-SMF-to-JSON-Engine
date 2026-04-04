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
T_DEC2   EQU   6      Decimal 1 Byte
T_DEC4   EQU   7      Decimal 1 Byte   
T_DTE    EQU   8      SMF DATE (PL4)
T_TME    EQU   9      SMF TIME (BIN4)
T_RS_STR EQU   10     RS Variable Length EBCDIC String (Tag-Len-Data)


         DS    0F                

TABLE30  EQU   *       

         DC    AL4(SMF30RTY-SMF30LEN),AL4(0)
         DC    AL1(T_DEC1),AL3(0)
         DC    CL16'smf_record_type'

         DC    AL4(SMF30SID-SMF30LEN),AL4(0)
         DC    AL1(T_CHR4),AL3(0)
         DC    CL16'smf_system_id'

         DC    AL4(SMF30TME-SMF30LEN),AL4(0)
         DC    AL1(T_TME),AL3(0)
         DC    CL16'time'

         DC    AL4(SMF30DTE-SMF30LEN),AL4(0)
         DC    AL1(T_DTE),AL3(0)
         DC    CL16'date'

         DC    AL4(SMF30RVN-SMF30PSS),AL4(SMF30SOF-SMF30LEN)
         DC    AL1(T_CHR2),AL3(0)
         DC    CL16'rec_version'

         DC    AL4(SMF30PNM-SMF30PSS),AL4(SMF30SOF-SMF30LEN)
         DC    AL1(T_CHR8),AL3(0)
         DC    CL16'addr_space_ind'

         DC    AL4(SMF30PGM-SMF30JBN),AL4(SMF30IOF-SMF30LEN)
         DC    AL1(T_CHR8),AL3(0)
         DC    CL16'program_name'

         DC    AL4(SMF30STM-SMF30JBN),AL4(SMF30IOF-SMF30LEN)
         DC    AL1(T_CHR8),AL3(0)
         DC    CL16'step_name'

         DC    AL4(SMF30CPT-SMF30PTY),AL4(SMF30COF-SMF30LEN)
         DC    AL1(T_DEC4),AL3(0)
         DC    CL16'cpu_step_time'

         DC    AL4(SMF30CPS-SMF30PTY),AL4(SMF30COF-SMF30LEN)
         DC    AL1(T_DEC4),AL3(0)
         DC    CL16'srb_time'

         DC    AL4(0)      * End of Table
