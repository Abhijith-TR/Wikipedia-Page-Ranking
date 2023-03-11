import random
import re
import pickle
import bz2
import matplotlib.pyplot as plt

# Global variable to store the number of pages
numberOfPages = 0
# File in which the graph will be stored
graphFile = open('pickleGraph.pkl', 'wb')
# Input file (wikidump)
mainFile = ""
# mainFile = bz2.open('enwiki-latest-pages-articles.xml.bz2', 'rb')

def findLinksBinary(title, textContent):
    # Making this local slows program down by a factor of 2
    global graphFile
    # Extracting the title only
    wikiTitle = re.search(r"<title>(.*)</title>", title)
    # Selecting the group from the regex above
    wikiTitle = wikiTitle.group(1)
    # Selecting titles without non-alphanumeric characters (e.g. 30px, File:, Category:)
    for char in wikiTitle:
        # The title should not contain non alphanumeric or space characters
        if (char.isalnum() == False and char.isspace() == False): return
    # Appending a space to the end
    wikiTitle += " "
    # Inserting into the file
    pickle.dump(wikiTitle, graphFile)
    # Extracting the links of the form [[ content | alias1 | alias2 ]]
    links = re.findall("\[\[([\w\s\|\:]*?)\]\]", textContent)
    # Initialize an empty list of links
    listOfLinks = []
    # Iterate through the links
    for link in links:
        # Removing non standard links (e.g. File:, Category:, 30px:)
        if (":" in link):
            continue
        # If the link contains multiple aliases
        if "|" in link:
            # Select the content using lazy regex
            smallerLink = re.search("([\w\s]*?)\|(.*)", link)
            # Select the first matched group
            smallerLink = smallerLink.group(1)
            # append link to list of links
            listOfLinks.append(smallerLink)
        else:
            # append link to list of links
            listOfLinks.append(link)
    # dump list of links into the file
    pickle.dump(listOfLinks, graphFile)
    # Increment the global counter for numberOfPages by 1
    global numberOfPages
    numberOfPages += 1

def createAdjacencyList():
    # get all the files required in the function
    global graphFile
    global mainFile
    # to indicate what part of the file we are in
    flag = 0
    # to store the title of the page
    title = ""
    # to store the content of a particular page
    textContent = ""
    # try-except set up so that when the lines run out, an exception is triggered and the loop breaks
    try:
        while (True):
            # read one line at a time from the bz2 file
            content = mainFile.readline()
            # copy the content to convert to str
            string = content
            # convert the byte stream from the file into string
            string = content.decode("utf-8")
            # the only case when this happens is the string being '\n'
            if (len(string) == 1): 
                # if newline do not add to the content that you need to read
                continue
            # remove spaces from the string
            string.strip()
            # if flag == 0 and string is a title, a new page has begun. Set flag = 1 and wait for text section
            if (flag == 0 and '<title>' in string):
                # Set flag to 1 to indicate that we are waiting for text
                flag = 1
                # Set the title to be the current line
                title = string
            # if flag == 1 and <text> is encountered, the actual content of the detected page has begun. Set flag = 2
            elif (flag == 1 and "<text" in string):
                # Set flag to 2 to indicate that we are now in the text section
                flag = 2
                # Add the current line to the text section of the page
                textContent += string
            # if flag == 2 and </text is not detected, the text section from the detected page is still going on. Keep reading lines and adding them to textContent
            elif (flag == 2 and "</text" not in string):
                # Add the current line to the text section of the page
                textContent += string
            # if flag == 2 and </text is detected, the page is over. Call findLinksBinary to perform its function
            # clear title and textContent and set flag == 0 to indicate that you are waiting for the next page
            elif (flag == 2 and "</text>" in string):
                # Extract the title and links and store them in the file
                findLinksBinary(title, textContent)
                # clear the title and content for the next time that you read it
                title = ""
                textContent = ""
                # set the flag to 0 to indicate that you are waiting for the next title
                flag = 0
    # the exception is triggered when you run out of content in the file
    except Exception as inst:
        pass
    # once the exception has been dealt with, close all the files that you used in the function
    finally:
        mainFile.close()
        graphFile.close()

# Function to initialize a dictionary of frequencies set to 0
# NOTE - Frequency refers to the number of visits
def initializeFrequencies():
    # Open the file which contains the dictionary of cursor positions in the big file
    positionFile = open('keyPositionDict.txt', 'rb')
    # Read the dictionary from the file into main memory
    keyPositionDict = pickle.load(positionFile)
    # Get a list of all the pages that contain cursors in the dictionary
    listOfPages = list(keyPositionDict.keys())
    # Dictionary to hold the frequencies of all the pages
    freqCount = {}
    # Iterate through all the page names that you find
    for page in listOfPages:
        # Set the initial visit count of all pages to 0
        freqCount[page] = 0
    # Close the file
    positionFile.close()
    # Return the objects that were created in the function
    return listOfPages, freqCount, keyPositionDict

