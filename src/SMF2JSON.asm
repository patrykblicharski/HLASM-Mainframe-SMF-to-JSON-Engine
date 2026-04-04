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
*
* COL 1  COL10 COL 16                                          COL 72
*        |     |                                               |
      
START    CSECT

         BAKR  R14,0        Branch And StacK Register(PUSH ALL)
         LR    R12,R15
         USING START,R12

* --- External subroutines declaration ---
         EXTRN SMF2ZIIP         


         WTO   '*** SMF2JSON: PROCESSING STARTED ***'
         OPEN  (SNAPDCB,OUTPUT)  
         OPEN  (SMFFILE,INPUT)
         OPEN  (JSONOUT,OUTPUT)

         MVI   BUF_DATA,C'['    * SET CLOSING BRACKET AT DATA START
         LHI   R1,5             * R1 = 5 (TOTAL RECORD LENGTH)
         STH   R1,BUF_RDW       * STORE LENGTH IN FIRST 2 BYTES OF RDW
         XC    BUF_RDW+2(2),BUF_RDW+2 * CLEAR BYTES (OFFSET 2)
         PUT   JSONOUT,BUFFERVB

NEXT_SMF GET   SMFFILE            * Read SMF File
         LR    R9,R1              * Save RDW

* --- CHECK FOR SPANNED RECORDS (VBS) ---
* The 3rd byte of RDW (offset 2) indicates the segment control:
* x'00' = Complete record (not spanned)
* x'01' = First segment of a spanned record
* x'02' = Intermediate segment of a spanned record
* x'03' = Last segment of a spanned record
         CLI   2(R9),X'00' * Is this a complete, non-spanned record?
         BE    RDW_OK      * Yes, proceed to processing

         CLI   2(R9),X'01'
         BNE   RDW_NO_1
         WTO   'First segment spanned skipped'
         J     NEXT_SMF
RDW_NO_1 CLI   2(R9),X'02'
         BNE   RDW_NO_2
         WTO   'Middle segment spanned skipped'
         J     NEXT_SMF
RDW_NO_2 CLI   2(R9),X'03'
         BNE   RDW_NO_3
         WTO   'Last segment spanned skipped'
         J     NEXT_SMF
RDW_NO_3 WTO   'INVALID RDW SEGMENT TYPE'
         J     NEXT_SMF

* --- SKIP TYPE 2 ---
RDW_OK   CLI   5(R9),X'02'        * type 2 record ?
         BE    NEXT_SMF           * If Yes Skip-it : Next
* --- SKIP TYPE 3 ---
         CLI   5(R9),X'03'        * type 3 record  ?
         BE    NEXT_SMF           * If Yes Skip-it : Next

* ---  TYPE 30 ---
         CLI   5(R9),30          * type 30 record  ?
         BNE    NO_30            * If Yes Skip-it : Next
         LARL  R8,TABLE30        * Load Table
         J     JSONOBJ
NO_30    EQU   *
* ---  TYPE 80 ---
         CLI   5(R9),80          * type 80 record  ?
         BNE    NO_80            * If Yes Skip-it : Next
         LARL  R8,TABLE80        * Load Table
         J     JSONOBJ
NO_80    J     NEXT_SMF
         

******
*         LLGH  R3,0(,R9)       * R3=(R1) en 16bits no signed
*         AR    R3,R9           * R3 = Adresse de fin
*         SNAP  DCB=SNAPDCB,ID=01,PDATA=REGS,STORAGE=((R9),(R3)) 
******


**********************************
* --- Processing a table entry ---
**********************************
JSONOBJ  EQU   *
         LARL  R5,BUF_DATA       * New Ligne R5=BUF_DATA
         CLI   FIRSTOBJ,X'01'    * First JSON Objet ?
         BE    FJSONOBJ

         MVI   0(R5),C','          * Add comma
         LA    R5,1(,R5)           * Avance le pointeur
         B     STARTOBJ

FJSONOBJ MVI   FIRSTOBJ,X'00'    * Tunr off flag

