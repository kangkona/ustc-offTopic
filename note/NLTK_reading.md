

- 遍历序列的各种方式
```
Python 表达式                       评论
for item in s                       遍历 s 中的元素
for item in sorted(s)               按顺序遍历 s 中的元素
for item in set(s)                  遍历 s 中的无重复的元素
for item in reversed(s)             按逆序遍历 s 中的元素
for item in set(s).difference(t)    遍历在集合 s 中不在集合 t 的元素
for item in random.shuffle(s)       按随机顺序遍历 s 中的元素

组合使用显威力： reversed(sorted(set(s)))
```

- zip && enumerate
```
>>> words = ['I', 'turned', 'off', 'the', 'spectroroute']
>>> tags = ['noun', 'verb', 'prep', 'det', 'noun']
>>> zip(words, tags)
[('I', 'noun'), ('turned', 'verb'), ('off', 'prep'),
('the', 'det'), ('spectroroute', 'noun')]
>>> list(enumerate(words))
[(0, 'I'), (1, 'turned'), (2, 'off'), (3, 'the'), (4, 'spectroroute')]
```
对于一些 NLP 的任务,有必要将一个序列分割成两个或两个以上的部分。例如:我们
可能需要用 90%的数据来“训练”一个系统,剩余 10%进行测试。要做到这一点,我们指
定想要分割数据的位置,然后在这个位置分割序列。
```
>>> text = nltk.corpus.nps_chat.words()
>>> cut = int(0.9 * len(text)) 
>>> training_data, test_data = text[:cut], text[cut:] 
>>> text == training_data + test_data 
True
>>> len(training_data) / len(test_data) 4
9
```
我们可以验证在此过程中的原始数据没有丢失,也不是复制。我们也可以验证两块大
小的比例是我们预期的。

让我们综合关于这三种类型的序列的知识,一起使用链表推导处理一个字符串中的词,
按它们的长度排序。
```
>>> words = 'I turned off the spectroroute'.split() 
>>> wordlens = [(len(word), word) for word in words] 
>>> wordlens.sort() 
>>> ' '.join(w for (_, w) in wordlens)
'I off the turned spectroroute'
```

- 从html中提取信息的通用办法
```
import re
def get_text(file):
"""Read text from a file, normalizing whitespace and stripping HTML markup."""
text = open(file).read()
text = re.sub('\s+', ' ', text)
text = re.sub(r'<.*?>', ' ', text)
return text
```

- 防御性编程
```
 def tag(word):
    assert isinstance(word, basestring), "argument to tag() must be a string"
    if word in ['a', 'the', 'all']:
        return 'det'
    else:
        return 'noun'
```
- FreqDist
```
def freq_words(file, min=1, num=10):
    text = open(file).read()
    tokens = nltk.word_tokenize(text)
    freqdist = nltk.FreqDist(t for t in tokens if len(t) >= min)
    return freqdist.keys()[:num]


def freq_words_verbose(file, min=1, num=10, verbose=False):
 '''如果设置了 verbose 标志将会报告其进展情况'''
    freqdist = FreqDist()
    if trace: print "Opening", file
    text = open(file).read()
    if trace: print "Read in %d characters" % len(file)
    for word in nltk.word_tokenize(text):
        if len(word) >= min:
            freqdist.inc(word)
            if trace and freqdist.N() % 100 == 0: print "."
    if trace: print
    return freqdist.keys()[:num]
```

- 调试＆＆Pdb

- CSV :Python有自己的CSV库，csv.reader

> 动态规划是一种在 NLP 中广泛使用的算法设计技术,它存储以前的计算结果,以避免
不必要的重复计算。

文本分类
===

- 过拟合： 如果你提供太多的特征,那么该算法将高度依赖你的训练数据的特性，而一般化到新的例子的效果不会很好。这个问题被称为过拟合。

- devtest： 一旦初始特征集被选定,完善特征集的一个非常有成效的方法是错误分析。首先,我们选择一个开发集,包含用于创建模型的语料数据。然后将这种开发集分为训练集和开发测试集。



- Topic映射到关键词组，映射的越多，表示越切题。
- 不去关注词法，语法阶段的错误，做到隔离。面面俱到的效果未必好。
```
algorithm : 主题检测
input: document
tools: 
     - 特征提取器(eg:给定一些词组，得到对于给定document的`布尔数组`)
     - 训练一个文档分类器
```

- 特征提取函数的行为就像有色眼镜一样,强调我们的数据中的某些属性(颜色),并使
其无法看到其他属性。分类器在决定如何标记输入时,将完全依赖它们强调的属性。


> Written with [StackEdit](https://stackedit.io/).