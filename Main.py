# !/usr/bin/env python3.9
# Program Name: ZoomToVimeo.py

# Description:  ZoomToVimeo is a Python script that uses Zoom and Vimeo's API to download
#               specific or all cloud recordings from a Zoom Businnes account, 
#               save them locally and then upload them to a Vimeo Businnes account. 
#               All via simple command line inputs.

#               This script uses the Server to Server OAUTH app
#               to access the Zoom API and an OAUTH app to access
#               the Vimeo API. 

# Created:      16/1/2023
# Author:       Alessandro Cvetković
# Website:      https://github.com/alek-tech/ZoomToVimeo
# Forked from:  https://github.com/ricardorodrigues-ca/zoom-recording-downloader

# IN THIS SCRIPTS ZOOM MEETINGS ARE CALLED RECORDINGS AND RECORDINGS ARE CALLED FILES.
import requests
import pandas as pd
from datetime import date, timedelta, datetime
from time import sleep
from dotenv import load_dotenv
from Functions import *

# import imaplib
# import ssl
# ctx = ssl.create_default_context()
# ctx.set_ciphers('DEFAULT')
# imapSrc = imaplib.IMAP4_SSL('mail.safemail.it', ssl_context = ctx)

class ZoomToVimeo():

    # CLEAR SCREEN BUFFER
    os.system('cls' if os.name == 'nt' else 'clear')

    # CONNECT TO VIMEO API
    vimeo_connect()

    ########### ADD PATH TO DOWNLOAD FOLDER HERE ###########
    DOWNLOAD_DIRECTORY = r'PATH/TO/FOLDER'

    # COMPLETED DOWNLOADS LOG
    COMPLETED_DOWNLOADS_LOG = os.sep.join([os.path.dirname(os.path.realpath(__file__)), "completed-downloads.log"])
    COMPLETED_DOWNLOADS_IDS = set()
    # COMPLETED UPLOADS LOG
    COMPLETED_UPLOADS_LOG = os.sep.join([os.path.dirname(os.path.realpath(__file__)), "completed-uploads.log"])
    COMPLETED_UPLOADS_IDS = set()

    # DEFAULT RECORDING DATES WE START TO DOWNLOAD FROM (class variables)
    RECORDING_START_YEAR = 2020
    RECORDING_START_MONTH = 1
    RECORDING_START_DAY = 1
    RECORDING_END_DATE = date.today()
    SINGLES_PATH = os.sep.join([os.path.dirname(os.path.realpath(__file__)), "Single_users.xlsx"])

    load_dotenv()

    def __init__(self):
        self.vimeo_token = os.environ.get("vimeo_token")
        self.zoom_token = get_token()
        self.token_expiry = datetime.now() + timedelta(minutes=50)
        self.auth_header = {'Authorization': f'Bearer {self.zoom_token}'}
        self.dates = choose_dates(self)
        self.specific_folder = specific_folder()
        self.load_completed_downloads = load_completed_downloads_ids(self)
        self.load_completed_uploads = load_completed_uploads_ids(self)
        self.correct_foldername = ""


    def all(self):
        #GET USERS EMAILS
        ems = get_all_users(self)
        #LOOP THROUGH EMAILS
        for em in ems: 
            print("\nGetting recordings of user: " + em + "\n")
            sleep(1.1)             
            if user_check(em):       
                vimeo_folder_id = int(user_check(em))
            else:
                vimeo_folder_id = None

            if self.specific_folder != False:
                vimeo_folder_id = int(self.specific_folder)    

            API_ENDPOINT_RECORDING_LIST = 'https://api.zoom.us/v2/users/' + em + '/recordings'
            recordings = []
            # GET INFO OF ALL RECORDINGS(MEETINGS) OF THE CURRENT EMAIL
            # CREATE REQUEST PARAMS FOR EACH REQUEST
            for start, end in dates_gen(date(self.RECORDING_START_YEAR, self.RECORDING_START_MONTH, self.RECORDING_START_DAY), self.RECORDING_END_DATE, timedelta(days=30)):
                post_data = params(start, end, em)
                recs = []
                # REFRESH ZOOM TOKEN IF EXPIRED
                if datetime.now() >= self.token_expiry:
                    while not get_token:
                        sleep(1)
                    else: 
                        print("New Zoom Token recieved. Resetting Token expiry timestamp.")
                        self.token_expiry = datetime.now() + timedelta(minutes=50)
                        pass
                # REQUEST RECORDINGS INFO 
                try:
                    response = requests.get(url=API_ENDPOINT_RECORDING_LIST,headers=self.auth_header, params=post_data)
                except:
                    print("Couldn't get user recordings")
                    exit(1)
                sleep(0.3)
                recordings_data = response.json()

                # APPEND RECORDINGS TO RECS(useful for debugging)
                for rec in recordings_data['meetings']:               
                    recs.append(rec)
                if len(recs) > 0:
                    print("Found",len(recs), "recordings between", start, "and", end)
                else:
                    pass

                # PUT INFO OF EACH RECORDING TO LIST
                recordings.extend(recordings_data['meetings'])

                #LOOP THROUGH RECORDING INFO
                for recording in recordings:
                    print("Recordings")
                    success = False
                    recording_id = recording['uuid']
                    if recording_id in self.COMPLETED_DOWNLOADS_IDS:
                        print("==> Skipping already downloaded recording: ", recording_id)
                        continue
                    # EXTRACT INFO ABOUT EVERY FILE FOUND IN CURRENT RECORDING INCLUDING DOWNLOAD URL
                    rec_files = get_recordings_files(self,recording)
                    # LOOP THROUGH FILES
                    for file_type, file_extension, download_url, recording_type, recording_id, recording_name, recording_date in rec_files: 
                        filename = recording_name + f".{file_extension.swapcase()}"
                        print("rec_files")
                        if recording_type != 'incomplete':
                            # REFRESH ZOOM TOKEN IF EXPIRED
                            if datetime.now() >= self.token_expiry:
                                while not get_token:
                                    sleep(1)
                                else: 
                                    print("New Zoom Token recieved. Resetting Token expiry timestamp.")
                                    self.token_expiry = datetime.now() + timedelta(minutes=50)
                                    # MODIFY DOWNLOAD URL IF NEW TOKEN RECIEVED
                                    for download in recording['recording_files']: 
                                        download_url = download['download_url'] + "?access_token=" + self.zoom_token
                                    pass  
                            # DOWNLOAD FILE
                            success |= download_file(self,download_url, em, filename)

                        else:
                            print("### Incomplete Recording " + filename + "from account " + em)
                            success = False 
                        if success:
                            # if successful, write the ID of this recording to the completed downloads ids
                            with open(self.COMPLETED_DOWNLOADS_LOG, 'a') as log:
                                self.COMPLETED_DOWNLOADS_IDS.add(recording_id)
                                log.write(recording_id)
                                log.write('\n')
                                log.flush()
                            
                            # UPLOAD FILE TO VIMEO
                            if recording_id in self.COMPLETED_UPLOAD_IDS:        
                                print("==> Skipping already uploaded recording: ", recording_id)
                                continue   
                            all_upload(self, em, filename, vimeo_folder_id, recording_id)

                        else:
                            pass
        print("\n*** All done! ***")
                                        
    def single(self):
        #LOOP THROUGH EXCEL FILE WITH EMAIL - FOLDER_ID PAIRS
        df = pd.read_excel(fr"{self.SINGLES_PATH}")#, sheet_name = "Sheet1")
        for i, row in df.iloc[0:].iterrows():    
            sleep(1.1) 
            em = row['Email']
            API_ENDPOINT_RECORDING_LIST = 'https://api.zoom.us/v2/users/' + em + '/recordings'
            try:
                vimeo_folder_id = int(row['Folder'])
            except:
                print("\nMissing Vimeo folder id for ",em, "in", "Single_users.xlsx")
                pass
            if self.specific_folder != False:
                vimeo_folder_id = int(self.specific_folder)
            else:
                vimeo_folder_id = float(row['Folder'])

            print("\nChecking user:", em, "\n")
            recordings = []
            # GET INFO OF ALL RECORDINGS(MEETINGS) OF THE CURRENT EMAIL
            # CREATE REQUEST PARAMS FOR EACH REQUEST
            for start, end in dates_gen(date(self.RECORDING_START_YEAR, self.RECORDING_START_MONTH, self.RECORDING_START_DAY), self.RECORDING_END_DATE, timedelta(days=30)):
                post_data = params(start, end, em)
                recs = []
                # REFRESH ZOOM TOKEN IF EXPIRED
                if datetime.now() >= self.token_expiry:
                    while not get_token:
                        sleep(1)
                    else: 
                        print("New Zoom Token recieved. Resetting Token expiry timestamp.\n")
                        self.token_expiry = datetime.now() + timedelta(minutes=50)
                        pass
                # REQUEST RECORDINGS INFO 
                try:
                    response = requests.get(url=API_ENDPOINT_RECORDING_LIST,headers=self.auth_header, params=post_data)
                except:
                    print("Couldn't get user recordings")
                    exit(1)
                sleep(0.3)
                recordings_data = response.json()

                # APPEND RECORDINGS TO RECS(useful for debugging)
                for rec in recordings_data['meetings']:               
                    recs.append(rec)
                if len(recs) > 0:
                    print("Found",len(recs), "recordings between", start, "and", end)
                else:
                    pass

                # PUT INFO OF EACH RECORDING TO LIST
                recordings.extend(recordings_data['meetings'])

                #LOOP THROUGH RECORDING INFO
                for recording in recordings:
                    success = False
                    recording_id = recording['uuid']
                    if recording_id in self.COMPLETED_DOWNLOADS_IDS:
                        print("==> Skipping already downloaded recording: ", recording_id)
                        continue
                    # EXTRACT INFO ABOUT EVERY FILE FOUND IN CURRENT RECORDING INCLUDING DOWNLOAD URL
                    rec_files = get_recordings_files(self, recording)
                    # LOOP THROUGH FILES
                    for file_type, file_extension, download_url, recording_type, recording_id, recording_name, recording_date in rec_files: 
                        filename = recording_name + f".{file_extension.swapcase()}"
                        if recording_type != 'incomplete':
                            # REFRESH ZOOM TOKEN IF EXPIRED
                            if datetime.now() >= self.token_expiry:
                                while not get_token:
                                    sleep(1)
                                else: 
                                    print("New Zoom Token recieved. Resetting Token expiry timestamp.")
                                    self.token_expiry = datetime.now() + timedelta(minutes=50)
                                    # MODIFY DOWNLOAD URL IF NEW TOKEN RECIEVED
                                    for download in recording['recording_files']: 
                                        download_url = download['download_url'] + "?access_token=" + self.zoom_token
                                    pass  
                            # DOWNLOAD FILE
                            success |= download_file(self,download_url, em, filename)
                        else:
                            print("### Incomplete Recording " + filename + "from account " + em)
                            success = False 

                        if success:
                            # if successful, write the ID of this recording to the completed downloads ids
                            with open(self.COMPLETED_DOWNLOADS_LOG, 'a') as log:
                                self.COMPLETED_DOWNLOADS_IDS.add(recording_id)
                                log.write(recording_id)
                                log.write('\n')
                                log.flush()
                            # UPLOAD FILE TO VIMEO   
                            if recording_id in self.COMPLETED_UPLOAD_IDS:        
                                print("==> Skipping already uploaded recording: ", recording_id)
                                continue          
                            single_upload(self, em, filename, vimeo_folder_id, recording_id)
                        else:
                            pass
        print("\n*** All done! ***")

if __name__ == "__main__":
    try:
        start = ZoomToVimeo()  
        start_program(start)
    except KeyboardInterrupt:
        print("\nSIGINT or CTRL-C detected. Exiting gracefully.")
        raise(SystemExit)
    
        

 
