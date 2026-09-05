*---------------------------------------------------------------------*
* MODULE   : SMF2ZIIP                                                 *
* FUNCTION : SMF RECORD TO JSON CONVERTER (zIIP ELIGIBLE)             *
* DESCRIPTION: PARSES SMF TYPE 30/80 USING MAPPING TABLES AND         *
* OUTPUTS FORMATTED JSON OBJECTS.                                     *
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

         COPY  CONFIG            * Global build configuration

         AIF   (&USEZIIP EQ 0).NOZIIP 
         IHASRB                  * Mapping for z/OS SRB block
         CVT   DSECT=YES         * Définit la structure CVTMAP
         COPY  ZSCHDSRB
.NOZIIP  ANOP

SMF2ZIIP CSECT   
SMF2ZIIP AMODE 31                * 31-bit addressing mode              

         AIF   (&USEZIIP EQ 0).TCB_PRO    Check if TCB mode
*--- SRB MODE PROLOGUE ---*
         ZSRBPRE                 * SRB initialization macro

         AGO   .START

*--- TCB MODE PROLOGUE (Standard Call) ---*
.TCB_PRO ANOP

         SAVE  (14,12)           * Save caller's registers
         LR    R12,R15        
         USING SMF2ZIIP,R12 
         LR    R11,R1
         USING MYPARMS,R11       * R1 points to MYPARMS in TCB mode


.START   ANOP

* --------------------------------------------------------------------
* COMMON INITIALIZATION                                               
* --------------------------------------------------------------------
         L     R10,P_WORKAREA      * Pointer to Workaera
         USING DYNAMIC_WORK,R10 

         MVI   DW_FIRSTOBJ,X'01'   *Initialize first object flag
         MVI   DW_FIRSTLBL,X'01'   *Initialize first label flag
         MVC   DW_DT_TAB,DT_TAB    *Initialize thread-safe month table 


* --- Parameters Extraction ---
         L     R9,P_SMFREC       * R9: Pointer to SMF Record
         L     R8,P_TABLE        * R8: Pointer to Mapping Table
         L     R5,P_JSONBUF      * R5: Output JSON Buffer cursor

*---------------------------------------------------------------------*
* MAIN PROCESSING LOOP                                                *
*---------------------------------------------------------------------*
*         LARL  R5,BUF_DATA       * New Ligne R5=BUF_DATA
         CLI   DW_FIRSTOBJ,X'01'    * First JSON Objet ?
         BE    FJSONOBJ

         MVI   0(R5),C','        * Add comma separator between objects
         LA    R5,1(,R5)         * R5=R5+1
         B     STARTOBJ

FJSONOBJ MVI   DW_FIRSTOBJ,X'00'    * Turn off flag

STARTOBJ EQU   *
         MVI   0(R5),C'{'        * Start of JSON Object
         LA    R5,1(,R5)

         MVI   DW_FIRSTLBL,X'01'    * First JSON Label into object ?
T_LOOP   EQU   *


         CLI   DW_FIRSTLBL,X'01'
         BE    NOFIRST
         
         MVI   0(R5),C','          * Add comma between JSON fields
         LA    R5,1(,R5)           * R5=R5+1
         B     STARTLBL

NOFIRST  MVI   DW_FIRSTLBL,X'00'

STARTLBL LHI   R2,16             * Max length for Label (16 bytes)
         BAL   R14,GEN_LBL       * Branch to Label Generation routine

         LLC   R1,8(,R8)         * Read CONSTANTS DATA TYPES
         SLL   R1,2              * Shift Left Logical : Index * 4 
         LARL  R15,BTAB
         L     R15,0(R1,R15)     * Load case address
         BR    R15               * Jump to conversion routine

BTAB     DS    0F                * Branch Table for Data Types
         DC    A(CASE0)          * 0: Skip
         DC    A(CASE1)          * 1: EBCDIC 1-byte
         DC    A(CASE2)          * 2: EBCDIC 2-bytes
         DC    A(CASE3)          * 3: EBCDIC 4-bytes
         DC    A(CASE4)          * 4: EBCDIC 8-bytes
         DC    A(CASE5)          * 5: Decimal 1-byte
         DC    A(CASE6)          * 6: Decimal 2-bytes        
         DC    A(CASE7)          * 7: Decimal 4-bytes
         DC    A(CASE8)          * 8: SMF Date (4-bytes)
         DC    A(CASE9)          * 9: SMF Time (4-bytes)
         DC    A(CASE10)         * 10: Relocate Section String
         DC    A(CASE11)         * 11: EBCDIC 16-bytes
         DC    A(CASE12)         * 12: EBCDIC 20-bytes

*--- Conversion Cases Mapping ---*
CASE0    EQU   *
         J     CONTINUE

CASE1    EQU   *
         LHI   R2,1              * SMF field length
         BAL   R14,GET_CHR       * Branch to Value Retrieval routine
         J     CONTINUE