# Function to perform the random walk
def randomWalk(numberOfSteps):
    # Get all the required objects from the function described above
    listOfPages, freqCount, keyPositionDict = initializeFrequencies()
    # Open the file where you will store the frequencies
    frequencyFile = open('frequencyDict.txt', 'wb')
    # Open the file that contains the adjacency list
    fileName = open('pickleGraph.pkl', 'rb')

    # Pick a random page as the starting page
    currentPage = random.choice(listOfPages)
    # Start the random walk
    for i in range(numberOfSteps):
        # If somehow you find a page that you do not have in the adjacency list
        if (currentPage not in freqCount):
            # Initialize the count of that page to 0
            freqCount[currentPage] = 0
        # If you find a page that is not there in the adjacency list
        if (currentPage not in keyPositionDict):
            # Randomly pick another page and teleport there
            currentPage = random.choice(listOfPages).strip(' ').lower()
            # Repeat the current step from the newly selected node
            i-=1
            continue
        else:
            # Increment the frequency of the page by 1
            freqCount[currentPage] += 1
            # Go to the position of the list of links of currentPage in the big file
            fileName.seek(keyPositionDict[currentPage], 0)
            # Fetch the list of links of currentPage from the file
            content = pickle.load(fileName)
            # Consider pages that are redirects. If a redirecting page is detected, pick a random node and teleport there
            # Also considers the unusual condition of two pages that only point to each other to prevent loops
            if (len(content) <= 5):
                # Pick a random page and teleport there and start the next iteration from that page instead
                currentPage = random.choice(listOfPages).strip(' ').lower()
                continue
            # If the page has a sufficient number of links, pick a random link from among them
            nextPage = random.choice(content)
            # Convert the name to lowercase as all the link names are in lowercase in the cursor position dictionary
            currentPage = nextPage.strip(' ').lower()

    # Dump the frequency count into a file for later use
    pickle.dump(freqCount, frequencyFile)
    # Close all the files that you used in the function
    frequencyFile.close()
    fileName.close()

# Function to display the top k pages
def displayTop(k):
    # Open the file that contains the dictionary with all the frequencies
    frequencyFile = open('frequencyDict.txt', 'rb')
    # Load the dictionary into main memory
    theFrequencies = pickle.load(frequencyFile)
    # Get a list of all the keys from the dictionary
    listOfKeys = list(theFrequencies.keys())
    # Sort all the keys in the decreasing order of number of visits
    listOfKeys.sort(key = lambda x : theFrequencies[x], reverse=True)
    # Iterate through the first k elements of the list
    for i in range(k):
        # Print the key and the number of visits that the page has had
        print(listOfKeys[i].upper(),"-", theFrequencies[listOfKeys[i]])
    # Close the file that was opened in the function
    frequencyFile.close()

# Function to give a plot of the number of visits (on x axis) v/s number of nodes (on y axis)
def plotFrequencies():
    # Open the file that contains the frequency dictionary
    frequencyFile = open('frequencyDict.txt', 'rb')
    # Load the dictionary into main memory
    theFrequencies = pickle.load(frequencyFile)
    # Get a list of all the keys from the dictionary
    listOfKeys = list(theFrequencies.keys())
    # Sort the keys in the decreasing order of frequencies
    listOfKeys.sort(key = lambda x : theFrequencies[x], reverse=True)
    # X stores the number of visits
    x = []
    # Y stores the number of keys
    y = []
    # Iterate maximum frequency + 1 times
    for i in range(theFrequencies[listOfKeys[0]]+1):
        # Append the number of visits to the x axis
        x.append(i)
        # Append the number of pages with these visits to the y axis
        y.append(0)
    # Go through dictionary that contains all the frequencies
    for i in theFrequencies:
        # Increment the corresponding value from the list of frequencies that you have
        y[theFrequencies[i]] += 1
    # Plot the graph
    plt.plot(x, y)
    # Set the x label
    plt.xlabel('Number of Visits')
    # Set the y label
    plt.ylabel('Number of Pages')
    # Display the graph
    plt.show()

