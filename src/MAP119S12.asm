* ====================================================================
* SMF TYPE 119 SUBTYPE 12 — TCP/IP Statistics
* Generated from temp/smf119-app pacsys layouts. Labels: CommServer/IFASMFR.
* ====================================================================
TABLE119_12 SMF_START

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
         SMF_FIELD SMF119SS_SAEvent_Type-SMF119SS_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=sssaeventtype

         SMF_FIELD SMF119SS_SAFlags-SMF119SS_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=sssaflags

         SMF_FIELD SMF119SS_SASecProtos-SMF119SS_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=sssasecprotos

         SMF_FIELD SMF119SS_SAJobname-SMF119SS_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_CHR8,JSON=sssajobname

         SMF_FIELD SMF119SS_SAUserID-SMF119SS_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_CHR8,JSON=sssauserid

         SMF_FIELD SMF119SS_SAIPProto-SMF119SS_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=sssaipproto

         SMF_FIELD SMF119SS_SASrvPortStart-SMF119SS_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sssasrvportstart

         SMF_FIELD SMF119SS_SASrvPortEnd-SMF119SS_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sssasrvportend

         SMF_FIELD SMF119SS_SAInitLifeConnCnt-SMF119SS_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=sssainitlifeconn

         SMF_FIELD SMF119SS_SAInitLifePartialConnCnt-SMF119SS_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=sssainitlifepart

         SMF_FIELD SMF119SS_SAInitLifeShortConnCnt-SMF119SS_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=sssainitlifeshor

         SMF_FIELD SMF119SS_SAInitActiveConnCnt-SMF119SS_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=sssainitactiveco

         SMF_FIELD SMF119SS_SAEndLifeConnCnt-SMF119SS_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=sssaendlifeconnc

         SMF_FIELD SMF119SS_SAEndLifePartialConnCnt-SMF119SS_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=sssaendlifeparti

         SMF_FIELD SMF119SS_SAEndLifeShortConnCnt-SMF119SS_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=sssaendlifeshort

         SMF_FIELD SMF119SS_SAEndActiveConnCnt-SMF119SS_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=sssaendactivecon

* --- section via SMF119S2Off ---
         SMF_FIELD SMF119SS_TLS_Source-SMF119SS_TLS_Source,TRIPLET=SMF119S2Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=sstlssource

         SMF_FIELD SMF119SS_TLS_CryptoFlags-SMF119SS_TLS_Source,TRIPLET=SMF119S2Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=sstlscryptoflags

         SMF_FIELD SMF119SS_TLS_Prot_Ver-SMF119SS_TLS_Source,TRIPLET=SMF119S2Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sstlsprotver

         SMF_FIELD SMF119SS_TLS_CS_Enc_Alg-SMF119SS_TLS_Source,TRIPLET=SMF119S2Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sstlscsencalg

         SMF_FIELD SMF119SS_TLS_CS_Msg_Auth-SMF119SS_TLS_Source,TRIPLET=SMF119S2Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sstlscsmsgauth

         SMF_FIELD SMF119SS_TLS_CS_Kex_Alg-SMF119SS_TLS_Source,TRIPLET=SMF119S2Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sstlscskexalg

         SMF_FIELD SMF119SS_TLS_SCert_Signature_Method-SMF119SS_TLS_Source,TRIPLET=SMF119S2Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sstlsscertsignat

         SMF_FIELD SMF119SS_TLS_SCert_Enc_Method-SMF119SS_TLS_Source,TRIPLET=SMF119S2Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sstlsscertencmet

         SMF_FIELD SMF119SS_TLS_SCert_Digest_Alg-SMF119SS_TLS_Source,TRIPLET=SMF119S2Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sstlsscertdigest

         SMF_FIELD SMF119SS_TLS_SCert_Key_Type-SMF119SS_TLS_Source,TRIPLET=SMF119S2Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sstlsscertkeytyp

         SMF_FIELD SMF119SS_TLS_SCert_Key_Len-SMF119SS_TLS_Source,TRIPLET=SMF119S2Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sstlsscertkeylen

         SMF_FIELD SMF119SS_TLS_CCert_Signature_Method-SMF119SS_TLS_Source,TRIPLET=SMF119S2Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sstlsccertsignat

         SMF_FIELD SMF119SS_TLS_CCert_Enc_Method-SMF119SS_TLS_Source,TRIPLET=SMF119S2Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sstlsccertencmet

         SMF_FIELD SMF119SS_TLS_CCert_Digest_Alg-SMF119SS_TLS_Source,TRIPLET=SMF119S2Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sstlsccertdigest

         SMF_FIELD SMF119SS_TLS_CCert_Key_Type-SMF119SS_TLS_Source,TRIPLET=SMF119S2Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sstlsccertkeytyp

         SMF_FIELD SMF119SS_TLS_CCert_Key_Len-SMF119SS_TLS_Source,TRIPLET=SMF119S2Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sstlsccertkeylen

