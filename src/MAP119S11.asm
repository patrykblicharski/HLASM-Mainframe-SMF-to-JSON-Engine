* ====================================================================
* SMF TYPE 119 SUBTYPE 11 — TCP/IP Statistics
* Generated from temp/smf119-app pacsys layouts. Labels: CommServer/IFASMFR.
* ====================================================================
TABLE119_11 SMF_START

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
         SMF_FIELD SMF119SC_SAEvent_Type-SMF119SC_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scsaeventtype

         SMF_FIELD SMF119SC_SASecProtos-SMF119SC_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scsasecprotos

         SMF_FIELD SMF119SC_SAFlags-SMF119SC_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scsaflags

         SMF_FIELD SMF119SC_SASecFlags-SMF119SC_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scsasecflags

         SMF_FIELD SMF119SC_SAIPProto-SMF119SC_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scsaipproto

         SMF_FIELD SMF119SC_SAJobname-SMF119SC_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_CHR8,JSON=scsajobname

         SMF_FIELD SMF119SC_SAJobID-SMF119SC_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_CHR8,JSON=scsajobid

         SMF_FIELD SMF119SC_SAUserID-SMF119SC_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_CHR8,JSON=scsauserid

         SMF_FIELD SMF119SC_SASTime-SMF119SC_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=scsastime

         SMF_FIELD SMF119SC_SASDate-SMF119SC_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DTE,JSON=scsasdate

         SMF_FIELD SMF119SC_SAETime-SMF119SC_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=scsaetime

         SMF_FIELD SMF119SC_SAEDate-SMF119SC_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DTE,JSON=scsaedate

         SMF_FIELD SMF119SC_SARPort-SMF119SC_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scsarport

         SMF_FIELD SMF119SC_SALPort-SMF119SC_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scsalport

         SMF_FIELD SMF119SC_SAConnID-SMF119SC_SAEvent_Type,TRIPLET=SMF119S1Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=scsaconnid

* --- section via SMF119S2Off ---
         SMF_FIELD SMF119SC_IPFlt_OutAct-SMF119SC_IPFlt_OutAct,TRIPLET=SMF119S2Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scipfltoutact

         SMF_FIELD SMF119SC_IPFlt_InbAct-SMF119SC_IPFlt_OutAct,TRIPLET=SMF119S2Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scipfltinbact

         SMF_FIELD SMF119SC_IPFlt_Rsvd1-SMF119SC_IPFlt_OutAct,TRIPLET=SMF119S2Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scipfltrsvd1

         SMF_FIELD SMF119SC_IPFlt_OutRuleExt-SMF119SC_IPFlt_OutAct,TRIPLET=SMF119S2Off-SMF119LEN,        X
               TYPE=T_CHR8,JSON=scipfltoutruleex

         SMF_FIELD SMF119SC_IPFlt_InRuleExt-SMF119SC_IPFlt_OutAct,TRIPLET=SMF119S2Off-SMF119LEN,        X
               TYPE=T_CHR8,JSON=scipfltinruleext