STARTOBJ EQU   *
         MVI   0(R5),C'{'        *Start JSON Obj
         LA    R5,1(,R5)

         MVI   FIRSTLBL,X'01'    * First JSON Label into object ?
T_LOOP   EQU   *


         CLI   FIRSTLBL,X'01'
         BE    NOFIRST
         
         MVI   0(R5),C','          * Add comma
         LA    R5,1(,R5)           * Avance le pointeur
         B     STARTLBL

NOFIRST  MVI   FIRSTLBL,X'00'

STARTLBL LHI   R2,16             * Max length for Label (16 bytes)
         BAL   R14,GEN_LBL       * Branch to Label Generation routine

         LLC   R1,8(,R8)         * Read CONSTANTS DATA TYPES
         SLL   R1,2              * Shift Left Logical : Index * 4 
         LARL  R15,BTAB
         L     R15,0(R1,R15)
         BR    R15               * Jump

BTAB     DS    0F
         DC    A(CASE0)       
         DC    A(CASE1)
         DC    A(CASE2)
         DC    A(CASE3)
         DC    A(CASE4)
         DC    A(CASE5)
         DC    A(CASE6)                  
         DC    A(CASE7) 
         DC    A(CASE8) 
         DC    A(CASE9)
         DC    A(CASE10)

CASE0    EQU   *
         WTO   'CASE 0'
         J     CONTINUE

CASE1    EQU   *
         WTO   'CASE 1'
         LHI   R2,1              * SMF field length
         BAL   R14,GET_CHR       * Branch to Value Retrieval routine
         J     CONTINUE


* CHR2 Type    EQU   2      EBCDIC STRING 2 Bytes
CASE2    EQU   *
         WTO   'CASE 2'
         LHI   R2,2              * SMF field length
         BAL   R14,GET_CHR       * Branch to Value Retrieval routine
         J     CONTINUE

* CHR4 Type    EQU   3      EBCDIC STRING 4 Bytes
CASE3    EQU   *
         WTO   'CASE 3'
         LHI   R2,4              * SMF field length
         BAL   R14,GET_CHR       * Branch to Value Retrieval routine
         J     CONTINUE

* CHR8 Type    EQU   4      EBCDIC STRING 8 Bytes  
CASE4    EQU   *
         WTO   'CASE 4'
         LHI   R2,8              * SMF field length
         BAL   R14,GET_CHR       * Branch to Value Retrieval routine         
         J     CONTINUE

* T_DEC1   EQU   5      Decimal 1 Byte
CASE5    EQU   *
         WTO   'CASE 5'
         LHI   R2,1              * SMF field length
         BAL   R14,GET_DEC       * Branch to Value Retrieval routine         
         J     CONTINUE

* T_DEC1   EQU   6      Decimal 1 Byte
CASE6    EQU   *
         WTO   'CASE 6'
         LHI   R2,2              * SMF field length
         BAL   R14,GET_DEC       * Branch to Value Retrieval routine         
         J     CONTINUE

* T_DEC1   EQU   7      Decimal 1 Byte
CASE7    EQU   *
         WTO   'CASE 7'
         LHI   R2,4              * SMF field length
         BAL   R14,GET_DEC       * Branch to Value Retrieval routine         
         J     CONTINUE

* T_DTE    EQU   8      SMF DATE (PL4)
CASE8    EQU   *
         WTO   'CASE 8'
         BAL   R14,GET_DATE       * Branch to Value Retrieval routine         
         J     CONTINUE

* T_TME    EQU   9      SMF TIME (BIN4)
CASE9    EQU   *
         WTO   'CASE 9'
         BAL   R14,GET_TIME       * Branch to Value Retrieval routine         
         J     CONTINUE

* T_RS_STR    EQU   10    RS Variable Length EBCDIC String
CASE10   EQU   *
         WTO   'CASE 10'
         BAL   R14,GET_RS_STR     * Branch to Value Retrieval routine         
         J     CONTINUE


CONTINUE EQU   *

