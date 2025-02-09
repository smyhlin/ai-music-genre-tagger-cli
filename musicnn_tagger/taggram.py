#!filepath: musicnn_tagger/taggram.py
from musicnn.extractor import extractor
import numpy as np
import matplotlib.pyplot as plt
import logging

logger = logging.getLogger(__name__)


def init_extractor(music_path = '', model='MSD_musicnn_big'):
    """
    Initializes the musicnn extractor for a given music path and model.
    Renamed from init_extractor to init_extractor for clarity and consistency.
    """
    # music_path = r"D:\GITHB\yt not found\Supersonic   FINIVOID.mp3"
    if 'vgg' in model:
        input_length = 3
    else:
        input_length = 30

    try: # Problem 4: Handle MSD_musicnn_big availability, use try-except to catch potential model loading issues
        taggram, tags = extractor(music_path, model, extract_features=False, input_length=input_length)
        return taggram, tags
    except Exception as e:
        logger.error(f"Error initializing extractor with model {model}: {e}")
        raise # Re-raise exception to be handled in tagger.py


def show_taggram(taggram, tags):
    """
    Displays the taggram visualization.
    """
    plt.rcParams["figure.figsize"] = (10,8) # set size of the figures
    fig, ax = plt.subplots()
    fontsize = 8 # set figures font size
    # title
    ax.title.set_text('Taggram')
    ax.title.set_fontsize(fontsize)
    in_length = 3 # seconds  by default, the model takes inputs of 3 seconds with no overlap

    # x-axis title
    ax.set_xlabel('(seconds)', fontsize=fontsize)

    # y-axis
    y_pos = np.arange(len(tags))
    ax.set_yticks(y_pos)
    ax.set_yticklabels(tags, fontsize=fontsize-1)

    # x-axis
    x_pos = np.arange(taggram.shape[0])
    x_label = np.arange(in_length/2, in_length*taggram.shape[0], 3)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x_label, fontsize=fontsize)

    # depict taggram
    ax.imshow(taggram.T, interpolation=None, aspect="auto")
    plt.show()


def show_tags_likelihood_mean(taggram, tags):
    """
    Displays the tags likelihood mean visualization.
    """
    plt.rcParams["figure.figsize"] = (10,8) # set size of the figures
    tags_likelihood_mean = np.mean(taggram, axis=0) # averaging the Taggram through time
    fig, ax = plt.subplots()
    fontsize = 8 # set figures font size

    # title
    ax.title.set_text('Tags likelihood (mean of the taggram)')
    ax.title.set_fontsize(fontsize)

    # y-axis title
    ax.set_ylabel('(likelihood)', fontsize=fontsize)

    # y-axis
    ax.set_ylim((0, 1))
    ax.tick_params(axis="y", labelsize=fontsize)

    # x-axis
    ax.tick_params(axis="x", labelsize=fontsize-1)
    pos = np.arange(len(tags))
    ax.set_xticks(pos)
    ax.set_xticklabels(tags, rotation=90)

    # depict song-level tags likelihood
    ax.bar(pos, tags_likelihood_mean)
    plt.show()


def get_sorted_tag_weights(taggram, tags):
    """
    Calculates and returns sorted tag weights from a taggram.
    Renamed from get_sorted_tag_weights to get_sorted_tag_weights for clarity and consistency.
    """
    tags_likelihood_mean = np.mean(taggram, axis=0)
    tag_weight_dict = dict(zip(tags, tags_likelihood_mean))
    sorted_tags = dict(sorted(tag_weight_dict.items(), key=lambda x: x[1], reverse=True))
    return sorted_tags

if __name__ == '__main__':
    music_path = r"music_root_folder_path"
    taggram, tags = init_extractor(music_path)
    show_taggram(taggram, tags)
    show_tags_likelihood_mean(taggram, tags)
    print(get_sorted_tag_weights(taggram, tags))