// Define it for the linker
int *malloc(int increment);
int free(int *a);

struct node
{
  int data;
  struct node *next;
};

int main()
{
  struct node *head = malloc(16);
  // First node
  head->data = 4;
  head->next = 42;

  int sum = 0;
  struct node *current = head;
  
  if (current != 0){
    int value = head->data;
    sum = 4;
  }

  return sum;
}
