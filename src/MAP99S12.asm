* ====================================================================
* SMF TYPE 99 SUBTYPE 12 — Subtype 12
* Auto-generated from Gatherer OpenAPI (tools/gen_gatherer_maps.py)
* All supported T_* section fields (no per-section caps)
* ====================================================================
TABLE99_12 SMF_START

         SMF_FIELD SMF99RTY-SMF99LEN,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF99SID-SMF99LEN,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF99TME-SMF99LEN,TYPE=T_TME,JSON=time

         SMF_FIELD SMF99DTE-SMF99LEN,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF99SSID-SMF99LEN,TYPE=T_CHR4,JSON=subsystem_id

         SMF_FIELD SMF99TID-SMF99LEN,TYPE=T_DEC2,JSON=subtype

* --- section SMF99_SUBTYPE12_PRODUCT_INFORMATION via SMF99POF ---
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

* --- section SMF99_SUBTYPE12_HEADER_DATA_SECTION via SMF99DOF ---
         SMF_FIELD SMF99C_VCM_SMF_SEQU-SMF99C_VCM_SMF_SEQU,TRIPLET=SMF99DOF-SMF99LEN,        X
               TYPE=T_DEC4,JSON=cvcmsmfsequ

         SMF_FIELD SMF99C_VCM_ERRORCODE-SMF99C_VCM_SMF_SEQU,TRIPLET=SMF99DOF-SMF99LEN,        X
               TYPE=T_DEC2,JSON=cvcmerrorcode

         SMF_FIELD SMF99C_VCM_INTERVAL_LEN-SMF99C_VCM_SMF_SEQU,TRIPLET=SMF99DOF-SMF99LEN,        X
               TYPE=T_DEC4,JSON=cvcmintervallen

         SMF_FIELD SMF99C_VCM_LPARPHYSPROCSHR-SMF99C_VCM_SMF_SEQU,TRIPLET=SMF99DOF-SMF99LEN,        X
               TYPE=T_DEC4,JSON=cvcmlparphysproc

         SMF_FIELD SMF99C_VCM_CURRENT_STATE-SMF99C_VCM_SMF_SEQU,TRIPLET=SMF99DOF-SMF99LEN,        X
               TYPE=T_DEC4,JSON=cvcmcurrentstate

         SMF_FIELD SMF99C_VCM_PREVIOUS_STATE-SMF99C_VCM_SMF_SEQU,TRIPLET=SMF99DOF-SMF99LEN,        X
               TYPE=T_DEC4,JSON=cvcmpreviousstat

         SMF_FIELD SMF99C_VCM_RESTART_CTR-SMF99C_VCM_SMF_SEQU,TRIPLET=SMF99DOF-SMF99LEN,        X
               TYPE=T_DEC4,JSON=cvcmrestartctr

         SMF_END
