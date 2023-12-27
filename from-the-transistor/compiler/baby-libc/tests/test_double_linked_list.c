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

  head->data = 4;
  head->next = middle;

  middle->data = 8;
  middle->next = 0;

  struct node *next_value = head->next;

  //int sum_a = head->data;
  int sum_b = next_value->data; // This dereference does not work.
  
  int sum = /*sum_a +*/ sum_b;

  return sum;
}
