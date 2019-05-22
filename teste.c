int global = 181;

int maim(int x){
float a = 0.9;
float b = 0.1;
int c = 0.3 * 0.1212;
global = x * a;
return 0; 
}
//Para criar uma llvm vv
//clang -S -emit-llvm teste.c
