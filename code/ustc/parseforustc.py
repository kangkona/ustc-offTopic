# -*- coding:UTF-8 -*-  
  
import xml.etree.ElementTree as ET  
import xml.dom.minidom as minidom
import re
  
#获取根节点  
def getRoot(xmlpath):  
    '''  
    xmlpath:xml文件的路径  
    '''  
    root = ET.parse(xmlpath).getroot()  
    return root  
  
#格式化输出xml文件  
def display(root):  
    rough_string = ET.tostring(root, 'utf-8')  
    reparsed = minidom.parseString(rough_string)  
    print reparsed.toprettyxml(indent="  " , encoding="utf-8");

def string2dict(strings):
    dict0 = {}
    for string in strings:
        lst = string.split()
        if len(lst) > 1:
            k = lst[0]
            v = string[len(k)+1:]
            dict0[k] = v
    return dict0

def parse(filename):
    fin = open(filename,"r")
    '''s.seek(0)'''
#     content = infile.read()
    docs = ET.Element('docs')
    pattern = re.compile(">\s+<")
    para_no = 0
    doc = None
    while True:
        line  = fin.readline()
        if not line:break
        if line.startswith(r'<TITLE'):
            line = line[1:-1]
            meta_list = re.split(pattern,line)
            meta_dict = string2dict(meta_list)
            doc = ET.SubElement(docs, "doc")
            for (k,v) in meta_dict:
                doc.set(k.lower(),v)
                
            para_no = 0
        
        else:
            para_no+=1
            if doc:
                para = ET.SubElement(doc,"para")
                para.set("number",para_no)
                line_nocorrect = re.sub('\[[^]]+\]','',line) #将对作文的批改内容去掉，还原回本来的作文
                para.set("content",line_nocorrect)
                para_errors = re.findall('\[[^]]+\]',line)

def filter(infile,outfile="ustc_out"):
    text = open(infile, "r")
    fout = open(outfile,"w")
    result = ""
    while True:
        line = text.readline()
        if not line:break
        if line.startswith(r'<TITLE'):
            result+="<start>"
            continue
        result+=line
    text.close()
    raw = re.sub('\[[^]]+\]','',result)
    fout.write(raw)
    fout.close()
    
         
        
    
             
                  
if __name__ == '__main__':
    filter("1_110101_ustc")  
