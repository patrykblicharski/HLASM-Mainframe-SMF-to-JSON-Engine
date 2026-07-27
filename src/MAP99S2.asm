* ====================================================================
* SMF TYPE 99 SUBTYPE 2 — Service class data
* Auto-generated from Gatherer OpenAPI (tools/gen_gatherer_maps.py)
* Section fields capped: 12/section, 48 total
* ====================================================================
TABLE99_2 SMF_START

         SMF_FIELD SMF99RTY-SMF99LEN,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF99SID-SMF99LEN,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF99TME-SMF99LEN,TYPE=T_TME,JSON=time

         SMF_FIELD SMF99DTE-SMF99LEN,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF99SSID-SMF99LEN,TYPE=T_CHR4,JSON=subsystem_id

         SMF_FIELD SMF99TID-SMF99LEN,TYPE=T_DEC2,JSON=subtype

* --- section SMF99_SUBTYPE2_PRODUCT_INFORMATION via SMF99POF ---
         SMF_FIELD SMF99VN2-SMF99VN2,TRIPLET=SMF99POF-SMF99LEN,        X
               TYPE=T_DEC2,JSON=vn2

         SMF_FIELD SMF99RVN-SMF99VN2,TRIPLET=SMF99POF-SMF99LEN,        X
               TYPE=T_CHR2,JSON=rvn

         SMF_FIELD SMF99PNM-SMF99VN2,TRIPLET=SMF99POF-SMF99LEN,        X
               TYPE=T_CHR8,JSON=pnm

         SMF_FIELD SMF99SLV-SMF99VN2,TRIPLET=SMF99POF-SMF99LEN,        X
               TYPE=T_CHR8,JSON=slv

         SMF_FIELD SMF99SNM-SMF99VN2,TRIPLET=SMF99POF-SMF99LEN,        X
               TYPE=T_CHR8,JSON=system_name

         SMF_END
