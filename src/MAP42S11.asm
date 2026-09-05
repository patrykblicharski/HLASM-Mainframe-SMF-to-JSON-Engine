* ====================================================================
* SMF TYPE 42 SUBTYPE 11 — Extended remote copy session statistics
* From catalog/smf42 (IBM Docs scrape). Nested DS sections omitted
* (offsets live inside job header — not fixed TRIPLET-safe).
* ====================================================================
TABLE42_11 SMF_START

* --- Header/Self-defining section ---
         SMF_FIELD SMF42RTY-SMF42RCL,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF42TME-SMF42RCL,TYPE=T_TME,JSON=time

         SMF_FIELD SMF42DTE-SMF42RCL,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF42SID-SMF42RCL,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF42SSI-SMF42RCL,TYPE=T_CHR4,JSON=subsystem_id

         SMF_FIELD SMF42STY-SMF42RCL,TYPE=T_DEC2,JSON=subtype

* --- Extended Remote Copy (XRC) Session Section via SMF42XRO ---
         SMF_FIELD S42XRID-S42XRID,TRIPLET=SMF42XRO-SMF42RCL,        X
               TYPE=T_CHR8,JSON=xrid

         SMF_FIELD S42XRTYP-S42XRID,TRIPLET=SMF42XRO-SMF42RCL,        X
               TYPE=T_CHR8,JSON=xrtyp

         SMF_FIELD S42XRSSN-S42XRID,TRIPLET=SMF42XRO-SMF42RCL,        X
               TYPE=T_DEC2,JSON=xrssn

         SMF_END
