from wordcloud import WordCloud
import matplotlib.pyplot as plt

def generate_wordcloud(reviews):
    text = " ".join(reviews)
    wc = WordCloud(width=800, height=400).generate(text)
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.savefig("static/wordcloud.png")
