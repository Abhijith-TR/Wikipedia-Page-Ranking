### **How to run the program**
You can run the program using python3 2020csb1062.py. You will be prompted for further options.

### **Functions Created**
- Line by line explanation of the code is in the python file

1. findLinksBinary(title, textContent) - Takes the title and content of that particular title as argument. Returns nothing.
Extracts content from <title>content</title> and extracts all the links from the file and inserts it as a list into the file
that will store the pickled content.

2. createAdjacencyList() - Takes no arguments (files are opened globally for performance). Reads the bz2 file one line at a
time. Extracts the title and the content corresponding to that title and sends textContent and title to function 1 to insert 
into the file.

3. initializeFrequencies() - Takes no arguments. Reads all the contents from the cursor dictionary. Initializes frequencies
of all pages to 0. Returns the list of pages, the frequency dictionary and the cursor dictionary

4. randomWalk(numberOfSteps) - Takes the number of steps in the random walk as argument. Teleports if it comes across pages
that have less than 5 links. Returns nothing

5. displayTop(k) - Display the top k pages. Returns nothing

6. plotFrequencies() - Plots the frequency vs number of pages graph.

### **What I did**

I created an adjacency list using the wikidump file. To account for the huge size of the bz2 file I worked with the file itself.
To make the write operation faster, I used pickle and dumped everything into a .pkl file. Then I read the adjacency list from
the file and noted the offset of every single list of links from the start of the file and stored that in another file. This 
had to be done as there is no way to fit the entire adjacency list in main memory. Now we can use the offset to identify the 
list corresponding to each page in main memory. Once this is done, we collect all the page names and use this to randomly 
pick a starting node. Once this is done, we can start the random walk and fetch the corresponding list of links from the actual
file using the cursor file every single time to perform the random walk. 

### **Observations**

1. The random walked graph observed exhibits the power law i.e., there exist a large number of nodes which are visited very few
times, however there is not an exponential drop. There still exist a good number of nodes that are visited a large number of 
times. This was expected and the results that we obtain verify this claim. This might also be a reasonable estimate of the 
number of inlinks that a page has i.e., there exist a not insignificant number of pages that have a large number of inlinks
and a large number of pages with very few inlinks. 

2. Most of the top pages that we see are major countries or major cities. This is to be expected as a large number of pages will
be linked to these events. For e.g., if we consider USA, a large number of pages on major companies, presidents, actors and 
so on will be linked to the country. Apart from these a large number of minor pages are also to be expected. This is because a
large number of contributors are also to be expcted and so even minor events from across the country may exist on wikipedia.
World war II is to be expected as a huge number of historical events and countries will be linked to this particular page.
Two notable abnormalities are 'The New York Times' and 'Association Football'. The New York Times, one can expect, has a 
large number of inlinks as it is an extremely popular news page. Many articles might have recieved an article at some point
from the New York Times and they may have links to the page themselves on the page. Association Football is also reasonably
expected as almost every nation and football club in the world would have links to this particular page. The same explanation 
can also be extended for other news pages such as 'The Guardian'.

3. The random walk is extremely effective at finding the top pages. Even on a graph of 10 million+ nodes, a random walk of just
a million steps managed to find the top nodes accurately. The ranking was slightly off from the walk of 70 million steps but 
the set of the top pages was the same. 

4. The graph exhibits a huge connected component similar to the bow tie structure of the web. There exhibits a huge chunk of
the wikipedia pages that are connected to each other. In a walk of almost 70 million steps, we still never managed to get stuck
in a loop that was outside this component simply by ignoring extremely miniscule pages. This shows that most of the pages that
are outside this connected component are simply minor pages that do not have many inlinks or outlinks. 