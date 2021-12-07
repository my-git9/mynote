[toc]



# 四种变量声明

```go
package main
import (
	"fmt"
)
func main(){
   // 方法一：声明一个变量 默认的值是0
	 var a int
	 fmt.Println("a=", a)
	 fmt.Printf("type of a = %T\n", a)
	 
   // 方法二：声明一个变量，初始化一个值,%T:通配字符类型
	 var b sting = 'bbbbbb'
	 fmt.Printf("bb = %s, type of aa=%T\n", b, b)
	 
	 // 方法三：在初始化的时候，可以省去数据类型，通过值自动匹配当前的数据类型
	 var c = 100
	 fmt.Println("c=", c)
  
  // 方法四：(常用的方法)省去var关键字，直接自动匹配
  // 只能放在函数体内
   e := 100
  fmt.Println("e=", e)
  
  //声明多个变量
  var xx, yy = 100, 200
  fmt.Println("xx=", xx, ",yy=",yy)
  
  var (
  	vv int = 100
    jj bool = true
  )
  fmt.Println("vv=",vv, ",jj=", jj)
}
```

# 常量

```go
package main

import (
	"fmt"
)
//const 来定义枚举类型:iota
// iota只能配合const使用
const (
  //可以在const()添加一个关键字iota,每行iota都会累加1，第一行的iota默认值是0
  BEIJING = 10*iota  //iota = 10*0
  SHANGHAI        //iota = 10*1
  SHENZHEN				//iota = 10*2
)

const (
	a, b = iota+1, iota+2 	// iota=0 a=0+1,b=0+2
  c, d										// iota=1  c=1+1,b=1+2
  e, f										// iota=2  e=2+1,f=2+2
  g, h  = iota*2, iota*3   // iota=3, g=3*2,h=3*3
  i,k 										// iota=4, g=4*2,h=4*3
)

func main() {
  //常量(只读属性)
  const length int = 10
  
  fmt.Println("length = ", length)
  
  fmt.Println(BEIJING,SHANGHAI,SHENZHEN,a, b, c, d,e, f,g, h,i,k )
  //length = 100 常量不允许修改
}
```

# 函数多返回值

```go
package main

import (
"fmt"
)

// "{"之前的int代表返回值为int型
func foo1(a string, b int) int {
  fmt.Println("a=", a)
  fmt.Println("b=", b)
  c := 100
  return c
}

// (int, int)代表返回值为两个int型,匿名
func foo2(a string, b int) (int, int){
   fmt.Println("a=", a)
   fmt.Println("b=", b)
   c := 100
   d := 200

   return c,d
}

// 返回多个返回值，有形参名，r1,r2属于foo3的形参
func foo3(a string, b int)(r1 int, r2 int){
   fmt.Println("a=", a)
   fmt.Println("b=", b)
  //给有名称的返回值赋值
   r1 = 1000
   r2 = 2000

   return
}

// 多个返回值类型一致
func foo4(a string, b int )(r1, r2 int){
    fmt.Println("a=", a)
   fmt.Println("b=", b)
   r1 = 10000
   r2 = 20000

   return
}

func main() {
  c := foo1("foo1", 333)
  fmt.Println("c=", c)

  ret1, ret2 := foo2("foo2", 999)
  fmt.Println("ret1=", ret1, "ret2=",ret2)

  ret3, ret4 := foo3("foo3", 9999999)
  fmt.Println("ret1=", ret3,"ret2=",ret4)

  // 给类型已经被定义的变量赋值，记得用"="而不是":="
  ret3, ret4 = foo4("foo4", 9999999)
  fmt.Println("ret1=", ret3,"ret2=",ret4)

}

```

# init函数与import导包

执行顺序：-----------> main ---> import pkg ---> const... ---> var... ---> init()--->main()

# import匿名及别名导包

一般情况包导入后必须使用

```go
package main

import (
  //匿名别名(前面加"_")，可以导入后不使用，注意：即使不使用，仍然会执行lib1中的init函数，即：init函数在导入时执行
	_"test/lib1"
  //"test/lib2"
  //别名
  mylib2 "test/lib2"
  // ***将包中的全部方法导入当前的main方法，最好不要轻易使用，容易冲突
  . "test/lib3"
)

func main(){
 // lib1.lib1test()
  //lib2.lib2test()
  //使用别名
  mylib2.lib2test()
  // ***可以直接使用包中的方法
  lib3test()
}
```

