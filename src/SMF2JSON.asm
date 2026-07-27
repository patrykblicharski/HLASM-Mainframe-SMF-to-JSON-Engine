*---------------------------------------------------------------------*
* PROGRAM: SMF2JSON                                                   *
* PURPOSE: CONVERT SMF RECORDS (30/70/71/72/73/74/75/76/77/78/79/80/89/99/113) TO JSON *
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
         IFASMFR (30,70,71,72,73,74,75,76,77,78,79,80,89,99,113)  * IBM SMF Record Mappings

         
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

* --- BEGIN GENERATED DISPATCH (tools/gen_gatherer_maps.py) ---
* ---  TYPE 30 ---
         CLI   5(R9),30
         BNE   NO_30
         LH    R1,22(,R9)        * subtype halfword
T30_1    CHI   R1,1
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
T30_DEF EQU   *
         LARL  R8,TABLE30        * unknown subtype default
         J     JSONOBJ
NO_30   EQU   *

* ---  TYPE 70 ---
         CLI   5(R9),70
         BNE   NO_70
         LH    R1,22(,R9)        * subtype halfword
T70_1    CHI   R1,1
         BNE   T70_2
         LARL  R8,TABLE70_1
         J     JSONOBJ
T70_2    CHI   R1,2
         BNE   T70_DEF
         LARL  R8,TABLE70_2
         J     JSONOBJ
T70_DEF EQU   *
         J     NEXT_SMF          * unsupported subtype
NO_70   EQU   *

* ---  TYPE 71 ---
         CLI   5(R9),71
         BNE   NO_71
         LH    R1,22(,R9)        * subtype halfword
T71_1    CHI   R1,1
         BNE   T71_DEF
         LARL  R8,TABLE71_1
         J     JSONOBJ
T71_DEF EQU   *
         J     NEXT_SMF          * unsupported subtype
NO_71   EQU   *

* ---  TYPE 72 ---
         CLI   5(R9),72
         BNE   NO_72
         LH    R1,22(,R9)        * subtype halfword
T72_3    CHI   R1,3
         BNE   T72_4
         LARL  R8,TABLE72_3
         J     JSONOBJ
T72_4    CHI   R1,4
         BNE   T72_5
         LARL  R8,TABLE72_4
         J     JSONOBJ
T72_5    CHI   R1,5
         BNE   T72_DEF
         LARL  R8,TABLE72_5
         J     JSONOBJ
T72_DEF EQU   *
         J     NEXT_SMF          * unsupported subtype
NO_72   EQU   *

* ---  TYPE 73 ---
         CLI   5(R9),73
         BNE   NO_73
         LH    R1,22(,R9)        * subtype halfword
T73_1    CHI   R1,1
         BNE   T73_DEF
         LARL  R8,TABLE73_1
         J     JSONOBJ
T73_DEF EQU   *
         J     NEXT_SMF          * unsupported subtype
NO_73   EQU   *

* ---  TYPE 74 ---
         CLI   5(R9),74
         BNE   NO_74
         LH    R1,22(,R9)        * subtype halfword
T74_1    CHI   R1,1
         BNE   T74_2
         LARL  R8,TABLE74_1
         J     JSONOBJ
T74_2    CHI   R1,2
         BNE   T74_3
         LARL  R8,TABLE74_2
         J     JSONOBJ
T74_3    CHI   R1,3
         BNE   T74_4
         LARL  R8,TABLE74_3
         J     JSONOBJ
T74_4    CHI   R1,4
         BNE   T74_5
         LARL  R8,TABLE74_4
         J     JSONOBJ
T74_5    CHI   R1,5
         BNE   T74_6
         LARL  R8,TABLE74_5
         J     JSONOBJ
T74_6    CHI   R1,6
         BNE   T74_7
         LARL  R8,TABLE74_6
         J     JSONOBJ
T74_7    CHI   R1,7
         BNE   T74_8
         LARL  R8,TABLE74_7
         J     JSONOBJ
T74_8    CHI   R1,8
         BNE   T74_9
         LARL  R8,TABLE74_8
         J     JSONOBJ
T74_9    CHI   R1,9
         BNE   T74_10
         LARL  R8,TABLE74_9
         J     JSONOBJ
T74_10   CHI   R1,10
         BNE   T74_DEF
         LARL  R8,TABLE74_10
         J     JSONOBJ
T74_DEF EQU   *
         J     NEXT_SMF          * unsupported subtype
NO_74   EQU   *

* ---  TYPE 75 ---
         CLI   5(R9),75
         BNE   NO_75
         LH    R1,22(,R9)        * subtype halfword
T75_1    CHI   R1,1
         BNE   T75_DEF
         LARL  R8,TABLE75_1
         J     JSONOBJ
T75_DEF EQU   *
         J     NEXT_SMF          * unsupported subtype
NO_75   EQU   *

* ---  TYPE 76 ---
         CLI   5(R9),76
         BNE   NO_76
         LH    R1,22(,R9)        * subtype halfword
T76_1    CHI   R1,1
         BNE   T76_DEF
         LARL  R8,TABLE76_1
         J     JSONOBJ
T76_DEF EQU   *
         J     NEXT_SMF          * unsupported subtype
NO_76   EQU   *

