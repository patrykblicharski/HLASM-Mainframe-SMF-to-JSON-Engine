* ====================================================================
* SMF TYPE 72 SUBTYPE 3 — Workload activity (WLM)
* ====================================================================
TABLE72_3 SMF_START

         SMF_FIELD SMF72RTY-SMF72LEN,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF72SID-SMF72LEN,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF72TME-SMF72LEN,TYPE=T_TME,JSON=time

         SMF_FIELD SMF72DTE-SMF72LEN,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF72SSI-SMF72LEN,TYPE=T_CHR4,JSON=subsystem_id

         SMF_FIELD SMF72STY-SMF72LEN,TYPE=T_DEC2,JSON=subtype

* --- product ---
         SMF_FIELD SMF72PRD-SMF72MFV,TRIPLET=SMF72PRS-SMF72LEN,        X
               TYPE=T_CHR8,JSON=product_name

         SMF_FIELD SMF72DAT-SMF72MFV,TRIPLET=SMF72PRS-SMF72LEN,        X
               TYPE=T_DTE,JSON=dat

         SMF_FIELD SMF72SAM-SMF72MFV,TRIPLET=SMF72PRS-SMF72LEN,        X
               TYPE=T_DEC4,JSON=sam

         SMF_FIELD SMF72MVS-SMF72MFV,TRIPLET=SMF72PRS-SMF72LEN,        X
               TYPE=T_CHR8,JSON=mvs_level

         SMF_FIELD SMF72XNM-SMF72MFV,TRIPLET=SMF72PRS-SMF72LEN,        X
               TYPE=T_CHR8,JSON=sysplex_name

         SMF_FIELD SMF72SNM-SMF72MFV,TRIPLET=SMF72PRS-SMF72LEN,        X
               TYPE=T_CHR8,JSON=system_name

* --- WLM control ---
         SMF_FIELD R723MNSP-R723MSCF,TRIPLET=SMF72WMS-SMF72LEN,        X
               TYPE=T_CHR8,JSON=policy_name

         SMF_FIELD R723MWNM-R723MSCF,TRIPLET=SMF72WMS-SMF72LEN,        X
               TYPE=T_CHR8,JSON=workload_name

         SMF_FIELD R723MCNM-R723MSCF,TRIPLET=SMF72WMS-SMF72LEN,        X
               TYPE=T_CHR8,JSON=class_name

         SMF_FIELD R723MCPG-R723MSCF,TRIPLET=SMF72WMS-SMF72LEN,        X
               TYPE=T_DEC2,JSON=period_count

         SMF_FIELD R723MIDN-R723MSCF,TRIPLET=SMF72WMS-SMF72LEN,        X
               TYPE=T_CHR8,JSON=serv_def_name

         SMF_FIELD R723MIDU-R723MSCF,TRIPLET=SMF72WMS-SMF72LEN,        X
               TYPE=T_CHR8,JSON=midu

         SMF_FIELD R723MOPT-R723MSCF,TRIPLET=SMF72WMS-SMF72LEN,        X
               TYPE=T_CHR2,JSON=mopt

         SMF_FIELD R723MTVL-R723MSCF,TRIPLET=SMF72WMS-SMF72LEN,        X
               TYPE=T_DEC4,JSON=mtvl

* --- service/report class period ---
         SMF_FIELD R723CPER-R723CRTX,TRIPLET=SMF72SCS-SMF72LEN,        X
               TYPE=T_DEC1,JSON=period_number

         SMF_FIELD R723CVAL-R723CRTX,TRIPLET=SMF72SCS-SMF72LEN,        X
               TYPE=T_DEC4,JSON=goal_value

         SMF_FIELD R723CPCT-R723CRTX,TRIPLET=SMF72SCS-SMF72LEN,        X
               TYPE=T_DEC2,JSON=cpct

         SMF_FIELD R723CIMP-R723CRTX,TRIPLET=SMF72SCS-SMF72LEN,        X
               TYPE=T_DEC2,JSON=importance

         SMF_FIELD R723CRCP-R723CRTX,TRIPLET=SMF72SCS-SMF72LEN,        X
               TYPE=T_DEC4,JSON=tran_complete

         SMF_FIELD R723CARC-R723CRTX,TRIPLET=SMF72SCS-SMF72LEN,        X
               TYPE=T_DEC4,JSON=carc

         SMF_FIELD R723CCUS-R723CRTX,TRIPLET=SMF72SCS-SMF72LEN,        X
               TYPE=T_DEC4,JSON=cpu_using

         SMF_FIELD R723CSWC-R723CRTX,TRIPLET=SMF72SCS-SMF72LEN,        X
               TYPE=T_DEC4,JSON=cswc

         SMF_FIELD R723CCDE-R723CRTX,TRIPLET=SMF72SCS-SMF72LEN,        X
               TYPE=T_DEC4,JSON=cpu_delay

* --- resource group ---
         SMF_FIELD R723GGNM-R723GGNM,TRIPLET=SMF72RGS-SMF72LEN,        X
               TYPE=T_CHR8,JSON=res_group_name

         SMF_FIELD R723GGMN-R723GGNM,TRIPLET=SMF72RGS-SMF72LEN,        X
               TYPE=T_DEC4,JSON=ggmn

         SMF_FIELD R723GGMX-R723GGNM,TRIPLET=SMF72RGS-SMF72LEN,        X
               TYPE=T_DEC4,JSON=ggmx

         SMF_END