* --- Update to RDW for Next Line---
*         LA    R0,BUF_DATA       * Load start address of data
*         SR    R5,R0             * R5 = R5 (end) - R0 (start)
*         AHI   R5,4              * Add 4 bytes for the RDW itself
*         STH   R5,BUF_RDW        * Store total length in first 2 bytes    
*         XC    BUF_RDW+2(2),BUF_RDW+2 * Safety: Set reserved to 0
*         PUT   JSONOUT,BUFFERVB  * Physical write to output file

* --- Next line ---
         LA    R8,28(,R8)           * R8=R8+28

         L     R1,0(,R8)         
         LTR   R1,R1             * Reach End of Table ?
         JNZ   T_LOOP

* --- End of JSON Object ---
         MVI   0(R5),C'}'        *Start JSON Obj
         LA    R5,1(,R5)
* --- Update to RDW for Next Line---
         LA    R0,BUF_DATA       * Load start address of data
         SR    R5,R0             * R5 = R5 (end) - R0 (start)
         AHI   R5,4              * Add 4 bytes for the RDW itself
         STH   R5,BUF_RDW        * Store total length in first 2 bytes    
         XC    BUF_RDW+2(2),BUF_RDW+2 * Safety: Set reserved to 0
         PUT   JSONOUT,BUFFERVB  * Physical write to output file

         J     NEXT_SMF
         



**********************************************************************

* END OF DATA REACHED

EOF      EQU   *

*         LR    R10,R0
*         LR    R11,R1
*         LLGH  R3,0(,R9)       * R3=(R1) en 16bits no signed
*         AR    R3,R9           * R3 = Adresse de fin
*         LA    R1,100(,R9)
*         LR    R1,R8
*         LA    R1,100(,R8)
*         SNAP  DCB=SNAPDCB,ID=02,PDATA=REGS,STORAGE=((R9),(R3)) 

* --- Insertion du caractère de fin JSON ---
         MVI   BUF_DATA,C']'    * SET CLOSING BRACKET AT DATA START
         LHI   R1,5             * R1 = 5 (TOTAL RECORD LENGTH)
         STH   R1,BUF_RDW       * STORE LENGTH IN FIRST 2 BYTES OF RDW
         XC    BUF_RDW+2(2),BUF_RDW+2 * CLEAR BYTES (OFFSET 2)
         PUT   JSONOUT,BUFFERVB

         CLOSE (SMFFILE)
         CLOSE (JSONOUT)
         CLOSE (SNAPDCB)
         
         WTO   '*** SMF2JSON: PROCESSING COMPLETE ***'

         PR



* ------------------------------------------------------------------
* ROUTINE : GEN_LBL (Version Moderne avec BAKR)
* Input   : R8 = Pointer to Table entry
*           R5 = Pointer to BUF_DATA
* R2 = Max field length (e.g., 16 bytes)
* Output  : R5 = Current pointer in BUF_DATA (after the ":")
* ------------------------------------------------------------------
GEN_LBL  EQU   *
         
         SR    R1,R1               * Clear Index (Counter)
         LA    R4,12(,R8)            * Label start address

SCAN_LP  EQU   *
         LA    R3,0(R1,R4)         * R5 = Current byte address
         CLI   0(R3),X'40'         * Check for SPACE character
         BE    FND_SIZE            * Found space -> End of string
         
         LA    R1,1(,R1)            * Increment Index
         CR    R1,R2               * Compare with Max Length (R2)
         BL    SCAN_LP             * Loop if Index < R2

FND_SIZE EQU   *                   * R1 = Effective length
*         MVI   BUF_DATA,C'"'       * Write opening quote
         MVI   0(R5),C'"'

         LTR   R1,R1               * Check if label is empty
         JZ    LBL_DONE
         
         LR    R3,R1               * Copy length for EX instruction
         BCTR  R3,0                * Length - 1 (for Execute)
         EX    R3,MVC_LBL          * Copy label to buffer
         
