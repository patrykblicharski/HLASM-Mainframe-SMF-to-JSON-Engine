*---------------------------------------------------------------------*
* PROGRAM: SMF2JSON                                                   *
* PURPOSE: CONVERT SMF RECORDS (30/70/71/72/80/89) TO JSON FORMAT     *
* FEATURES: SUPPORTS STANDARD TCB MODE OR zIIP SRB OFFLOAD            *
*---------------------------------------------------------------------*
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

      
         COPY  CONFIG         * System-wide configuration
         IFASMFR (30,70,71,72,80,89)  * IBM SMF Record Mappings

         
         AIF   (&USEZIIP EQ 0).NOZIIP    Check if zIIP mode

         IWMYCON             * WLM Constants
         CVT   DSECT=YES     *Communications Vector Table for IWMECREA
         IHASRB              * SRB Control Block Mapping
         COPY  ZSCHDSRB

.NOZIIP  ANOP


START    CSECT
START    AMODE 31                  * 31-bit addressing mode
               

         BAKR  R14,0       *Save caller's environment to Linkage Stack
         LR    R12,R15     *Establish Base Register
         USING START,R12


         EXTRN SMF2ZIIP    * External SRB Routine     
*--- Environment Setup Logic ---*
         AIF   (&USEZIIP EQ 1).MODE_SRB
         WTO   'INF: SMF2JSON - RUNNING IN STANDARD TCB MODE'
         AGO   .CONT
.MODE_SRB ANOP
         WTO   'INF: SMF2JSON - RUNNING IN zIIP SRB MODE'

         TESTAUTH FCTN=1          * SRB Autorisation Test
         LTR   R15,R15            * R15=0 si OK
         BZ    DO_SRB            * Branch Authorized
         WTO   'ERR: NOT AUTHORIZED FOR SRB DISPATCH'
         ABEND 777,DUMP
DO_SRB   EQU   *
.CONT    ANOP


*--- Resource Acquisition ---*
         STORAGE OBTAIN,LENGTH=DW_SIZE,LOC=ANY,COND=NO
         ST    R1,P_WORKAREA    * R1 Addr

         OPEN  (SMFFILE,INPUT)
         OPEN  (JSONOUT,OUTPUT)

         MVI   DW_FJSON,X'01'   *Initialize first object flag

*--- JSON Header (Array Start) ---*
         MVI   BUF_DATA,C'['    * SET CLOSING BRACKET AT DATA START
         LHI   R1,5             * R1 = 5 (TOTAL RECORD LENGTH)
         STH   R1,BUF_RDW       * STORE LENGTH IN FIRST 2 BYTES OF RDW
         XC    BUF_RDW+2(2),BUF_RDW+2 * CLEAR BYTES (OFFSET 2)
         PUT   JSONOUT,BUFFERVB

*--- Main Processing Loop ---*
NEXT_SMF GET   SMFFILE            * Read SMF File
         LR    R9,R1              * Save RDW

*--- Spanned Records Handling (VBS) ---*
         CLI   2(R9),X'00' * Is this a complete, non-spanned record?
         BE    RDW_OK      * Yes, proceed to processing
         WTO   'WRN: SPANNED RECORD SEGMENT SKIPPED'
         J     NEXT_SMF

* --- SKIP TYPE 2 ---
RDW_OK   CLI   5(R9),X'02'        * type 2 record ?
         BE    NEXT_SMF           * If Yes Skip-it : Next
* --- SKIP TYPE 3 ---
         CLI   5(R9),X'03'        * type 3 record  ?
         BE    NEXT_SMF           * If Yes Skip-it : Next

* ---  TYPE 30 (subtype at SMF30STP / offset 22) ---
         CLI   5(R9),30
         BNE   NO_30
         LH    R1,22(,R9)        * SMF30STP
         CHI   R1,1
         BNE   T30_2
         LARL  R8,TABLE30_1
         J     JSONOBJ
T30_2    CHI   R1,2
         BNE   T30_3
         LARL  R8,TABLE30_2
         J     JSONOBJ
T30_3    CHI   R1,3
         BNE   T30_4
         LARL  R8,TABLE30_3
         J     JSONOBJ
T30_4    CHI   R1,4
         BNE   T30_5
         LARL  R8,TABLE30_4
         J     JSONOBJ
