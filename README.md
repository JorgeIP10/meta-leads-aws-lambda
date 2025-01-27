# Meta leads
This repository implements a way to get leads from a Meta page and send them to a database and to a Gmail account.
## Environment variables
### Meta API variables
|VARIABLE|                 DESCRIPTION                 |
|:-:|:-------------------------------------------:|
|**ACCESS_TOKEN_PAGE**|      Access token for your Meta page.       |
|**URL_BASE**|                API Graph URL                |
|**PAGE_ID**| Id of the facebook page you want to access. |
### Database variables
|       VARIABLE        |                 DESCRIPTION                 |
|:---------------------:|:-------------------------------------------:|
|     **HOSTNAME**      |              Your DB hostname               |
|     **DATABASE**      |              Your DB name                  |
|    **DB_USERNAME**    |                  Your DB user                  |
|    **DB_PASSWORD**    |              Your DB password               |
|       **PORT**        |                  Your DB port                  |
### Use case variables
|          VARIABLE          |                      DESCRIPTION                       |
|:--------------------------:|:------------------------------------------------------:|
|   **GMAIL_SENDER_EMAIL**   |                  Gmail of the sender                   |
| **GMAIL_SENDER_PASSWORD**  |         Password of the sender (app password)          |
| **GMAIL_RECEIVER_EMAIL_X** |       Gmail of the person X receiving the leads        |
|**GMAIL_CONFIRMATION_EMAIL_X**| Gmail of the person X receiving the confirmation email |
