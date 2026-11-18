/* C-style C++ starting point. Replace the data structure for each problem.
   Keep ElemType and use a typedef appropriate for that problem's tests.
   Compile: g++ -std=c++11 -Wall -Wextra -pedantic solution.cpp -o solution */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

typedef int ElemType;

typedef struct {
    ElemType *data;
    size_t size;
    size_t capacity;
} Stack;

/* Call once on a new Stack. Destroy it before initializing it again. */
int StackInit(Stack *stack, size_t capacity) {
    if (stack == NULL) {
        return 0;
    }
    stack->data = NULL;
    stack->size = 0;
    stack->capacity = 0;
    if (capacity == 0 || capacity > SIZE_MAX / sizeof(ElemType)) {
        return 0;
    }
    stack->data = (ElemType *)malloc(capacity * sizeof(ElemType));
    stack->size = 0;
    stack->capacity = stack->data == NULL ? 0 : capacity;
    return stack->data != NULL;
}

int StackPush(Stack *stack, ElemType value) {
    if (stack == NULL || stack->size == stack->capacity) {
        return 0;
    }
    stack->data[stack->size++] = value;
    return 1;
}

int StackPop(Stack *stack, ElemType *value) {
    if (stack == NULL || value == NULL || stack->size == 0) {
        return 0;
    }
    *value = stack->data[--stack->size];
    return 1;
}

void StackDestroy(Stack *stack) {
    if (stack != NULL) {
        free(stack->data);
        stack->data = NULL;
        stack->size = 0;
        stack->capacity = 0;
    }
}

int main(void) {
    Stack stack = {NULL, 0, 0};
    ElemType value = 0;
    if (!StackInit(&stack, 2)) {
        return 1;
    }
    int ok = !StackPop(&stack, &value);
    ok = ok && StackPush(&stack, 10);
    ok = ok && StackPush(&stack, 20);
    ok = ok && !StackPush(&stack, 30);
    ok = ok && StackPop(&stack, &value) && value == 20;
    ok = ok && StackPop(&stack, &value) && value == 10;
    ok = ok && !StackPop(&stack, &value);
    StackDestroy(&stack);
    printf("stack template tests: %s\n", ok ? "PASS" : "FAIL");
    return ok ? 0 : 1;
}