# 指针

```go
package main

import "fmt"

func changeValue(p *int){
  *p = 10
}

func main(){
  var a int = 1
  changeValue(&a)
  fmt.Println("a = ", a) //a=10
}

```



```go
package main

import "fmt"

func swap(pa *int, pb *int){
  var temp int 
  temp = *pa // temp = main::a
  *pa = *pb  // main::a = main:b
  *pb = temp // mian::b = temp
}

func main(){
  var a int = 10
  var b int = 20
  
  // 使用swap函数交换值
  swap(&a, &b)
  fmt.Println("a=", a,"b=",b)

  var p *int 
  p = &a
  
  fmt.Println(&a)
  fmt.Println(p)
  
  var pp **int //二级指针
  pp = &p
  fmt.Println(&p)
  fmt.Println(pp)
}
```

# defer语句调用顺序

```go
package main

import "fmt"

func main(){
  // 写入defer关键字，类似java中的final，在函数结束前执的语句
  // 1、可以写多条，压栈模式(stack栈，写入后出)，如下，先执行end2再执行end1
  // 2、调用在return之后
	defer fmt.Println("main end1")
	defer fmt.Println("main end2")
  
	fmt.Println("hello go1")
  fmt.Println("hello go2")
}
```



# 数组与动态数组

- 数组

```go
package main

// 数组传参
// 1、值拷贝，数值不可修改
// 2、[4]int 参数形式的也只能接受[4]int格式的数组，例如一个数组格式为[10]int，是无法传进下面的函数的
func printArray(myArray [4]int){
  for index, value := range myArray{
    fmt.Println("index=", index, ",value=", value)
  }  
  
  // 赋值后，数组本身数据并不会被修改
  myArray[0] = 100
}

func main(){
  //固定长度数组，外面数组元素默认值为零
  var myArray1 [10]int
  
  myArray2 := [4]int{1,2,3,4}
  
  // 两种遍历数组方式
  for i := 0; i < len(myArray1); i++ {
    fmt.Println(myArray1[i])
  }
  
  for index, value := range myArray2{
    fmt.Println("index=", index, ",value=", value)
  }
   
  // 查看数组的数据类型
  fmt.Printf("myArray1 type = %T\n", myArray1)
}
```

 	- 动态数组(切片,slice)

```go
package main

import "fmt"

// 1、引用传递，传递的是数组的指针，可以修改数组的数值
// 2、动态数组本身就是指针
func printArray(myArray []int){
  // _ 表示匿名变量
  for _, value := range myArray{
    fmt.Println("index=", index, ",value=", value)
  }
  
  myArray[0] = 100
}

func main(){
  myArray := []int{1,2,3,4} //动态数组，切片slice
  
  fmt.Println("==========")
  
  for _, value := range myArray{
    fmt.Println("value = ", value)
  }
}
```

# slice

## slice四种声明方式

```go
package main

import "fmt"

func main(){
  // 1、声明slice1是一个切片，并且初始化，默认值是1,2,3，长度是3
  slice1 := []int{1,2,3}
  
  // 2、声明slice2是一个切片，但没有给slice分配空间
  var slice2 []int
  // 开辟空间，开辟空间之前是无法赋值的，即slice1[0]=1 会报错
  slice2 = make([]int, 3) //开辟3个空间，默认值是0
  
  //3、声明slice3是一个切片，同时给slice3分配空间
  var slice3 []int = make([]int, 3)
  
  // 4、声明slice3是一个切片，同时给slice3分配空间（简写）
  slice4 := make([]int, 3)
  
  // 判断一个slice是否为0
  if slice1 == nil {
    fmt.Println("slice1 是空切片")
  } else {
    fmt.Println("slice1 是有空间的")
  }
}

```

## slice追加与截取

### 切片容量的追加

```go
package main

import "fmt"

func main(){
  // num长度为3，容量为5
  var num = make([]int, 3, 5) // [0,0,0] len=3 ,cap=5
  
  fmt.Printf("len = %d,cap =%d, slice = %v\n", len(num), cap(num), num)
  
  //追加元素
  //1、当append超出cap值，cap会动态扩展一倍
  //2、cap值如果不设置，默认等于len
  num = append(num, 1) // [0,0,0,1] len=4 cap=5
  num = append(num, 2)
  num = append(num, 3) // [0,0,0,1,2,3] len=6 cap=10 

}
```