# function to fetch the links corresponding to a given page
def fetchLinks(pageName):
    # Convert the page name to lowercase
    pageName = pageName.lower()
    # Open the file with the cursor positions
    positionFile = open('keyPositionDict.txt', 'rb')
    # Open the file with the adjacency list
    theGraph = open('pickleGraph.pkl', 'rb')
    # Load dictionary of cursor positions into main memory
    cursorDictionary = pickle.load(positionFile)
    # If the page name is invalid print it
    if (pageName not in cursorDictionary):
        print("Invalid Page Name")
    # If the page name is valid
    else:
        # Go to the position that contains the list of links of the page name
        theGraph.seek(cursorDictionary[pageName])
        # Load the graph into main memory
        print(pickle.load(theGraph))
    # Close the files that were used in the function
    theGraph.close()
    positionFile.close()

def findCursorPositions():
    # Open the file that contains the adjacency list
    fileName = open('pickleGraph.pkl', 'rb')
    # Open the file to store the cursor positions of all page names
    keyPositionDictFile = open('keyPositionDict.txt', "wb")
    # Initialising empty dictionaries to store the lengths of lists
    lengthOfLinkList = {}
    # Initialising empty dictionary to store the cursor positions
    keyPositionDict = {}
    # Variable to store the heading
    heading = ""

    # Keep doing until file is over. Once no more lines exist, exception is triggered and except executes break
    while (True):
        try:
            # load heading from the file
            content = pickle.load(fileName)
            # load the position of the list corresponding to the list of links of the page name
            currentFilePointerPosition = fileName.tell()
            # Copy the content into a different variable
            heading = content
            # Remove unnecessary spaces and " from the heading of the link (they do not exist, just for safety)
            heading = heading.strip(' "').lower()
            # If the heading has already been encounted before (redirects)
            if (heading in lengthOfLinkList):
                # Store the file location of the list of links of the page name
                curPos = currentFilePointerPosition
                # Read the list of links from the file
                listOfLink = pickle.load(fileName)
                # If the length of this list is more than the list that we had, then this is the actual page
                # The old one was the redirect
                if (len(listOfLink) > lengthOfLinkList[heading]):
                    # Update the position of the list of links of that page name to the current location
                    lengthOfLinkList[heading] = len(listOfLink)
                    # Update the cursor position of the page name to the value that you stored earlier
                    keyPositionDict[heading] = curPos
                # If the length of this list is lesser, then this list is the redirect. IGNORE
                else:
                    continue
            # If the page name has never occured before
            else:
                # Note the current position that you are at
                curPos = currentFilePointerPosition
                # Load the list of links corresponding to the file
                listOfLink = pickle.load(fileName)
                # Set the length of the list of links corresponding to the page name
                lengthOfLinkList[heading] = len(listOfLink)
                # Set the cursor position of the page that you are at
                keyPositionDict[heading] = curPos
        # If the exception occurs
        except Exception as Inst:
            # Stop the loop
            break

    # Dump the dictionary of cursor positions that you created into the file
    pickle.dump(keyPositionDict, keyPositionDictFile)
    # Close the files that you used
    fileName.close()
    keyPositionDictFile.close()

# Just a user interface
if __name__ == '__main__':
    # Print all the options in the file
    print('Options - In order to do complete operation')
    print('1. Create adjacency list file')
    print('2. Create cursor dictionary')
    print('3. Random Walk')
    print('4. View top k pages')
    print('5. Graph of Frequency vs No of nodes')
    # Keep repeating till the user asks to stop
    while (True):
        # Collect the user option
        print('Enter your choice: ', end = '')
        x = int(input())
        if (x == 1):
            # Ask for the name of the input bz2 file
            print('Enter the name of the input file : ', end = "")
            mainFile = input()
            # Open the file directly as bz2
            mainFile = bz2.open(mainFile, 'rb')
            # Call the function to make the adjacency list
            print('Making Adjacency List')
            createAdjacencyList()
            print('Adjacency List Created!')
            print()
        elif (x == 2):
            # Create a file containing all the cursor positions
            print('Creating Cursor Dictionary')
            findCursorPositions()
            print('Cursor Dictionary Created!')
            print()
        elif (x == 3):
            # Ask for the number of steps in the random walk
            print('How many steps in the random walk? ', end = "")
            numberOfSteps = int(input())
            # Perform the random walk
            print('Random Walking')
            randomWalk(numberOfSteps)
            print("Random Walk Complete!")
        elif (x == 4):
            # Ask for the value of k
            print('How many ranks do you wish to see? (k) ', end = "")
            k = int(input())
            if (k <= 0):
                print('Invalid value of k')
                continue
            # Display the top k pages
            displayTop(k)
            print()
        elif (x == 5):
            # Plot of no of visits vs no of pages
            plotFrequencies()
        else:
            break