* --- section via SMF119S3Off ---
         SMF_FIELD SMF119SC_TLS_Prot_Ver-SMF119SC_TLS_Prot_Ver,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sctlsprotver

         SMF_FIELD SMF119SC_TLS_Source-SMF119SC_TLS_Prot_Ver,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=sctlssource

         SMF_FIELD SMF119SC_TLS_Handshake_Type-SMF119SC_TLS_Prot_Ver,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=sctlshandshakety

         SMF_FIELD SMF119SC_TLS_Handshake_Role-SMF119SC_TLS_Prot_Ver,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=sctlshandshakero

         SMF_FIELD SMF119SC_TLS_Rsvd1-SMF119SC_TLS_Prot_Ver,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sctlsrsvd1

         SMF_FIELD SMF119SC_TLS_Session_ID_Len-SMF119SC_TLS_Prot_Ver,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=sctlssessionidle

         SMF_FIELD SMF119SC_TLS_CS_Enc_Alg-SMF119SC_TLS_Prot_Ver,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sctlscsencalg

         SMF_FIELD SMF119SC_TLS_CS_Msg_Auth-SMF119SC_TLS_Prot_Ver,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sctlscsmsgauth

         SMF_FIELD SMF119SC_TLS_CS_Kex_Alg-SMF119SC_TLS_Prot_Ver,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sctlscskexalg

         SMF_FIELD SMF119SC_TLS_FIPS_Mode-SMF119SC_TLS_Prot_Ver,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=sctlsfipsmode

         SMF_FIELD SMF119SC_TLS_CryptoFlags-SMF119SC_TLS_Prot_Ver,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=sctlscryptoflags

         SMF_FIELD SMF119SC_TLS_Rsvd2-SMF119SC_TLS_Prot_Ver,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sctlsrsvd2

         SMF_FIELD SMF119SC_TLS_SCert_Signature_Method-SMF119SC_TLS_Prot_Ver,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sctlsscertsignat

         SMF_FIELD SMF119SC_TLS_SCert_Enc_Method-SMF119SC_TLS_Prot_Ver,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sctlsscertencmet

         SMF_FIELD SMF119SC_TLS_SCert_Digest_Alg-SMF119SC_TLS_Prot_Ver,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sctlsscertdigest

         SMF_FIELD SMF119SC_TLS_Rsvd3-SMF119SC_TLS_Prot_Ver,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=sctlsrsvd3

         SMF_FIELD SMF119SC_TLS_SCert_Serial_Len-SMF119SC_TLS_Prot_Ver,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=sctlsscertserial

         SMF_FIELD SMF119SC_TLS_SCert_Time_Type-SMF119SC_TLS_Prot_Ver,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=sctlsscerttimety

         SMF_FIELD SMF119SC_TLS_SCert_Key_Type-SMF119SC_TLS_Prot_Ver,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sctlsscertkeytyp

         SMF_FIELD SMF119SC_TLS_SCert_Key_Len-SMF119SC_TLS_Prot_Ver,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sctlsscertkeylen

         SMF_FIELD SMF119SC_TLS_CCert_Signature_Method-SMF119SC_TLS_Prot_Ver,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sctlsccertsignat

         SMF_FIELD SMF119SC_TLS_CCert_Enc_Method-SMF119SC_TLS_Prot_Ver,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sctlsccertencmet

         SMF_FIELD SMF119SC_TLS_CCert_Digest_Alg-SMF119SC_TLS_Prot_Ver,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sctlsccertdigest

         SMF_FIELD SMF119SC_TLS_Rsvd4-SMF119SC_TLS_Prot_Ver,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=sctlsrsvd4

         SMF_FIELD SMF119SC_TLS_CCert_Serial_Len-SMF119SC_TLS_Prot_Ver,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=sctlsccertserial

         SMF_FIELD SMF119SC_TLS_CCert_Time_Type-SMF119SC_TLS_Prot_Ver,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=sctlsccerttimety

         SMF_FIELD SMF119SC_TLS_CCert_Key_Type-SMF119SC_TLS_Prot_Ver,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sctlsccertkeytyp

         SMF_FIELD SMF119SC_TLS_CCert_Key_Len-SMF119SC_TLS_Prot_Ver,TRIPLET=SMF119S3Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=sctlsccertkeylen

