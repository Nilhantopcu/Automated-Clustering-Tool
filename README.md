# Işık University Departmental Web Pages Clustering
## Overview
This project is a simple tool for crawling Işık University's departmental web pages and clustering them based on their content using various clustering methods. The project aims to evaluate the performance of clustering algorithms when applied to departmental web pages.

## Crawling Işık University's Departmental Web Pages
The program starts crawling Işık University's departmental web pages from the seed URL: https://www.isikun.edu.tr/international/programs. The crawling process is limited to 1 level (depth = 2) starting from the seed page.

During the crawling phase, the program creates a word/frequency matrix (departmental_data.txt) representing the downloaded web pages. Only pages containing departmental information are indexed.

## Clustering
After the crawling process, the program prompts the user to choose a clustering technique (Hierarchical or K-means). For K-means clustering, the user can specify the value of k (default is 5).

- For Hierarchical Clustering, the results are shown as a string dendrogram.
- For K-Means Clustering, the results are displayed in text form by listing each member of each cluster.

## Usage
1. Run the program
2. Follow the on-screen instructions to crawl pages and perform clustering.
3. Change clustering method or regenerate clusters as needed.

## Important Notes
- The program indexes only pages containing departmental information.
- Please clearly indicate your method to discriminate pages for indexing.
- Provide suggestions to improve clustering performance and verify them.
