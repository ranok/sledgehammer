#include <stdlib.h>
#include <stdio.h>

#include "../poisonpill.h"

int main()
{
  int i = 1;
  while (i <= 100) {
    if (i % 3 == 0) {
      printf("fizz");
    }
    if (i % 5 == 0) {
      printf("buzz");
    }
    if (i % 3 != 0 && i % 5 != 0) {
      printf("%d", i);
    }
    printf("\r\n");
    i++;
  }
  return 0;
}
