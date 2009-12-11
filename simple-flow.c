int lol(int a, int b)
{
    int *ptr;
    if (a + 1 == 42) {
        ptr = b;
        a = *ptr;
    }
    return 1;
}
