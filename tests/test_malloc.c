#include <stdlib.h>
#include <stdio.h>

int main()
{
  char * str = malloc(32);
  printf("Malloc'd buffer at: 0x%p\r\n", str);
  
  // Make sure to NULL-terminate the buffer for safety!
  str[31] = '\0';

  return 0;
}
