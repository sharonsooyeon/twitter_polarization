from selenium import webdriver
from bs4 import BeautifulSoup
import time
import os
from collections import OrderedDict

global browser
browser = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver')

'''
Takes in a username whose Twitter feed should be scraped for a num_conversations 
number of tweets.
Returns a OrderedDict where keys   are each tweet's ID, and 
                            values are each a list of the corresponding tweet's replies.
Also makes a directory for the inputted user and saves each conversation as a separate txt file.

The purpose of this function with respect to our project is that we would like to 
investigate how millennials engage with journalists and politics on Twitter.

Known problems with this function:
    * Unable to handle tweets with replies greater than about 1,000 replies. An API 
      would be useful here, but no known API is able to scrape conversations.
    * `browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")` 
      seems to be incompatible with conversation display on Twitter. It works for 
      tweet display (i.e. when one visits a particular user's Twitter profile, it is
      able to display the desired amount of tweets from that user), but once a specific 
      conversation thread is selected, it fails to reach the bottommost tweet.
        * However, this problem may be acceptable, since our group is interested in 
          investigating how journalists such as Lauren Duca interact with millennials 
          on Twitter. Twitter displays the replies in order of which reply got the most 
          amount of attention from the original poster. It may be pointless to collect 
          the bottommost replies to a tweet, given they probably got no attention from 
          the original poster.
'''
def get_conversations(username, num_conversations):
    browser.get('https://twitter.com/' + username)
    num_scrolls = int(round(num_conversations/20)) # 20 replies displayed per scroll
    for j in range(num_scrolls): # to display all tweets before getting page_source
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    
    '''step 1: get the ID of each tweet so we can view that tweet's conversation'''
    tweet_IDs = []
    # first, check for pinned tweets. Can't catch for all tweets at once because 
    # pinned tweets have a different class name than regular tweets
    pinned_tweets = soup.find_all('li',attrs={'class':'js-stream-item stream-item stream-item js-pinned '})
    if len(pinned_tweets) > 0:
        for pinned_tweet in pinned_tweets:
            tweet_IDs.append(pinned_tweet['data-item-id'])
    # now get the IDs of regular tweets
    tweets = soup.find_all('li',attrs={'class':'js-stream-item stream-item stream-item '})
    for tweet in tweets:
        tweet_IDs.append(tweet['data-item-id'])
    
    '''step 2: find number of replies for each tweet so we know how much to scroll for each conversation'''
    num_replies = soup.find_all('span',attrs={'class':'ProfileTweet-actionCountForAria'})
    num_replies = [int(num.text[:-8].replace(',','')) for num in num_replies if 'replies' in num.text]
    
    '''step 3: zip the tweet IDs with their respective number of replies'''
    tweets = zip(tweet_IDs, num_replies)
    
    '''step 4: display each conversation thread and scrape relevant information'''
    conversations = OrderedDict() # the data structure to store each conversation.
    original_directory = os.getcwd() # so we can return to it later
    os.mkdir(username) # so we have a place to store all their conversations
    os.chdir(username)
    i = 0 # for naming the conversations for its file; 
          # each conversation thread is stored in a separate file
    for tweet in tweets:
        browser.get('https://twitter.com/' + username + '/status/' + tweet[0])
        
        '''
        # make sure that all replies are displayed before getting the page_source
        num_scrolls = int(round(tweet[1]/20)) # 20 replies displayed per scroll
        for j in range(num_scrolls):
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
        '''
        
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        original_tweet = soup.find('title').text
        containers = soup.find_all('div',attrs={'class':'js-tweet-text-container'})
        replies = []
        for container in containers:
            if container.find('a',attrs={'href':'/' + username}): # not all containers are replies
                replies.append(container.text)
        
        # store the conversation into a dictionary data structure; 
        # key   = the tweet ID
        # value = a list of replies in order of which replies got the most activity 
        #         from the original poster
        conversations[tweet[0]] = replies
        
        # store the conversation into a new file
        with open(str(i) + '_' + tweet[0] + '.txt','w') as outfile:
            outfile.write(original_tweet.encode('utf8') + '\n')
            for reply in replies:
                outfile.write('\t' + reply.encode('utf8'))
        i += 1
    
    os.chdir(original_directory)
    return conversations

lauren = get_conversations('laurenduca', 20)
lily = get_conversations('lkherman', 20)
browser.close()