import tweepy
import regex as re
from tweepy import OAuthHandler
from textblob import TextBlob
from tkinter import *
import mysql.connector
import tkinter.ttk as ttk
from ttkthemes import ThemedStyle
import matplotlib.pyplot as plt

win = Tk()
style = ThemedStyle(win)
style.set_theme("elegance")
win.title("Twitter Sentiment search")
win.configure(background="#D9D9D9")
# labels
Label(win, text="Welcome to the world of Twitter Sentiments", fg="#260026",bg="#D9D9D9", font="Broadway 16").grid(padx=100,row=0, column=0,pady=20, columnspan=3)
photo = PhotoImage(file = r"C:\Users\HP\Desktop\Minor_project\searchtab.png")
photoimage = photo.subsample(15, 20)
Label(win, text="Enter your Name", font="Aharoni 12",bg='#D9D9D9').grid(row=1, column=0, sticky=W)
Label(win, text="Enter your Email-id", font="Aharoni 12",bg='#D9D9D9').grid(row=2, column=0, sticky=W)
Label(win, text="Enter your search topic", font="Aharoni 12",bg='#D9D9D9').grid(row=4, column=0, sticky=W)
Label(win, text="Enter the no. of tweets to search upon", font="Aharoni 12",bg='#D9D9D9').grid(row=5, column=0, sticky=W)

# variables
username = StringVar()
email = StringVar()
topic = StringVar()
cnt = IntVar()

# Entry Box
name_entry = Entry(win, width=30, textvariable=username,borderwidth="3").grid(pady=3,row=1, column=1, sticky=W)
mail_entry = Entry(win, width=30, textvariable=email,borderwidth="3").grid(pady=3,row=2, column=1, sticky=W)
topic_entry = Entry(win, width=30, textvariable=topic,borderwidth="3").grid(pady=3,row=4, column=1, sticky=W)
count_entry = Entry(win, width=10, textvariable=cnt,borderwidth="3").grid(pady=3,row=5, column=1, sticky=W)




class TwitterAccess:
    '''
    Generic Twitter Class for sentiment analysis.
    '''

    def __init__(self):
        '''
        Class constructor
        '''
        # keys and tokens from the Twitter Dev Console
        consumer_key = '3nk2y8cPKoBzVxjx8TE8tqBUy'
        consumer_secret = '3VWXJ3LuRJhy4FxCyKbm5qnvefFd00pvUM2By0WKAL7aEzYmGu'
        access_token = '1279483751072854016-Sixcf1Biy0ItUyxTInXw45Xxd9AA3W'
        access_token_secret = 'jmuk3wqcodlWIb0ZRUJn1dbWBnF5pFf6FWay9ITh5smgP'

        # attempt authentication
        try:
            # create OAuthHandler object
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            # set access token and secret
            self.auth.set_access_token(access_token, access_token_secret)
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            messagebox.showinfo(title='Error', message='Authentication Failed')

    def clean_tweet(self, tweet):
        '''
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", tweet).split())

    def get_tweet_sentiment(self, tweet):
        '''
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        '''
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
        # set sentiment
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'

    def get_tweets(self, query, count=20):
        '''
        Main function to fetch tweets and parse them.
        '''
        # empty list to store parsed tweets
        tweets = []

        try:
            # call twitter api to fetch tweets
            fetched_tweets = self.api.search(q=query, count=count)

            # parsing tweets one by one
            for tweet in fetched_tweets:
                # empty dictionary to store required params of a tweet
                parsed_tweet = {}

                # saving text of tweet
                parsed_tweet['text'] = tweet.text
                # saving sentiment of tweet
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)

                # appending parsed tweet to tweets list
                if tweet.retweet_count > 0:
                    # if tweet has retweets, ensure that it is appended only once
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)

                    # return parsed tweets
            return tweets

        except tweepy.TweepError as e:
            # print error (if any)
            print("Error : " + str(e))


def main():
    try:
        # creating object of TwitterAccess Class
        api = TwitterAccess()
        # calling function to get tweets

        tweets = api.get_tweets(query=topic.get(), count=cnt.get())


        # picking positive tweets from tweets
        ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
        # percentage of positive tweets
        p = round(100 * len(ptweets) / len(tweets), 2)
        # picking negative tweets from tweets
        ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
        # percentage of negative tweets
        n = round(100 * len(ntweets) / len(tweets), 2)
        # percentage of neutral tweets
        ne = 100 - (p + n)
    except (TclError):
        messagebox.showinfo(title='Error', message='Do not leave empty and enter only integer values')
        return
    except(TypeError):
        messagebox.showinfo(title='Error', message='Please Enter all values')
        return

    name = username.get()
    if not name:
        messagebox.showinfo(title='Error', message='Enter Name')
        return
    mail = email.get()
    if not mail:
        messagebox.showinfo(title='Error', message='Enter Email ID')
        return
    if not re.match(r"^[A-Za-z0-9\.\+-]+@[A-Za-z0-9\.-]+\.[a-zA-Z]*$", mail):
        messagebox.showinfo(title='Error', message='Enter Valid Email ID')
        return
    stopic = topic.get()
    if not stopic:
        messagebox.showinfo(title='Error', message='Enter Topic')
        return
    count = cnt.get()
    if not count:
        messagebox.showinfo(title='Error', message='Enter no. of results')
        return

    def plotPieChart(p, n, ne, stopic, count):
        labels = ['Positive [' + str(p) + '%]', 'Neutral [' + str(ne) + '%]', 'Negative [' + str(n) + '%]']
        sizes = [p, ne, n]
        colors = ['yellowgreen', 'gold', 'red']
        patches, texts = plt.pie(sizes, colors=colors, startangle=90)
        plt.legend(patches, labels, loc="best")
        plt.title('How people are reacting on ' + stopic + ' by analyzing ' + str(count) + ' Tweets.')
        plt.axis('equal')
        plt.tight_layout()
        plt.show()

    m = ' Positive sentiments=' + str(p) + " % \n Negative Tweets=" + str(n) + "% \n Neutral Tweets=" + str(ne) + "%"
    messagebox.showinfo(title=topic.get(), message=m)
    plotPieChart(p, n, ne, stopic, count)
    mydb = mysql.connector.connect(host="localhost", user="root", password="root", database="user")
    mycursor = mydb.cursor()
    mycursor.execute(
        "INSERT INTO records (Name,Email_Id,Count,Positive,Negative,Neutral,SearchTopic) VALUES(%s,%s,%s,%s,%s,%s,%s)",
        (name, mail, count, p, n, ne, stopic))
    mycursor.close()
    mydb.commit()
    mydb.close()


def search():
    # calling main function
    main()


# Button
btn = ttk.Button(win, text="SEARCH", command=search, image=photoimage, compound=LEFT).grid(row=6, column=0, columnspan=2, pady=10)

win.mainloop()
