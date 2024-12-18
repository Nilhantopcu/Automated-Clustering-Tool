import urllib.request as urllib2
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import shelve
import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import sys

ignorewords = set(['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it'])

class Crawler:
    def __init__(self, dbtables):
        self.dbtables = dbtables

    def __del__(self):
        self.close()

    def close(self):
        if hasattr(self, 'urllist'): self.urllist.close()
        if hasattr(self, 'wordlocation'): self.wordlocation.close()
        if hasattr(self, 'link'): self.link.close()
        if hasattr(self, 'linkwords'): self.linkwords.close()

    def add_to_index(self, url, soup):
        if self.is_indexed(url):
            print('skip', url + ' already indexed')
            return False

        print('Indexing ' + url)
        url = str(url) 
        
        text = self.get_text_only(soup)
        words = self.separate_words(text)

        for word in words:
            word = str(word) 

            if word in ignorewords:
                continue

            self.wordlocation.setdefault(word, {})

            self.wordlocation[word].setdefault(url, [])
            self.wordlocation[word][url].append(1)  

        return True

    def create_word_frequency_matrix(self):
        with open('departmental_data.txt', 'w') as f:
            for word, locations in self.wordlocation.items():
                f.write(word + '\t')
                for url, freq in locations.items():
                    f.write(f'{url}:{freq[0]}\t')
                f.write('\n')

    def crawl(self, pages, depth=2):
        for i in range(depth):
            newpages = set()
            for page in pages:
                try:
                    c = urllib2.urlopen(page)
                except:
                    print("Could not open {}".format(page))
                    continue
                soup = BeautifulSoup(c.read(), 'html.parser')
                added = self.add_to_index(page, soup)

                if not added:
                    continue

                outgoing_link_count = 0
                links = soup('a')
                for link in links:
                    if 'href' in link.attrs:
                        url = urljoin(page, link['href'])
                        if url.find("'") != -1:
                            continue
                        url = url.split('#')[0] 
                        if url[0:4] == 'http' and not self.is_indexed(url):
                            newpages.add(url)
                        link_text = self.get_text_only(link)
                        added = self.add_link_ref(page, url, link_text)
                        if added:
                            outgoing_link_count += 1

                self.urllist[str(page)] = outgoing_link_count
            pages = newpages

    def is_indexed(self, url):
        if not self.urllist.get(str(url)):
            return False
        else:
            return True

    def add_link_ref(self, url_from, url_to, link_text):
        from_url = str(url_from)  
        to_url = str(url_to)  

        if from_url == to_url:
            return False

        self.link.setdefault(to_url, {})
        self.link[to_url][from_url] = None

        words = self.separate_words(link_text)
        for word in words:
            word = str(word)  

            if word in ignorewords:
                continue

            self.linkwords.setdefault(word, [])

            self.linkwords[word].append((from_url, to_url))

        return True

    def create_index_tables(self):
        self.urllist = shelve.open(self.dbtables['urllist'], writeback=True, flag='c')
        self.wordlocation = shelve.open(self.dbtables['wordlocation'], writeback=True, flag='c')
        self.link = shelve.open(self.dbtables['link'], writeback=True, flag='c')
        self.linkwords = shelve.open(self.dbtables['linkwords'], writeback=True, flag='c')

    def get_text_only(self, soup):
            v = soup.string
            if v is None:
                c = soup.contents
                result_text = ''
                for t in c:
                    sub_text = self.get_text_only(t)
                    result_text += sub_text + '\n'
                return result_text
            else:
                return v.strip()

    def separate_words(self, text):
        splitter = re.compile('\\W+')
        return [s.lower() for s in splitter.split(text) if s != '']

    def cluster_pages(self):
        clustering_technique = input("Hangi kümeleme tekniğini kullanmak istersiniz? (Hiyerarşik / K-ortalama): ").lower()

        if clustering_technique == 'hiyerarşik':
            self.hierarchical_clustering()
        elif clustering_technique == 'k-ortalama':
            k_value = int(input("K-ortalama kümeleme için k değerini girin (varsayılan: 5): ") or 5)
            self.k_means_clustering(k_value)
        else:
            print("Geçersiz kümeleme tekniği. Lütfen 'Hiyerarşik' veya 'K-ortalama' seçin.")

    def format_dendrogram(den, labels):
        def llf(id):
            return labels[id]

        plt.figure(figsize=(12, 8))
        dendrogram(den, leaf_label_func=llf, leaf_rotation=0, leaf_font_size=12, orientation='right')
        plt.show()

    def hierarchical_clustering(self):
        data = self.prepare_data_for_clustering()
        linkage_matrix = linkage(data, 'ward')
        labels = list(self.wordlocation.keys())
        self.plot_dendrogram(linkage_matrix, labels)  

    def plot_dendrogram(self, den, labels):
        def llf(id):
            return labels[id]

        plt.figure(figsize=(12, 8))
        dendrogram(den, leaf_label_func=llf, leaf_rotation=0, leaf_font_size=12, orientation='right')
        plt.show()



    def k_means_clustering(self, k):
        data = self.prepare_data_for_clustering()

        kmeans = KMeans(n_clusters=k, random_state=0)
        clusters = kmeans.fit_predict(data)

        for cluster_id in range(k):
            members = [word for word, cluster in zip(self.wordlocation.keys(), clusters) if cluster == cluster_id]
            print(f"Cluster {cluster_id + 1}: {members}")

    def prepare_data_for_clustering(self):
        data = []
        for word, locations in self.wordlocation.items():
            row = [locations.get(url, [0])[0] for url in self.urllist.keys()]
            data.append(row)

        return np.array(data)


sys.setrecursionlimit(10000)  

db_tables = {'urllist': 'urllist', 'wordlocation': 'wordlocation', 'link': 'link', 'linkwords': 'linkwords'}
my_crawler = Crawler(db_tables)
my_crawler.create_index_tables()
pages_to_crawl = ['https://www.isikun.edu.tr/international/programs']
my_crawler.crawl(pages_to_crawl)
my_crawler.create_word_frequency_matrix()

my_crawler.cluster_pages()
my_crawler.close()