### 切片的截取

```go
package main

import "fmt"

func main(){
  s := []int{1, 2, 3} //len=3,cap=3 [1,2,3]
  
  //1、s1与s实际仍然指向同一指针，如果修改s1，s也会被修改
  //2、copy一个数组
  s2 := make([]int, 3)
  copy(s2, s)
  s1 := s[0:2] //[1,2]
  
  //s1 := s[:] //[1,2,3]
  
  //s1 := s[1:]  //[2,3]
  
  //s1 := s[:1] //[1,2]
  
  //通过切片s切片s1
 // s := make([]int, len, cap)
  
  fmt.Println(s1)
  
}
```

# map

类似python的字典

## map三种定义方式

```go
package main

import "fmt"

func main(){
  // =====>第一种声明方式
  // 声明myMap1是一个map类型 key是string，value是string
  var myMap1 map[string]string
  
  //使用map前，需要先用make给map分配数据空间
  myMap1 = make(map[string]string, 10)
  
  myMap1["one"] = "java"
  myMap1["two"] = "c"
  myMap1["three"] = "c++"
  // 打印的顺序并不是顺序的排序，而是按自带的哈希排序
  fmt.Println(myMap1)
  
  // =====>第二种声明方式
  myMap2 := make(map[string]string, 10)
  myMap2["one"] = "java"
  myMap2["two"] = "c"
  myMap2["three"] = "c++"
  fmt.Println(myMap2)
  
  // ======>第三种声明方式
  myMap3 := map[string]string{
    "one": "java"
    "two": "three"
    "three": "c++"
  }
  fmt.Println(myMap3)
}

```

## map使用方式

```go
package main

//传参
func printMap(cityMap map[string]string){
  // cityMap 是一个引用传递，值可以被修改
  for key, value := range cityMap {
    fmt.Println("key=", key)
    fmt.Println("value=", value)
  }  
}

func main(){
  cityMap := make(map[string]string)
  
  // 添加
  cityMap["China"] = "Beijing"
  cityMap["Japan"] = "Toky"
  cityMap["USA"] = "NewYork"
  
  //删除
  delete(cityMap, "Japan")
  
  //修改
  cityMap["USA"] = "DC"
  
    //遍历
  for key, value := range cityMap {
    fmt.Println("key=", key)
    fmt.Println("value=", value)
  }
  
  printMap(cityMap)
}
```

# 面向对象

## struct 基本定义与使用

```go
package main

import "fmt"

// 声明一种行的数据类型myint,是int的一个别名
type myint int

//定义一个结构体(多种类型组成一个复杂的属性)
type Book struct {
  title string
  auth string
}

// 传参
func changeBook(book Book){
  //传递一个book的副本
  book.auth = "666"
}

func changeBook2(book *Book){
  //指针传递
  book.auth = "777"
}


func main(){
  var book1 Book
  book1.title = "Golang"
  book1.auth = "zhang3"
  
  fmt.Println("%v\n", bookl)
}

```

## 面向对象类的表示与封装

```go
package main

// 类:type + func (this Hero) *

// 类名、属性名、方法名首字母大写，表示对外(其他包)可以访问，否则只能在包内使用
type Hero struct{
  // 如果类的属性首字母大写，表示该属性是对外能提供访问的，否则只能够类的内部访问
  Name string
  Ad int
  level 
}

// 如果类的方法的属性首字母大写，表示该属性是对外能提供服务，即可以在被其他包导入后使用 对象名.Show()
func (this *Hero) Show(){
  fmt.Println("hero = ", this)
  fmt.Println("Name=" this.Name)
  fmt.Println("Ad=" this.Ad)
}

func (this *Hero) GetName() string{
  fmt.Println("Name=" this.Name)
  return this.Name
}

func (this *Hero) SetName(newName string){
  this.Name = newName
}

func main(){
  //创建一个对象
  hero := Hero{Name: "zhange", Ad:100, Level:1}
  
  hero.GetName()
}
```

## 面向对象继承

