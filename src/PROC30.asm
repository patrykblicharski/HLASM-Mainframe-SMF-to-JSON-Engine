* --- Register definitions ---
R0       EQU   0
R1       EQU   1
R2       EQU   2
R3       EQU   3
R4       EQU   4
R5       EQU   5
R6       EQU   6
R7       EQU   7
R8       EQU   8
R9       EQU   9
R10      EQU   10
R11      EQU   11
R12      EQU   12
R13      EQU   13
R14      EQU   14
R15      EQU   15

PROC_30  CSECT
         IFASMFR (30)   * SMF Records structs
         
PROC_30  CSECT
         BAKR  R14,0         
         LR    R12,R15        
         USING PROC_30,R12

* --- R1 = adress to PARMLIST
         L     R2,0(,R1)       * get ADDR_SMF
         USING SMF30RHD,R2

         OPEN  (SNAPDCB,OUTPUT)   

* --- Extract SID (Offset +14) ---
         MVC   SIDJSON,SMF30SID
         LA    R1,SIDWTO      
         SVC   35  

* --- Extract WID Work address space (Offset +18) ---
         MVC   WIDJSON,SMF30WID
         LA    R1,WIDWTO     
         SVC   35    
* --- Extract STP Record subtype (Offset +22, size 2) ---
         SR    R4,R4             
         LH    R4,SMF30STP       * LOAD HALFWORD (2 bytes) in R4
* --- Conversion EBCDIC for 5 digits (0-65535) ---
         CVD   R4,DOUBLE         * Conversion Binaire -> Packed Decimal
* DOUBLE : 8 bytes. for 65535, packed data : 000000000065535C
         UNPK  STPJSON(5),DOUBLE+5(3) 
         OI    STPJSON+4,X'F0'
         LA    R1,STPWTO     
         SVC   35   
* Navigate to subsystem section (SMF TYPE 30)



* First Triplet : subsystem section (Offset, Length, Nomber)
* This section contains general record and system ident. information
         LA    R1,SMF30SOF    *Offset to subsystem section
         L     R3,0(,R1)      * R3=OFFSET
         ALR   R3,R2

         SR    R4,R4
         LH    R4,SMF30SLN    * Section Length
         SR    R5,R5
         LH    R5,SMF30SON    * Number of section
         LTR   R5,R5          * Test if Number sections is zero
         BZ    SKIP_SUB

*smf_record_type :
*1 : Job start or start of other work unit.
*2 : Activity since previous interval ended.
*Produced only wheninterval recording is active.
*3 : Activity for the last interval before step termination. Produced
*only when interval recording is active.
*4 : Step total
*5 : Job termination or termination of other work unit.
*6 : System address space

         USING SMF30PSS,R3    *PRODUCT OR SUBSYSTEM SECTION
         MVC   RVNJSON,SMF30RVN
         LA    R1,RVNWTO     
         SVC   35   
         MVC   PNMJSON,SMF30PNM
         LA    R1,PNMWTO     
         SVC   35   
         MVC   OSLJSON,SMF30OSL
         LA    R1,OSLWTO     
         SVC   35  
         MVC   SYNJSON,SMF30SYN
         LA    R1,SYNWTO     
         SVC   35  
         MVC   SYPJSON,SMF30SYP
         LA    R1,SYPWTO     
         SVC   35  

SKIP_SUB SR    R4,R4
         
* 2nd Triplet : Identification section (Offset, Length, Nomber)
         LA    R1,SMF30IOF    *Offset to Identification section
         L     R3,0(,R1)      * R3=OFFSET
         ALR   R3,R2
 
         LH    R4,SMF30ILN    * Section Length
         SR    R5,R5
         LH    R5,SMF30ION    * Number of section
         LTR   R5,R5          * Test if Number sections is zero
         BZ    SKIP_ID

         USING SMF30ID,R3    *PRODUCT OR SUBSYSTEM SECTION
         MVC   JBNJSON,SMF30JBN
         LA    R1,JBNWTO     
         SVC   35  
         MVC   PGMJSON,SMF30PGM *PROGRAM NAME
         LA    R1,PGMWTO     
         SVC   35  
         MVC   STMJSON,SMF30STM *STEP NAME
         LA    R1,STMWTO     
         SVC   35              
         MVC   UIFJSON,SMF30UIF *User identification
         LA    R1,UIFWTO     
         SVC   35     

SKIP_ID  SR    R4,R4