T30_5    CHI   R1,5
         BNE   T30_6
         LARL  R8,TABLE30_5
         J     JSONOBJ
T30_6    CHI   R1,6
         BNE   T30_DEF
         LARL  R8,TABLE30_6
         J     JSONOBJ
T30_DEF  LARL  R8,TABLE30        * unknown subtype -> default map
         J     JSONOBJ
NO_30    EQU   *

* ---  TYPE 70 (RMF CPU / crypto; subtype SMF70STY) ---
         CLI   5(R9),70
         BNE   NO_70
         LH    R1,22(,R9)
         CHI   R1,1
         BNE   T70_2
         LARL  R8,TABLE70_1
         J     JSONOBJ
T70_2    CHI   R1,2
         BNE   T70_DEF
         LARL  R8,TABLE70_2
         J     JSONOBJ
T70_DEF  J     NEXT_SMF          * unsupported 70 subtype
NO_70    EQU   *

* ---  TYPE 71 SUBTYPE 1 (paging) ---
         CLI   5(R9),71
         BNE   NO_71
         LH    R1,22(,R9)
         CHI   R1,1
         BNE   NO_71
         LARL  R8,TABLE71_1
         J     JSONOBJ
NO_71    EQU   *

* ---  TYPE 72 SUBTYPE 3 (WLM workload) ---
         CLI   5(R9),72
         BNE   NO_72
         LH    R1,22(,R9)
         CHI   R1,3
         BNE   NO_72
         LARL  R8,TABLE72_3
         J     JSONOBJ
NO_72    EQU   *

* ---  TYPE 80 ---
         CLI   5(R9),80
         BNE   NO_80
         LARL  R8,TABLE80
         J     JSONOBJ
NO_80    EQU   *

* ---  TYPE 89 ---
         CLI   5(R9),89
         BNE   NO_89
         LARL  R8,TABLE89
         J     JSONOBJ
NO_89    J     NEXT_SMF
         

JSONOBJ  EQU   *

         LARL  R5,BUF_DATA       * New Ligne R5=BUF_DATA

         CLI   DW_FJSON,X'01'    * First JSON Objet ?
         BE    FJSONOBJ

         MVI   0(R5),C','        * Close JSON object
         LA    R5,1(,R5)
         B     STARTOBJ

FJSONOBJ MVI   DW_FJSON,X'00'    *Initialize first object flag

STARTOBJ LA    R1,MYPARMS        * Parameter block for SRB/TCB
         ST    R9,P_SMFREC       * Input SMF record pointer
         ST    R8,P_TABLE        * Mapping table pointer
         ST    R5,P_JSONBUF      * Output buffer pointer

*--- Execute Transformation ---*
         AIF   (&USEZIIP EQ 1).SRB_RUN        
         L     R15,=V(SMF2ZIIP)    * Direct call in TCB mode
         BASR  R14,R15             * Call using (TCB Mode)
         AGO   .CONTRUN
.SRB_RUN ANOP
* --- Running in (SRB) ---      
         ZSCHDSRB EP=SMF2ZIIP,PARM=MYPARMS,TOKEN=MYETOKEN     
         WAIT  ECB=MY_ECB

.CONTRUN ANOP


*--- JSON Record Finalization ---*
         L     R5,P_JSONLEN      * Length returned by SMF2ZIIP
         L     R4,P_JSONBUF
         AR    R5,R4             * Point to end of generated JSON


* --- Update to RDW for Next Line---
         LA    R0,BUF_DATA       * Load start address of data
         SR    R5,R0             * R5 = R5 (end) - R0 (start)
         AHI   R5,4              * Add 4 bytes for the RDW itself
         STH   R5,BUF_RDW        * Store total length in first 2 bytes    
         XC    BUF_RDW+2(2),BUF_RDW+2 * Safety: Set reserved to 0
         PUT   JSONOUT,BUFFERVB  * Physical write to output file
         J     NEXT_SMF


     
