select log_title
from logging
where

/* Only uploads */
log_type="upload"
and log_action="upload"

/* Only mobile uploads */
and log_title in (select page_title from categorylinks join page on page_id=cl_from where cl_to="Uploaded_with_Mobile/Android")

/* Timeframe settings */
and log_timestamp > "20171101000000" and log_timestamp < "20190801000000";