* CHR2 Type    EQU   2      EBCDIC STRING 2 Bytes
CASE2    EQU   *
         LHI   R2,2              * SMF field length
         BAL   R14,GET_CHR       * Branch to Value Retrieval routine
         J     CONTINUE

* CHR4 Type    EQU   3      EBCDIC STRING 4 Bytes
CASE3    EQU   *
         LHI   R2,4              * SMF field length
         BAL   R14,GET_CHR       * Branch to Value Retrieval routine
         J     CONTINUE

* CHR8 Type    EQU   4      EBCDIC STRING 8 Bytes  
CASE4    EQU   *
         LHI   R2,8              * SMF field length
         BAL   R14,GET_CHR       * Branch to Value Retrieval routine         
         J     CONTINUE

* T_DEC1   EQU   5      Decimal 1 Byte
CASE5    EQU   *
         LHI   R2,1              * SMF field length
         BAL   R14,GET_DEC       * Branch to Value Retrieval routine         
         J     CONTINUE

* T_DEC1   EQU   6      Decimal 1 Byte
CASE6    EQU   *
         LHI   R2,2              * SMF field length
         BAL   R14,GET_DEC       * Branch to Value Retrieval routine         
         J     CONTINUE

* T_DEC1   EQU   7      Decimal 1 Byte
CASE7    EQU   *
         LHI   R2,4              * SMF field length
         BAL   R14,GET_DEC       * Branch to Value Retrieval routine         
         J     CONTINUE

* T_DTE    EQU   8      SMF DATE (PL4)
CASE8    EQU   *
         BAL   R14,GET_DATE       * Branch to Value Retrieval routine         
         J     CONTINUE

* T_TME    EQU   9      SMF TIME (BIN4)
CASE9    EQU   *
         BAL   R14,GET_TIME       * Branch to Value Retrieval routine         
         J     CONTINUE

* T_RS_STR    EQU   10    RS Variable Length EBCDIC String
CASE10   EQU   *
         BAL   R14,GET_RS_STR     * Branch to Value Retrieval routine         
         J     CONTINUE

* T_CHR16  EQU   11     EBCDIC STRING 16 Bytes
CASE11   EQU   *
         LHI   R2,16             * SMF field length
         BAL   R14,GET_CHR       * Branch to Value Retrieval routine
         J     CONTINUE

* T_CHR20  EQU   12     EBCDIC STRING 20 Bytes
CASE12   EQU   *
         LHI   R2,20             * SMF field length
         BAL   R14,GET_CHR       * Branch to Value Retrieval routine
         J     CONTINUE

CONTINUE EQU   *

* --- Next line ---
         LA    R8,28(,R8)       *Advance to next table entry (28-byte)

         L     R1,0(,R8)        * Check for end-of-table sentinel 
         LTR   R1,R1            * Reach End of Table ?
         JNZ   T_LOOP


* --- End of JSON Object ---
         MVI   0(R5),C'}'        * Close JSON object
         LA    R5,1(,R5)

*--- Processing Complete ---*
         L     R4,P_JSONBUF
         SR    R5,R4            * Calculate total generated length
         ST    R5,P_JSONLEN     * Store in return parameter


         AIF   (&USEZIIP EQ 0).TCB_RET

*--- SRB MODE EXIT ---*

         L     R2,P_ECB_ADDR        * Signal Driver via ECB
         POST  (R2),0               * Signal completion to Driver
         BR    R14                  * Return 

*--- TCB MODE EXIT ---*
.TCB_RET ANOP
         RETURN (14,12),RC=0       * Restore and return





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
CONV_IT  CVD   R1,DW_DBLWORD        * Convert Binary R1 to Packed Dec.
         
         MVI   0(R5),C'"'          * Write opening quote
         
         MVC   DW_WORK_DEC(10),ED_PAT * Prepare Edit Pattern
         ED    DW_WORK_DEC(10),DW_DBLWORD+3 * Format decimal digits
         

* --- 3. Leading Space Suppression ---
         LA    R4,DW_WORK_DEC         * Start of formatted area
         LA    R1,10               * Max length to scan
SCAN_DEC CLI   0(R4),X'40'         * Is it a blank (suppressed zero)?
         BNE   COPY_DEC            * No -> Found first digit
         LA    R4,1(,R4)            * Next byte
         BCT   R1,SCAN_DEC         
* Security Check R1 = 0 
         LA    R4,DW_WORK_DEC+9
         LA    R1,1
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
DT_YY    UNPK  DW_WORK_DT(3),1(2,R3)  *Unpack YY (e.g., X'26' -> F2F6)
         MVC   3(2,R5),DW_WORK_DT     * Copy YY to buffer
         MVI   5(R5),C'-'          * First separator

* --- 2. Leap Year Check (R0 = Year) ---
         PACK  DW_DBLWORD,DW_WORK_DT(2)  * Pack "26" -> X'026F'
         CVB   R0,DW_DBLWORD          * R0 = Binary Year
         STC   R0,DW_DT_FEBR          
         TM    DW_DT_FEBR,X'03'       * Divisible by 4?
         BNZ   DT_GETD             
         MVI   DW_DT_TAB+1,29         * Leap year: Feb = 29

