* ====================================================================
* SMF TYPE 42 SUBTYPE 9 — B37/D37/E37 abend information
* From catalog/smf42 (IBM Docs scrape). Nested DS sections omitted
* (offsets live inside job header — not fixed TRIPLET-safe).
* ====================================================================
TABLE42_9 SMF_START

* --- Header/Self-defining section ---
         SMF_FIELD SMF42RTY-SMF42RCL,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF42TME-SMF42RCL,TYPE=T_TME,JSON=time

         SMF_FIELD SMF42DTE-SMF42RCL,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF42SID-SMF42RCL,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF42SSI-SMF42RCL,TYPE=T_CHR4,JSON=subsystem_id

         SMF_FIELD SMF42STY-SMF42RCL,TYPE=T_DEC2,JSON=subtype

* --- B37/D37/E37 abend data section via SMF42ABO ---
         SMF_FIELD S42ASYID-S42ASYID,TRIPLET=SMF42ABO-SMF42RCL,        X
               TYPE=T_CHR4,JSON=asyid

         SMF_FIELD S42JOBN-S42ASYID,TRIPLET=SMF42ABO-SMF42RCL,        X
               TYPE=T_CHR8,JSON=jobn

         SMF_FIELD S42RDST-S42ASYID,TRIPLET=SMF42ABO-SMF42RCL,        X
               TYPE=T_DEC4,JSON=rdst

         SMF_FIELD S42RDSD-S42ASYID,TRIPLET=SMF42ABO-SMF42RCL,        X
               TYPE=T_DTE,JSON=rdsd

         SMF_FIELD S42AAUID-S42ASYID,TRIPLET=SMF42ABO-SMF42RCL,        X
               TYPE=T_CHR8,JSON=aauid

         SMF_FIELD S42ASTPN-S42ASYID,TRIPLET=SMF42ABO-SMF42RCL,        X
               TYPE=T_DEC1,JSON=astpn

         SMF_FIELD S42FLAGS-S42ASYID,TRIPLET=SMF42ABO-SMF42RCL,        X
               TYPE=T_DEC1,JSON=flags

         SMF_FIELD S42DSORG-S42ASYID,TRIPLET=SMF42ABO-SMF42RCL,        X
               TYPE=T_DEC2,JSON=dsorg

         SMF_FIELD S42ADISP-S42ASYID,TRIPLET=SMF42ABO-SMF42RCL,        X
               TYPE=T_DEC1,JSON=adisp

         SMF_FIELD S42UCBTP-S42ASYID,TRIPLET=SMF42ABO-SMF42RCL,        X
               TYPE=T_DEC4,JSON=ucbtp

         SMF_FIELD S42NEXT-S42ASYID,TRIPLET=SMF42ABO-SMF42RCL,        X
               TYPE=T_DEC1,JSON=next

         SMF_FIELD S42TNTRK-S42ASYID,TRIPLET=SMF42ABO-SMF42RCL,        X
               TYPE=T_DEC4,JSON=tntrk

         SMF_FIELD S42ASSAT-S42ASYID,TRIPLET=SMF42ABO-SMF42RCL,        X
               TYPE=T_DEC4,JSON=assat

         SMF_END
