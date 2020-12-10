import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
import re
from wordcloud import WordCloud,STOPWORDS
from textblob import TextBlob
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
import tweepy

consumer_key = 'kbhmaJw28BMcE49dgUXLBXu8Q'
consumer_secret = 'LLmsOB2TyauXIOEOxKO4qMft8oxkThJaObF5pgCDO2E9IvfWs3'
access_token = '1269875018256846848-2tSHRpdUQHpIOZaJPLbqE7OosHD67D'
access_token_secret = '0SIgsHZKgBYDrDNXAqmGd54tabfakhm7rd117SJZP6ZnO'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)
#Implement the following 3 lines to use the all Twitter-range search function
#searchTerm = input("Enter keyword to search the automobile company: ")
#numberOfSearch = int(input("Number of tweets you want to analyze: "))
#posts = tweepy.Cursor(api.search, q=searchTerm, lang='en',tweet_mode='extended').items(numberOfSearch)

#Enter the company name and the number of tweets you want to analyze.
Name_input = input("Enter the Automobile Company you want to analyze: ")
Number_input = int(input("Number of tweets you want to analyze(No more than 400 so that you can search for last month): "))


#Get timeline
posts = api.user_timeline(screen_name= Name_input,count = Number_input,
                          lang = 'en',tweet_mode = 'extended')

#Get most recent_id and extract textfields from tweets
last_id = int(posts.max_id-1)

#Since the max count equals 200, if user wants to search more than 200 tweets,then use extend here.
if Number_input > 200:
    remain_posts = api.user_timeline(screen_name = Name_input,count = Number_input-200,
                                     since_id = last_id,lang = 'en',tweet_mode = 'extended')
    posts.extend(remain_posts)

##Create dataframe and Show all tweets
print()
print("Show recent",Name_input,"tweets with full text: \n")
df = pd.DataFrame([tweet.full_text for tweet in posts],columns = ['Tweets'])

#Create a function that can clean the data
def clean_data(text):
    text = re.sub(r'https?:\/\/\S+', '', text)
    text = re.sub(r'@[A-Za-z0-9]+', '', text)
    text = re.sub(r'^\s+|\s+$', '', text)
    text = re.sub(r'#', '',text)
    text = re.sub(r'RT[\s]+', '',text)
    text = re.sub(r'RT[\s]+','',text)
    words = text.split(" ")
    words = [w for w in words if len(w) > 2]  # ignore a, an, be, ...
    words = [w.lower() for w in words]
    words = [w for w in words if w not in STOPWORDS]
    clean_word = ' '.join(words)
    return clean_word

#Show the dataframe
df['Tweets'] = df['Tweets'].apply(clean_data)

#Create a function to get the subjectivity and the polarity
def getSubjectivity(text):
    return TextBlob(text).subjectivity

def getPolarity(text):
    return TextBlob(text).polarity

#Create two new columns
df['Subjectivity'] = df['Tweets'].apply(getSubjectivity)
df['Polarity'] = df['Tweets'].apply(getPolarity)

#Create a function to compute the negative,neutral and positive analysis
def getAnalysis(score):
    if score < 0:
        return 'Negative'
    elif score == 0:
        return 'Neutral'
    elif score >0:
        return 'Positive'

df['Analysis'] = df['Polarity'].apply(getAnalysis)
print(df)

#Set the inital score, if positive, gain 3 points; if neutal, gain 1 point; if negative, lose 3 points
Sum_Positive = 0
Sum_Neutral = 0
Sum_Negative = 0

#Print the positive tweets
j=0
sortedDF = df.sort_values(by=['Polarity'])
#print("Show all the Positive Tweets:")
print()
for i in range(0, sortedDF.shape[0]):
    if(sortedDF['Analysis'][i] == 'Positive'):
# Delete the # for the following two codes to show All positive contents
        #print(str(j)+ ')' + sortedDF['Tweets'][i])
        #print()
        j = j+1
        Sum_Positive = Sum_Positive + 2
print("There are ",j," positive results.")

#Print the neutral tweets
m=0
sortedDF = df.sort_values(by=['Polarity'],ascending='False')
#print("Show all the Neutral Tweets: ")
for i in range(0, sortedDF.shape[0]):
    if(sortedDF['Analysis'][i] == 'Neutral'):
        m = m+1
        Sum_Neutral = Sum_Neutral + 0.5
print("There are ",m," neutral results.")

#Print the negative tweets
n=0
sortedDF = df.sort_values(by=['Polarity'],ascending='False')
for i in range(0, sortedDF.shape[0]):
    if(sortedDF['Analysis'][i] == 'Negative'):
#the following two lines to show All negative contents
        #print(str(n)+ ')' + sortedDF['Tweets'][i])
        #print()
        n = n+1
        Sum_Negative = Sum_Negative - 2
print("There are ",n," negative results.")

#Show the total Score of the company
Final_Score= Sum_Positive+Sum_Neutral+Sum_Negative
print()
print("The Positive Score: ",Sum_Positive)
print("The Neutral Score: ",Sum_Neutral)
print("The Negative Score: ",Sum_Negative)
print("The Final Sentiment Score of this automobile company is: ",Final_Score)
print()

def getPercentage(part,total):
    numberOfPercent = round(part/total,2)
    percentage = numberOfPercent *100
    return(percentage)

t=j+m+n
print("The Positive Percentage: ",getPercentage(j,t),'%')
print("The Neutral Percentage: ",getPercentage(m,t),'%')
print("The Negative Percentage: ",getPercentage(n,t),'%')


#Visualize the Score
fig,ax = plt.subplots()
bar_x = [1,2,3,4]
bar_tick_label = ['Positive','Neutral','Negative','Total Score']
bar_height = [Sum_Positive, Sum_Neutral, Sum_Negative, Final_Score]
bar_label=[Sum_Positive, Sum_Neutral, Sum_Negative, Final_Score]
bar_plot = plt.bar(bar_x, bar_height, tick_label=bar_tick_label)

def autolabel(rect):
    for idx,rect in enumerate(bar_plot):
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/6.,0.79*height,
                bar_label[idx],ha='center',va='bottom', rotation=90)

autolabel(bar_plot)
plt.ylim(-200,600)
plt.title('Sentiment Score Graph')
plt.xlabel('Polarity of Tweets')
plt.ylabel('Scores')
plt.show()


#Plot the polarity and subjectivity
plt.figure(figsize=(8,6))
for i in range(0,df.shape[0]):
    plt.scatter(df['Polarity'][i],df['Subjectivity'][i],color='Blue')
plt.title('Sentiment Analysis Graph')
plt.xlabel('Polarity')
plt.ylabel('Subjectivity')
plt.show()

#Create the Wordcloud
final_word = ','.join([twts for twts in df['Tweets']])
wcloud_3 = WordCloud(height=500, width=400,random_state=21,background_color="black", max_words=500, max_font_size=120)
wcloud_3.generate(final_word)

#Show image of Wordcloud
f = plt.figure(figsize=(50,50))
plt.imshow(wcloud_3, interpolation='bilinear')
plt.title('Twitter Generated Cloud', size=170)
plt.axis("off")
plt.show()










