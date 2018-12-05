# commonsmisc

This repo contains some scripts for using with Commons mobile app, in future maybe other ways too. All scripts reside in https://tools.wmflabs.org/urbanecmbot/commonsmisc/, just append filename. 

## uploadsbyuser.py

This script return a single number representing number of total uploads of certain given user. This includes reuploads of files either uploaded by the same user or by somebody else. 

### Overview
* HTTP method: GET
* Output - single number or nouser when no user was given
* Parameters
  * user - mandatory - string - username of user you want to examine - you can use spaces or underscores, Martin Urbanec and Martin_Urbanec is the same
* Example request: http://tools.wmflabs.org/urbanecmbot/commonsmisc/uploadsbyuser.py?user=Martin%20Urbanec

## feedback.py

This script returns various numbers about certain given user, like number of thanks they received or number of usages of their files at projects of the Wikimedia Foundation. 

### Overview
* HTTP method: GET
* Output - JSON
  * Keys are described below
  * status - string - ok or error, depending on successfullness of the request
  * user - username of the user we're examining (you can use spaces or underscores, Martin Urbanec and Martin_Urbanec is the same)
  * errorCode - string - when status=="error", this described what actually happened, currently it may only be mustpassparams which means that not all mandatory parameters (see below) were passed to the script. 
  * uniqueUsedImages - number - how many images was used in at least one article
  * articlesUsingImages - number - how many times was images uploaded by examined user used
  * thanksReceived - number - how many thanks have the user recieved
  * featuredImages - dictionary - how many images received particular award of Commons users
    * key is category name of the award, value is number of images that are in that category = received that award
  * deletedUploads - number - how many uploads uploaded by examined user was deleted
* Parameters
  * user - mandatory - string - username of user you want to examine (you can use spaces or underscores, Martin Urbanec and Martin_Urbanec is the same)
  * fetch - optional - array; separated by | - values from the output that you want to receive - default value is calculate everything possible
* Example requests
  * Everything about Martin Urbanec: https://tools.wmflabs.org/urbanecmbot/commonsmisc/feedback.py?user=Martin_Urbanec
  * Featured images by Martin Urbanec and how many thanks did he receive: https://tools.wmflabs.org/urbanecmbot/commonsmisc/feedback.py?user=Martin_Urbanec&fetch=featuredImages|thanksReceived
