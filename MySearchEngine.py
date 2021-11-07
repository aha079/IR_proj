from collections import *
import math
import re
import os


class PorterStemmer:

    def __init__(self):

        self.b = ""  
        self.k = 0
        self.k0 = 0
        self.j = 0   

    def ends(self, s):

        length = len(s)
        if s[length - 1] != self.b[self.k]: 
            return 0
        if length > (self.k - self.k0 + 1):
            return 0
        if self.b[self.k-length+1:self.k+1] != s:
            return 0
        self.j = self.k - length
        return 1

    def step1(self):
        if self.ends("ها"):    
            self.k = self.k - 2
        elif (self.ends("تر")):
            self.k = self.k - 2    
        elif self.ends("ترین"):   self.k = self.k - 4
        elif self.ends("ام"):   self.k = self.k - 2
        elif self.ends("ان"):   self.k = self.k - 2
        elif (self.ends("ه")):  self.k = self.k - 1
                
    def stem(self, p):
        self.b = p
        self.k = len(p)-1
        self.k0 = 0
        if self.k <= self.k0 + 1:
            return self.b 

        self.step1()
        return self.b[self.k0:self.k+1]

class MySearchEngine:

    def tokenizing(self, text, matched_lists):
        match = []
        match_hypend = re.findall("\w+\-\n+\w*", text)
        for word in match_hypend:
            hypen = word.replace("-\n", "")
            match.append(hypen)
        text = re.sub("\w+\-\n+\w*", "", text)

        match_email = re.findall("\w[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}\w", text)
        match.extend(match_email)
        text = re.sub("\w[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}\w", "", text)

        match_quotation = re.findall("\s+\'(?:.*)'", text)
        for word in match_quotation:
            quotation = word.replace("\n", "")
            match.append(quotation)
        text = re.sub("\s+\'(?:.*)'", "", text)

        match_url = re.findall("https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+", text)
        match.extend(match_url)
        text = re.sub("https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+", "", text)

        match_ip = re.findall("\d{1,3}\.+\d{1,3}\.+\d{1,3}\.+\d{1,9}", text)
        match.extend(match_ip)
        text = re.sub("\d{1,3}\.+\d{1,3}\.+\d{1,3}\.+\d{1,9}", "", text)

        match_acronym = re.findall("((?:[A-Z]\.[A-Z.]*){2,})", text)
        match.extend(match_acronym)
        text = re.sub("((?:[A-Z]\.[A-Z.]*){2,})", "", text)

        match_capital = re.findall("(?:[A-Z][a-z]+\s){2,}", text)
        for word in match_capital:
            capital = word.replace("\n", "")
            match.append(capital)
        text = re.sub("(?:[A-Z][a-z]+\s){2,}", "", text)
        split_list = []
        split_list = re.split("\s+|\n|[,:;(')?!{}.-]\s*", text)
        for element in split_list:
            if element == '':
                split_list.remove(element)
        for element in split_list:
            match.append(element)
        matched_lists.append(match)
        
        return matched_lists


    def stopwords_func(self, matched_lists, stopwords_list):
        outer_list = []
        for lists in matched_lists:
            inner_list = []
            for words in lists:
                inner = words.lower()
                inner_list.append(inner)
            outer_list.append(inner_list)
        Nostopwords = []
        for element in outer_list:
            remove_stopwords = [token for token in element if token not in stopwords_list]
            Nostopwords.append(remove_stopwords)
        return Nostopwords


    def stemming(self, Nostopwords):
        stemmer = PorterStemmer()
        Nostop_outer = []
        for lists in Nostopwords:
            Nostop_inner = []
            for words in lists:
                stem = stemmer.stem(words)
                if stem != '':
                    Nostop_inner.append(stem)
            Nostop_outer.append(Nostop_inner)
        return Nostop_outer

    def termFrequency(self, Nostop_outer):
        termfrequency = []
        for inner_list in Nostop_outer:
            counts = Counter(inner_list)
            termfrequency.append(counts)
        return termfrequency

    def idf(self, termfrequency, document_ID):
        DF = defaultdict(int)
        keys = []
        dic_idf = {}
        for dic in termfrequency:
            for key in dic:
                keys.append(key)
        for word in keys:
            DF[word] += 1

        for key in DF:
            idf = math.log10(len(document_ID) / (DF[key] + 1))
            dic_idf[key] = round(idf, 3)

        i = 0
        for dic in termfrequency:
            dic['doc_id'] = document_ID[i]
            i += 1
        return dic_idf

    def invert_file(self, termfrequency, dic_idf):
        text_string = ""
        for key in dic_idf:
            term = key
            for dic in termfrequency:
                if key in dic:
                    term = term + "," + str(dic['doc_id']) + "," + str(dic[key])
            term = term + "," + str(round(dic_idf[key], 3))
            text_string = text_string + "\n" + term
        save_path = '.'
        output = os.path.join(save_path, "index.txt")
        output_file = open(output, "w", encoding="utf8")
        output_file.write(text_string)
        output_file.close()

    def Document_vector(self, termfrequency, dic_idf):
        document_vector = {}
        weight = []
        term = []
        for dic in termfrequency:
            each_term = []
            each_weight = []
            for vocab in dic_idf:
                each_term.append(vocab)
                if vocab in dic:
                    tf_idf = dic[vocab] * dic_idf[vocab]
                    each_weight.append(tf_idf)
                if vocab not in dic:
                    tf_idf = 0
                    each_weight.append(tf_idf)
            weight.append(each_weight)
            term.append(each_term)
        document_vector = [dict(zip(*z)) for z in zip(term, weight)]
        return document_vector

    def Query_vector(self, dic_idf, stopwords_list):
        query = input("Please enter query(if you want exit enter exit):")
        query_tokens = []
        query_list = []
        query_tokens = query.split()
        stemmed_list = []
        if query_tokens[0]=="exit":
            return [],2
        for words in query_tokens:
            if words.lower() not in stopwords_list:
                query_list.append(words)

        stemmer = PorterStemmer()
        for words in query_list:
            stem = stemmer.stem(words)
            stemmed_list.append(stem)
        query_dic = Counter(stemmed_list)
        flag = 0
        query_vector = {}
        if any(key in dic_idf for key in query_dic) == True:
            query_term = []
            query_weight = []
            for vocab in dic_idf:
                query_term.append(vocab)
                if vocab in query_dic:
                    tfidf_query = query_dic[vocab] * dic_idf[vocab]
                    query_weight.append(tfidf_query)
                else:
                    tfidf_query = 0
                    query_weight.append(tfidf_query)        
            query_vector = dict(zip(query_term, query_weight))
        else:
            flag = 1
        return query_vector, flag

    def cosine_similarity(self, document_vector, query_vector, document_ID):
        cosine_list = []
        for doc in document_vector:
            num = 0
            denum = 0
            sum_doc = 0
            sum_query = 0
            for key in doc:
                num = num + doc[key] * query_vector[key]
                sum_doc = sum_doc + (doc[key] * doc[key])
                sum_query = sum_query + (query_vector[key] * query_vector[key])
                denum = (math.sqrt(sum_doc)) * (math.sqrt(sum_query))
            cosine_list.append(round((num / denum), 3))
        cosine_dic = {}
        for i in range(0, len(document_ID)):
            if abs(cosine_list[i]-0)<0.00001:
                continue
            cosine_dic[document_ID[i]] = cosine_list[i]
        cosine_dic = sorted(cosine_dic.items(), key=lambda x: x[1], reverse=True)
        return cosine_dic



