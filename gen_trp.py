#!/usr/bin/env python

import sys;
import os;
import fnmatch;

def refs_between_lines(fileName, startIndex, endIndex):
    refs = set();
    fp = open(fileName, 'r');
    lines = fp.readlines();
    for i in range(startIndex+1, endIndex):
        refs.add(lines[i].split(' ')[0]);
    #for i, line in enumerate(fp):
    #    if (i>startIndex and i<endIndex):
    #        refs.add(line.split(' ')[0]);
    #    if i >= endIndex:
    #        break;
    fp.close();

    return refs;


if __name__=="__main__":

    folderName='.';
    if(len(sys.argv)>1):
        folderName=sys.argv[1];
    
    if(len(sys.argv)>2):
        assoc=sys.argv[2];

    i=0;

    for fileName in os.listdir(folderName):
        addr_list = dict();
        i=i+1;

        if fnmatch.fnmatch(fileName, 'trace_file_*'):
            fileName = folderName+'/'+fileName;
            lineNumber=0;

            print str(i)+' '+fileName;
            
            for line in open(fileName, 'r'):
                address = line.split(' ')[0];
                #print address;
                if address not in addr_list.keys():
                    addr_list[address]=[];

                addr_list[address].append(lineNumber);
                lineNumber+=1;

            #print addr_list;

            for addr in addr_list.keys():
                for i in range(0, len(addr_list[addr])-1):
                    refs = refs_between_lines(fileName, addr_list[addr][i], addr_list[addr][i+1]);
                    #print refs;

    #print addr_list;