```go
package main

type Human struct {
	name string
  sex string
}

func (this *Human) Eat(){
  fmt.Print("Human.Eat()...")
}

func (this *Human) Walk(){
  fmt.Print("Human.Walk()...")
}

//新建SuperMan类，即成Human类
type SuperMan struct {
  //SuperMan类继承了Human类的方法
  Human
  
  level int
}

//重定义父类方法Eat()
func (this *SuperMan) Eat(){
  fmt.Println("SuperMan.Eat()....")
}

func (this *SuperMan) Print(){
  fmt.Println("name=", this.name)
  fmt.Println("sex=", this.sex)
  fmt.Println("level," this.level)
}

//子类的新方法
func main(){
  fmt.Println("SuperMan.Fly()...")
}

func main(){
  h := Human{"zhang3", "female"}
  
  h.Eat()
  h.Walk()
  
  //定义一个子类对象
  s := SuperMan{Human("li4", "female"), 88}
  
 /*或者这样定义子类对象
  var s SuperMan
  s.name = "li4"
  s.sex = "male"
  s.level = 88
  */
  
  s.Walk()//父类的方法
  s.Eat()//子类的方法
  s.Fly()//子类的方法
  s.Print()
}

```

## 面向对象多态

多态要素：

- 有一个父类(有接口)
- 有子类(实现了父类的全部接口方法)
- 父类类型的变量(指针)指向(引用)子类的具体数据变量

```go
package main

//本质是一个指针
type AnimalIF interface {
  Sleep()
  GetColor() string
  GetType() string
}

// 具体类
type Cat struct{
  color string //猫的颜色
}

func (this *Cat) Sleep(){
  fmt.Println("Cat is sleep")
}

func (this *Cat) GetColor() string{
  return this.color
}

func (this *Cat) GetType() string{
  return "Cat"
}


//具体类
type Dog struct{
  color string
}

func (this *Dog) Sleep(){
  fmt.Println("Dog is sleep")
}

func (this *Dog) GetColor() string{
  return this.color
}

func (this *Dog) GetType() string{
  return "Dog"
}

func showAnimal(animal AnimalIF){
  animal.Sleep() //多态
  fmt.Println("color=", animal.GetColor())
  fmt.Println("kind=", animal.GetType())
}

func main(){
  /*
  var animal AnimalIF //接口的数据类型，父类指针
  animal = &Cat{"Green"}
  animal.Sleep() //调用的是Cat的Sleep()方法
  
  animal = &Dog{"Yellow"}
  animal.Sleep() //调用Dog的sleep方法，多态现象
  */
  cat := Cat{"Green"}
  dog := Dog{"Yellow"}
  
  showAnimal(&cat)
  showAnimal(&dog)
}

```

# interface空接口万能类型与类型断言机制

Interfance{}特性：

- 空接口
- Int,string,float32,struct.....都实现了interface{}
- 就可以用interface{}类型 引用任意的数据类型

```go
package main()

//interface{}是万能数据类型
func myFunc(arg interface{}){
  fmt.Printon("myFunc is called...")
  fmt.Println(arg)
  
  /* interface{}如何区分 此时的底层数据类型到底是什么？
  	给interface{}提供"类型断言"的机制 arg.(string)
  */
  value, ok := arg.(string)  
  if !ok{
    fmt.Println("arg is not string type")
  } else{
    fmt.Println("arg is not string type, value=", value)  
    fmt.Printf("value type is %T\n", value)
  }  
}

type Book struct {
  auth string
}

func main(){
  book := Book("Golang")
  
  // 都可以打印出来
  myFunc(book)
  myFunc(100)
  myFunc("anc")
  myFunc(3.14)
}

```

# 变量的内置pair结构

变量结构

