import os
import sys
import glob
import yaml
import pathlib
import SubIncCore


def checkValidQTBCat(given_category: str, known_movie_cats: list, proc_if_none: bool) -> bool:
    if given_category == "":
        if proc_if_none:
            return True
        return False

    if given_category.lower() in known_movie_cats:
        return True
    return False


def getMovieList(file_list: list) -> list:
    known_movie_extensions = [".mp4", ".avi", ".mkv"]
    movie_list = []
    for file in file_list:
        file_extension = pathlib.Path(file).suffix.lower()
        if file_extension in known_movie_extensions:
            movie_list.append(file)
    return movie_list


def loadDirProcSettings() -> dict:
    try:
        with open('config/dirProcessorSettings.yaml') as dp_settings_file:
            dp_settings_dict = yaml.load(dp_settings_file, Loader=yaml.Loader)
            return dp_settings_dict
    except Exception as e:
        print("[-] Could not load dirProcessorSettings.yaml : " + str(e))
        raise Exception("[-] Could not load dirProcessorSettings.yaml : " + str(e))


def main():
    # Get current working dir and app dir
    working_dir: str = os.getcwd()
    app_dir: str = os.path.dirname(os.path.realpath(sys.argv[0]))

    # Check for arguments
    if len(sys.argv) > 1:
        working_dir = sys.argv[1]

    working_dir = os.path.abspath(working_dir)
    print("[+] Working directory : " + working_dir)
    print("[+] App directory : " + app_dir)

    # Load settings after changing cwd
    os.chdir(app_dir)
    dp_pref_dict = loadDirProcSettings()

    # Check if qBittorent Category has been passed and check if it is a movie one
    if len(sys.argv) == 4 and sys.argv[2] == "-qBC":
        given_category = sys.argv[3]
        if not checkValidQTBCat(given_category, dp_pref_dict["accepted_movie_categories"], dp_pref_dict["process_folder_if_category_empty"]) :
            return

    # Get list of video files in working dir
    files_list = glob.glob(working_dir + '/**/*.*', recursive=True)
    movie_list = getMovieList(files_list)

    # If no movies found exit
    if len(movie_list) == 0:
        print("[+] No video files found")
        return

    # Otherwise print count
    print("[+] Found " + str(len(movie_list)) + " movies")

    # Create object
    sdi = SubIncCore.SubDownInc()

    # Process all movies
    for movie in movie_list:
        try:
            sdi.processMovie(movie)
        except Exception as e:
            print("[+] Failed " + movie)


if __name__ == "__main__":
    main()