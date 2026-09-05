* ====================================================================
* SMF TYPE 42 SUBTYPE 10 — Volume selection failure
* From catalog/smf42 (IBM Docs scrape). Nested DS sections omitted
* (offsets live inside job header — not fixed TRIPLET-safe).
* ====================================================================
TABLE42_10 SMF_START

* --- Header/Self-defining section ---
         SMF_FIELD SMF42RTY-SMF42RCL,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF42TME-SMF42RCL,TYPE=T_TME,JSON=time

         SMF_FIELD SMF42DTE-SMF42RCL,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF42SID-SMF42RCL,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF42SSI-SMF42RCL,TYPE=T_CHR4,JSON=subsystem_id

         SMF_FIELD SMF42STY-SMF42RCL,TYPE=T_DEC2,JSON=subtype

* --- Volume Selection Failure Section via SMF42VSF ---
         SMF_FIELD SMF42JBN-SMF42JBN,TRIPLET=SMF42VSF-SMF42RCL,        X
               TYPE=T_CHR8,JSON=jbn

         SMF_FIELD SMF42PGN-SMF42JBN,TRIPLET=SMF42VSF-SMF42RCL,        X
               TYPE=T_CHR8,JSON=pgn

         SMF_FIELD SMF42STN-SMF42JBN,TRIPLET=SMF42VSF-SMF42RCL,        X
               TYPE=T_CHR8,JSON=stn

         SMF_FIELD SMF42DDN-SMF42JBN,TRIPLET=SMF42VSF-SMF42RCL,        X
               TYPE=T_CHR8,JSON=ddn

         SMF_FIELD SMF42RSP-SMF42JBN,TRIPLET=SMF42VSF-SMF42RCL,        X
               TYPE=T_DEC4,JSON=rsp

         SMF_FIELD SMF42UNT-SMF42JBN,TRIPLET=SMF42VSF-SMF42RCL,        X
               TYPE=T_CHR2,JSON=unt

         SMF_FIELD SMF42DCL-SMF42JBN,TRIPLET=SMF42VSF-SMF42RCL,        X
               TYPE=T_DEC2,JSON=dcl

         SMF_FIELD SMF42MCL-SMF42JBN,TRIPLET=SMF42VSF-SMF42RCL,        X
               TYPE=T_DEC2,JSON=mcl

         SMF_FIELD SMF42SLN-SMF42JBN,TRIPLET=SMF42VSF-SMF42RCL,        X
               TYPE=T_DEC2,JSON=sln

         SMF_FIELD SMF42SGL-SMF42JBN,TRIPLET=SMF42VSF-SMF42RCL,        X
               TYPE=T_DEC2,JSON=sgl

         SMF_END