* ---  TYPE 77 ---
         CLI   5(R9),77
         BNE   NO_77
         LH    R1,22(,R9)        * subtype halfword
T77_1    CHI   R1,1
         BNE   T77_DEF
         LARL  R8,TABLE77_1
         J     JSONOBJ
T77_DEF EQU   *
         J     NEXT_SMF          * unsupported subtype
NO_77   EQU   *

* ---  TYPE 78 ---
         CLI   5(R9),78
         BNE   NO_78
         LH    R1,22(,R9)        * subtype halfword
T78_2    CHI   R1,2
         BNE   T78_3
         LARL  R8,TABLE78_2
         J     JSONOBJ
T78_3    CHI   R1,3
         BNE   T78_DEF
         LARL  R8,TABLE78_3
         J     JSONOBJ
T78_DEF EQU   *
         J     NEXT_SMF          * unsupported subtype
NO_78   EQU   *

* ---  TYPE 79 ---
         CLI   5(R9),79
         BNE   NO_79
         LH    R1,22(,R9)        * subtype halfword
T79_1    CHI   R1,1
         BNE   T79_2
         LARL  R8,TABLE79_1
         J     JSONOBJ
T79_2    CHI   R1,2
         BNE   T79_3
         LARL  R8,TABLE79_2
         J     JSONOBJ
T79_3    CHI   R1,3
         BNE   T79_4
         LARL  R8,TABLE79_3
         J     JSONOBJ
T79_4    CHI   R1,4
         BNE   T79_5
         LARL  R8,TABLE79_4
         J     JSONOBJ
T79_5    CHI   R1,5
         BNE   T79_6
         LARL  R8,TABLE79_5
         J     JSONOBJ
T79_6    CHI   R1,6
         BNE   T79_7
         LARL  R8,TABLE79_6
         J     JSONOBJ
T79_7    CHI   R1,7
         BNE   T79_9
         LARL  R8,TABLE79_7
         J     JSONOBJ
T79_9    CHI   R1,9
         BNE   T79_11
         LARL  R8,TABLE79_9
         J     JSONOBJ
T79_11   CHI   R1,11
         BNE   T79_12
         LARL  R8,TABLE79_11
         J     JSONOBJ
T79_12   CHI   R1,12
         BNE   T79_14
         LARL  R8,TABLE79_12
         J     JSONOBJ
T79_14   CHI   R1,14
         BNE   T79_15
         LARL  R8,TABLE79_14
         J     JSONOBJ
T79_15   CHI   R1,15
         BNE   T79_DEF
         LARL  R8,TABLE79_15
         J     JSONOBJ
T79_DEF EQU   *
         J     NEXT_SMF          * unsupported subtype
NO_79   EQU   *

* ---  TYPE 99 ---
         CLI   5(R9),99
         BNE   NO_99
         LH    R1,22(,R9)        * subtype halfword
T99_1    CHI   R1,1
         BNE   T99_2
         LARL  R8,TABLE99_1
         J     JSONOBJ
T99_2    CHI   R1,2
         BNE   T99_6
         LARL  R8,TABLE99_2
         J     JSONOBJ
T99_6    CHI   R1,6
         BNE   T99_12
         LARL  R8,TABLE99_6
         J     JSONOBJ
T99_12   CHI   R1,12
         BNE   T99_14
         LARL  R8,TABLE99_12
         J     JSONOBJ
T99_14   CHI   R1,14
         BNE   T99_DEF
         LARL  R8,TABLE99_14
         J     JSONOBJ
T99_DEF EQU   *
         J     NEXT_SMF          * unsupported subtype
NO_99   EQU   *

* ---  TYPE 113 ---
         CLI   5(R9),113
         BNE   NO_113
         LH    R1,22(,R9)        * subtype halfword
T113_1   CHI   R1,1
         BNE   T113_2
         LARL  R8,TABLE113_1
         J     JSONOBJ
T113_2   CHI   R1,2
         BNE   T113_DEF
         LARL  R8,TABLE113_2
         J     JSONOBJ
T113_DEF EQU   *
         J     NEXT_SMF          * unsupported subtype
NO_113   EQU   *

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
* --- END GENERATED DISPATCH ---
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
         COPY  MAP72S4
         COPY  MAP72S5
         COPY  MAP73S1
         COPY  MAP74S1
         COPY  MAP74S2
         COPY  MAP74S3
         COPY  MAP74S4
         COPY  MAP74S5
         COPY  MAP74S6
         COPY  MAP74S7
         COPY  MAP74S8
         COPY  MAP74S9
         COPY  MAP74S10
         COPY  MAP75S1
         COPY  MAP76S1
         COPY  MAP77S1
         COPY  MAP78S2
         COPY  MAP78S3
         COPY  MAP79S1
         COPY  MAP79S2
         COPY  MAP79S3
         COPY  MAP79S4
         COPY  MAP79S5
         COPY  MAP79S6
         COPY  MAP79S7
         COPY  MAP79S9
         COPY  MAP79S11
         COPY  MAP79S12
         COPY  MAP79S14
         COPY  MAP79S15
         COPY  MAP99S1
         COPY  MAP99S2
         COPY  MAP99S6
         COPY  MAP99S12
         COPY  MAP99S14
         COPY  MAP113S1
         COPY  MAP113S2
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
