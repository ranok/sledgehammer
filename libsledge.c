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
static void * (*libc_calloc)(size_t, size_t) = NULL;
static void * (*libc_realloc)(void *, size_t) = NULL;

#define REPLACE(func) \
static void init_ ## func(void) \
{ \
  libc_ ## func = dlsym(RTLD_NEXT, #func); \
  if (NULL == libc_ ## func) { \
    fprintf(stderr, "Unable to find libc's " #func ": %s\r\n", dlerror()); \
    exit(-1); \
  } \
}

REPLACE(malloc)

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

REPLACE(calloc)

void * calloc(size_t num, size_t sz) 
{
  if (NULL == libc_calloc) {
    init_calloc();
    srand(time(NULL));
  }
  if ((rand() % 100) + 1 > FAIL_PROB) {
    return NULL;
  } else {
    return libc_calloc(num, sz); 
  }
}

REPLACE(realloc)

void * realloc(void * ptr, size_t sz)
{
  if (NULL == libc_realloc) {
    init_realloc();
    srand(time(NULL));
  }
  if ((rand() % 100) + 1 > FAIL_PROB) {
    return NULL;
  } else {
    return libc_realloc(ptr, sz);
  }
}