* 3rd Triplet : I/O activity section (Offset, Length, Nomber)
         LA    R1,SMF30UOF    *Offset to Identification section
         L     R3,0(,R1)      * R3=OFFSET
         ALR   R3,R2

         LH    R4,SMF30ULN    * Section Length
         SR    R5,R5
         LH    R5,SMF30UON    * Number of section
         LTR   R5,R5          * Test if Number sections is zero
         BZ    SKIP_URA
         
         USING SMF30URA,R3     *I/O ACTIVITY SECTION

         MVC   DOUBLE(8),SMF30AIW   
* --- Conversion ---
         L     R1,DOUBLE            
         ST    R1,TEMPVAL
         UNPK  HEXWORK(9),TEMPVAL(5)
         NC    HEXWORK(8),MASK0F
         TR    HEXWORK(8),HEXTAB
         MVC   URAJSON(8),HEXWORK  

         LA    R1,URAWTO
         SVC   35

         MVC   DOUBLE(8),SMF30AIS   
* --- Conversion ---
         L     R1,DOUBLE            
         ST    R1,TEMPVAL
         UNPK  HEXWORK(9),TEMPVAL(5)
         NC    HEXWORK(8),MASK0F
         TR    HEXWORK(8),HEXTAB
         MVC   AISJSON(8),HEXWORK  

         LA    R1,AISWTO
         SVC   35

SKIP_URA SR    R4,R4

* 4st Triplet : Completion section (Offset, Length, Nomber)
         LA    R1,SMF30TOF    *Offset to Completion section
         L     R3,0(,R1)      * R3=OFFSET
         ALR   R3,R2

         LH    R4,SMF30TLN    * Section Length
         SR    R5,R5
         LH    R5,SMF30TON    * Number of section
         LTR   R5,R5          * Test if Number sections is zero
         BZ    SKIP_CMP

         USING SMF30CMP,R3     *COMPLETION SECTION

* --- Extract Completion code  ---
         SR    R4,R4             
         LH    R4,SMF30SCC       * LOAD HALFWORD (2 bytes) in R4
* --- Conversion EBCDIC for 5 digits (0-65535) ---
         CVD   R4,DOUBLE         * Conversion Binaire -> Packed Decimal
* DOUBLE : 8 bytes. for 65535, packed data : 000000000065535C
         UNPK  CMPJSON(5),DOUBLE+5(3) 
         OI    CMPJSON+4,X'F0'
         LA    R1,CMPWTO     
         SVC   35  

SKIP_CMP SR    R4,R4

* 5st Triplet : Processor section (Offset, Length, Nomber)
         LA    R1,SMF30COF    *Offset to Completion section
         L     R3,0(,R1)      * R3=OFFSET
         ALR   R3,R2

         LH    R4,SMF30CLN    * Section Length
         SR    R5,R5
         LH    R5,SMF30CON    * Number of section
         LTR   R5,R5          * Test if Number sections is zero
         BZ    SKIP_CAS

         USING SMF30CAS,R3     *CPU ACCOUNTING SECTION

         MVC   DOUBLE(8),SMF30CPT   
* --- Conversion ---
         L     R1,DOUBLE            
         ST    R1,TEMPVAL
         UNPK  HEXWORK(9),TEMPVAL(5)
         NC    HEXWORK(8),MASK0F
         TR    HEXWORK(8),HEXTAB
         MVC   CPTJSON(8),HEXWORK  
         LA    R1,CPTWTO
         SVC   35

         MVC   DOUBLE(8),SMF30CPS   
* --- Conversion ---
         L     R1,DOUBLE            
         ST    R1,TEMPVAL
         UNPK  HEXWORK(9),TEMPVAL(5)
         NC    HEXWORK(8),MASK0F
         TR    HEXWORK(8),HEXTAB
         MVC   CPSJSON(8),HEXWORK  
         LA    R1,CPSWTO
         SVC   35

*         LLGH  R3,0(,R2)       * R3=(R1) en 16bits no signed
*         AR    R3,R2           * R3 = Adresse de fin
*         SNAP  DCB=SNAPDCB,ID=50,PDATA=REGS,STORAGE=((R2),(R3))    
*         CLOSE (SNAPDCB)

SKIP_CAS PR

         DS    0D                 * Doubleword alignment : 64bits
DOUBLE   DS    D

         DS    0F                 * Fullword alignment : 32 bits
SIDWTO   DC    AL2(SIDEND-SIDWTO)
         DC    XL2'0000'
         DC    C'"smf_system_id": "'
SIDJSON  DC    CL4'    '         
         DC    C'",'
