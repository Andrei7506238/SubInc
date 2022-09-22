import requests
import datetime
import os
import sys
import json
import movieHashCalculator


class SubDownInc:
    # Settings dictionary
    settings_dict: dict
    auth_dict: dict

    # Settings
    language: str
    mkvmerge_file_path: str
    log_file_path: str
    prefix_for_subtitled_movie: str
    bool_delete_original_movie_after_task: bool
    bool_delete_srt_file_after_task: bool
    bool_softcode_subtitle: bool
    bool_use_bearer_auth: bool

    # Auth
    api_key = ""
    uname = ""
    upass = ""
    user_token = ""

    def loadSettings(self):
        self.mkvmerge_file_path = self.settings_dict["mkvmerge-path"]
        self.language = self.settings_dict["languages"]
        self.bool_delete_original_movie_after_task = self.settings_dict["replace-original-file-after-task-done"]
        self.bool_delete_srt_file_after_task = self.settings_dict["delete-subtitle-file-after-task-done"]
        self.prefix_for_subtitled_movie = self.settings_dict["subtitled_movie_prefix"]
        self.bool_use_bearer_auth = self.settings_dict["use-bearer-auth"]
        self.log_file_path = self.settings_dict["error-file_path"]
        self.bool_softcode_subtitle = self.settings_dict["softcode_subtitle"]

    def loadAuth(self):
        self.api_key = self.auth_dict["api-key"]
        self.uname = self.auth_dict["username"]
        self.upass = self.auth_dict["password"]

    def __init__(self, arg_settings: dict = None, arg_auth: dict = None):
        self.settings_dict = arg_settings
        self.auth_dict = arg_auth

        #Read settings from file if they weren't provided
        if arg_settings is None:
            try:
                with open('config\\settings.json') as settings_file:
                    self.settings_dict = json.load(settings_file)
            except Exception as e:
                self.saveErrorsToLog(e, " INIT ERROR")

        if arg_auth is None:
            try:
                with open('config\\auth.json') as auth_file:
                    self.auth_dict = json.load(auth_file)
            except Exception as e:
                self.saveErrorsToLog(e, " INIT ERROR")

        self.loadSettings()
        self.loadAuth()

        # Try to log if bearer auth is set true
        try:
            if self.bool_use_bearer_auth:
                self.user_token = self.loginToOpenSubtitles()
            else:
                print("Using simple API-KEY auth ")
        except Exception as e:
            print("Auth not working - using simple API-KEY auth - " + str(e))

    def saveErrorsToLog(self, error: Exception, full_path_movie: str):
        error_msg = str(error)
        print(error_msg)
        if len(self.log_file_path):
            with open(self.log_file_path, "a") as log:
                log.write("\n\n")
                log.write(datetime.datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)") + "\n")
                log.write(full_path_movie + " : " + error_msg)
                raise error

    def loginToOpenSubtitles(self) -> str:
        login_url = 'https://api.opensubtitles.com/api/v1/login'
        login_headers = {"Api-Key": self.api_key, "Content-Type": "application/json"}
        login_payload = {"username": self.uname, "password": self.upass}

        login_response = requests.post(url=login_url, headers=login_headers, data=json.dumps(login_payload))
        if login_response.status_code != 200:
            raise Exception("Auth Error OpenSubtitles.com :" + str(login_response.status_code))

        return login_response.json()["token"]

    def searchForSubtitles(self, file_name: str, movie_hash: str) -> int:
        search_url = "https://api.opensubtitles.com/api/v1/subtitles"
        search_headers = {"Api-Key": self.api_key, "Content-Type": "application/json"}
        search_query = {"query": file_name, "moviehash": movie_hash, "languages": self.language}

        search_response = requests.get(search_url, headers=search_headers, params=search_query)

        if search_response.status_code != 200 or search_response.json()["total_count"] == 0:
            raise Exception("Couldn't find subtitle for movie " + file_name + " (hash : " + movie_hash + ")")

        return int(search_response.json()["data"][0]["attributes"]["files"][0]["file_id"])

    def getDownloadLink(self, subtitle_id: int):
        dwn_url = "https://api.opensubtitles.com/api/v1/download"
        if self.bool_use_bearer_auth:
            dwn_headers = {"Api-Key": self.api_key, "Authorization": "Bearer " + self.user_token,
                           "Content-Type": "application/json"}
        else:
            dwn_headers = {"Api-Key": self.api_key, "Content-Type": "application/json"}
        dwn_payload = {"file_id": subtitle_id}

        dwn_response = requests.post(dwn_url, headers=dwn_headers, data=json.dumps(dwn_payload))

        if dwn_response.status_code != 200:
            raise Exception("Download link get error :" + str(dwn_response.status_code))

        return dwn_response.json()["link"]

    def downloadAndSaveSubtitle(self, dwn_link: str, full_path_subtitle: str):
        response = requests.get(dwn_link)
        if response.status_code != 200:
            raise Exception("Error at downloading link " + dwn_link)
        open(full_path_subtitle, "wb").write(response.content)

    def softcodeSubtitle(self, movie_file_path: str, subtitle_file_path: str, final_file_path: str):
        command = self.mkvmerge_file_path + ' --output \"' + final_file_path + '\" \"' + movie_file_path + '\" \"' + subtitle_file_path + '\"'
        os.system(command)

    def replaceOriginal(self, original_filePath, new_filePath):
        os.remove(original_filePath)
        os.renames(new_filePath, original_filePath)

    def processMovie(self, full_path_movie: str):
        # Break full_path_movie into components
        parts = os.path.split(full_path_movie)
        dir_path = parts[0] + "\\"
        movie_name_with_extension = parts[1]
        movie_name = movie_name_with_extension[:len(movie_name_with_extension) - 4]

        # Generate final movie name
        full_path_subtitled_movie = dir_path + self.prefix_for_subtitled_movie + movie_name_with_extension

        try:
            # Generate movie hash
            movie_hash = movieHashCalculator.hashFile(full_path_movie)
            # Get subtitle id
            subtitle_id = self.searchForSubtitles(movie_name, movie_hash)
            # Get download link
            dwn_link = self.getDownloadLink(subtitle_id)

            # Download subtitle and write it in the same dir as movie
            full_path_subtitle = dir_path + movie_name + self.prefix_for_subtitled_movie + self.language + ".srt"
            self.downloadAndSaveSubtitle(dwn_link, full_path_subtitle)

            # If there is no need for softcoding exit now
            if not self.bool_softcode_subtitle:
                return

            # Softcode subtitle into movie
            self.softcodeSubtitle(full_path_movie, full_path_subtitle, full_path_subtitled_movie)

            # Replace original movie
            if self.bool_delete_original_movie_after_task:
                self.replaceOriginal(full_path_movie, full_path_subtitled_movie)

            # Delete subtitle file
            if self.bool_delete_srt_file_after_task:
                os.remove(full_path_subtitle)

        except Exception as e:
            self.saveErrorsToLog(e, full_path_movie)


def main():
    # Get filename argument
    if len(sys.argv) < 2:
        print("You have to specify the filename as command line argument. Check Github repo for instructions")
        exit(1)
    if len(sys.argv) > 2:
        print("Put path with spaces between double quotes")
        exit(1)
    full_path_movie = sys.argv[1]

    # Create object
    sdi = SubDownInc()
    sdi.processMovie(full_path_movie)


if __name__ == "__main__":
    main()
