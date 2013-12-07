#!/usr/bin/env python

import sys
import os
import fnmatch


# Final TRP map as trp_map[mem_addr][unique_mem_references_list] = count
trp_map = {}
# Maps each address to its set index in cache
# TODO: Convert to set instead of map. Memory addresses only read once via cache index
cacheset_addr_map = {}
# Maps each memory address to a list of line numbers in the trace file
addr_lines_map = {}
# The final solution of memory blocks to lock
lock_addresses = {}

num_hit = 0
max_hit = 0


##
# Find number of unique memory references between address reference at indices
# (Same address will be in the file at start_index and end_index
##
def refs_between_lines(file_name, start_index, end_index):
    refs = ()                                    # I need to make this a tuple because it is a key in the final TRP

    fp = open(file_name, 'r')
    lines = fp.readlines()                       # Read all lines of file to list

    for i in range(start_index+1, end_index):
        mem_addr = lines[i].split(' ')[0]        # Get memory addr referenced in line i of the file
        if mem_addr not in refs:                 # Check if mem addr is already in the tuple (Only take unique mem refs)
            refs = refs+(lines[i].split(' ')[0],)    # Add memory address to tuple

    fp.close()
    return refs                                  # This will be a tuple of unique addresses referenced
                                                 # between start and end index in file (non-inclusive)


##
# Get number of hits to addresses in address_set
# given all memory blocks in lockset are locked.
# All addresses in address_set should map to the
# same cache set
##
def get_num_hit(address_set, lock_set):
    global trp_map
    global addr_lines_map

    numhit = 0
    for addr in address_set:
        if addr not in lock_set:
            for s_fs in trp_map[addr]:
                numhit += trp_map[addr][s_fs]
        else:
            numhit += len(addr_lines_map[addr])

    return numhit


OPTIMAL_ALGORITHM = """
##
# addr_set is a copy of cacheset_addr_map[cacheset_index]
##
def do_search(addr_set, lock_set, cache_assoc, cacheset_index):
    global lock_addresses
    global num_hit
    global max_hit

    if (len(lock_set) == cache_assoc) or (len(addr_set) == 0):
        new_hit = get_num_hit(addr_set, lock_set)
        if new_hit > max_hit:
            lock_addresses[cacheset_index] = lock_set
            max_hit = new_hit
            return



##
# Run the optimal locking algorithm for cache set 'cacheset_index'
##
def optimal_cache_locking(cacheset_index, cache_assoc):
    global lock_addresses
    global num_hit
    global max_hit

    lock_addresses[cacheset_index] = ()

    max_hit = get_num_hit(cacheset_addr_map[cacheset_index], set())
    do_search(copy.copy(cacheset_addr_map[cacheset_index]), set(), cache_assoc, cacheset_index)
"""


def heuristic_cache_locking(cacheset_index, cache_assoc):
    lock_addresses[cacheset_index] = set()
    do_continue = True

    while do_continue:
        current_hit = get_num_hit(cacheset_addr_map[cacheset_index], lock_addresses[cacheset_index])
        benefit = 0
        selected_block = ''
        use_addresses = [x for x in cacheset_addr_map[cacheset_index] if x not in lock_addresses[cacheset_index]]
        for addr in use_addresses:
            new_lockset = set(list(lock_addresses[cacheset_index])+[addr])
            new_hit = get_num_hit(cacheset_addr_map[cacheset_index], new_lockset)
            if (new_hit - current_hit) > benefit:
                benefit = new_hit - current_hit
                selected_block = addr

        if benefit > 0:
            lock_addresses[cacheset_index].add(selected_block)
        else:
            do_continue = False
        if len(lock_addresses[cacheset_index]) == cache_assoc:
            do_continue = False


if __name__ == "__main__":

    folder_name = 'trace-stringsearch-small'     # Base folder to search for trace files
    if len(sys.argv) > 1:
        folder_name = sys.argv[1]

    cache_assoc = 2                              # Associativity of cache
    if len(sys.argv) > 2:
        cache_assoc = sys.argv[2]

    file_index = 0

    for file_name in os.listdir(folder_name):
        addr_lines_map = {}

        if fnmatch.fnmatch(file_name, 'trace_file_*'):
            file_name = folder_name+'/'+file_name
            line_number = 0

            # Computing the cache set that the address maps to
            file_name_split = file_name.split('_')
            cacheset_index = file_name_split[len(file_name_split) - 1]

            file_index += 1

            for line in open(file_name, 'r'):    # First read each file to get list of line numbers each addr is in
                address = line.split(' ')[0]     # Get the addr (remove the cache set it wil go to)

                if cacheset_index not in cacheset_addr_map.keys():
                    cacheset_addr_map[cacheset_index] = set()

                cacheset_addr_map[cacheset_index].add(address)       # Storing address to set-index mapping

                if address not in addr_lines_map.keys():
                    addr_lines_map[address] = []

                addr_lines_map[address].append(line_number)
                line_number += 1                 # Add the current line to the list of lines the addr is referenced in

            for addr in addr_lines_map.keys():
                trp_map[addr] = {}               # Initializing map for that addr to empty dict

                for i in range(0, len(addr_lines_map[addr])-1):
                                                 # Get unique memory references between addr at startIndex and endIndex
                                                 # i.e., the unique references between two references of same address
                    refs = refs_between_lines(file_name, addr_lines_map[addr][i], addr_lines_map[addr][i+1])

                    if len(refs) < cache_assoc:  # Only add references if |refs| < associativity
                        if refs not in trp_map[addr].keys():
                            trp_map[addr][refs] = 1
                        else:
                            trp_map[addr][refs] += 1

            heuristic_cache_locking(cacheset_index, cache_assoc)

    print trp_map                                # The final TRP map
    print len(trp_map)
    print lock_addresses
