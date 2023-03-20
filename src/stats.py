import preprocessing as pp
import pipeline
from pipeline import FunctionApplier, apply_pipeline, ist_pipeline
import matplotlib.pyplot as plt
from collections import Counter
from ast import literal_eval
import numpy as np
from scipy.stats import norm
from matplotlib_venn import venn2
import pandas as pd
from multiprocessing import Process



RAW_DATA = '../datasets/sample/1mio-raw.csv'
CLEANED_DATA = '../datasets/sample/news_sample_cleaned.csv'
CLEANED_DATA_NUM = '../datasets/sample/news_sample_cleaned_num.csv'


class Word_frequency(FunctionApplier):
    def __init__(self, nwords = 50):
        self.swords = nwords
        self.words = []
        self.frequency = Counter()
        self.sorted_frequency = []

    def function_to_apply(self, content):
        # Update/add list of word
        content: list = literal_eval(  str(content) )
        # content = [x for x in content if x != "<number>"]
        self.frequency.update(content)
        # Return the sorted dictionary based on the frequency of each word
        self.sorted_frequency = sorted(self.frequency.items(), key=lambda x: x[1], reverse=True)
        # print("sorted_frequency", self.sorted_frequency)
        return content
    
    def plot(self):
        # Extract the words and their frequency from the sorted list
        # print(self.sorted_frequency)
        words = [x[0] for x in self.sorted_frequency[:self.swords]]
        frequency = [x[1] for x in self.sorted_frequency[:self.swords]]
        # Plot a barplot using matplotlib
        plt.bar(words, frequency)
        plt.ylabel('Frequency')
        plt.title(f'Frequency of the {self.swords} most frequent words')
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.show()

    def plotVenn(self, other_sorted_frequency: list[tuple[str, int]]): 
        words = [x[0] for x in self.sorted_frequency[:self.swords]]
        frequency = [x[1] for x in self.sorted_frequency[:self.swords]]

        other_words = [x[0] for x in other_sorted_frequency[:self.swords]]
        other_frequency = [x[1] for x in other_sorted_frequency[:self.swords]]

        set1 = set(words)
        set2 = set(other_words)

        venn2([set1, set2], set_labels=("Reliable", "Fake"))

        venn2_circles = venn2([set1, set2], set_labels=("Reliable", "Fake"))
        venn2_circles.get_patch_by_id('10').set_color('orange')
        venn2_circles.get_patch_by_id('10').set_alpha(0.5)
        
        intersection_label = venn2_circles.get_label_by_id('11')
        intersection_label.set_text('\n'.join(list(set1.intersection(set2))))
        
        # intersection_label.set_position((0.08, 0))
        disjoint_words1 = set(words) - set(other_words)
        disjoint_words2 = set(other_words) - set(words)

        # set the text of the disjoint words
        venn2_circles.get_label_by_id('01').set_text('\n'.join(list(disjoint_words1)))
        venn2_circles.get_label_by_id('10').set_text('\n'.join(list(disjoint_words2)))
        # set the text of the intersection int the middle of the venn diagram
        intersection_label.set_fontsize(10)
        # venn2_circles.get_label_by_id('10').set_fontsize(14)

        plt.show()


    # plot the frequency of the words from the fake news and plot the frequency of the words from the real news
    def plot_fake_real(self, other_sorted_frequency: list[tuple[str, int]], set_labels: tuple[str, str] = ("Fake", "Reliable") ):
        # Extract the words and their frequency from the sorted list
        words = [x[0] for x in self.sorted_frequency[:self.swords]]
        frequency = [x[1] for x in self.sorted_frequency[:self.swords]]

        other_words = [x[0] for x in other_sorted_frequency[:self.swords]]
        other_frequency = [x[1] for x in other_sorted_frequency[:self.swords]]

        disjoint_words = set(words) - set(other_words)
        print("disjoint_words", disjoint_words)

        # map the word frequency from the fake news word list to the words from the real news
        for i in range(len(words)):
            if not words[i] in other_words:
                other_frequency[i] = 0

        # Set the width of the bars
        bar_width = 0.35

        print("freq", frequency)
        print("\n\n")
        print("otherfreq", other_frequency)

        # Set the positions of the bars on the x-axis
        fake_pos = np.arange(len(words))
        reliable_pos = fake_pos + bar_width

        # Create the figure and axis objects
        fig, ax = plt.subplots()

        # Plot the bars for fake news
        ax.bar(fake_pos, frequency, width=bar_width, color='b', label=set_labels[0])

        # Plot the bars for reliable news
        ax.bar(reliable_pos, other_frequency, width=bar_width, color='g', label=set_labels[1])

        # Add labels and title to the plot
        ax.set_xlabel('Words')
        ax.set_ylabel('Frequency')
        ax.set_xticks(fake_pos + bar_width / 2)
        ax.set_xticklabels(words)
        ax.set_title('Word Frequency Comparison')
        
        # rotate the xticks
        plt.xticks(rotation=90)

        # Add a legend to the plot
        ax.legend()

        # Show the plot
        plt.show()

class Count_Items(FunctionApplier):
    def __init__(self):
        self.count = {
            "urls": 0,
            "dates": 0,
            "numbers": 0 
        }

    def function_to_apply(self, content):
        # Update/add list of word
        content: list = literal_eval(str(content))
        self.countItems(content)
        

    def countItems(self, content):
        # pp.Exploration.countItems(data)
        for text in content:
            self.count["urls"] += text.count("<url>")
            self.count["dates"] += text.count("<date>")
            self.count["numbers"] += text.count("<num>")


