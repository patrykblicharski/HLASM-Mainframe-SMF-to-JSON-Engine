//SMFEXTRL JOB (DBA),'SMF LOGSTREAM',CLASS=A,MSGCLASS=X
//*
//*-------------------------------------------------------------------*
//* SUMMARY: SMF DATA EXTRACTION FROM LOGSTREAM                       *
//* PURPOSE: EXTRACT RECORDS FROM SYSTEM LOGGER FOR JSON PROCESSING    *
//*-------------------------------------------------------------------*
//* CONFIGURATION
//*-------------------------------------------------------------------*
// SET OUTFILE='IBMUSER.SMF.LOG.FILE'
// SET LSNAME='IFASMF.DEFAULT'           
//*-------------------------------------------------------------------*
//* STEP 0: CLEANUP PREVIOUS OUTPUT FILE
//*-------------------------------------------------------------------*
//DEL      EXEC PGM=IDCAMS
//SYSPRINT DD SYSOUT=*
//SYSIN    DD *
  DELETE &OUTFILE
  SET MAXCC = 0
/*
//*-------------------------------------------------------------------*
//* STEP 1: EXTRACT FROM LOGSTREAM USING IFASMFDL
//*-------------------------------------------------------------------*
//STEP1    EXEC PGM=IFASMFDL
//DUMPOUT  DD  DSN=&OUTFILE,DISP=(NEW,CATLG),UNIT=SYSDA,
//             SPACE=(CYL,(10,10),RLSE),
//             DCB=(RECFM=VBS,LRECL=32760)
//SYSPRINT DD  SYSOUT=*
//SYSIN    DD  *
  LSNAME(&LSNAME,TRUE)
  OUTDD(DUMPOUT,TYPE(30,70,71,72,80,89,101,102))
  /* Optional: Time filter to limit size */
  /* DATE(2026111,2026111) */
  /* START(0800) END(1200)  */
/*