* --- 3. Extract Julian Day (R1 = DDD) ---
DT_GETD  EQU   * 
         MVC   DW_WORK_DT(4),=X'0000000F' * Reset work area
         MVC   DW_WORK_DT(2),2(R3)    * Copy X'084F' into WORK_DT
* Now WORK_DT contains X'084F000F'. 
* We use ZAP to clean it and align it into DBLWORD.
         ZAP   DW_DBLWORD,DW_WORK_DT(2)  *Force X'084F' WDBLWORD safely
         CVB   R1,DW_DBLWORD          * R1 = Binary Day (e.g., 84)
* Verification: If SMF had 084F, CVB R1 now contains exactly 84.

* --- 4. Calculate Month (R6) and Day (R1) ---
         LA    R4,DW_DT_TAB           * R4 points to Month Table
         LA    R6,1                * R6 = Month Counter
DT_LOOP  SR    R0,R0
         IC    R0,0(,R4)            * R0 = Days in current month
         CR    R1,R0               * Is Day <= Days in Month?
         BNH   DT_DONE             * Yes -> Month/Day found
         SR    R1,R0               * No -> Subtract days
         LA    R4,1(,R4)            * Next month
         LA    R6,1(,R6)            * Increment Month
         B     DT_LOOP

DT_DONE  CVD   R6,DW_DBLWORD          * Convert Month (R6) to Packed
         UNPK  DW_WORK_DT(3),DW_DBLWORD+6(2)
         OI    DW_WORK_DT+2,X'F0'     * Fix sign
         MVC   6(2,R5),DW_WORK_DT+1   * Write MM
         MVI   8(R5),C'-'          * Second separator
         
         CVD   R1,DW_DBLWORD          * Convert remaining Day (R1)
         UNPK  DW_WORK_DT(3),DW_DBLWORD+6(2)
         OI    DW_WORK_DT+2,X'F0'     * Fix sign
         MVC   9(2,R5),DW_WORK_DT+1   * Write DD

* --- 5. Wrap up ---
         MVI   11(R5),C'"'         
         LA    R5,12(,R5)           * Total length 12 bytes
         MVI   DW_DT_TAB+1,28         * Reset Feb for next record
         
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
         CVD   R1,DW_DBLWORD          * Convert Hours to Packed
         UNPK  DW_WORK_TM(3),DW_DBLWORD+6(2)
         OI    DW_WORK_TM+2,X'F0'     * Fix sign
         MVC   1(2,R5),DW_WORK_TM+1   * Write HH
         MVI   3(R5),C':'          * Separator

* --- 3. Minutes ---
*         LR    R0,R6               * restore R0
         LR    R1,R0               * R1 = Remaining seconds
         SR    R0,R0               * Clear R0
         LA    R4,60
         DR    R0,R4                * R1 = Minutes, R0 = Seconds

         CVD   R1,DW_DBLWORD
         UNPK  DW_WORK_TM(3),DW_DBLWORD+6(2)
         OI    DW_WORK_TM+2,X'F0'
         MVC   4(2,R5),DW_WORK_TM+1   * Write MM
         MVI   6(R5),C':'          * Separator

* --- 4. Seconds ---

         CVD   R0,DW_DBLWORD          * R0 is the remainder (Seconds)
         UNPK  DW_WORK_TM(3),DW_DBLWORD+6(2)
         OI    DW_WORK_TM+2,X'F0'
         MVC   7(2,R5),DW_WORK_TM+1   * Write SS

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


* --- Constants Data area for GET_DEC ---     
ED_PAT   DC    X'40202020202020202021' * Edit Pattern

* --- Constants Data area for GET_DATE ---
DT_TAB   DC    AL1(31,28,31,30,31,30,31,31,30,31,30,31)


         LTORG

*---------------------------------------------------------------------*
* DSECT DEFINITIONS                                                   *
*---------------------------------------------------------------------*

MYPARMS  DSECT
P_EYE    DC    CL8'MYDATA'       *Eyecatcher
DW_FJSON DS    X
P_SMFREC DS    A                 * Input SMF Record Address
P_TABLE  DS    A                 * Mapping Table Address
P_JSONBUF DS   A                 * Output JSON Buffer Address
P_JSONLEN DS   F                 * Generated Length (Return)
P_WORKAREA DS   A                * Dynamic storage pointer
P_ECB_ADDR DS   A             
P_STATUS DS    X    
         DS    XL3               * Padding
P_SRB_BASE DS    A

DYNAMIC_WORK DSECT
DW_SAVEAREA  DS    18F
DW_DBLWORD   DS    D
DW_FIRSTLBL  DS    X
DW_FIRSTOBJ  DS    X
DW_DT_FEBR   DS    X
DW_WORK_TM   DS    CL3
DW_WORK_DT   DS    CL8
DW_WORK_DEC  DS    CL10
DW_DT_TAB    DS    XL12    * Copie locale du tableau des mois
DW_SIZE      EQU   *-DYNAMIC_WORK


         END
         