* --- section via SMF119S3Off ---
         SMF_FIELD SMF119SS_SSH_Source-SMF119SS_SSH_Source,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=sssshsource

         SMF_FIELD SMF119SS_SSH_Prot_Ver-SMF119SS_SSH_Source,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=sssshprotver

         SMF_FIELD SMF119SS_SSH_CryptoFlags-SMF119SS_SSH_Source,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=sssshcryptoflags

         SMF_FIELD SMF119SS_SSH_Auth_Method-SMF119SS_SSH_Source,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sssshauthmethod

         SMF_FIELD SMF119SS_SSH_Auth_Method2-SMF119SS_SSH_Source,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sssshauthmethod2

         SMF_FIELD SMF119SS_SSH_In_Enc_Alg-SMF119SS_SSH_Source,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sssshinencalg

         SMF_FIELD SMF119SS_SSH_In_Msg_Auth-SMF119SS_SSH_Source,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sssshinmsgauth

         SMF_FIELD SMF119SS_SSH_Kex_Method-SMF119SS_SSH_Source,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sssshkexmethod

         SMF_FIELD SMF119SS_SSH_Out_Enc_Alg-SMF119SS_SSH_Source,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sssshoutencalg

         SMF_FIELD SMF119SS_SSH_Out_Msg_Auth-SMF119SS_SSH_Source,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sssshoutmsgauth

         SMF_FIELD SMF119SS_SSH_SKey_Type-SMF119SS_SSH_Source,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sssshskeytype

         SMF_FIELD SMF119SS_SSH_SKey_Len-SMF119SS_SSH_Source,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sssshskeylen

         SMF_FIELD SMF119SS_SSH_CKey_Type-SMF119SS_SSH_Source,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sssshckeytype

         SMF_FIELD SMF119SS_SSH_CKey_Len-SMF119SS_SSH_Source,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sssshckeylen

         SMF_FIELD SMF119SS_SSH_SCert_Signature_Method-SMF119SS_SSH_Source,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sssshscertsignat

         SMF_FIELD SMF119SS_SSH_SCert_Enc_Method-SMF119SS_SSH_Source,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sssshscertencmet

         SMF_FIELD SMF119SS_SSH_SCert_Digest_Alg-SMF119SS_SSH_Source,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sssshscertdigest

         SMF_FIELD SMF119SS_SSH_SCert_Key_Type-SMF119SS_SSH_Source,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sssshscertkeytyp

         SMF_FIELD SMF119SS_SSH_SCert_Key_Len-SMF119SS_SSH_Source,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sssshscertkeylen

         SMF_FIELD SMF119SS_SSH_CCert_Signature_Method-SMF119SS_SSH_Source,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sssshccertsignat

         SMF_FIELD SMF119SS_SSH_CCert_Enc_Method-SMF119SS_SSH_Source,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sssshccertencmet

         SMF_FIELD SMF119SS_SSH_CCert_Digest_Alg-SMF119SS_SSH_Source,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sssshccertdigest

         SMF_FIELD SMF119SS_SSH_CCert_Key_Type-SMF119SS_SSH_Source,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sssshccertkeytyp

         SMF_FIELD SMF119SS_SSH_CCert_Key_Len-SMF119SS_SSH_Source,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sssshccertkeylen

