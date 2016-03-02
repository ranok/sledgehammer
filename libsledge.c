/*
  Library designed to be used via the LD_PRELOAD option to cause common library
  functions to fail, testing the error handling capabilities of the program.

  To use, build with 'make libsledge' and set the environment variable LD_PRELOAD to 
  ./libsledge.so before executing the program's unit test or other testing framework.

  Author: Jacob Torrey <jacob@jacobtorrey.com>
  Date: 3/2/2016
*/

#define __USE_GNU
#define _GNU_SOURCE

#include <dlfcn.h>
#include <time.h>
#include <stdlib.h>
#include <stdio.h>

#ifndef FAIL_PROB
#define FAIL_PROB 50
#endif // Ends FAIL_PROB

static void * (*libc_malloc)(size_t) = NULL;

static void init_malloc(void)
{
  libc_malloc = dlsym(RTLD_NEXT, "malloc");
  if (NULL == libc_malloc) {
    fprintf(stderr, "Unable to find libc's malloc: %s\r\n", dlerror());
    exit(-1);
  }
}

/* Overload malloc() system call to randomly fail */
void * malloc(size_t sz) 
{
  if (NULL == libc_malloc) {
    init_malloc();
    srand(time(NULL));
  }
  if ((rand() % 100) + 1 > FAIL_PROB) {
    return NULL;
  } else {
    return libc_malloc(sz); 
  }
}