def main():
    path = "doc"
    document_ID = []
    searchEngine = MySearchEngine()
    matched_lists = []
    for file in os.listdir(path):
        document_ID.append(file)
        filename = os.path.join(path, file)
        file = open(filename, "r", encoding="utf8")
        text = file.read()
        matched_lists = searchEngine.tokenizing(text, matched_lists)
    stop = open("stopword.txt","r")
    stopwords = stop.read()
    stopwords_list = []
    for word in stopwords.split():
        stopwords_list.append(word)

    Nostopwords = searchEngine.stopwords_func(matched_lists, stopwords_list)
    Nostop_outer = searchEngine.stemming(Nostopwords)
    termfrequency = searchEngine.termFrequency(Nostop_outer)
    idf = searchEngine.idf(termfrequency, document_ID)
    tf = termfrequency
    searchEngine.invert_file(tf, idf)
    document_vector = searchEngine.Document_vector(tf, idf)
    while(1):
        query_v = searchEngine.Query_vector(idf, stopwords_list)
        query_vector = query_v[0]
        flag = query_v[1]
        if flag==2:
            break
        if flag == 1:
            print("No Match found")
        else:
            cosine_dic = searchEngine.cosine_similarity(document_vector, query_vector, document_ID)
        for item in cosine_dic:
            print(item)


main()
