* ====================================================================
* SMF TYPE 42 SUBTYPE 3 — SMS configuration changed
* From catalog/smf42 (IBM Docs scrape). Nested DS sections omitted
* (offsets live inside job header — not fixed TRIPLET-safe).
* ====================================================================
TABLE42_3 SMF_START

* --- Header/Self-defining section ---
         SMF_FIELD SMF42RTY-SMF42RCL,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF42TME-SMF42RCL,TYPE=T_TME,JSON=time

         SMF_FIELD SMF42DTE-SMF42RCL,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF42SID-SMF42RCL,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF42SSI-SMF42RCL,TYPE=T_CHR4,JSON=subsystem_id

         SMF_FIELD SMF42STY-SMF42RCL,TYPE=T_DEC2,JSON=subtype

* --- Event audit section via SMF42EAO ---
         SMF_FIELD SMF42EAC-SMF42EAC,TRIPLET=SMF42EAO-SMF42RCL,        X
               TYPE=T_CHR8,JSON=eac

         SMF_FIELD SMF42ERC-SMF42EAC,TRIPLET=SMF42EAO-SMF42RCL,        X
               TYPE=T_DEC4,JSON=erc

         SMF_FIELD SMF42ERS-SMF42EAC,TRIPLET=SMF42EAO-SMF42RCL,        X
               TYPE=T_DEC4,JSON=ers

         SMF_FIELD SMF42EUA-SMF42EAC,TRIPLET=SMF42EAO-SMF42RCL,        X
               TYPE=T_DEC4,JSON=eua

         SMF_FIELD SMF42EOS-SMF42EAC,TRIPLET=SMF42EAO-SMF42RCL,        X
               TYPE=T_DEC1,JSON=eos

         SMF_FIELD SMF42ENS-SMF42EAC,TRIPLET=SMF42EAO-SMF42RCL,        X
               TYPE=T_DEC1,JSON=ens

         SMF_FIELD SMF42ETY-SMF42EAC,TRIPLET=SMF42EAO-SMF42RCL,        X
               TYPE=T_CHR8,JSON=ety

         SMF_FIELD SMF42ESL-SMF42EAC,TRIPLET=SMF42EAO-SMF42RCL,        X
               TYPE=T_DEC2,JSON=esl

         SMF_FIELD SMF42ESY-SMF42EAC,TRIPLET=SMF42EAO-SMF42RCL,        X
               TYPE=T_CHR8,JSON=esy

         SMF_END
