// Define it for the linker
int *malloc(int increment);

struct node
{
  int data;
  struct node *next;
};

int main()
{
  struct node *head = malloc(16);

  head->data = 4;
  head->next = head;

  struct node *next_value = head->next; // Should hold the same value as the the head

  int sum = next_value->data;  

  return sum;
}