*--- Cleanup and Exit ---*
EOF      EQU   *

         MVI   BUF_DATA,C']'    * Close JSON array
         LHI   R1,5             * R1 = 5 (TOTAL RECORD LENGTH)
         STH   R1,BUF_RDW       * Store length in first 2 bytes of RDW
         XC    BUF_RDW+2(2),BUF_RDW+2 * Clear bytes (Offset 2)
         PUT   JSONOUT,BUFFERVB

         CLOSE (SMFFILE)
         CLOSE (JSONOUT)


         L     R1,P_WORKAREA
         STORAGE RELEASE,LENGTH=DW_SIZE,ADDR=(R1),COND=YES

         WTO   'INF: PROCESSING COMPLETE'
         PR



         LTORG

*--- Data Areas ---*

         DS    0F             * Fullword alignment : 32 bits 

MYETOKEN DS    CL8            * Enclave Token
WLM_RC   DS    F
WLM_RSN  DS    F
MY_ECB   DC    F'0'         * Zone de synchro TCB/SRB

SMFFILE  DCB   DDNAME=SMFFILE,                                         X
               DSORG=PS,                                               X
               MACRF=GL,                                               X
               EODAD=EOF

EP_ADDR_SAVE   DS    A
PARM_ADDR_SAVE DS   A

* ==================================================================
* 
* ==================================================================
MYPARMS  DS    0F
P_EYE    DC    CL8'MYDATA'      *Eyecatcher
DW_FJSON DS X
* Used by SRB Dispatcher
P_SMFREC DS    A                * Input SMF Record Address
P_TABLE  DS    A                * Mapping Table Address
P_JSONBUF DS   A                * Output JSON Buffer Address
P_JSONLEN DS   F                * Generated Length (Return)
P_WORKAREA DS   A               * Dynamic storage pointer
P_ECB_ADDR DS   A             
P_STATUS DS    X        
         DS    XL3              * Padding
P_SRB_BASE DS    A


* --- JSON Output ----
BUFFERVB DS    0H
BUF_RDW  DC    AL2(0)              * Total length (Data + 4)
         DC    AL2(0)              * Always 0
BUF_DATA DS    CL2048              * JSON data
JSONOUT  DCB   DDNAME=JSONOUT,                                         X
               DSORG=PS,                                               X
               MACRF=PM,                                               X
               RECFM=VB,                                               X
               LRECL=1024

* --- MACRO Defintions for Mapping files ----
         MACRO
&NAME    SMF_START
&NAME    DS    0F
         MEND

         MACRO
&NAME    SMF_FIELD &OFF,&TRIPLET=,&TYPE=,&TAG=,&JSON=
.*
&NAME    DS    0F                  
.*
&V_BASE  SETC  '0'
&V_SUB   SETC  '0'

         AIF   (N'&TRIPLET EQ 0).SKIPB
&V_BASE  SETC  '&TRIPLET'
.SKIPB   ANOP
         AIF   (N'&TAG EQ 0).SKIPS
&V_SUB   SETC  '&TAG'
.SKIPS   ANOP
.*
         DC    AL4(&OFF)           Offset
         DC    AL4(&V_BASE)        Base TRIPLET
         DC    AL1(&TYPE)          Type
         DC    AL1(&V_SUB)         Tag ID for Relocate Section
         DC    AL2(0)              Padding
         DC    CL16'&JSON'         JSON Label
         MEND

         MACRO
         SMF_END
         DC    AL4(0)              *End of Tabe
         MEND


*--- Mapping Tables ---*
         DS    0F                  * Alignement
         COPY  TYPES               * T_* datatype constants
         COPY  MAP30               * type 30 default
         COPY  MAP30S1
         COPY  MAP30S2
         COPY  MAP30S3
         COPY  MAP30S4
         COPY  MAP30S5
         COPY  MAP30S6
         COPY  MAP70S1
         COPY  MAP70S2
         COPY  MAP71S1
         COPY  MAP72S3
         COPY  MAP80
         COPY  MAP89

DYNAMIC_WORK DSECT
DW_SAVEAREA  DS    18F
DW_DBLWORD   DS    D
DW_FIRSTLBL  DS    X
DW_FIRSTOBJ  DS    X
DW_DT_FEBR   DS    X
DW_WORK_TM   DS    CL3
DW_WORK_DT   DS    CL8
DW_WORK_DEC  DS    CL10
DW_DT_TAB    DS    XL12    
DW_SIZE      EQU   *-DYNAMIC_WORK         

         END   START
