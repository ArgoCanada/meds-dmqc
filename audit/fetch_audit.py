
import ftplib

### get latest DOXY audit
audit_file = 'ftp.mbari.org'
ftp = ftplib.FTP(audit_file)
ftp.login()
ftp.cwd('pub/BGC_argo_audits/DOXY/meds')
fn = ftp.nlst()[0]
lf = open(fn, 'wb')
ftp.retrbinary('RETR ' + fn, lf.write)
lf.close()