LBL_DONE EQU   *
*         LA    R5,BUF_DATA+1(R1)   * Position after copied text
*         LARL  R5,BUF_DATA      * Already done on T_LOOP label
         LA    R5,1(R1,R5)
         MVI   0(R5),C'"'          * Write closing quote
         MVI   1(R5),C':'          * Write colon separator
         LA    R5,2(,R5)            * Advance cursor: R5 = R5 + 2
         
         BR    R14                  * Return

* --- Target Instruction ---
*MVC_LBL  MVC   BUF_DATA+1(0),12(R8)
MVC_LBL  MVC   1(0,R5),12(R8)      * Write to (R5+1)

TEST     EQU   *
         L     R1,4(R8)           *Load Triplet Offset
*DEBUG
         AR    R1,R9              *R1 =  Base Addr Triplet
         L     R6,0(,R1)
         BR    R14 

* ------------------------------------------------------------------
* ROUTINE : GET_CHR (Extracts EBCDIC SMF value and writes to buffer)
* Input   : R8 = Pointer to Table entry
* R9 = SMF Record base address (Header)
* R2 = Max data length
* R5 = Current pointer in BUF_DATA (after the ":")
* ------------------------------------------------------------------
GET_CHR  EQU   *  
         SR    R0,R0              * R0=0
         L     R1,4(,R8)           *Load Triplet DSECT

         LTR   R1,R1              *if DSECT is null : no Triplet
         JZ    CHRNOTRI           *Jump if no Triplet data

         AR    R1,R9              *R1 = Offset Addr Triplet Addr
         ICM   R0,B'1111',0(R1)  * to avoid alignment issue 
         BNZ   CHRNOTRI
         MVI   0(R5),C'"'
         LA    R5,1(,R5)
         MVI   0(R5),C'"'
         LA    R5,1(,R5)
         BR    R14         
* R0 = Offset Triplet

CHRNOTRI EQU   *


         L     R3,0(,R8)           * Load OFFSET from Table (AL4)
         AR    R3,R9              * R3 = SMF Base + Offset = Data Addr
         AR    R3,R0              * R3 = R3+ R0 (Offset Triplet)

         MVI   0(R5),C'"'         * Set opening quote

         LR    R1,R2              * R1 = Max length (from R2)
         BCTR  R1,0               * Length - 1 (for Execute)
         EX    R1,MVC_VAL         * Copy from R3 to 1(R5)

         LA    R5,1(R2,R5)        * R5 = R5 + 1 + R2
         MVI   0(R5),C'"'         * Set closing quote
         LA    R5,1(,R5)           * Advance cursor: R5 = R5 + 1

         BR    R14                 * Return

* --- Target Instruction ---
MVC_VAL  MVC   1(0,R5),0(R3)       * Copy from SMF(R3) to Buffer(R5+1)




* ------------------------------------------------------------------
* ROUTINE : GET_DEC (Supports 1, 2, or 4 byte binary inputs)
* Input   : R8 = Pointer to Table entry
* R9 = SMF Record base address
* R2 = Input length (1, 2, or 4)
* R5 = Current pointer in BUF_DATA
* ------------------------------------------------------------------
GET_DEC  EQU   * 
         SR    R0,R0              * R0=0
         L     R1,4(,R8)           *Load Triplet DSECT         

         LTR   R1,R1              *if DSECT is null : no Triplet
         JZ    DECNOTRI           *Jump if no Triplet data

         AR    R1,R9              *R1 = Offset Addr Triplet Addr
         ICM   R0,B'1111',0(R1)  * to avoid alignment issue 
         BNZ   DECNOTRI
         MVI   0(R5),C'"'
         LA    R5,1(,R5)
         MVI   0(R5),C'"'
         LA    R5,1(,R5)
         BR    R14
* R0 = Offset Triplet

DECNOTRI EQU   *
         L     R3,0(,R8)           * Load OFFSET from Table (AL4)
         AR    R3,R9              * R3 = SMF Base + Offset = Data Addr
         AR    R3,R0              * R3 = R3+ R0 (Offset Triplet)


* --- 1. Selective Load based on R2 ---
         CH    R2,=H'4'            * Is it 4 bytes?
         BE    LOAD_4
         CH    R2,=H'2'            * Is it 2 bytes?
         BE    LOAD_2
         
