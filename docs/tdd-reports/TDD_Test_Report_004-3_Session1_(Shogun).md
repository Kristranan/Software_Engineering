# TDD_Test_Report_004-3_Session1_(Shogun)

| **Feature** | **Expected output** | **Test Case Number** | **Test Case Name** | **Dev** | **Test Date** |
| --- | --- | --- | --- | --- | --- |
| 004-3 | Heat equal to limit: heat_exceeded=False | 1 | Heat equals limit | Shogun | Not recorded |
| 004-3 | Heat above limit: heat_exceeded=True | 2 | Heat above limit | Shogun | Not recorded |
| 004-3 | Freeze equal to limit: freeze_exceeded=False | 3 | Freeze equals limit | Shogun | Not recorded |
| 004-3 | Freeze above limit: freeze_exceeded=True | 4 | Freeze above limit | Shogun | Not recorded |
| 004-3 | Heat exceeded True; freeze at limit False | 5 | Heat and freeze compared independently | Shogun | Not recorded |

Testcase 1 Try heat_s = heat_limit_s expected : heat exceeded => False

Red - Not yet implement comparison.py

![screenshot](images/TDD_Test_Report_004-3_Session1_Shogun_image01.png)

result: 

![screenshot](images/TDD_Test_Report_004-3_Session1_Shogun_image02.png)

Green - Implement comparison.py

![screenshot](images/TDD_Test_Report_004-3_Session1_Shogun_image03.png)

result: 

![screenshot](images/TDD_Test_Report_004-3_Session1_Shogun_image04.png)

Refactor - Not yet need to refactor

Testcase 2 Try heat_s > heat_limit_s expected : heat exceeded => True

Green

![screenshot](images/TDD_Test_Report_004-3_Session1_Shogun_image05.png)

result: 

![screenshot](images/TDD_Test_Report_004-3_Session1_Shogun_image06.png)

Testcase 3 Try freeze_s = freeze_limit_s expected : freeze exceeded => False

Green

![screenshot](images/TDD_Test_Report_004-3_Session1_Shogun_image07.png)

result: 

![screenshot](images/TDD_Test_Report_004-3_Session1_Shogun_image08.png)

Testcase 4 Try freeze_s > freeze_limit_s expected : freeze exceeded => True

Green

![screenshot](images/TDD_Test_Report_004-3_Session1_Shogun_image09.png)

result: 

![screenshot](images/TDD_Test_Report_004-3_Session1_Shogun_image10.png)

Testcase 5 Check if heat_limit_s and freeze_limit_s work separately

Green

![screenshot](images/TDD_Test_Report_004-3_Session1_Shogun_image11.png)

result

![screenshot](images/TDD_Test_Report_004-3_Session1_Shogun_image12.png)