* --- section via SMF119S4Off ---
         SMF_FIELD SMF119SC_SSH_Prot_Ver-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scsshprotver

         SMF_FIELD SMF119SC_SSH_Source-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scsshsource

         SMF_FIELD SMF119SC_SSH_FIPS_Mode-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scsshfipsmode

         SMF_FIELD SMF119SC_SSH_CryptoFlags-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scsshcryptoflags

         SMF_FIELD SMF119SC_SSH_Rsvd1-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=scsshrsvd1

         SMF_FIELD SMF119SC_SSH_Comp-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_CHR8,JSON=scsshcomp

         SMF_FIELD SMF119SC_SSH_Auth_Method-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scsshauthmethod

         SMF_FIELD SMF119SC_SSH_Auth_Method2-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scsshauthmethod2

         SMF_FIELD SMF119SC_SSH_In_Enc_Alg-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scsshinencalg

         SMF_FIELD SMF119SC_SSH_In_Msg_Auth-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scsshinmsgauth

         SMF_FIELD SMF119SC_SSH_Kex_Method-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scsshkexmethod

         SMF_FIELD SMF119SC_SSH_Out_Enc_Alg-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scsshoutencalg

         SMF_FIELD SMF119SC_SSH_Out_Msg_Auth-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scsshoutmsgauth

         SMF_FIELD SMF119SC_SSH_Rsvd2-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scsshrsvd2

         SMF_FIELD SMF119SC_SSH_SKey_Type-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scsshskeytype

         SMF_FIELD SMF119SC_SSH_SKey_Len-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scsshskeylen

         SMF_FIELD SMF119SC_SSH_CKey_Type-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scsshckeytype

         SMF_FIELD SMF119SC_SSH_CKey_Len-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scsshckeylen

         SMF_FIELD SMF119SC_SSH_SKey_FPLen-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scsshskeyfplen

         SMF_FIELD SMF119SC_SSH_CKey_FPLen-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scsshckeyfplen

         SMF_FIELD SMF119SC_SSH_SCert_Signature_Method-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scsshscertsignat

         SMF_FIELD SMF119SC_SSH_SCert_Enc_Method-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scsshscertencmet

         SMF_FIELD SMF119SC_SSH_SCert_Digest_Alg-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scsshscertdigest

         SMF_FIELD SMF119SC_SSH_Rsvd3-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scsshrsvd3

         SMF_FIELD SMF119SC_SSH_SCert_Serial_Len-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scsshscertserial

         SMF_FIELD SMF119SC_SSH_SCert_Time_Type-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scsshscerttimety

         SMF_FIELD SMF119SC_SSH_SCert_Key_Type-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scsshscertkeytyp

         SMF_FIELD SMF119SC_SSH_SCert_Key_Len-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scsshscertkeylen

         SMF_FIELD SMF119SC_SSH_CCert_Signature_Method-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scsshccertsignat

         SMF_FIELD SMF119SC_SSH_CCert_Enc_Method-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scsshccertencmet

         SMF_FIELD SMF119SC_SSH_CCert_Digest_Alg-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scsshccertdigest

         SMF_FIELD SMF119SC_SSH_Rsvd4-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scsshrsvd4

         SMF_FIELD SMF119SC_SSH_CCert_Serial_Len-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scsshccertserial

         SMF_FIELD SMF119SC_SSH_CCert_Time_Type-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scsshccerttimety

         SMF_FIELD SMF119SC_SSH_CCert_Key_Type-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scsshccertkeytyp

         SMF_FIELD SMF119SC_SSH_CCert_Key_Len-SMF119SC_SSH_Prot_Ver,TRIPLET=SMF119S4Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scsshccertkeylen

