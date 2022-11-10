# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

import os
import sys
import urllib.request
from functools import lru_cache
from multiprocessing import Pool, TimeoutError

import numpy as np
from bs4 import BeautifulSoup
from serpapi import GoogleSearch

from qa.util import pretty_print

import json


def blockPrint():
    """Calling this function stops the serpAPI from print to stdout."""

    sys.stdout = open(os.devnull, "w")


def enablePrint():
    """This function undos blockPrint, restoring standard stdout behavior."""

    sys.stdout = sys.__stdout__


def cosine_similarity(a, b):
    """Compute the cosine similarity between vectors a and b."""

    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


@lru_cache(maxsize=256)
def serp_api_google_search(search_term, serp_api_token, url):
    """Search Google based on a query, a return an object containing results.

    Returns:
        GoogleSearch object with the results of the search.
    """

    q = search_term
    if url:
        q = f"site:{url} {search_term}"
    params = {
        "api_key": serp_api_token,
        "engine": "google",
        "q": q,
        "google_domain": "google.com",
        "gl": "us",
        "hl": "en",
        "num": "5"
    }
    blockPrint()
    # https://github.com/serpapi/google-search-results-python
    results = GoogleSearch(params)
    print("WHAT")
    enablePrint()
    return results


def serp_api_search(search_term, serp_api_token, url, verbosity=0):
    """Iterates over organic results and top stories.
    
    Returns: 
        a list of tuples of the form (url, text)
    """

    # When running "grounded qa" as Docker, then check directory /serpapi-dumps
    file_name_serpapi_dump = "/serpapi-dumps/serpapi_search_results.json"
    if os.path.isfile("serpapi_search_results.json"):
        # When running "grounded qa" from the command line, then check current directory
        file_name_serpapi_dump = "serpapi_search_results.json"

    results = None

    if verbosity > 1:
        pretty_print("OKGREEN", f"Check whether SerpAPI dump file exists '{file_name_serpapi_dump}' ...")
    if os.path.isfile(file_name_serpapi_dump):
        if verbosity > 1:
            pretty_print("OKGREEN", f"Load local JSON file: {file_name_serpapi_dump}")
        json_file = open(file_name_serpapi_dump)
        results = json.load(json_file)
        json_file.close()
    else:
        response = serp_api_google_search(search_term, serp_api_token, url)
        results = response.get_dict()
        if verbosity > 1:
            pretty_print("OKGREEN", f"Search results from SerpAPI/Google: {results}")

    response_urls = []
    text = ""
    url = ""
    for key in ["organic_results", "top_stories"]:
        if key in results:
            i = 0
            while i < len(results[key]):
                url = results[key][i]["link"]
                if "snippet" in results[key][i]:
                    text = results[key][i]["snippet"]
                i += 1
                if verbosity > 1:
                    pretty_print("OKGREEN", f"URL from SerpAPI/Google: {url}")
                response_urls.append([url, text])
    return response_urls


def open_link(url):
    """Follow a link and return its contents.

    Returns:
        html of the page
    """

    user_agent = "Mozilla/5.0"

    headers = {
        "User-Agent": user_agent,
    }

    pretty_print("OKGREEN", f"Open link '{url}' ...")

    request = urllib.request.Request(url, None, headers)  # The assembled request
    response = urllib.request.urlopen(request)
    return response


def paragraphs_from_html(body):
    """Extract a list of paragraphs from the html."""

    pretty_print("OKGREEN", f"Extract content from HTML '{body}' ...")

    soup = BeautifulSoup(body, "html.parser")
    paragraphs = []
    for data in soup.find_all("p"):
        tag = data.get_text()
        if not tag.isspace() and len(tag.split()) > 10:
            paragraphs.append(tag)
    return paragraphs


def get_paragraphs_text_from_url(k):
    """Extract a list of paragraphs from the contents pointed to by an url."""

    i, search_result_url = k
    try:
        pretty_print("OKGREEN", f"Try to load data from '{search_result_url}' ...")
        html = open_link(search_result_url)
        return paragraphs_from_html(html)
    except Exception as e:
        pretty_print("FAIL", f"ERROR: Page '{search_result_url}' could not be loaded! Exception: {e}")
        return []


def get_results_paragraphs_multi_process(search_term, serp_api_token, url=None, verbosity=0):
    """Given a query, retrieve relevant paragraphs from the search results.
    
    This function will first search for documents matching a query. Then, for
    each document amongst the most relevant documents in that set, it will find
    the paragraph which most closely matches the query, and aggregate those in
    a list, which is returned.
    """

    results = serp_api_search(search_term, serp_api_token, url, verbosity)

    if not results:
        pretty_print("FAIL", f"No search results")
        return [], []

    urls = [r[0] for r in results][:5]
    url_paragraphs = [[]] * len(urls)
    indexed_urls = list(zip(range(len(urls)), urls))

    def async_handle_timeout(res):
        try:
            result = res.get(timeout=3)
            return result
        except TimeoutError:
            pretty_print("FAIL", f"Timeout Error!")
            return []

    pool = Pool(len(urls))
    multiple_results = [pool.apply_async(get_paragraphs_text_from_url, args=(url,)) for url in indexed_urls]
    url_paragraphs = [async_handle_timeout(res) for res in multiple_results]

    paragraphs = []
    paragraph_sources = []
    for i in range(len(url_paragraphs)):
        if verbosity > 1:
            pretty_print("OKGREEN", f"Append paragraph '{url_paragraphs[i]}' ...")
        paragraphs += url_paragraphs[i]
        paragraph_sources += [urls[i]] * len(url_paragraphs[i])
    return paragraphs, paragraph_sources


def embedding_search(paragraphs, paragraph_sources, search_term, co, model="small", verbosity=0):
    """Embed paragraphs and search for the closest ones to a query."""

    if verbosity > 1:
        pretty_print("OKGREEN", f"Get embeddings for paragraphs and search term '{search_term}' ...")

    embeddings = co.embed(texts=paragraphs + [search_term], model=model, truncate="LEFT").embeddings
    paragraph_embeddings = embeddings[:-1]
    search_embedding = embeddings[-1]
    distances = [cosine_similarity(x, search_embedding) for x in paragraph_embeddings]
    return sorted(list(zip(paragraphs, paragraph_sources, distances)), key=lambda x: x[2])
