* ====================================================================
* SMF TYPE 119 SUBTYPE 21 — TCP/IP Statistics
* Generated from temp/smf119-app pacsys layouts. Labels: CommServer/IFASMFR.
* ====================================================================
TABLE119_21 SMF_START

* --- header ---
         SMF_FIELD SMF119RTY-SMF119LEN,TYPE=T_DEC1,JSON=smf_record_type

         SMF_FIELD SMF119TME-SMF119LEN,TYPE=T_TME,JSON=time

         SMF_FIELD SMF119DTE-SMF119LEN,TYPE=T_DTE,JSON=date

         SMF_FIELD SMF119SID-SMF119LEN,TYPE=T_CHR4,JSON=smf_system_id

         SMF_FIELD SMF119SSI-SMF119LEN,TYPE=T_CHR4,JSON=ssi

         SMF_FIELD SMF119STY-SMF119LEN,TYPE=T_DEC2,JSON=subtype

* --- section via SMF119IDOff ---
         SMF_FIELD SMF119TI_SYSName-SMF119TI_SYSName,TRIPLET=SMF119IDOff-SMF119LEN,        X
               TYPE=T_CHR8,JSON=system_name

         SMF_FIELD SMF119TI_SysplexName-SMF119TI_SYSName,TRIPLET=SMF119IDOff-SMF119LEN,        X
               TYPE=T_CHR8,JSON=sysplex_name

         SMF_FIELD SMF119TI_Stack-SMF119TI_SYSName,TRIPLET=SMF119IDOff-SMF119LEN,        X
               TYPE=T_CHR8,JSON=stack_name

         SMF_FIELD SMF119TI_ReleaseID-SMF119TI_SYSName,TRIPLET=SMF119IDOff-SMF119LEN,        X
               TYPE=T_CHR8,JSON=tireleaseid

         SMF_FIELD SMF119TI_Comp-SMF119TI_SYSName,TRIPLET=SMF119IDOff-SMF119LEN,        X
               TYPE=T_CHR8,JSON=ticomp

         SMF_FIELD SMF119TI_ASName-SMF119TI_SYSName,TRIPLET=SMF119IDOff-SMF119LEN,        X
               TYPE=T_CHR8,JSON=as_name

         SMF_FIELD SMF119TI_UserID-SMF119TI_SYSName,TRIPLET=SMF119IDOff-SMF119LEN,        X
               TYPE=T_CHR8,JSON=user_id

         SMF_FIELD SMF119TI_ASID-SMF119TI_SYSName,TRIPLET=SMF119IDOff-SMF119LEN,        X
               TYPE=T_DEC2,JSON=tiasid

         SMF_FIELD SMF119TI_Reason-SMF119TI_SYSName,TRIPLET=SMF119IDOff-SMF119LEN,        X
               TYPE=T_DEC1,JSON=tireason

* --- section via SMF119S1Off ---
         SMF_FIELD SMF119TN_NTLU-SMF119TN_NTLU,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_CHR8,JSON=tnntlu

         SMF_FIELD SMF119TN_NTAppl-SMF119TN_NTLU,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_CHR8,JSON=tnntappl

         SMF_FIELD SMF119TN_NTLdev-SMF119TN_NTLU,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=tnntldev

         SMF_FIELD SMF119TN_NTRPort-SMF119TN_NTLU,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=tnntrport

         SMF_FIELD SMF119TN_NTLPort-SMF119TN_NTLU,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=tnntlport

         SMF_FIELD SMF119TN_NTHostNm-SMF119TN_NTLU,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_CHR8,JSON=tnnthostnm

         SMF_FIELD SMF119TN_NTiTime-SMF119TN_NTLU,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=tnntitime

         SMF_FIELD SMF119TN_NTiDate-SMF119TN_NTLU,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DTE,JSON=tnntidate

         SMF_FIELD SMF119TN_NTtTime-SMF119TN_NTLU,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=tnntttime

         SMF_FIELD SMF119TN_NTtDate-SMF119TN_NTLU,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DTE,JSON=tnnttdate

         SMF_FIELD SMF119TN_NTDur-SMF119TN_NTLU,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=tnntdur

         SMF_FIELD SMF119TN_NTSType-SMF119TN_NTLU,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=tnntstype

         SMF_FIELD SMF119TN_NTLUSel-SMF119TN_NTLU,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=tnntlusel

         SMF_FIELD SMF119TN_NTSSL-SMF119TN_NTLU,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=tnntssl

         SMF_FIELD SMF119TN_NTCopt-SMF119TN_NTLU,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=tnntcopt

         SMF_FIELD SMF119TN_NT32opt-SMF119TN_NTLU,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=tnnt32opt

         SMF_FIELD SMF119TN_NTRCode-SMF119TN_NTLU,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_CHR8,JSON=tnntrcode

         SMF_FIELD SMF119TN_NTLMode-SMF119TN_NTLU,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_CHR8,JSON=tnntlmode

         SMF_FIELD SMF119TN_NTDevt-SMF119TN_NTLU,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_CHR20,JSON=tnntdevt

* --- section via SMF119S3Off ---
         SMF_FIELD SMF119TN_NTRRts-SMF119TN_NTRRts,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=tnntrrts

         SMF_FIELD SMF119TN_NTRIPRts-SMF119TN_NTRRts,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=tnntriprts

         SMF_FIELD SMF119TN_NTRCountTrans-SMF119TN_NTRRts,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=tnntrcounttrans

         SMF_FIELD SMF119TN_NTRCountIP-SMF119TN_NTRRts,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=tnntrcountip

         SMF_FIELD SMF119TN_NTRGrpIndex-SMF119TN_NTRRts,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=tnntrgrpindex

         SMF_FIELD SMF119TN_NTRDR-SMF119TN_NTRRts,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=tnntrdr

* --- section via SMF119S4Off ---
         SMF_FIELD SMF119TN_NTBucketBndry1-SMF119TN_NTBucketBndry1,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=tnntbucketbndry1

         SMF_FIELD SMF119TN_NTBucketBndry2-SMF119TN_NTBucketBndry1,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=tnntbucketbndry2

         SMF_FIELD SMF119TN_NTBucketBndry3-SMF119TN_NTBucketBndry1,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=tnntbucketbndry3

         SMF_FIELD SMF119TN_NTBucketBndry4-SMF119TN_NTBucketBndry1,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=tnntbucketbndry4

         SMF_FIELD SMF119TN_NTBucket1Rts-SMF119TN_NTBucketBndry1,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=tnntbucket1rts

         SMF_FIELD SMF119TN_NTBucket2Rts-SMF119TN_NTBucketBndry1,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=tnntbucket2rts

         SMF_FIELD SMF119TN_NTBucket3Rts-SMF119TN_NTBucketBndry1,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=tnntbucket3rts

         SMF_FIELD SMF119TN_NTBucket4Rts-SMF119TN_NTBucketBndry1,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=tnntbucket4rts

         SMF_FIELD SMF119TN_NTBucket5Rts-SMF119TN_NTBucketBndry1,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=tnntbucket5rts

         SMF_END