LOAD_1   SR    R1,R1               * CRITICAL: Clear R1 first
         IC    R1,0(,R3)            * Insert 1 byte into R1
         B     CONV_IT
         
LOAD_2   SR    R1,R1               * Clear entire R1
         ICM   R1,B'0011',0(R3)    * Insert 2 bytes (No sign ext)
         B     CONV_IT
         
LOAD_4   L     R1,0(,R3)            * Load 4 bytes (Fullword)

* --- 2. Conversion and Formatting ---
CONV_IT  CVD   R1,DBLWORD          * Convert Binary R1 to Packed Dec.
         
         MVI   0(R5),C'"'          * Write opening quote
         
         MVC   WORK_DEC(10),ED_PAT * Prepare Edit Pattern
         ED    WORK_DEC(10),DBLWORD+3 * Format decimal digits
         

* --- 3. Leading Space Suppression ---
         LA    R4,WORK_DEC         * Start of formatted area
         LA    R1,10               * Max length to scan
SCAN_DEC CLI   0(R4),X'40'         * Is it a blank (suppressed zero)?
         BNE   COPY_DEC            * No -> Found first digit
         LA    R4,1(,R4)            * Next byte
         BCT   R1,SCAN_DEC         
         
COPY_DEC EQU   * * R1 = Length, R4 = Start Address
         LR    R3,R1               * Keep length R3 for cursor update
         BCTR  R1,0                * Length - 1 for EX
         EX    R1,MVC_DEC          * Copy result to 1(R5)
         
* --- 4. Close Quote and Update Cursor ---
         LA    R5,1(R3,R5)         * R5 = R5 + 1(quote) + R3(digits)
         MVI   0(R5),C'"'          * Set closing quote
         LA    R5,1(,R5)            * Next free byte
         
         BR    R14                 * Return to caller

* --- Target Instruction ---
MVC_DEC  MVC   1(0,R5),0(R4)       * Target for EX



* ------------------------------------------------------------------
* ROUTINE : GET_DATE (ISO YYYY-MM-DD) - Final Verified Version
* Input   : R8 = Offset / R9 = SMF Base / R5 = Buffer
* ------------------------------------------------------------------
GET_DATE EQU   * 
         L     R3,0(,R8)            * Load OFFSET
         AR    R3,R9               * R3 = Address of 0cyydddF

         MVI   0(R5),C'"'          * Write opening quote

* --- 1. Century and Year (YYYY) ---
         TM    0(R3),X'01'         * Test Century bit
         BNO   DT_19
         MVC   1(2,R5),=C'20'      * 20xx
         B     DT_YY
DT_19    MVC   1(2,R5),=C'19'      * 19xx
DT_YY    UNPK  WORK_DT(3),1(2,R3)  * Unpack YY (e.g., X'26' -> F2F6)
         MVC   3(2,R5),WORK_DT     * Copy YY to buffer
         MVI   5(R5),C'-'          * First separator

* --- 2. Leap Year Check (R0 = Year) ---
         PACK  DBLWORD,WORK_DT(2)  * Pack "26" -> X'026F'
         CVB   R0,DBLWORD          * R0 = Binary Year
         STC   R0,DT_FEBR          
         TM    DT_FEBR,X'03'       * Divisible by 4?
         BNZ   DT_GETD             
         MVI   DT_TAB+1,29         * Leap year: Feb = 29

* --- 3. Extract Julian Day (R1 = DDD) ---
DT_GETD  EQU   * MVC   WORK_DT(4),=X'0000000F' * Reset work area
         MVC   WORK_DT(2),2(R3)    * Copy X'084F' into WORK_DT
* Now WORK_DT contains X'084F000F'. 
* We use ZAP to clean it and align it into DBLWORD.
         ZAP   DBLWORD,WORK_DT(2)  * Force X'084F' into DBLWORD safely
         CVB   R1,DBLWORD          * R1 = Binary Day (e.g., 84)
