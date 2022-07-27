from re import X
import re
import json
import requests

from os import path
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
from wordcloud import WordCloud, ImageColorGenerator


from flask import Flask,render_template, url_for, request

from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import matplotlib.pyplot as plt
import string



nltk.download('vader_lexicon')

app = Flask(__name__)

@app.route('/')
def first():
    return(render_template("home.html"))


# Functions
@app.route('/extract/', methods=["POST","GET"])
def result():
    if request.method=="GET":
        return render_template('index.html',lyrics= {})
    global artist, song
    artist_name = request.form.get(str("artist"))
    song_name = request.form.get(str("song")).lower()
    link = 'https://api.lyrics.ovh/v1/' + artist_name.replace(' ', '%20') + '/' + song_name.replace(' ', '%20')

    req = requests.get(link)
    json_data = json.loads(req.content)
       
    lyrics = json_data['lyrics']

    print(lyrics)

    return render_template('index.html',lyrics=lyrics)
    

    
@app.route('/analyze/', methods=["POST","GET"])
def analyze(): 
    if request.method=="GET":
        return render_template('analyze.html',lyrics= {})
    global artist, song
    artist_name = request.form.get(str("artist"))
    song_name = request.form.get(str("song")).lower()
    link = 'https://api.lyrics.ovh/v1/' + artist_name.replace(' ', '%20') + '/' + song_name.replace(' ', '%20')

    req = requests.get(link)
    json_data = json.loads(req.content)
        
    lyrics = json_data['lyrics']
    
    sid = SentimentIntensityAnalyzer()
    x=" ".join(lyrics)
    score = sid.polarity_scores(x)
    print(score)
    if score["neg"] < 0:
        return render_template('analyze.html', message="The lyrics contain a lot of negative words, and may not be safe to listen😟😟😟😟")
    elif score["pos"] > 0:
        return render_template('analyze.html', message="The lyrics contain a lot of positive words, and would be safe to listen😇😇😇😇!!!")
    else:
        return render_template('analyze.html', message="The lyrics contain a lot of neutral words, and might either be safe or unsafe to listen😐😐😐! Check the wordcloud")
        

    
@app.route('/wordcloud/', methods=["POST","GET"])   
def wordcloud():
    if request.method=="GET":
        return render_template('word_cloud.html',lyrics= {})
    artist_name = request.form.get(str("artist"))
    song_name = request.form.get(str("song")).lower()
    link = 'https://api.lyrics.ovh/v1/' + artist_name.replace(' ', '%20') + '/' + song_name.replace(' ', '%20')

    req = requests.get(link)
    json_data = json.loads(req.content)
        
    lyrics = json_data['lyrics']
    
    z=lyrics
    print(z)
    clean = re.sub(r'@[A-Za-z09]+', '', z)
    clean = re.sub(r'#', '', clean)
    clean = re.sub(r'RT[\s]+', '', clean)
    z = re.sub(r'https?:\/\/?', '', clean)
    toknized_lyrics = nltk.word_tokenize(z)
    #Stopword
    STOPWORDS = stopwords.words('english')
    STOPWORDS.extend(['eh','LYRICS','Verse','woo','aw','really','yeah',"n't",'aah','de','wo','ya','la','yoo','1','2','3','4','5','6','7','8','9','10','Go','0','E','though','Its',',','say','Lyrics',':','Even','Hey','(',')','.','I','...','go','do' 'ti', 'Length', 'Name', 'aah', 'TH', 'dtype', 'Object', '480', '481', 'ni', 'won', 'woo', 'awon', 'oh', 'ah', 'AAH', 'ahh' ,'and' ,'PH', 'Ph', 'Eh', 'ehn', 'eh' ,'hello','object', 'mi','Lyric'])
    
    #remove stopwords
    Lyrics_without_stopwords = [t for t in toknized_lyrics if t not in STOPWORDS]   
    #stemming
    pst= PorterStemmer()
    
    stemmed_lyrics = (Lyrics_without_stopwords)
    for words in  stemmed_lyrics:
        pst.stem(words)
    

    # Create a wordcloud to display most common words
    wordcloud = WordCloud(stopwords=STOPWORDS,collocations=True,max_font_size=50, max_words=20, background_color="black").generate(' '.join(stemmed_lyrics))
    plt.rcParams["figure.figsize"] = (15,15)
    plt.title('Lyrics Wordcloud')
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.show()
    plt.savefig("static/WordCloud.png")
    return render_template('word_cloud.html')




if __name__ == "__main__":
    app.run(debug=True)