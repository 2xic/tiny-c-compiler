// Need to handle imports

// Put this into the PLT
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
  struct node *middle = malloc(16);
  struct node *tail = malloc(16);

  // First node
  head->data = 4;
  head->next = 0;
  // Next node
  middle->data = 8;
  middle->next = tail;
  // Last node
  tail->data = 16;
  tail->next = 0;

  int sum = 0;
  struct node *current = head;

  int a = 0;
  
  if (current != 0)
  {
    int sum_value = current->data;

    sum = sum + sum_value;
    current = current->next;
    a++;
  }

  return sum;
}