class Contribution(FunctionApplier): 
    def __init__(self):
        # initialize the data as a pandas dataframe
        # self.data = pd.DataFrame(columns=['domain', 'type', 'content'])
        self.data = []
        # self.data = pd.DataFrame()


    def function_to_apply(self, content: pd.DataFrame):
        # self.data.append(pd.DataFrame(content))
        self.data.append(content)


    def contributionPlot2(self):
        
        threshold = 1
        self.data = pd.DataFrame(self.data)

        # group the articles by domain and category, and count the number of articles in each group
        counts = self.data.groupby(['domain', 'type'])['content'].count().unstack()
        # convert the counts to percentages and round to two decimal places
        percentages = counts.apply(lambda x: x / x.sum() * 100).round(2)
        # filter the percentages to only show the contributions above the threshold
        percentages = percentages[percentages > threshold]
        # drop the rows with all NaN values
        percentages = percentages.dropna(how='all')
        # create a stacked horizontal bar chart of the percentages
        ax = percentages.plot(kind='barh', stacked=True, figsize=(10, 8))
        # set the x-axis label to show the percentages
        ax.set_xlabel('Percentage')
        # set the legend to display outside the chart
        ax.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
        
        title = f'Contribution of Domains to Categories ( ≥ {threshold}%)'
        ax.set_title(title)

        # show the chart
        plt.show()



# make class to count each type fake, real, unreliable, reliable etc. and make a frequency plot
class Article_Type_frequency(FunctionApplier):
    # kg = 20
    def __init__(self):
        self.frequency = Counter()
        self.sorted_frequency = []
        self.items = 13

    def function_to_apply(self, type):
        # Update/add list of word
        type = str(type)
        # print(self.frequency)
        self.frequency.update({type: 1})
        # Return the sorted dictionary based on the frequency of each word
        self.sorted_frequency = sorted(self.frequency.items(), key=lambda x: x[1], reverse=True)
        # print("sorted_frequency", self.sorted_frequency)
        return type

    def plot(self):
        # print(self.sorted_frequency)
        # Extract the words and their frequency from the sorted list
        words = [x[0] for x in self.sorted_frequency[:self.items]]
        frequency = [x[1] for x in self.sorted_frequency[:self.items]]
        # Plot a barplot using matplotlib
        plt.bar(words, frequency)
        plt.ylabel('Frequency')
        plt.title(f'Frequency of the {self.items} most frequent words')
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.show()

    def plotDistribution(self):
        # Extract the words and their frequency from the sorted list
        words = [x[0] for x in self.sorted_frequency]
        frequency = [x[1] for x in self.sorted_frequency]

        total_frequency = sum(frequency)

        # Compute the probability of each word.
        probabilities = [x / total_frequency for x in frequency]

        # sort the words by their probability
        # sorted_probability = sorted(probability, reverse=True)
        # Sort the words based on their probability.
        sorted_indices = np.argsort(probabilities)[::-1]
        sorted_probabilities = [probabilities[i] for i in sorted_indices]

        # Compute the cumulative probability of each word.
        cumulative_probabilities = np.cumsum(sorted_probabilities)

        plt.bar(words, sorted_probabilities)
        plt.xlabel('Type')
        plt.ylabel('Frequency')
        plt.title('Type Frequency Distribution')
        plt.show()


def clean():
    ist_pipeline(RAW_DATA)

def plot_in_processes(plot_funcs):
    """Spawn multiple processes to plot matplotlib plots."""
    processes = []
    for plot_func in plot_funcs:
        process = Process(target=plot_func)
        process.start()
        processes.append(process)
    for process in processes:
        process.join()


def runStats():



    size = 10000
    
    wf = Word_frequency()
    apply_pipeline(
        CLEANED_DATA_NUM, 
        [
            (wf, "content"),
        ],
        batch_size=size,
        get_batch=True,
        type="fake"
        # exclude=["reliable"]
    )

    wf2 = Word_frequency()
    apply_pipeline(
        CLEANED_DATA_NUM, 
        [
            (wf2, "content"),
        ],
        batch_size=size,
        get_batch=True,
        type="reliable"
    )

    cp = Contribution()
    apply_pipeline(
        CLEANED_DATA_NUM, 
        [
            (cp, None),
        ],
        batch_size=size,
        get_batch=True,
        # type="reliable"
    )


    # print(ss.count)

    # atf.plotDistribution()
    # atf.plotDistribution()
    # wf.plot()

    # wf.plotVenn(wf2.sorted_frequency)

    cp.contributionPlot2()
    # wf2.plot_fake_real(wf.sorted_frequency, set_labels=("Reliable", "Fake"))
    # wf.plot()

    # wf.plot_fake_real(wf2.sorted_frequency)
    # plot_in_processes([cp.contributionPlot2, wf.plot])



def runStats2():
    
    wf = Word_frequency()
    ss = Count_Items()
    atf = Article_Type_frequency()
    apply_pipeline(
        CLEANED_DATA, 
        [
            (wf, "content"),
            (ss, "content"),
            (atf, "type")
        ],
        batch_size=100,
        get_batch=True
    )

    print(ss.count)

    # atf.plotDistribution()
    # atf.plotDistribution()
    wf.plot()


runStats()
# clean()



