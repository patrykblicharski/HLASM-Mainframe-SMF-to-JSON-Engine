* ====================================================================
* SMF TYPE 42 SUBTYPE 1 — BMF cache summary / storage-class buffer manager hits
* From catalog/smf42 (IBM Docs scrape). Nested DS sections omitted
* (offsets live inside job header — not fixed TRIPLET-safe).
* ====================================================================
TABLE42_1 SMF_START

* --- Header/Self-defining section ---
         SMF_FIELD SMF42RTY-SMF42RCL,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF42TME-SMF42RCL,TYPE=T_TME,JSON=time

         SMF_FIELD SMF42DTE-SMF42RCL,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF42SID-SMF42RCL,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF42SSI-SMF42RCL,TYPE=T_CHR4,JSON=subsystem_id

         SMF_FIELD SMF42STY-SMF42RCL,TYPE=T_DEC2,JSON=subtype

* --- BMF totals section via SMF42BMO ---
         SMF_FIELD SMF42TNA-SMF42TNA,TRIPLET=SMF42BMO-SMF42RCL,        X
               TYPE=T_DEC4,JSON=tna

         SMF_FIELD SMF42TMT-SMF42TNA,TRIPLET=SMF42BMO-SMF42RCL,        X
               TYPE=T_DEC4,JSON=tmt

         SMF_FIELD SMF42TRT-SMF42TNA,TRIPLET=SMF42BMO-SMF42RCL,        X
               TYPE=T_DEC4,JSON=trt

         SMF_FIELD SMF42TRH-SMF42TNA,TRIPLET=SMF42BMO-SMF42RCL,        X
               TYPE=T_DEC4,JSON=trh

         SMF_FIELD SMF42TDT-SMF42TNA,TRIPLET=SMF42BMO-SMF42RCL,        X
               TYPE=T_DEC4,JSON=tdt

         SMF_FIELD SMF42TDH-SMF42TNA,TRIPLET=SMF42BMO-SMF42RCL,        X
               TYPE=T_DEC4,JSON=tdh

         SMF_FIELD SMF42BUF-SMF42TNA,TRIPLET=SMF42BMO-SMF42RCL,        X
               TYPE=T_DEC4,JSON=buf

         SMF_FIELD SMF42BMX-SMF42TNA,TRIPLET=SMF42BMO-SMF42RCL,        X
               TYPE=T_DEC4,JSON=bmx

         SMF_FIELD SMF42LRU-SMF42TNA,TRIPLET=SMF42BMO-SMF42RCL,        X
               TYPE=T_DEC2,JSON=lru

         SMF_FIELD SMF42UIC-SMF42TNA,TRIPLET=SMF42BMO-SMF42RCL,        X
               TYPE=T_DEC2,JSON=uic

* --- Storage class summary section via SMF42SCO ---
         SMF_FIELD SMF42PNL-SMF42PNL,TRIPLET=SMF42SCO-SMF42RCL,        X
               TYPE=T_DEC2,JSON=pnl

         SMF_FIELD SMF42SRT-SMF42PNL,TRIPLET=SMF42SCO-SMF42RCL,        X
               TYPE=T_DEC4,JSON=srt

         SMF_FIELD SMF42SRH-SMF42PNL,TRIPLET=SMF42SCO-SMF42RCL,        X
               TYPE=T_DEC4,JSON=srh

         SMF_FIELD SMF42SDT-SMF42PNL,TRIPLET=SMF42SCO-SMF42RCL,        X
               TYPE=T_DEC4,JSON=sdt

         SMF_FIELD SMF42SDH-SMF42PNL,TRIPLET=SMF42SCO-SMF42RCL,        X
               TYPE=T_DEC4,JSON=sdh

         SMF_END
