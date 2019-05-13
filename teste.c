#include<stdio.h>

int or(int a,float b){
	int c = a+1;
	return c;
}

float retFloat(){
	return 1.0;
}

int main(){
	return 0;
}
//Para criar uma llvm vv
//clang -S -emit-llvm teste.c  
