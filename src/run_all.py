"""Run every step in order: download, FishBase, whale budget, animals, figures, page."""
import animals
import download
import figures
import fishbase
import webpage
import whale

if __name__ == "__main__":
    download.main()
    fishbase.main()
    whale.main()
    animals.main()
    figures.main()
    webpage.main()
