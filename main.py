import requests
import datetime
import os
import sys
import json
import movieHashCalculator


def loginToOpenSubtitles(api_key: str, uname: str, upass: str):
    login_url = 'https://api.opensubtitles.com/api/v1/login'
    login_headers = {"Api-Key": api_key, "Content-Type": "application/json"}
    login_payload = {"username": uname, "password": upass}

    login_response = requests.post(url=login_url, headers=login_headers, data=json.dumps(login_payload))
    if login_response.status_code != 200:
        raise Exception("Auth Error OpenSubtitles.com :" + str(login_response.status_code))

    return login_response.json()["token"]


def searchForSubtitles(api_key: str, file_name: str, movie_hash: str, language: str):
    search_url = "https://api.opensubtitles.com/api/v1/subtitles"
    search_headers = {"Api-Key": api_key, "Content-Type": "application/json"}
    search_query = {"query": file_name, "moviehash": movie_hash, "languages": language}

    search_response = requests.get(search_url, headers=search_headers, params=search_query)

    if search_response.status_code != 200:
        raise Exception("Search error :" + str(search_response.status_code))

    if search_response.json()["total_count"] == 0:
        return False, 0

    return True, int(search_response.json()["data"][0]["attributes"]["files"][0]["file_id"])


def getDownloadLink(api_key: str, subtitle_id: int):
    dwn_url = "https://api.opensubtitles.com/api/v1/download"
    dwn_headers = {"Api-Key": api_key, "Content-Type": "application/json"}
    dwn_payload = {"file_id": subtitle_id}

    dwn_response = requests.post(dwn_url, headers=dwn_headers, data=json.dumps(dwn_payload))

    if dwn_response.status_code != 200:
        raise Exception("Download link get error :" + str(dwn_response.status_code))

    return dwn_response.json()["link"]


def getDownloadLinkAuthUser(token: str, subtitle_id: int):
    dwn_url = "https://api.opensubtitles.com/api/v1/download"
    dwn_headers = {"Authorization": "Bearer ", "Content-Type": "application/json"}
    dwn_payload = {"file_id": subtitle_id}

    dwn_response = requests.post(dwn_url, headers=dwn_headers, data=json.dumps(dwn_payload))

    if dwn_response.status_code != 200:
        raise Exception("Download link get error :" + str(dwn_response.status_code))

    return dwn_response.json()["link"]

def getSubtitleReady(dir_path: str, file_name: str, full_file_path: str, language: str, use_bearer_auth: bool):
    # Read credentials from auth.json
    with open('config\\auth.json') as auth_file:
        auth_settings = json.load(auth_file)
    api_key = auth_settings["api-key"]
    uname = auth_settings["username"]
    upass = auth_settings["password"]


    # Get hash of the movie
    mvhash = movieHashCalculator.hashFile(full_file_path)

    # Search for subtitle
    subtitle_id = -1
    response_1 = searchForSubtitles(api_key, file_name, mvhash, language)  # Try for name and hash
    response_2 = searchForSubtitles(api_key, "", mvhash, language)  # Try for hash only
    response_3 = searchForSubtitles(api_key, file_name, "", language)  # Try for name only

    if response_1[0]:
        subtitle_id = response_1[1]
    elif response_2[0]:
        subtitle_id = response_2[1]
    elif response_3[0]:
        subtitle_id = response_3[1]

    if subtitle_id == -1:
        raise Exception("Couldn't find subtitle for movie " + file_name + " (hash : " + mvhash + ")")


    # Get subtitle download link
    if use_bearer_auth:
        # Login to OpenSubtitles
        try:
            token = loginToOpenSubtitles(api_key, uname, upass)
            dwn_link = getDownloadLinkAuthUser(token, subtitle_id)
        except:
            print("Auth not working - using simple app API-KEY")
            dwn_link = getDownloadLink(api_key, subtitle_id)
    else:
        dwn_link = getDownloadLink(api_key, subtitle_id)

    # Download subtitle and save it in the save directory as the movie
    response = requests.get(dwn_link)
    if response.status_code != 200:
        raise Exception("Error at downloading link " + dwn_link)
    subtitle_full_path = dir_path + file_name + "_SUB_" + language + ".srt"
    open(subtitle_full_path, "wb").write(response.content)
    return subtitle_full_path


def softcodeSubtitle(mkvmerge_file_path, movie_file_path, subtitle_file_path, final_file_path):
    command = mkvmerge_file_path + ' --output \"' + final_file_path + '\" \"' + movie_file_path + '\" \"' + subtitle_file_path + '\"'
    os.system(command)


def deleteOriginal(original_filePath, new_filePath):
    os.remove(original_filePath)
    os.renames(new_filePath, original_filePath)


def main():
    # Import settings
    try:
        with open('config\\settings.json') as settings_file:
            user_settings = json.load(settings_file)
    except:
        print("Eroare - fisierul config\\settings.json nu a putut fi deschis")
        exit(1)

    mkvmerge_file_path = user_settings["mkvmerge-path"]
    languages = user_settings["languages"]
    delete_original_movie_after_task = user_settings["replace-original-file-after-task-done"]
    delete_srt_file_after_task = user_settings["delete-subtitle-file-after-task-done"]
    prefix_for_subtitled_movie = user_settings["subtitled_movie_prefix"]
    use_bearer_auth = user_settings["use-bearer-auth"]

    # Get filename, path, extension
    if len(sys.argv) != 2:
        print("You have to specify the filename as command line argument. Check Github repo for instructions")
        exit(1)
    full_path_movie = sys.argv[1]
    parts = os.path.split(full_path_movie)
    dir_path = parts[0] + "\\"
    movie_name_with_extension = parts[1]
    movie_name = movie_name_with_extension[:len(movie_name_with_extension)-4]

    try:
        full_path_subtitle = getSubtitleReady(dir_path, movie_name, full_path_movie, languages, use_bearer_auth)
        full_path_subtitled_movie = dir_path + prefix_for_subtitled_movie + movie_name_with_extension
        softcodeSubtitle(mkvmerge_file_path, full_path_movie, full_path_subtitle, full_path_subtitled_movie)

        if delete_original_movie_after_task:
            deleteOriginal(full_path_movie, full_path_subtitled_movie)
        if delete_srt_file_after_task:
            os.remove(full_path_subtitle)
    except Exception as e:
        print(str(e))
        with open("files_error_log", "a") as log:
            log.write("\n\n")
            log.write(datetime.datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)") + "\n")
            log.write(full_path_movie + " - " + str(e))
            exit(1)


if __name__ == "__main__":
    main()
