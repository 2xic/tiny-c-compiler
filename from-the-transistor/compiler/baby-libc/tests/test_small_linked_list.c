// Need to handle imports

// Put this into the PLT
int *malloc(int increment);
int free(int *a);

struct node
{
  int data;
};

int main()
{
  struct node *head = malloc(16);
  head->data = 4;

  int sum = head->data;
  
  return sum;
}