* Verification: If SMF had 084F, CVB R1 now contains exactly 84.

* --- 4. Calculate Month (R6) and Day (R1) ---
         LA    R4,DT_TAB           * R4 points to Month Table
         LA    R6,1                * R6 = Month Counter
DT_LOOP  SR    R0,R0
         IC    R0,0(,R4)            * R0 = Days in current month
         CR    R1,R0               * Is Day <= Days in Month?
         BNH   DT_DONE             * Yes -> Month/Day found
         SR    R1,R0               * No -> Subtract days
         LA    R4,1(,R4)            * Next month
         LA    R6,1(,R6)            * Increment Month
         B     DT_LOOP

DT_DONE  CVD   R6,DBLWORD          * Convert Month (R6) to Packed
         UNPK  WORK_DT(3),DBLWORD+6(2)
         OI    WORK_DT+2,X'F0'     * Fix sign
         MVC   6(2,R5),WORK_DT+1   * Write MM
         MVI   8(R5),C'-'          * Second separator
         
         CVD   R1,DBLWORD          * Convert remaining Day (R1)
         UNPK  WORK_DT(3),DBLWORD+6(2)
         OI    WORK_DT+2,X'F0'     * Fix sign
         MVC   9(2,R5),WORK_DT+1   * Write DD

* --- 5. Wrap up ---
         MVI   11(R5),C'"'         
         LA    R5,12(,R5)           * Total length 12 bytes
         MVI   DT_TAB+1,28         * Reset Feb for next record
         
         BR    R14                 * Return to caller





