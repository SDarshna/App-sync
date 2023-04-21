# App-sync
Syncing custom Apps between Prisma Access and Prisma SDWAN

This script is used to sync the custom apps from Prisma Access to Prisma SDWAN. This script can be used as a cron job to sync the custom apps on a periodic basis. Script has the logic to identify the already synced apps from Prisma Access to Prisma SDWAN via the "tag" option of the SDWAN application.

**Note: A custom application can be defined with more options on the Prisma Access end including regex pattern matches, qualifiers which is not supported by Prisma SDWAN. In such a case the Prisma SDWAN application is created if a Prisma Access custom app is defined with a domain match in the following contexts:
"http-req-host-header", "http-req-headers", "ssl-req-chello-sni","ssl-rsp-certificate" . Also a qualifier or a regex pattern match additionally can be defined in the PA config which cannot be applied at Prisma SDWAN. Hence the policies may need to be fine tuned at Prisma SDWAN end to accomodate the stricter app match.

Usage: 
The script can be used in a cron job for a periodic sync between Prisma Access and Prisma SDWAN.
A one time execution of the script gives the following output:

Prompt>./custom_app_sync.py
Apps successfully replicated from Prisma Access to Prisma SDWAN: ['alvisofin-peoplesoft', 'sharepoint-online-delete', 'Meta']
Apps replicated from Prisma Access to Prisma SDWAN with reduced configuration : ['sharepoint-online-delete', 'Meta', 'alvisofin-peoplesoft']

In the above output: 
Apps successfully replicated from Prisma Access to Prisma SDWAN >>>>> Indicate the name of the applications which were synced from PA to P-SDWAN during teh current sync.
Apps replicated from Prisma Access to Prisma SDWAN with reduced configuration : >>>>>>>>>> Indicates the list of applications which have got synced from PA to P-SDWAN but without finer config options due to limited functionality at the P-SDWAN end.