* --- section via SMF119S4Off ---
         SMF_FIELD SMF119SS_IPSec_IKEMajVer-SMF119SS_IPSec_IKEMajVer,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=ssipsecikemajver

         SMF_FIELD SMF119SS_IPSec_IKEMinVer-SMF119SS_IPSec_IKEMajVer,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=ssipsecikeminver

         SMF_FIELD SMF119SS_IPSec_IKETunLclAuthMeth-SMF119SS_IPSec_IKEMajVer,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=ssipseciketunlcl

         SMF_FIELD SMF119SS_IPSec_IKETunRmtAuthMeth-SMF119SS_IPSec_IKEMajVer,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=ssipseciketunrmt

         SMF_FIELD SMF119SS_IPSec_IKETunAuthAlg-SMF119SS_IPSec_IKEMajVer,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=ssipseciketunaut

         SMF_FIELD SMF119SS_IPSec_IKETunEncAlg-SMF119SS_IPSec_IKEMajVer,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=ssipseciketunenc

         SMF_FIELD SMF119SS_IPSec_IKETunDHGroup-SMF119SS_IPSec_IKEMajVer,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=ssipseciketundhg

         SMF_FIELD SMF119SS_IPSec_IKETunPseudoRandFunc-SMF119SS_IPSec_IKEMajVer,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=ssipseciketunpse

         SMF_FIELD SMF119SS_IPSec_LclCert_Sign_Meth-SMF119SS_IPSec_IKEMajVer,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=ssipseclclcertsi

         SMF_FIELD SMF119SS_IPSec_LclCert_Enc_Meth-SMF119SS_IPSec_IKEMajVer,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=ssipseclclcerten

         SMF_FIELD SMF119SS_IPSec_LclCert_Digest_Alg-SMF119SS_IPSec_IKEMajVer,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=ssipseclclcertdi

         SMF_FIELD SMF119SS_IPSec_LclCert_Key_Type-SMF119SS_IPSec_IKEMajVer,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=ssipseclclcertke

         SMF_FIELD SMF119SS_IPSec_LclCert_Key_Len-SMF119SS_IPSec_IKEMajVer,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=ssipseclclcertk2

         SMF_FIELD SMF119SS_IPSec_RmtCert_Sign_Meth-SMF119SS_IPSec_IKEMajVer,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=ssipsecrmtcertsi

         SMF_FIELD SMF119SS_IPSec_RmtCert_Enc_Meth-SMF119SS_IPSec_IKEMajVer,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=ssipsecrmtcerten

         SMF_FIELD SMF119SS_IPSec_RmtCert_Digest_Alg-SMF119SS_IPSec_IKEMajVer,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=ssipsecrmtcertdi

         SMF_FIELD SMF119SS_IPSec_RmtCert_Key_Type-SMF119SS_IPSec_IKEMajVer,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=ssipsecrmtcertke

         SMF_FIELD SMF119SS_IPSec_RmtCert_Key_Len-SMF119SS_IPSec_IKEMajVer,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=ssipsecrmtcertk2

         SMF_FIELD SMF119SS_IPSec_PFSGroup-SMF119SS_IPSec_IKEMajVer,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=ssipsecpfsgroup

         SMF_FIELD SMF119SS_IPSec_EncapMode-SMF119SS_IPSec_IKEMajVer,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=ssipsecencapmode

         SMF_FIELD SMF119SS_IPSec_AuthProto-SMF119SS_IPSec_IKEMajVer,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=ssipsecauthproto

         SMF_FIELD SMF119SS_IPSec_AuthAlg-SMF119SS_IPSec_IKEMajVer,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=ssipsecauthalg

         SMF_FIELD SMF119SS_IPSec_EncAlg-SMF119SS_IPSec_IKEMajVer,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=ssipsecencalg

* --- section via SMF119S5Off ---
         SMF_FIELD SMF119SS_DN_Len-SMF119SS_DN_Len,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=ssdnlen

         SMF_FIELD SMF119SS_DN_Type-SMF119SS_DN_Len,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=ssdntype

         SMF_END
