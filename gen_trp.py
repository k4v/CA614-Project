#!/usr/bin/env python

import sys
import os
import fnmatch


##
# Find number of unique memory references between address reference at indices
# (Same address will be in the file at start_index and end_index
##
def refs_between_lines(file_name, start_index, end_index):
    refs = tuple()

    fp = open(file_name, 'r')
    lines = fp.readlines()    # Read all lines of file to list

    for i in range(start_index+1, end_index):
        mem_addr = lines[i].split(' ')[0]    # Get memory addr referenced in line i of the file
        if mem_addr not in refs:    # Check if mem addr is also in the tuple (Only take unique mem references)
            refs = refs+(lines[i].split(' ')[0],)    # Add memory address to tuple

    fp.close()

    return refs    # This will be unique addresses referenced between start and end index in file (non-inclusive)


if __name__ == "__main__":

    folder_name = 'trace-stringsearch-small'    # Base folder to search for trace files
    if len(sys.argv) > 1:
        folder_name = sys.argv[1]

    cache_assoc = 2
    if len(sys.argv) > 2:
        cache_assoc = sys.argv[2]

    trp_map = dict()    # Final TRP map as trp_map[mem_addr][unique_mem_references_list] = count

    file_index = 0

    for file_name in os.listdir(folder_name):
        addr_list = dict()

        if fnmatch.fnmatch(file_name, 'trace_file_65'):
            file_name = folder_name+'/'+file_name
            line_number = 0

            file_index += 1
            print str(file_index)+' '+file_name

            for line in open(file_name, 'r'):
                address = line.split(' ')[0]

                if address not in addr_list.keys():
                    addr_list[address] = []

                addr_list[address].append(line_number)
                line_number += 1

            print addr_list

            for addr in addr_list.keys():
                trp_map[addr] = {(): 0}
                print 'Computing TCS for '+addr
                for i in range(0, len(addr_list[addr])-1):
                    refs = refs_between_lines(file_name, addr_list[addr][i], addr_list[addr][i+1])

                    if len(refs) < cache_assoc:
                        if refs not in trp_map[addr].keys():
                            trp_map[addr][refs] = 1
                        else:
                            trp_map[addr][refs] += 1

                    print refs

    print trp_map