SIDEND   EQU   *
WIDWTO   DC    AL2(WIDEND-WIDWTO)
         DC    XL2'0000'
         DC    C'"work_address_space_ind": "'
WIDJSON  DC    CL4'    '         
         DC    C'",'
WIDEND   EQU   *
STPWTO   DC    AL2(STPEND-STPWTO)
         DC    XL2'0000'
         DC    C'"smf_record_subtype": "'
STPJSON  DC    CL5'     '         
         DC    C'",'
STPEND   EQU   *  
RVNWTO   DC    AL2(RVNEND-RVNWTO)
         DC    XL2'0000'
         DC    C'"smf_record_version": "'
RVNJSON  DC    CL2'  '         
         DC    C'",'
RVNEND   EQU   *  
PNMWTO   DC    AL2(PNMEND-PNMWTO)
         DC    XL2'0000'
         DC    C'"product_name": "'
PNMJSON  DC    CL8'        '         
         DC    C'",'
PNMEND   EQU   *  
OSLWTO   DC    AL2(OSLEND-OSLWTO)
         DC    XL2'0000'
         DC    C'"os_level": "'
OSLJSON  DC    CL8'        '         
         DC    C'",'
OSLEND   EQU   *  
SYNWTO   DC    AL2(SYNEND-SYNWTO)
         DC    XL2'0000'
         DC    C'"system_name": "'
SYNJSON  DC    CL8'        '         
         DC    C'",'
SYNEND   EQU   *  
SYPWTO   DC    AL2(SYPEND-SYPWTO)
         DC    XL2'0000'
         DC    C'"sysplex_name": "'
SYPJSON  DC    CL8'        '         
         DC    C'",'
SYPEND   EQU   *  
JBNWTO   DC    AL2(JBNEND-JBNWTO)
         DC    XL2'0000'
         DC    C'"job_name": "'
JBNJSON  DC    CL8'        '         
         DC    C'",'
JBNEND   EQU   *  
PGMWTO   DC    AL2(PGMEND-PGMWTO)
         DC    XL2'0000'
         DC    C'"program_name": "'
PGMJSON  DC    CL8'        '         
         DC    C'",'
PGMEND   EQU   *  
STMWTO   DC    AL2(STMEND-STMWTO)
         DC    XL2'0000'
         DC    C'"step_name": "'
STMJSON  DC    CL8'        '         
         DC    C'",'
STMEND   EQU   *  
UIFWTO   DC    AL2(UIFEND-UIFWTO)
         DC    XL2'0000'
         DC    C'"user_id": "'
UIFJSON  DC    CL8'        '         
         DC    C'",'
UIFEND   EQU   *  
URAWTO   DC    AL2(URAEND-URAWTO)
         DC    XL2'0000'
         DC    C'"dasd_io_pending_cu_queue_time": "'
URAJSON  DC    CL8'        '         
         DC    C'",'
URAEND   EQU   *
AISWTO   DC    AL2(AISEND-AISWTO)
         DC    XL2'0000'
         DC    C'"dasd_io_start_subchannel_count": "'
AISJSON  DC    CL8'        '         
         DC    C'",'
AISEND   EQU   *
CMPWTO   DC    AL2(CMPEND-CMPWTO)
         DC    XL2'0000'
         DC    C'"completion_code": "'
CMPJSON  DC    CL5'     '         
         DC    C'",'
CMPEND   EQU   * 
CPTWTO   DC    AL2(CPTEND-CPTWTO)
         DC    XL2'0000'
         DC    C'"cpu_step_time": "'
CPTJSON  DC    CL8'        '         
         DC    C'",'
CPTEND   EQU   *
CPSWTO   DC    AL2(CPSEND-CPSWTO)
         DC    XL2'0000'
         DC    C'"srb_time": "'
CPSJSON  DC    CL8'        '         
         DC    C'",'
CPSEND   EQU   *

TEMPVAL  DS    F                    * 32 bits Temp stockage 
HEXWORK  DS    CL9                  * working zone for UNPK

* --- For Bin/Hexa convertion
MASK0F   DC    8X'0F'               * 8 bytes 0x0F
HEXTAB   DC    C'0123456789ABCDEF'  * Convertion table

         DS    0F                 * Fullword alignment : 32 bits

* Warning : comma to cols number 72 
SNAPDCB  DCB   DSORG=PS,MACRF=(W),DDNAME=SNAP,RECFM=VBA,               X
               LRECL=125,BLKSIZE=882         
         END
         