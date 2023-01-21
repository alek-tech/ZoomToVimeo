# ZoomToVimeo
Python program to download Zoom cloud recordings, save them locally and upload them to a Vimeo Businnes Account.

Description:

ZoomToVimeo is a Python script that uses Zoom's and Vimeo's API to download specific or all cloud recordings from a Zoom Businnes account, 
save them locally and then upload them to a Vimeo Businnes account. All via simple command line inputs.

Download options for Zoom videos include:
 - Selecting specific users or all users.
 - Selecting only recordings made from a certin date forward.
 - Downloading only specific file types for example 'shared_screen_with_speaker_view' from each recording.

Vimeo upload options include:
 - Upload Recordings to specific folder or folders.
--------------------------------------------------------------------------------------

Attention: 

 - You will need Python 3.6 or greater

 - You will require a Zoom Developer account to create a Zoom Server to Server OAUTH app.
   as well as a Vimeo Businnes account to create the correspoding OAUTH app there.

 - If you haven't made the apps already check the links in the reference.txt file for tutorials and guides.
----------------------------------------------------------------------------------------
Important note:

 - Names of recordings uploaded to Vimeo will be cut to 128 characters if longer since this is the Vimeo Video name limit.

 - Strange characters will also be removed from names in order to be able to save them correctly on all platforms.
--------------------------------------------------------------------------------------------
Installation & Setup

1. $ git clone https://github.com/alek-tech/ZoomToVimeo

2. $ cd ZoomToVimeo

3. $ pip3 install -r requirements.txt

4. Open the .env file and add your Zoom and Vimeo credentials between the quotation marks.

5. Open the Main.py file and write the path to the folder where you wish to download the recordings in the following variable:

     DOWNLOAD_DIRECTORY = r'PATH TO FOLDER'

6. Run file with ```sh python Main.py ```
------------------------------------------------------------------------------------------

Usage


The program has 2 main options. "ALL" and "SINGLE".

 - If you want to download and upload zoom recordings from all users of this zoom account type "all" at the 3rd question of the Initial inputs.

 - If you want to download recordings only from specific users, go to the single_users.xlsx file in the directory folder and add the users email under the "Email" cell(column A), 
   one email for each cell. You can also add a Vimeo folder id under the "Folder" cell(column C) if you wish to upload the specific user recordings to an existing Vimeo folder. 


At startup the program gives you 3 options:

 1. If you wish to upload the downloaded recordings in a specific Vimeo folder, type "yes" and provide the folder id which you can see in the Vimeo folder url.( IN THIS CASE THIS HAS PRIORITY)

 2. If you want to download recordings made from a certain date forward. type "yes" and input date.

 3. Choose either "all" or "single" which are the options described above.
--------------------------------------------------------------------------------------------

Other options:

 - If you only want to download the recordings without uploading them to Vimeo, open the Main.py file and comment out the functions all_upload or single_upload 
   depending on which of the 2 options you're gonna be using.
   
 - To download only recordings of specific file types for example 'shared_screen_with_speaker_view', open Functions.py, go to function "get_recordings_files" (around line 125)
   and follow the short instructions on how to enable the file type filter.
--------------------------------------------------------------------------------------------

Bugs: If the scripts is interrupted while a recording is being uploaded, the partial recording will be uploaded and will have to be deleted manually. 