![image-20211206233749544](https://tva1.sinaimg.cn/large/008i3skNgy1gx4jf7893nj311c0jcaau.jpg)

```go
package main

import (
	"fmt"
	"io"
  "os"
)

func main(){
  var a string
  //pair<static type:string, value:"ace">
  a = "ace"
  
  // pair <concrete type:string, value:"ace">
  // 赋值过程中pair值是不变的
  var allType interface{}
  allType = a
  
  str,_ := allType.(string)
  fmt.Println(str) //ace
  
 
  
  
  
  // pair赋值过程中值是不变的
  // ttp: pair<type: *os.File, value:"/dev/tty"文件描述符>
  tty,err = os.OpenFile("/dev/tty", os.O_RDWR, 0)
  
  if err != nil{
    fmt.Println("open file error", err)
    return
  }
  
  //r: pair<type:	, value:	>
  var r io.Reader
  //r: pair<type: *os.File, value:"/dev/tty"文件描述符>
  r = tty
  
  var w io.Writer
  //r: pair<type: *os.File, value:"/dev/tty"文件描述符>
  w = r.(io.Writer)
  
}
```

# reflect

```go
//ValueOf 用来获取参数接口中的数据的值，如果接口为空则返回0
func ValueOf(i interface{}) Value {...}

// TypeOf 用来动态获取输入参数接口中的值类型，如果为空则返回nil
func TypeOf(i interface{}) Type {...}
```

```go
package mian

import (
	"fmt"
  "reflect"
)

//简单例子
func reflectNum(arg interface{}){
  fmt.Println("type:", reflect.TypeOf(arg))
  fmt.Println("type:", reflect.ValueOf(arg))
}


func main(){
  var num float64 = 1.2345
  reflectNum(num) //result----type:float64 value:1.2345
  
  user: User{1, ""}
}
```

```go
package mian

import (
	"fmt"
  "reflect"
)

// 复杂例子
type User struct{
  Id int
  Name string
  Age	int
}

func (this *User) Call(){
  fmt.Println("user is called ...")
  fmt.Printf("%v\n", this)
}

func main(){
  
  user:= User{1, "Areld", 18}
  
  DofiledAndMethod(user)
}

func DoFileAndMethod(input interface{}){
  //获取input的type
  inputType := reflect.TypeOf(input)
  fmt.Println("inputType is:", inputType.Name())
  
  //获取input的value
  inputValue ：= reflect.ValueOf(input)
  fmt.Println("%s: %v = %v\n", field.Name, field.Type, value)
  
  //通过type获取里面的字段
  //1、获取interface的reflect.Type，通过Type得到NumField，进行遍历
  //2、得到每个field，数据类型
  //3、通过filed有一个indterface()方法等到 对应的value
  for i := 0; i < inputType.NumField();i++{
    field := inputType.Field(i)
    value := inputValue.Field(i).Interface()
    
    fmt.Printf("%s: %v = %v\n", field.Name, field.Type, value)
    /*输出结果：
    inputType is :User
    inputValue is : {i AceId 18}
    Id: int = 1
    Name: string = AceId
    Age: int = 18
    */
  }
  
  //通过type 获取里面的方法，调用
  for i := 0; i < inputType.NumMethod(); i++{
    m := inputType.Method(i)
    fmt.Printf("%s: %v\n", m.Name, m.Type)
    /*输出结果：
     Call: func(main.User)
    */
  }
}

```

# 结构体标签

```go
package main

type resume struct {
  // 定义标签：`doc: "name" ...`
  Name string	`info: "name", doc:"我的名字"`
  Sex string	`info:"sex"`
}


func findTag(str interface()){
  //通过reflect获取元素
  t := reflect.TypeOf(str).Elem()
  
  for i := 0;i<t.NumField(); i++{
    // 获取info标签
    tagstring := t.Field(i).Tag.Get("info")
    fmt.Println("info", tagstring)
  }
}

func main(){
  var re resume
  
  findTag(&re)
}
```

# 结构体标签在json中使用

```go
package main

import (
	"encoding/json"
  "fmt"
)

type Movie struct{
  Title string	`json: "title"`
  Year int	`json: "year"`
  Price int `json: "rmb"`
  Actors []string `json:"actors"`
}

func main(){
  movie := Movie{"喜剧之王", 2000, 10, []string{"xingye", "zhangbozhi"}}
  
  //编码的过程  结构体----> json
  jsonStr, err := json.Marshal(movie)
  if err != nil{
    fmt.Println("json marshal error", err)
    return
  }
  
  fmt.Printf("jsonStr=%s\n", jsonStr)
  
  
  myMovie := Movie{}
  //解码的过程  json ----> 结构体
  err = json.Unmarshal(jsonStr, &myMovie)
  if err != nil{
    fmt.Println("json unmarshal error", err)
    return
  }
  fmt.Printf("jsonStr=%s\n", jsonStr)
}
```

# goroutine

## 创建goroutine

```go
package main

//从goroutine
func newTask(){
  i := 0
  for {
    i++
    fmt.Printf("new goroutine : i =%d\n", i)
    time.Sleep(1*time.Second)
  }
  // 退出当前goroutine
  runtime.Goexit()
}

//主goroutine
func main(){
  //创建一个goroutine 去执行newTask
  go newTask()
  
  i := 0
  
  for {
    i++
    fmt.Printf(i)
    time.Sleep(1*time.Second)
  }
  
  //匿名函数
  go func(a int, b int){
    fmt.Println("a=",a, "b=", b)
    return true
  }(10,20)
  
}
```

# channel

多个goroutine之间数据交互

## 创建一个channel

```go
package main

import "fmt"

func main(){
  //定义一个channel
  c := make(chan int)
  
  go func(){
    defer fmt.Println("goroutine结束")
    
    fmt.Println("goroutine 正在运行...")
    
    c <- 666 //将666发送给c
  }()
  
  num := <-c //从c中接受数据，并赋值给num
  
  fmt.Println("num =", num)
  fmt.Println("main goroutine 结束...") 
}
```

```go
// goroutine1 与 goroutine2 会有同步机制，即，goroutine1如果已经写入channel数据，goroutine2从channel取出数据之前goroutine1会处于阻塞状态(无缓冲)
graph LR;
	goroutine1-->channel[cname]
	channel[cname]-->goroutine2
```

## 有缓冲无缓冲channel

- 特点
  - 当channel已经满，再向里面写数据，就会阻塞
  - 当channel为空，从里面取数据也会阻塞

```go
package main

import (
	"fmt"
  "time"
)

func main(){
  c := make(chan int, 3) //带有缓冲的channel
  
  fmt.Println("len(c) = ", len(c), ", cap(c)", cap(c))
  
  go func(){
    defer fmt.Println("子go程结束")
    
    for i := 0; i<4; i++ {
      c <- i
      fmt.Println("子go程正在运行，发送的元素="， i, "len(c)=", len(c), ",cap(c)",cap(c))
    }
  }()
  
  time.Sleep(2 * time.Second)
  
  for i :=0; i<4; i++{
    num := <-c //从c中接收数据，并复制给num
    fmt.Println("num=", num)
  }
  
  fmt.Println("main 结束")
  
}


```

## 关闭channel

- 确定没有数据写入了可以关闭channel
- channel关闭后无法向内写数据
- 关闭channel后，可以继续从中接收数据
- 对于nil channel，无论收发都会被阻塞

```go
package main

func main(){
  c: make(chan int)
  
  go func(){
    for i := 0; i<5; i++{
      c <- i
    }
    
    //close 可以关闭一个channel
    close()
  }()
  
  for {
    // ok 如果为true表示channel没有关闭，如果为false表示channel已经关闭
    if data, ok := <-c; ok{
      fmt.Println(data)
    } else{
      break
    }
  }
  
  fmt.Println("Main Finished...")
}
```

## channel与range

```go
package main

func main(){
  c: make(chan int)
  
  go func(){
    for i := 0; i<5; i++{
      c <- i
    }
    
    //close 可以关闭一个channel
    close()
  }()
  
  //可以使用range迭代数据
  for data := range c{
    fmt.Println(data)
  }
  
  fmt.Println("Main Finished...")
}
```

## channel与select

单流程下一个go只能监控一个channel的状态，select可以完成监控多个channel的状态

```go
package main

import "fmt"

func fibonacii(c, quit chan int){
  x, y := 1,1
  
  for {
    select {
      case c <-x:
      	//如果c可写，则case就会进来
      	x = y
      	y = x + y
      case <- quit:
      fmt.Print("quit")
      return
    }
  }
}

func main(){
  c := make(chan int)
  quit := make(chan int)
  
  go runc(){
    for i := 0; i<6; i++{
      fmt.Println(<-c)
    }
    
    quit <-0
  }()
  
  //main.go
  fibonacii(c, quit)
}
```



# 常用方法

## flag

```go
package main

import (
  "flag"
  "fmt"
  "strings"
)

//flag.Bool还会提供-h或--help参数是输出的消息
var n = flag.Bool("n", false, "omit trailing newline")  // -n 使echo忽略正常输出时结尾换行符;
var sep = flag.String("s", " ", "separator")  // -s sep 使用sep替换默认参数输出时使用的空格分隔符

func main(){
  flag.Parse() //更新标识变量的默认值
  fmt.Print(strings.Join(flag.Args(), *sep))
  if !*n {  
    fmt.Println()
  }
}
```