* ------------------------------------------------------------------
* ROUTINE : GET_TIME (Formats SMF Binary Time to "HH:MM:SS")
* Input   : R8 = Pointer to Table entry (Offset)
* R9 = SMF Record base address
* R5 = Current pointer in BUF_DATA
* Registers used: R0, R1, R3, R4
* ------------------------------------------------------------------
GET_TIME EQU   *
         L     R3,0(,R8)            * Load OFFSET from Table
         AR    R3,R9               * R3 = Time Address (4 bytes binary
         MVI   0(R5),C'"'          * Write opening quote

* --- 1. Total Seconds ---
         L     R1,0(,R3)            * R1 = Binary hundredths
         LA    R4,100
         SR    R0,R0               * CRITICAL: Clear R0 for division
         DR    R0,R4              * Division par R4

* --- 2. Hours ---
         SR    R0,R0               * Clear R0 for dividend R0-R1
         LHI   R4,3600
         DR    R0,R4               * R1 = Hours, R0 = Remainder

*         LR    R6,R0               * save R0 in a safe place: R6
         CVD   R1,DBLWORD          * Convert Hours to Packed
         UNPK  WORK_TM(3),DBLWORD+6(2)
         OI    WORK_TM+2,X'F0'     * Fix sign
         MVC   1(2,R5),WORK_TM+1   * Write HH
         MVI   3(R5),C':'          * Separator

* --- 3. Minutes ---
*         LR    R0,R6               * restore R0
         LR    R1,R0               * R1 = Remaining seconds
         SR    R0,R0               * Clear R0
         LA    R4,60
         DR    R0,R4                * R1 = Minutes, R0 = Seconds

         CVD   R1,DBLWORD
         UNPK  WORK_TM(3),DBLWORD+6(2)
         OI    WORK_TM+2,X'F0'
         MVC   4(2,R5),WORK_TM+1   * Write MM
         MVI   6(R5),C':'          * Separator

* --- 4. Seconds ---

         CVD   R0,DBLWORD          * R0 is the remainder (Seconds)
         UNPK  WORK_TM(3),DBLWORD+6(2)
         OI    WORK_TM+2,X'F0'
         MVC   7(2,R5),WORK_TM+1   * Write SS

         MVI   9(R5),C'"'          * Closing quote
         LA    R5,10(,R5)           * Advance cursor (10 bytes total)
         
         BR    R14  



* ------------------------------------------------------------------
* ROUTINE : GET_RS_STR (Version avec Compteur et Offset Corrigé)
* Input   : R8 = Pointer to Table entry 
* R9 = SMF Record base address (RDW)
* R5 = Current pointer in BUF_DATA
* ------------------------------------------------------------------
GET_RS_STR EQU   *
         
         L     R3,0(,R8)           * Load OFFSET from Table
         AR    R3,R9               * R3 = SMF80REL

         SR    R7,R7
         ICM   R7,B'0011',2(R3)  *R7=SMF80CNT
         LTR   R7,R7
         JZ    RS_NOTF

         SR    R1,R1
         ICM   R1,B'0011',0(R3)  *R2=SMF80REL to avoid alignment issue
         AR    R1,R9
         LA    R3,4(,R1)         *R3=R1+4 cause section from SMF80FLG

* Compare 1 byte at R3 (Tag) with the Target Tag at offset 9 of R8
RS_SCAN  CLC   0(1,R3),9(R8)      * Is is the right Tag ?
         BE    RS_FOUND           * OUI -> Extraction

* Compute next Tag
         SR    R1,R1
         IC    R1,1(,R3)        * R1 = Size (0-255)
         LA    R3,2(R1,R3)      * R3 = R3 + 2 (Tag+Len) + L
         BCT   R7,RS_SCAN       * Decrease SMF80CNT
         B     RS_NOTF          * If R7=0 then not found
RS_FOUND EQU   *                * R3 = Start of Tag
         MVC   0(1,R5),=C'"' 
         LA    R5,1(,R5)
         SR    R2,R2
         IC    R2,1(,R3)        * R1 = Size of Tag
         LR    R1,R2            * R1=R2 Nb bytes to copy
         BCTR  R1,0             * R1 = R1 - 1
         LA    R3,2(,R3)        * jump Type Tag + Size Tag
         EX    R1,MVC_RS
         AR    R5,R2             * Update BUF_DATA pointer
         MVC   0(1,R5),=C'"' 
         LA    R5,1(,R5)

         BR    R14 

RS_NOTF  EQU   *
         MVC   0(2,R5),=C'""'     * Ou "null"
         LA    R5,2(,R5)

RS_EXIT  EQU   *
         BR    R14
MVC_RS   MVC   0(0,R5),0(R3)      * Copy (R3) to (R5) 

         LTORG


         DS    0D
* --- Data Area  ---         
DBLWORD  DS    D                   * Doubleword for CVD    

WORK_TM  DS    CL3                 * Temp area for UNPK
WORK_DT  DS    CL8                 * Increased to 8 bytes for safety
     
ED_PAT   DC    X'40202020202020202021' * Edit Pattern
WORK_DEC DS    CL10                * Work area for formatting

* --- Data area for GET_DATE ---
DT_TAB   DC    AL1(31,28,31,30,31,30,31,31,30,31,30,31)
DT_FEBR  DS    X







         DS    0F                 * Fullword alignment : 32 bits
FIRSTLBL DC    X'01'              * 01 = 1st label record, 00 = Nexts
FIRSTOBJ DC    X'01'              * 01 = 1st JSON obj, 00 = Nexts
         DS    0F                 * Fullword alignment : 32 bits


* Warning : comma to cols number 72 
SNAPDCB  DCB   DSORG=PS,MACRF=(W),DDNAME=SNAP,RECFM=VBA,               X
               LRECL=125,BLKSIZE=882
         DS    0F                 * Fullword alignment : 32 bits 

* --- Définitions des zones ---
SMFFILE  DCB   DDNAME=SMFFILE,                                         X
               DSORG=PS,                                               X
               MACRF=GL,                                               X
               EODAD=EOF



* --- JSON Output ----
BUFFERVB DS    0H                  * Aligne sur un Halfword
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
         DC    AL4(0)              Fin de table (Sentinelle)
         MEND
* mapping table SMF Type 30
         DS    0F                  * Alignement
         COPY  MAP30
         COPY  MAP80   

         IFASMFR (30)      * SMF Records structs
         IFASMFR (80)      * SMF Records structs         
         END   START
