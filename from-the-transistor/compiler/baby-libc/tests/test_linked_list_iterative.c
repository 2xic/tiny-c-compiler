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
  head->next = middle;
  // Next node
  middle->data = 8;
  middle->next = tail;
  // Last node
  tail->data = 16;
  tail->next = 0;

  int sum = 0;
  struct node *current = head;

  
  if(current != 0){
    int value = current->data;
    int next = current->next; 
    current = next;
    sum = sum + value;
  }
  if(current != 0){
    int value = current->data;
    int next = current->next; 
    current = next;
    sum = sum + value;
  }
  if(current != 0){
    int value = current->data;
    int next = current->next; 
    current = next;
    sum = sum + value;
  }
  // THe firth ... Should not be accessed.
  if(current != 0){
    int value = current->data;
    int next = current->next; 
    current = next;
    sum = sum + value;
  }


  return sum;
}
