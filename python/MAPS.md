# SMF2JSON — implemented maps

Inventory of record types and subtypes currently registered in `smf2json/maps`.

| Type | Subtype | Description |
|------|---------|-------------|
| **14** | — | INPUT / RDBACK data set activity (non-VSAM) |
| **15** | — | OUTPUT / UPDAT / INOUT / OUTIN data set activity (non-VSAM) |
| **17** | — | Scratch data set status |
| **30** | **1** | Common address space work — job initiation |
| **30** | **2** | Common address space work — interval |
| **30** | **3** | Common address space work — step or interval termination |
| **30** | **4** | Common address space work — step total |
| **30** | **5** | Common address space work — job termination |
| **30** | **6** | Common address space work — system address space |
| **42** | **20** | DFSMS — STOW Initialize |
| **42** | **21** | DFSMS — Member Delete |
| **42** | **22** | DFSMS — DFSMSrmm audit records |
| **42** | **23** | DFSMS — DFSMSrmm security records |
| **42** | **24** | DFSMS — Member add/replace |
| **42** | **25** | DFSMS — Member rename |
| **61** | — | ICF DEFINE activity |
| **65** | — | ICF DELETE activity |
| **66** | — | ICF ALTER activity |
| **80** | — | RACF processing (z/OS 3.1 fixed + relocate; no SMFxSTY — discriminate by `SMF80EVT`) |
| **89** | — | Usage data (header subset) |
| **119** | **1** | TCP/IP — TCP connection initiation |
| **119** | **2** | TCP/IP — TCP connection termination |
| **119** | **3** | TCP/IP — FTP client transfer completion |
| **119** | **4** | TCP/IP — profile event (NMTP **partial**) |
| **119** | **5** | TCP/IP — TCP/IP statistics |
| **119** | **6** | TCP/IP — interface statistics |
| **119** | **7** | TCP/IP — server port statistics |
| **119** | **8** | TCP/IP — stack start/stop |
| **119** | **10** | TCP/IP — UDP endpoint close |
| **119** | **11** | TCP/IP — zERT connection detail |
| **119** | **12** | TCP/IP — zERT summary |
| **119** | **20** | TCP/IP — TN3270E server session initiation |
| **119** | **21** | TCP/IP — TN3270E server session termination |
| **119** | **22** | TCP/IP — TSO Telnet client initiation |
| **119** | **23** | TCP/IP — TSO Telnet client termination |
| **119** | **24** | TCP/IP — TN3270E Telnet profile |
| **119** | **32** | TCP/IP — DVIPA status change |
| **119** | **33** | TCP/IP — DVIPA removed |
| **119** | **34** | TCP/IP — DVIPA target added |
| **119** | **35** | TCP/IP — DVIPA target removed |
| **119** | **36** | TCP/IP — DVIPA target server started |
| **119** | **37** | TCP/IP — DVIPA target server ended |
| **119** | **38** | TCP/IP — SMC-D link statistics |
| **119** | **39** | TCP/IP — SMC-D link start |
| **119** | **40** | TCP/IP — SMC-D link end |
| **119** | **41** | TCP/IP — SMC-R link group statistics |
| **119** | **42** | TCP/IP — SMC-R link start |
| **119** | **43** | TCP/IP — SMC-R link end |
| **119** | **44** | TCP/IP — RNIC statistics |
| **119** | **45** | TCP/IP — ISM statistics |
| **119** | **48** | TCP/IP — CSSMTP configuration |
| **119** | **49** | TCP/IP — CSSMTP connection |
| **119** | **50** | TCP/IP — CSSMTP mail message |
| **119** | **51** | TCP/IP — CSSMTP JES spool |
| **119** | **52** | TCP/IP — CSSMTP statistics |
| **119** | **70** | TCP/IP — FTP server transfer completion |
| **119** | **71** | TCP/IP — FTPD configuration |
| **119** | **72** | TCP/IP — FTP server logon failure |
| **119** | **73** | TCP/IP — IKE tunnel activation / refresh |
| **119** | **74** | TCP/IP — IKE tunnel deactivation / expire |
| **119** | **75** | TCP/IP — Dynamic tunnel activation / refresh |
| **119** | **76** | TCP/IP — Dynamic tunnel deactivation |
| **119** | **77** | TCP/IP — Dynamic tunnel added |
| **119** | **78** | TCP/IP — Dynamic tunnel removed |
| **119** | **79** | TCP/IP — Manual tunnel activation |
| **119** | **80** | TCP/IP — Manual tunnel deactivation |
| **119** | **81** | TCP/IP — VTAM 3270 IDS |

**Not mapped (known gaps):** SMF 119 subtypes **94–98** (OpenSSH, no layouts); 119-4 NMTP sections beyond the partial set (PORT/INTF/route/IPSec/…).