* --- section via SMF119S5Off ---
         SMF_FIELD SMF119SC_IPSec_IKETunID-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=scipseciketunid

         SMF_FIELD SMF119SC_IPSec_IKEMajVer-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scipsecikemajver

         SMF_FIELD SMF119SC_IPSec_IKEMinVer-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scipsecikeminver

         SMF_FIELD SMF119SC_IPsec_Rsvd1-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scipsecrsvd1

         SMF_FIELD SMF119SC_IPSec_IKETunLclAuthMeth-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scipseciketunlcl

         SMF_FIELD SMF119SC_IPSec_IKETunRmtAuthMeth-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scipseciketunrmt

         SMF_FIELD SMF119SC_IPSec_IKETunAuthAlg-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scipseciketunaut

         SMF_FIELD SMF119SC_IPSec_IKETunEncAlg-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scipseciketunenc

         SMF_FIELD SMF119SC_IPSec_IKETunDHGroup-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scipseciketundhg

         SMF_FIELD SMF119SC_IPSec_IKETunPseudoRandFunc-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scipseciketunpse

         SMF_FIELD SMF119SC_IPSec_IKETunLifesize-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=scipseciketunlif

         SMF_FIELD SMF119SC_IPSec_IKETunLifetime-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=scipseciketunli2

         SMF_FIELD SMF119SC_IPSec_IKETunReauthIntvl-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=scipseciketunrea

         SMF_FIELD SMF119SC_IPSec_LclCert_Sign_Meth-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scipseclclcertsi

         SMF_FIELD SMF119SC_IPSec_LclCert_Enc_Meth-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scipseclclcerten

         SMF_FIELD SMF119SC_IPSec_LclCert_Digest_Alg-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scipseclclcertdi

         SMF_FIELD SMF119SC_IPsec_Rsvd2-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scipsecrsvd2

         SMF_FIELD SMF119SC_IPSec_LclCert_Serial_Len-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scipseclclcertse

         SMF_FIELD SMF119SC_IPSec_LclCert_Time_Type-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scipseclclcertti

         SMF_FIELD SMF119SC_IPSec_LclCert_Key_Type-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scipseclclcertke

         SMF_FIELD SMF119SC_IPSec_LclCert_Key_Len-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scipseclclcertk2

         SMF_FIELD SMF119SC_IPSec_RmtCert_Sign_Meth-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scipsecrmtcertsi

         SMF_FIELD SMF119SC_IPSec_RmtCert_Enc_Meth-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scipsecrmtcerten

         SMF_FIELD SMF119SC_IPSec_RmtCert_Digest_Alg-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scipsecrmtcertdi

         SMF_FIELD SMF119SC_IPSec_Rsvd3-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scipsecrsvd3

         SMF_FIELD SMF119SC_IPSec_RmtCert_Serial_Len-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scipsecrmtcertse

         SMF_FIELD SMF119SC_IPSec_RmtCert_Time_Type-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scipsecrmtcertti

         SMF_FIELD SMF119SC_IPSec_RmtCert_Key_Type-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scipsecrmtcertke

         SMF_FIELD SMF119SC_IPSec_RmtCert_Key_Len-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scipsecrmtcertk2

         SMF_FIELD SMF119SC_IPSec_TunID-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=scipsectunid

         SMF_FIELD SMF119SC_IPSec_TunFlags-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scipsectunflags

         SMF_FIELD SMF119SC_IPSec_TunType-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scipsectuntype

         SMF_FIELD SMF119SC_IPSec_TunState-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scipsectunstate

         SMF_FIELD SMF119SC_IPSec_Rsvd4-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scipsecrsvd4

         SMF_FIELD SMF119SC_IPSec_EncapMode-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scipsecencapmode

         SMF_FIELD SMF119SC_IPSec_AuthProto-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC1,JSON=scipsecauthproto

         SMF_FIELD SMF119SC_IPSec_AuthAlg-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scipsecauthalg

         SMF_FIELD SMF119SC_IPSec_EncAlg-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scipsecencalg

         SMF_FIELD SMF119SC_IPSec_PFSGroup-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scipsecpfsgroup

         SMF_FIELD SMF119SC_IPSec_Lifesize-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=scipseclifesize

         SMF_FIELD SMF119SC_IPSec_Lifetime-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=scipseclifetime

         SMF_FIELD SMF119SC_IPSec_VPNLifeExpire-SMF119SC_IPSec_IKETunID,TRIPLET=SMF119S5Off-SMF119LEN,        X
               TYPE=T_DEC4,JSON=scipsecvpnlifeex

* --- section via SMF119S6Off ---
         SMF_FIELD SMF119SC_DN_Len-SMF119SC_DN_Len,TRIPLET=SMF119S6Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scdnlen

         SMF_FIELD SMF119SC_DN_Type-SMF119SC_DN_Len,TRIPLET=SMF119S6Off-SMF119LEN,        X
               TYPE=T_DEC2,JSON=scdntype

         SMF_END
