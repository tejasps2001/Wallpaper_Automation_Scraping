#! python3
#! startup.py - Open walllhaven link and download images.

import os
import bs4
import requests
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By

wallsLink = "https://wallhaven.cc/search?categories=111&purity=100&ratios=16x9&sorting=random&order=desc"
home_directory = os.path.expanduser('~')
targetFolder = os.path.join(home_directory, 'Temp')
try:
    os.makedirs(targetFolder)
except:
    pass
invalidSymbols = '\\/:*?"<>|'


def main():
    # Set target folder.
    os.chdir(targetFolder)
    print("Opening browser...")
    browser = webdriver.Firefox()
    browser.get(wallsLink)
    browserWindow = pyautogui.getWindowsWithTitle("Mozilla Firefox")[0]
    browserWindow.minimize()

    # Get the CSS elements of the previews. They contain links to the images.
    imgs_preview = browser.find_elements(By.CLASS_NAME, "preview")
    print("Downloading images... ", end="")
    for img_preview in imgs_preview:
        getImage(img_preview)

    print("Done.")
    print(f'Images in {targetFolder}.')
    browser.close()


def getImage(previewElement):
    imgSite = previewElement.get_attribute("href")

    # Get the wallpaper webpage. If '429 Client Error: Too Many
    # Requests', exit.
    wall = requests.get(imgSite)
    try:
        wall.raise_for_status()
    except:
        return

    soup = bs4.BeautifulSoup(wall.text, "html.parser")

    # Getting the element having the link to full image.
    imgElem = soup.select("#wallpaper")
    # print(str(imgElem))
    imgInfo = imgElem[0].attrs

    # Add https if link doesn't have it.
    if not imgInfo["src"].startswith("https:"):
        imgInfo["src"] = "https:" + imgInfo["src"]
    imgLink = imgInfo["src"]

    # Get name from image's alt.
    imgName = imgInfo["alt"]
    if len(imgName) > 50:
        imgName = imgName[:50] 	

    # Add the extension to the filename.
    imgName += "." + imgLink.rsplit(sep=".", maxsplit=1)[1]

    # Remove invalid symbols from filename.
    for char in invalidSymbols:
        imgName = imgName.replace(char, "_")

    # Get the image.
    img = requests.get(imgLink)
    img.raise_for_status()

    # Write the image to a file.
    with open(imgName, "wb") as imgFile:
        for chunk in img.iter_content(100000):
            imgFile.write(chunk)


# Threading causes HTTPError 429. Rate limiting.
#     downloadThreads = []
#     for i in range(other):
#         downloadThread = threading.Thread(target=dwnldImg, args=[imgs_preview, i])
#         downloadThreads.append(downloadThread)
#         downloadThread.start()

#     # Wait for all threads to end.
#     for downloadThread in downloadThreads:
#         downloadThread.join()

main()
