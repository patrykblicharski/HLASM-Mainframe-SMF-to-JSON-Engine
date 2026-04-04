*---------------------------------------------------------------------
* MODULE   : SMF2ZIIP                                                 
* FUNCTION : SMF TO JSON CONVERTER - ZIIP OFFLOAD ENGINE              
* STATUS   : UNDER DEVELOPMENT / WORK IN PROGRESS                     
*---------------------------------------------------------------------
* *
* COMING SOON: THE POWER OF ZIIP EXPLOITATION                        
* *
* THIS MODULE IS THE FUTURE HOME OF THE SMF2JSON OFFLOAD LOGIC.      
* GOAL: REDUCE GENERAL PURPOSE PROCESSOR (CP) CONSUMPTION BY         
* SHIFTING HEAVY STRING MANIPULATION AND JSON FORMATTING TO          
* THE ZIIP ASSIST PROCESSORS.                                        
* *
* STRATEGY:                                                          
* - SWITCH TO ENCLAVE SERVICE (SRB MODE)                             
* - MINIMIZE TCB-TO-SRB SWITCHING OVERHEAD                           
* - MAXIMIZE COST-SAVING CONVERSION PERFORMANCE                      
* *
* STAY TUNED. CODESPACE INITIALIZED.                                 
* *
*--------------------------------------------------------------------

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

         
SMF2ZIIP CSECT
         BAKR  R14,0         
         LR    R12,R15        
         USING SMF2ZIIP,R12


         PR
      
         END
         