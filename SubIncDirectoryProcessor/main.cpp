#include <iostream>
#include <fstream>
#include <vector>
#include <list>
#include <stdlib.h>
#include <string.h>
#include <string>
#include <filesystem>	//ISO C++17 Standard

std::string getFileExtension(std::string FilePath) {
	return std::filesystem::path(FilePath).extension().string();
}

bool isMovie(std::string extension) {
	//If no extension return false
	if (extension == "") return false;
	
	//Convert to lowercase
	std::for_each(extension.begin(), extension.end(), [](char& c) {
		c = ::tolower(c);
	});

	if (extension == ".mp4") return true;
	if (extension == ".m4v") return true;
	if (extension == ".mpg") return true;
	if (extension == ".mov") return true;
	if (extension == ".wmv") return true;
	if (extension == ".avi") return true;
	if (extension == ".flw") return true;
	if (extension == ".f4v") return true;
	if (extension == ".webm") return true;
	if (extension == ".mkv") return true;

	return true;
}

void addSubtitlesToAllMovies(const std::list<std::string>& moviesPaths) {
	for (auto& moviePath : moviesPaths) {
		std::string SubIncMainPyFileCommandRun = "py main.py " + moviePath;
		std::system(SubIncMainPyFileCommandRun.c_str());
	}
}

bool checkValidVideoCategory(std::string& givenCategory) {
	//Convert to lowercase
	std::for_each(givenCategory.begin(), givenCategory.end(), [](char& c) {
		c = ::tolower(c);
	});

	std::ifstream categoryFile("config\\validCategories.txt");
	std::string tmpCat;

	if(!categoryFile.good()){
		std::cerr << "File validCategories.txt can't be opened";
		exit(1);
	}

	while (categoryFile) {
		std::getline(categoryFile, tmpCat);
		if (tmpCat == givenCategory) {
			return true;
		}
	}

	return false;
}

void setWorkingPath(const std::string& program_path) {
	std::filesystem::current_path(program_path);
}

int main(int argc, char* argv[]) {
	//Get path of the directory in which this .exe file is located, set working path to that
	std::string program_path = std::filesystem::weakly_canonical(std::filesystem::path(argv[0])).parent_path().string();
	setWorkingPath(program_path);

	//Check if first argument is directory name
	if (argc < 2) {
		std::cerr << "No directory has been passed as command line argument. Check github repo for instructions";
		exit(1);
	}
	
	//Check if a qBittorent category has been passed and if it is a movie one
	if (argc == 3) {
		std::string givenCategory = std::string(argv[2]);
		if (givenCategory.length() && !checkValidVideoCategory(givenCategory)) {
			std::cout << "Category doesn't match with any of validMovieCategories.txt";
			exit(0);
		}
	}

	//Get list of video files in given directory
	std::string mainDirectory(argv[1]);
	std::list<std::string> moviesPaths;

	for (const auto& file : std::filesystem::recursive_directory_iterator(mainDirectory)) {
		std::string filePath = file.path().string();
		if (isMovie(getFileExtension(filePath)))
			moviesPaths.push_back(filePath);
	}

	//If we found any movie run the SubInc.py script for each
	if (moviesPaths.size()) {
		std::cout << "Found " << moviesPaths.size() << " video files. Trying to add subtitles...\n";
		addSubtitlesToAllMovies(moviesPaths);
	}
	//Else show message
	else {
		std::cout << "No video files found.\n";
	}
}